import hashlib
from collectors.cleaners.text_cleaner import normalize_title, normalize_company, normalize_location

def generate_job_hash(title: str, company: str, location: str) -> str:
    """
    Generates a unique MD5 hash based on normalized title, company, and location.
    Used to identify duplicate job postings across different sources.
    """
    t = normalize_title(title)
    c = normalize_company(company)
    l = normalize_location(location)
    raw_string = f"{t}|{c}|{l}"
    return hashlib.md5(raw_string.encode('utf-8')).hexdigest()
