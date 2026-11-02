import streamlit as st

st.set_page_config(page_title="PYQ Planner", layout="wide")
st.title("PYQ Planner")
st.write("Upload your syllabus and previous year papers to get a study strategy.")

syllabus = st.file_uploader("Syllabus PDF", type="pdf")
papers = st.file_uploader("Previous year papers (PDFs)", type="pdf", accept_multiple_files=True)

if st.button("Analyze"):
    st.write("Syllabus:", syllabus.name if syllabus else "none")
    st.write("Papers:", len(papers))
    for p in papers:
        st.write("-", p.name)