import io

import streamlit as st

from extract import detect_year, looks_scanned, read_pdf_pages, remove_repeated_lines
from ocr import ocr_pdf_pages

st.set_page_config(page_title="PYQ Planner", layout="wide")
st.title("PYQ Planner")
st.write("Upload your syllabus and previous year papers to get a study strategy.")


@st.cache_data(show_spinner=False)
def load_paper(data):
    """Read a PDF's text, using OCR for scanned PDFs. Cached by file content."""
    pages = read_pdf_pages(io.BytesIO(data))
    scanned = looks_scanned(pages)
    if scanned:
        pages = ocr_pdf_pages(data)
    return remove_repeated_lines(pages), scanned


syllabus = st.file_uploader("Syllabus PDF", type="pdf")
papers = st.file_uploader("Previous year papers (PDFs)", type="pdf", accept_multiple_files=True)

if st.button("Analyze"):
    if not papers:
        st.warning("Upload at least one question paper.")
        st.stop()
    for paper in papers:
        with st.spinner(f"Reading {paper.name} (scanned pages take a few seconds each)..."):
            pages, scanned = load_paper(paper.getvalue())
        year = detect_year(paper.name, pages[0] if pages else "")
        with st.expander(f"{paper.name} | year: {year} | {len(pages)} pages", expanded=True):
            if scanned:
                st.info("Scanned PDF: the text was read with OCR, so check it for mistakes.")
            if not "".join(pages).strip():
                st.warning("No text could be read from this file.")
            st.text("\n\n".join(pages))