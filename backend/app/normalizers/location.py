"""
Phase 11.4 T6: Location Normalization
Maps raw location strings to structured city/state/country.
Handles Indian city aliases, NCR metro region, remote variants.

Examples:
  Bangalore → {city: Bengaluru, state: Karnataka, country: India}
  Mumbai Metropolitan → {city: Mumbai, state: Maharashtra, country: India}
  Pimpri Chinchwad → {city: Pune, state: Maharashtra, country: India}
  WFH → {city: Remote, state: None, country: India, is_remote: True}
"""
import re
import logging
from typing import Optional
from sqlalchemy.orm import Session
import functools

logger = logging.getLogger("location_normalizer")


# ─────────────────────────────────────────────────────────────
# Location normalization map
# Format: "raw_lower" → {"city": ..., "state": ..., "country": ..., "is_remote": bool}
# ─────────────────────────────────────────────────────────────
LOCATION_MAP: dict[str, dict] = {

    # ─── Bengaluru ───────────────────────────────────────────
    "bangalore": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "bengaluru": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "bengaluru urban": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "bengaluru rural": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "bangalore urban": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "bangalore rural": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "bangalore karnataka": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "bengaluru, karnataka": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "bangalore, karnataka": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "bengaluru, india": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "whitefield": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "electronic city": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "koramangala": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "hsr layout": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "indiranagar": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},
    "marathahalli": {"city": "Bengaluru", "state": "Karnataka", "country": "India"},

    # ─── Mumbai ──────────────────────────────────────────────
    "mumbai": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "bombay": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "mumbai metropolitan": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "greater mumbai": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "mumbai, maharashtra": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "mumbai city": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "bandra": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "andheri": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "powai": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "lower parel": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "worli": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "bkc": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
    "bandra kurla complex": {"city": "Mumbai", "state": "Maharashtra", "country": "India"},

    # ─── Navi Mumbai / Thane ─────────────────────────────────
    "navi mumbai": {"city": "Navi Mumbai", "state": "Maharashtra", "country": "India"},
    "thane": {"city": "Thane", "state": "Maharashtra", "country": "India"},

    # ─── Pune ────────────────────────────────────────────────
    "pune": {"city": "Pune", "state": "Maharashtra", "country": "India"},
    "pimpri chinchwad": {"city": "Pune", "state": "Maharashtra", "country": "India"},
    "pimpri-chinchwad": {"city": "Pune", "state": "Maharashtra", "country": "India"},
    "hinjewadi": {"city": "Pune", "state": "Maharashtra", "country": "India"},
    "hinjawadi": {"city": "Pune", "state": "Maharashtra", "country": "India"},
    "pune, maharashtra": {"city": "Pune", "state": "Maharashtra", "country": "India"},
    "hadapsar": {"city": "Pune", "state": "Maharashtra", "country": "India"},
    "kharadi": {"city": "Pune", "state": "Maharashtra", "country": "India"},
    "magarpatta": {"city": "Pune", "state": "Maharashtra", "country": "India"},
    "wakad": {"city": "Pune", "state": "Maharashtra", "country": "India"},
    "baner": {"city": "Pune", "state": "Maharashtra", "country": "India"},

    # ─── Delhi NCR ───────────────────────────────────────────
    "delhi": {"city": "Delhi", "state": "Delhi", "country": "India"},
    "new delhi": {"city": "Delhi", "state": "Delhi", "country": "India"},
    "ncr": {"city": "Delhi NCR", "state": "Delhi", "country": "India"},
    "delhi ncr": {"city": "Delhi NCR", "state": "Delhi", "country": "India"},
    "delhi/ncr": {"city": "Delhi NCR", "state": "Delhi", "country": "India"},
    "national capital region": {"city": "Delhi NCR", "state": "Delhi", "country": "India"},
    "gurugram": {"city": "Gurugram", "state": "Haryana", "country": "India"},
    "gurgaon": {"city": "Gurugram", "state": "Haryana", "country": "India"},
    "noida": {"city": "Noida", "state": "Uttar Pradesh", "country": "India"},
    "greater noida": {"city": "Greater Noida", "state": "Uttar Pradesh", "country": "India"},
    "faridabad": {"city": "Faridabad", "state": "Haryana", "country": "India"},
    "ghaziabad": {"city": "Ghaziabad", "state": "Uttar Pradesh", "country": "India"},

    # ─── Hyderabad ───────────────────────────────────────────
    "hyderabad": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
    "secunderabad": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
    "hyderabad, telangana": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
    "cyberabad": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
    "hitech city": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
    "hitec city": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
    "gachibowli": {"city": "Hyderabad", "state": "Telangana", "country": "India"},
    "madhapur": {"city": "Hyderabad", "state": "Telangana", "country": "India"},

    # ─── Chennai ─────────────────────────────────────────────
    "chennai": {"city": "Chennai", "state": "Tamil Nadu", "country": "India"},
    "madras": {"city": "Chennai", "state": "Tamil Nadu", "country": "India"},
    "chennai, tamil nadu": {"city": "Chennai", "state": "Tamil Nadu", "country": "India"},
    "siruseri": {"city": "Chennai", "state": "Tamil Nadu", "country": "India"},
    "sholinganallur": {"city": "Chennai", "state": "Tamil Nadu", "country": "India"},

    # ─── Kolkata ─────────────────────────────────────────────
    "kolkata": {"city": "Kolkata", "state": "West Bengal", "country": "India"},
    "calcutta": {"city": "Kolkata", "state": "West Bengal", "country": "India"},
    "kolkata, west bengal": {"city": "Kolkata", "state": "West Bengal", "country": "India"},
    "salt lake city": {"city": "Kolkata", "state": "West Bengal", "country": "India"},
    "sector v kolkata": {"city": "Kolkata", "state": "West Bengal", "country": "India"},

    # ─── Other Indian Cities ─────────────────────────────────
    "ahmedabad": {"city": "Ahmedabad", "state": "Gujarat", "country": "India"},
    "surat": {"city": "Surat", "state": "Gujarat", "country": "India"},
    "vadodara": {"city": "Vadodara", "state": "Gujarat", "country": "India"},
    "baroda": {"city": "Vadodara", "state": "Gujarat", "country": "India"},

    "coimbatore": {"city": "Coimbatore", "state": "Tamil Nadu", "country": "India"},
    "trichy": {"city": "Tiruchirappalli", "state": "Tamil Nadu", "country": "India"},
    "tiruchirappalli": {"city": "Tiruchirappalli", "state": "Tamil Nadu", "country": "India"},
    "madurai": {"city": "Madurai", "state": "Tamil Nadu", "country": "India"},

    "jaipur": {"city": "Jaipur", "state": "Rajasthan", "country": "India"},
    "jodhpur": {"city": "Jodhpur", "state": "Rajasthan", "country": "India"},
    "udaipur": {"city": "Udaipur", "state": "Rajasthan", "country": "India"},

    "bhopal": {"city": "Bhopal", "state": "Madhya Pradesh", "country": "India"},
    "indore": {"city": "Indore", "state": "Madhya Pradesh", "country": "India"},

    "lucknow": {"city": "Lucknow", "state": "Uttar Pradesh", "country": "India"},
    "kanpur": {"city": "Kanpur", "state": "Uttar Pradesh", "country": "India"},
    "agra": {"city": "Agra", "state": "Uttar Pradesh", "country": "India"},

    "chandigarh": {"city": "Chandigarh", "state": "Punjab", "country": "India"},
    "mohali": {"city": "Mohali", "state": "Punjab", "country": "India"},
    "panchkula": {"city": "Panchkula", "state": "Haryana", "country": "India"},
    "amritsar": {"city": "Amritsar", "state": "Punjab", "country": "India"},

    "patna": {"city": "Patna", "state": "Bihar", "country": "India"},
    "bhubaneswar": {"city": "Bhubaneswar", "state": "Odisha", "country": "India"},
    "nagpur": {"city": "Nagpur", "state": "Maharashtra", "country": "India"},

    "kochi": {"city": "Kochi", "state": "Kerala", "country": "India"},
    "cochin": {"city": "Kochi", "state": "Kerala", "country": "India"},
    "thiruvananthapuram": {"city": "Thiruvananthapuram", "state": "Kerala", "country": "India"},
    "trivandrum": {"city": "Thiruvananthapuram", "state": "Kerala", "country": "India"},
    "calicut": {"city": "Kozhikode", "state": "Kerala", "country": "India"},
    "kozhikode": {"city": "Kozhikode", "state": "Kerala", "country": "India"},

    "mangalore": {"city": "Mangaluru", "state": "Karnataka", "country": "India"},
    "mangaluru": {"city": "Mangaluru", "state": "Karnataka", "country": "India"},
    "mysore": {"city": "Mysuru", "state": "Karnataka", "country": "India"},
    "mysuru": {"city": "Mysuru", "state": "Karnataka", "country": "India"},
    "hubli": {"city": "Hubballi", "state": "Karnataka", "country": "India"},
    "hubballi": {"city": "Hubballi", "state": "Karnataka", "country": "India"},

    "visakhapatnam": {"city": "Visakhapatnam", "state": "Andhra Pradesh", "country": "India"},
    "vizag": {"city": "Visakhapatnam", "state": "Andhra Pradesh", "country": "India"},

    "dehradun": {"city": "Dehradun", "state": "Uttarakhand", "country": "India"},

    "india": {"city": None, "state": None, "country": "India"},
    "pan india": {"city": None, "state": None, "country": "India"},
    "across india": {"city": None, "state": None, "country": "India"},
    "all india": {"city": None, "state": None, "country": "India"},

    # ─── Remote ──────────────────────────────────────────────
    "remote": {"city": "Remote", "state": None, "country": None, "is_remote": True},
    "work from home": {"city": "Remote", "state": None, "country": None, "is_remote": True},
    "wfh": {"city": "Remote", "state": None, "country": None, "is_remote": True},
    "fully remote": {"city": "Remote", "state": None, "country": None, "is_remote": True},
    "100% remote": {"city": "Remote", "state": None, "country": None, "is_remote": True},
    "remote (india)": {"city": "Remote", "state": None, "country": "India", "is_remote": True},
    "remote india": {"city": "Remote", "state": None, "country": "India", "is_remote": True},
    "anywhere": {"city": "Remote", "state": None, "country": None, "is_remote": True},

    # ─── Global ──────────────────────────────────────────────
    "global": {"city": None, "state": None, "country": "Global"},
    "worldwide": {"city": None, "state": None, "country": "Global"},
    "international": {"city": None, "state": None, "country": "Global"},
}


@functools.lru_cache(maxsize=4096)
def normalize_location(raw: str) -> dict:
    """
    Normalize a raw location string to structured form.
    Returns dict with: city, state, country, is_remote.
    """
    if not raw:
        return {"city": None, "state": None, "country": "India", "is_remote": False}

    key = raw.strip().lower()

    # Direct lookup
    if key in LOCATION_MAP:
        result = LOCATION_MAP[key].copy()
        result.setdefault("is_remote", False)
        result.setdefault("country", "India")
        return result

    # Try stripping common suffixes like ", india" or ", in"
    for suffix in [", india", ", in", " india"]:
        if key.endswith(suffix):
            trimmed = key[: -len(suffix)].strip()
            if trimmed in LOCATION_MAP:
                result = LOCATION_MAP[trimmed].copy()
                result.setdefault("is_remote", False)
                result.setdefault("country", "India")
                return result

    # Partial match — check if any key is contained in the raw string
    for map_key, data in LOCATION_MAP.items():
        if map_key in key and len(map_key) > 4:
            result = data.copy()
            result.setdefault("is_remote", False)
            result.setdefault("country", "India")
            return result

    # Fallback: return raw as city, India as country
    return {"city": raw.strip().title(), "state": None, "country": "India", "is_remote": False}


def get_normalized_city(raw: str) -> str:
    """Convenience function: return just the normalized city name."""
    norm = normalize_location(raw)
    return norm.get("city") or raw


def run_location_normalization(db: Session) -> dict:
    """
    Batch-update all opportunities with normalized city/location.
    Updates Opportunity.location with the canonical city name.
    """
    from app.models import Opportunity
    updated = 0
    unchanged = 0

    try:
        locs = (
            db.query(Opportunity.location)
            .filter(Opportunity.location != None)
            .distinct()
            .all()
        )

        for (location,) in locs:
            norm = normalize_location(location)
            canonical_city = norm.get("city") or location
            if canonical_city != location:
                db.query(Opportunity).filter(
                    Opportunity.location == location
                ).update({"location": canonical_city}, synchronize_session=False)
                updated += 1
            else:
                unchanged += 1

        db.commit()
        logger.info(f"Location normalization: {updated} updated, {unchanged} unchanged.")
    except Exception as e:
        db.rollback()
        logger.error(f"Location normalization error: {e}")

    return {"updated": updated, "unchanged": unchanged, "total": updated + unchanged}
