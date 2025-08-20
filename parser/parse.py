import re
from typing import List, Dict
from .patterns import SECTION_HEADERS, EMAIL_RE, PHONE_RE, DEGREE_RE

def _extract_contact(text: str) -> Dict[str, str]:
    email = EMAIL_RE.search(text)
    phone = PHONE_RE.search(text)
    # name heuristic: first non-empty line that isn't email/phone/section
    name = ""
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if EMAIL_RE.search(s) or PHONE_RE.search(s):
            continue
        if any(p.search(s) for p in SECTION_HEADERS.values()):
            continue
        # keep it short-ish
        if 2 <= len(s.split()) <= 6 and len(s) <= 60:
            name = s
            break
    return {
        "name": name,
        "email": email.group(0) if email else "",
        "phone": phone.group(0) if phone else ""
    }

def _split_sections(text: str) -> Dict[str, List[str]]:
    lines = text.splitlines()
    sections = {"skills": [], "education": [], "experience": [], "other": []}
    current = "other"

    for ln in lines:
        line = ln.strip()
        if not line:
            continue
        matched = False
        for key, pat in SECTION_HEADERS.items():
            if pat.search(line):
                current = key
                matched = True
                break
        if matched:
            continue
        sections[current].append(line)
    return sections

def _extract_skills(nlp, sections, skills_list: set) -> List[str]:
    # Prefer explicit skills section; otherwise scan whole text
    candidates = []
    if sections.get("skills"):
        candidates = sections["skills"]
    else:
        # take the first 30 lines as summary area
        candidates = sum([sections.get("other", [])[:30], sections.get("experience", [])[:10]], [])

    text = " ".join(candidates).lower()
    found = set()
    # dictionary match (fast + robust)
    for skill in skills_list:
        if len(skill) < 2: 
            continue
        if skill in text:
            found.add(skill)
    # simple lemmatized token match (to catch plurals)
    doc = nlp(" ".join(candidates))
    tokens = {t.lemma_.lower() for t in doc if not t.is_punct and not t.is_space}
    for skill in skills_list:
        if skill in tokens:
            found.add(skill)
    return sorted(found)

def _extract_education(sections) -> List[str]:
    edu_lines = sections.get("education", [])
    if not edu_lines:
        # backstop: scan entire text-ish
        edu_lines = [l for l in (sections.get("other", []) + sections.get("experience", [])) if DEGREE_RE.search(l)]
    # group lines into bullet-like items
    items, buf = [], []
    for line in edu_lines:
        if re.match(r"^[-•\u2022]\s+", line):
            if buf: items.append(" ".join(buf)); buf=[]
            items.append(line.lstrip("-•\u2022 ").strip())
        elif any(w in line.lower() for w in ["university", "college", "institute", "school"]) or DEGREE_RE.search(line):
            buf.append(line.strip())
        else:
            if buf: 
                buf.append(line.strip())
                items.append(" ".join(buf)); buf=[]
    if buf:
        items.append(" ".join(buf))
    # dedupe and clean
    seen, out = set(), []
    for i in items:
        s = re.sub(r"\s+", " ", i).strip()
        if s and s.lower() not in seen:
            out.append(s); seen.add(s.lower())
    return out[:10]

def _extract_experience(sections) -> List[str]:
    exp_lines = sections.get("experience", [])
    # Heuristic chunking by bullets or company-like lines
    items, buf = [], []
    for line in exp_lines:
        if re.match(r"^[-•\u2022]\s+", line):
            if buf: items.append(" ".join(buf)); buf=[]
            items.append(line.lstrip("-•\u2022 ").strip())
        elif any(w in line.lower() for w in ["company", "inc", "llc", "technologies", "solutions", "engineer", "developer", "manager"]):
            if buf: items.append(" ".join(buf)); buf=[]
            buf.append(line.strip())
        else:
            buf.append(line.strip())
    if buf: items.append(" ".join(buf))
    # cleanup
    out = []
    seen = set()
    for i in items:
        s = re.sub(r"\s+", " ", i).strip()
        if len(s) > 5 and s.lower() not in seen:
            out.append(s); seen.add(s.lower())
    return out[:15]

def parse_resume(text: str, nlp, skills_list: set) -> Dict:
    contact = _extract_contact(text)
    sections = _split_sections(text)
    skills = _extract_skills(nlp, sections, skills_list)
    education = _extract_education(sections)
    experience = _extract_experience(sections)
    return {
        **contact,
        "skills": skills,
        "education": education,
        "experience": experience
    }
