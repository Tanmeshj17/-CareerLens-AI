import re

def parse_salary(salary_string: str):
    """
    Phase 8.6: Parse raw salary string to structured values.
    Defaults to INR (₹) if none is specified.
    """
    if not salary_string:
        return None, None, "INR", None

    s = salary_string.lower().replace(",", "")
    
    currency = "INR"
    if "$" in s or "usd" in s: currency = "USD"
    elif "€" in s or "eur" in s: currency = "EUR"
    elif "£" in s or "gbp" in s: currency = "GBP"
    elif "aed" in s: currency = "AED"
    
    period = "Yearly"
    if "month" in s or "pm" in s or "/mo" in s:
        period = "Monthly"
    elif "hour" in s or "/hr" in s:
        period = "Hourly"
        
    # Extract numbers
    # Pattern to find numbers which might have decimals e.g., 8.5
    numbers = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', s)]
    
    # Scale multipliers (lpa = * 100,000, k = * 1000)
    multiplier = 1
    if "lpa" in s or "lakh" in s or "lac" in s:
        multiplier = 100000
    elif "k" in s and not "k month" in s: # basic check for 'k' meaning thousand
        # But wait, "10k" usually means 10,000. Let's do it if 'k' follows a digit.
        pass

    # A better check for multipliers
    if "lpa" in s or "lakh" in s or "lac" in s:
        multiplier = 100000
        period = "Yearly" # LPA is explicitly Yearly
        
    # Apply 'k' multiplier for digits followed by 'k'
    for match in re.finditer(r'(\d+(?:\.\d+)?)\s*k\b', s):
        val = float(match.group(1)) * 1000
        if val not in numbers:
            numbers.append(val)
        # Remove the unmultiplied base from numbers if it exists
        if float(match.group(1)) in numbers:
            numbers.remove(float(match.group(1)))

    if not numbers:
        return None, None, currency, period
        
    numbers = sorted([n * multiplier if n < 1000 and multiplier > 1 else n for n in numbers])
    
    if len(numbers) == 1:
        return int(numbers[0]), int(numbers[0]), currency, period
    else:
        return int(numbers[0]), int(numbers[-1]), currency, period
