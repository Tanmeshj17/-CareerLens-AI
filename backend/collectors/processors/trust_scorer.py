TRUST_SCORES = {
    "official career page": 100,
    "official": 100,
    "linkedin": 90,
    "wellfound": 85,
    "angel.co": 85,
    "cutshort": 85,
    "naukri": 80,
    "foundit": 75,
    "monster": 75,
    "indeed": 75,
}

def calculate_trust_score(source_name: str) -> int:
    if not source_name:
        return 60
    norm_source = source_name.lower().strip()
    # Check direct match
    if norm_source in TRUST_SCORES:
        return TRUST_SCORES[norm_source]
    # Check partial match
    for key, score in TRUST_SCORES.items():
        if key in norm_source or norm_source in key:
            return score
    return 60
