import io
import json
import pandas as pd
import streamlit as st
from parser.extract import extract_text_from_pdf_bytes, extract_text_from_docx_bytes
from parser.normalize import clean_text
from parser.parse import parse_resume
from parser.nlp import get_nlp
from parser.patterns import load_skills_list

st.set_page_config(page_title="Smart Resume Parser", page_icon="🧠", layout="wide")

st.title("🧠 Smart Resume Parser")
st.caption("Extract skills, education, experience, and contact info from resumes (PDF/DOCX).")

nlp = get_nlp()
skills_master = load_skills_list()

uploaded = st.file_uploader("Upload one or more resumes (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

results = []
if uploaded:
    with st.spinner("Parsing resumes..."):
        for file in uploaded:
            try:
                if file.type == "application/pdf" or file.name.lower().endswith(".pdf"):
                    text = extract_text_from_pdf_bytes(file.read())
                else:
                    text = extract_text_from_docx_bytes(file.read())

                cleaned = clean_text(text)
                parsed = parse_resume(cleaned, nlp, skills_master)
                parsed["source_file"] = file.name
                results.append(parsed)
            except Exception as e:
                results.append({
                    "source_file": file.name,
                    "name": "",
                    "email": "",
                    "phone": "",
                    "skills": [],
                    "education": [],
                    "experience": [],
                    "error": str(e)
                })

if results:
    # Normalize for display
    def flatten_for_table(r):
        return {
            "source_file": r.get("source_file", ""),
            "name": r.get("name", ""),
            "email": r.get("email", ""),
            "phone": r.get("phone", ""),
            "skills": ", ".join(r.get("skills", [])),
            "education": " | ".join(r.get("education", [])),
            "experience": " | ".join(r.get("experience", [])),
            "error": r.get("error", "")
        }
    table = pd.DataFrame([flatten_for_table(r) for r in results])

    st.subheader("Parsed Results")
    st.dataframe(table, use_container_width=True)

    # Downloads
    st.download_button(
        "⬇️ Download JSON", data=json.dumps(results, indent=2), file_name="resume_parsed.json", mime="application/json"
    )
    st.download_button(
        "⬇️ Download CSV", data=table.to_csv(index=False), file_name="resume_parsed.csv", mime="text/csv"
    )
else:
    st.info("Upload some resumes to see parsed results.")
