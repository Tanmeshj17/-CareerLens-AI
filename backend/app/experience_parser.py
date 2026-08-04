import re
from typing import Tuple

def parse_experience(exp_string: str) -> Tuple[int, int, str]:
    """
    Parses unstructured experience strings into min_experience, max_experience, and category.
    Returns (min_exp, max_exp, category).
    Category can be: 'Fresher', 'Entry', 'Junior', 'Mid', 'Senior', 'Expert', 'Unknown'
    """
    if not exp_string:
        return (0, 0, 'Unknown')
        
    s = exp_string.lower().strip()
    
    # Fresher keywords
    if "fresher" in s or "0 years" in s or s == "0":
        return (0, 0, 'Fresher')
        
    # Ranges like 0-1, 1-2, 2-4, 7-10
    range_match = re.search(r'(\d+)\s*-\s*(\d+)', s)
    if range_match:
        min_exp = int(range_match.group(1))
        max_exp = int(range_match.group(2))
    else:
        # Single numbers like "3+ Years", "5 Years"
        single_match = re.search(r'(\d+)', s)
        if single_match:
            min_exp = int(single_match.group(1))
            # if there's a '+', assume max is min + 2
            max_exp = min_exp + 2 if '+' in s else min_exp
        else:
            if "entry" in s:
                return (0, 1, 'Entry')
            elif "experienced" in s or "expert" in s:
                return (5, 10, 'Expert')
            else:
                return (0, 0, 'Unknown')
                
    # Determine category based on min_exp
    if min_exp == 0 and max_exp <= 1:
        category = 'Entry'
    elif min_exp <= 2:
        category = 'Junior'
    elif min_exp <= 5:
        category = 'Mid'
    elif min_exp <= 8:
        category = 'Senior'
    else:
        category = 'Expert'
        
    return (min_exp, max_exp, category)
