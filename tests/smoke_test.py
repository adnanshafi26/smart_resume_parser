from parser.normalize import clean_text
from parser.parse import parse_resume
from parser.patterns import load_skills_list
from parser.nlp import get_nlp

SAMPLE = """
John A. Doe
Email: john.doe@example.com | +1 555-123-4567

SKILLS
Python, Pandas, NumPy, SQL, Docker, AWS

EXPERIENCE
Software Engineer, Example Inc. (2021 - Present)
- Built data pipelines in Python and SQL on AWS

EDUCATION
B.Tech, Computer Science, ABC University, 2017 - 2021
"""

def test_parse_minimal():
    nlp = get_nlp()
    skills = load_skills_list()
    parsed = parse_resume(clean_text(SAMPLE), nlp, skills)
    assert "john.doe@example.com" == parsed["email"]
    assert "python" in parsed["skills"]
    assert any("Software Engineer" in e for e in parsed["experience"])
    assert any("B.Tech" in e or "Computer Science" in e for e in parsed["education"])
