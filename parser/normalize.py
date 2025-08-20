import re
from unidecode import unidecode

def clean_text(text: str) -> str:
    if not text:
        return ""
    t = unidecode(text)              # normalize unicode accents
    t = t.replace("\r", "\n")
    t = re.sub(r"[ \t]+", " ", t)    # collapse spaces
    t = re.sub(r"\n{2,}", "\n\n", t) # collapse blank lines
    t = t.strip()
    return t
