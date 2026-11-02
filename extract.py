import re
from collections import Counter

import pdfplumber

QUESTION_START = re.compile(r"^(q\.?\s*#|\(?[a-z#]{1,4}\)|#[.)])")


def read_pdf_pages(file):
    """Return the text of each page of a PDF (a file path or an uploaded file)."""
    pages = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return pages


def normalise_line(line):
    """Lowercase a line and replace digits, so 'Page 1 of 4' and 'Page 2 of 4' match."""
    return re.sub(r"\d+", "#", line.strip().lower())


def remove_repeated_lines(pages, min_share=0.6):
    """Remove lines that appear on most pages (headers, footers, page numbers)."""
    if len(pages) < 3:
        return pages
    counts = Counter()
    for text in pages:
        counts.update({normalise_line(l) for l in text.splitlines() if l.strip()})
    limit = len(pages) * min_share
    noisy = {
        line for line, n in counts.items()
        if n >= limit and not QUESTION_START.match(line)
    }
    return [
        "\n".join(l for l in text.splitlines() if normalise_line(l) not in noisy)
        for text in pages
    ]


def detect_year(filename, first_page_text=""):
    """Find a 4-digit year in the file name, then in the first page."""
    for source in (filename, first_page_text):
        match = re.search(r"(?<!\d)((?:19|20)\d{2})(?!\d)", source)
        if match:
            return match.group(1)
    return "Unknown"


def looks_scanned(pages):
    """A PDF with almost no extractable text is probably a scan."""
    chars = sum(len(p.strip()) for p in pages)
    return chars < 50 * max(len(pages), 1)