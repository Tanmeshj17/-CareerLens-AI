import re

def clean_text(text: str) -> str:
    if not text:
        return ""
    # Remove excessive whitespace, replace smart quotes, etc.
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")
    return text.strip()

def normalize_title(title: str) -> str:
    if not title:
        return ""
    title = title.lower()
    # Remove terms like "hiring", "immediate joiner", "urgent", etc.
    title = re.sub(r'\b(hiring|immediate|urgent|joiner|needed|wanted|apply)\b', '', title)
    # Remove details in parentheses
    title = re.sub(r'\(.*?\)', '', title)
    # Remove extra spaces and special characters
    title = re.sub(r'[^a-zA-Z0-9\s#\+\.]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title.strip()

def normalize_company(company: str) -> str:
    if not company:
        return ""
    company = company.lower()
    # Remove common suffixes like inc, ltd, corp, pvt, co
    company = re.sub(r'\b(inc|ltd|corp|corporation|pvt|private|limited|co|company|solutions|technologies|services)\b', '', company)
    company = re.sub(r'[^a-zA-Z0-9\s]', '', company)
    company = re.sub(r'\s+', ' ', company)
    return company.strip()

def normalize_location(location: str) -> str:
    if not location:
        return "remote"
    location = location.lower()
    # Standardize hybrid / remote
    if "remote" in location:
        return "remote"
    if "hybrid" in location:
        # Keep city, but tag as hybrid
        city_match = re.sub(r'\(hybrid\)|hybrid', '', location)
        city = re.sub(r'[^a-zA-Z0-9\s]', '', city_match).strip()
        return f"{city} (hybrid)"
    location = re.sub(r'[^a-zA-Z0-9\s]', '', location)
    location = re.sub(r'\s+', ' ', location)
    return location.strip()
