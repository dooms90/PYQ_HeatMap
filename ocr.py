import numpy as np
import pymupdf

_engine = None


def _get_engine():
    """Load the OCR model once; loading takes a few seconds."""
    global _engine
    if _engine is None:
        from rapidocr_onnxruntime import RapidOCR
        _engine = RapidOCR()
    return _engine


def _group_into_lines(boxes):
    """Turn OCR boxes [(points, text, score)] into text lines, top to bottom, left to right."""
    items = []
    for points, text, _score in boxes:
        ys = [p[1] for p in points]
        xs = [p[0] for p in points]
        items.append({"x": min(xs), "top": min(ys), "bottom": max(ys), "text": text})
    items.sort(key=lambda i: i["top"])
    lines = []
    for item in items:
        centre = (item["top"] + item["bottom"]) / 2
        height = item["bottom"] - item["top"]
        if lines and abs(centre - lines[-1]["centre"]) < height * 0.6:
            lines[-1]["items"].append(item)
        else:
            lines.append({"centre": centre, "items": [item]})
    return [
        " ".join(i["text"] for i in sorted(line["items"], key=lambda i: i["x"]))
        for line in lines
    ]


def ocr_pdf_pages(data, zoom=2.5):
    """OCR every page of a PDF given as bytes. Returns one text string per page."""
    engine = _get_engine()
    pages = []
    with pymupdf.open(stream=data, filetype="pdf") as doc:
        for page in doc:
            pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), colorspace=pymupdf.csRGB)
            image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
            result, _ = engine(image)
            pages.append("\n".join(_group_into_lines(result or [])))
    return pages