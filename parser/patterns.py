import re
import csv
from pathlib import Path

# Section headers (common variants)
SECTION_HEADERS = {
    "skills": re.compile(r"^\s*(skills|technical skills|key skills)\b[:\-]?", re.I),
    "education": re.compile(r"^\s*(education|academic background|qualifications)\b[:\-]?", re.I),
    "experience": re.compile(r"^\s*(experience|work experience|professional experience|employment history)\b[:\-]?", re.I),
    "projects": re.compile(r"^\s*(projects|personal projects)\b[:\-]?", re.I),
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s\-\.]?)?(\(?\d{2,4}\)?[\s\-\.]?)?\d{3,4}[\s\-\.]?\d{4}")

DEGREE_RE = re.compile(
    r"\b(B\.?E\.?|B\.?Tech\.?|B\.?Sc\.?|B\.?A\.?|M\.?E\.?|M\.?Tech\.?|M\.?Sc\.?|M\.?A\.?|MBA|Ph\.?D\.?)\b", re.I
)

def load_skills_list():
    """Load skills corpus from data/skills_master.csv (one skill per line)."""
    csv_path = Path(__file__).resolve().parents[1] / "data" / "skills_master.csv"
    skills = set()
    if csv_path.exists():
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.reader(f):
                if not row: 
                    continue
                skills.add(row[0].strip().lower())
    else:
        # fallback mini-list
        skills = {"python", "java", "c++", "javascript", "html", "css", "sql", "react", "node.js", "pandas", "numpy", "spacy"}
    return skills
