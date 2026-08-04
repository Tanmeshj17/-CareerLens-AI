import hashlib
from collectors.cleaners.text_cleaner import normalize_title, normalize_company, normalize_location

def legacy_generate_job_hash(title: str, company: str, location: str) -> str:
    """Legacy MD5 hash (Phase 1-8.5). Will be phased out."""
    t = normalize_title(title)
    c = normalize_company(company)
    l = normalize_location(location)
    raw_string = f"{t}|{c}|{l}"
    return hashlib.md5(raw_string.encode('utf-8')).hexdigest()

def generate_sha256_fingerprint(title: str, company: str, location: str, salary: str, source_job_id: str, description: str, job_type: str) -> str:
    """Phase 8.6: Strict SHA256 fingerprint for precise job identity."""
    t = normalize_title(title)
    c = normalize_company(company)
    l = normalize_location(location)
    
    # Normalize extra fields for hashing
    s = str(salary).strip().lower() if salary else ""
    j_id = str(source_job_id).strip().lower() if source_job_id else ""
    # For description, take first 200 chars normalized to catch minor changes vs total different roles
    d = str(description).strip().lower()[:200] if description else ""
    j_type = str(job_type).strip().lower() if job_type else ""
    
    raw_string = f"{t}|{c}|{l}|{s}|{j_id}|{d}|{j_type}"
    return hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

# Backward-compatible alias — keeps any surviving imports working
generate_job_hash = legacy_generate_job_hash
