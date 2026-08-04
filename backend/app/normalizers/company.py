"""
Phase 11.4 T5: Company Name Normalization
Normalizes company name variants to canonical forms.
Uses stdlib only — no external deps.

Examples:
  TCS → Tata Consultancy Services
  Infosys Ltd → Infosys
  PWC → PricewaterhouseCoopers
"""
import re
import logging
from typing import Optional
from sqlalchemy.orm import Session
import functools

logger = logging.getLogger("company_normalizer")

# ─────────────────────────────────────────────────────────────
# Canonical company alias dictionary
# Format: "raw_variant_lower" → "Canonical Name"
# ─────────────────────────────────────────────────────────────
COMPANY_CANONICAL: dict[str, str] = {
    # TCS
    "tcs": "Tata Consultancy Services",
    "tata consultancy services": "Tata Consultancy Services",
    "tata consultancy services ltd": "Tata Consultancy Services",
    "tata consultancy services limited": "Tata Consultancy Services",
    "tcs ltd": "Tata Consultancy Services",
    "tcs limited": "Tata Consultancy Services",
    "tata consultancy": "Tata Consultancy Services",

    # Infosys
    "infosys": "Infosys",
    "infosys ltd": "Infosys",
    "infosys limited": "Infosys",
    "infosys technologies": "Infosys",
    "infosys bpo": "Infosys",
    "infosys bpm": "Infosys",

    # Wipro
    "wipro": "Wipro",
    "wipro ltd": "Wipro",
    "wipro limited": "Wipro",
    "wipro technologies": "Wipro",
    "wipro bpo": "Wipro",

    # HCL
    "hcl": "HCL Technologies",
    "hcl technologies": "HCL Technologies",
    "hcl tech": "HCL Technologies",
    "hcltech": "HCL Technologies",
    "hcl technologies ltd": "HCL Technologies",

    # Tech Mahindra
    "tech mahindra": "Tech Mahindra",
    "tech mahindra ltd": "Tech Mahindra",
    "tech mahindra limited": "Tech Mahindra",
    "techmahindra": "Tech Mahindra",

    # Cognizant
    "cognizant": "Cognizant",
    "cognizant technology solutions": "Cognizant",
    "cts": "Cognizant",
    "cognizant technology solutions india": "Cognizant",

    # Accenture
    "accenture": "Accenture",
    "accenture india": "Cognizant",
    "accenture solutions pvt ltd": "Accenture",
    "accenture plc": "Accenture",

    # IBM
    "ibm": "IBM",
    "ibm india": "IBM",
    "international business machines": "IBM",
    "ibm india private limited": "IBM",

    # Capgemini
    "capgemini": "Capgemini",
    "capgemini india": "Capgemini",
    "capgemini technology services": "Capgemini",
    "capgemini technology services india": "Capgemini",

    # Deloitte
    "deloitte": "Deloitte",
    "deloitte india": "Deloitte",
    "deloitte consulting": "Deloitte",
    "deloitte touche tohmatsu": "Deloitte",
    "deloitte usind": "Deloitte",

    # EY / Ernst & Young
    "ey": "EY",
    "ernst & young": "EY",
    "ernst and young": "EY",
    "ey india": "EY",
    "ernst & young global limited": "EY",

    # PwC
    "pwc": "PricewaterhouseCoopers",
    "pricewaterhousecoopers": "PricewaterhouseCoopers",
    "pricewaterhousecoopers pvt ltd": "PricewaterhouseCoopers",
    "pwc india": "PricewaterhouseCoopers",
    "price waterhouse coopers": "PricewaterhouseCoopers",

    # KPMG
    "kpmg": "KPMG",
    "kpmg india": "KPMG",
    "kpmg global services": "KPMG",
    "kpmg assurance and consulting services": "KPMG",

    # Oracle
    "oracle": "Oracle",
    "oracle india": "Oracle",
    "oracle corporation": "Oracle",
    "oracle financial services": "Oracle",
    "oracle india private limited": "Oracle",

    # SAP
    "sap": "SAP",
    "sap india": "SAP",
    "sap labs india": "SAP",
    "sap se": "SAP",

    # Microsoft
    "microsoft": "Microsoft",
    "microsoft india": "Microsoft",
    "microsoft india (r&d) pvt ltd": "Microsoft",
    "microsoft corporation": "Microsoft",

    # Google
    "google": "Google",
    "google india": "Google",
    "google llc": "Google",
    "google india private limited": "Google",
    "alphabet": "Google",

    # Amazon
    "amazon": "Amazon",
    "amazon india": "Amazon",
    "amazon development centre india": "Amazon",
    "amazon web services": "Amazon Web Services",
    "aws": "Amazon Web Services",
    "amazon web services india": "Amazon Web Services",

    # Meta
    "meta": "Meta",
    "facebook": "Meta",
    "meta platforms": "Meta",
    "meta platforms inc": "Meta",

    # Apple
    "apple": "Apple",
    "apple india": "Apple",
    "apple inc": "Apple",

    # Flipkart
    "flipkart": "Flipkart",
    "flipkart internet pvt ltd": "Flipkart",
    "flipkart india": "Flipkart",

    # Zomato
    "zomato": "Zomato",
    "zomato limited": "Zomato",
    "zomato india": "Zomato",

    # Swiggy
    "swiggy": "Swiggy",
    "bundl technologies": "Swiggy",

    # PhonePe
    "phonepe": "PhonePe",
    "phonepe private limited": "PhonePe",

    # Razorpay
    "razorpay": "Razorpay",
    "razorpay software pvt ltd": "Razorpay",

    # Paytm
    "paytm": "Paytm",
    "one 97 communications": "Paytm",
    "one97 communications": "Paytm",

    # BYJU's
    "byjus": "BYJU's",
    "byju's": "BYJU's",
    "think and learn": "BYJU's",

    # Ola
    "ola": "Ola",
    "ola electric": "Ola",
    "ani technologies": "Ola",

    # Uber
    "uber": "Uber",
    "uber india": "Uber",
    "uber technologies": "Uber",

    # Nykaa
    "nykaa": "Nykaa",
    "fsg india": "Nykaa",

    # Freshworks
    "freshworks": "Freshworks",
    "freshdesk": "Freshworks",

    # Zoho
    "zoho": "Zoho",
    "zoho corporation": "Zoho",
    "zoho corp": "Zoho",

    # Mphasis
    "mphasis": "Mphasis",
    "mphasis limited": "Mphasis",

    # L&T Technology Services
    "ltts": "L&T Technology Services",
    "l&t technology services": "L&T Technology Services",
    "larsen & toubro technology services": "L&T Technology Services",

    # Mindtree (now LTIMindtree)
    "mindtree": "LTIMindtree",
    "ltimindtree": "LTIMindtree",
    "lti mindtree": "LTIMindtree",
    "l&t infotech": "LTIMindtree",
    "larsen and toubro infotech": "LTIMindtree",

    # Hexaware
    "hexaware": "Hexaware",
    "hexaware technologies": "Hexaware",
    "hexaware technologies limited": "Hexaware",

    # Persistent Systems
    "persistent systems": "Persistent Systems",
    "persistent": "Persistent Systems",

    # Tata Elxsi
    "tata elxsi": "Tata Elxsi",

    # NIIT Technologies (now Coforge)
    "coforge": "Coforge",
    "niit technologies": "Coforge",

    # Minda Industries
    "minda": "Minda Industries",

    # Recruitment agencies
    "randstad": "Randstad India",
    "randstad india": "Randstad India",
    "teamlease": "TeamLease Services",
    "teamlease services": "TeamLease Services",
    "quess corp": "Quess Corp",
    "quess": "Quess Corp",
    "adecco": "Adecco India",
    "adecco india": "Adecco India",
    "manpowergroup": "ManpowerGroup India",
    "manpower": "ManpowerGroup India",
    "abc consultants": "ABC Consultants",
    "michael page": "Michael Page India",
    "kelly services": "Kelly Services India",
    "ciel hr": "CIEL HR Services",
    "genius consultants": "Genius Consultants",
}

# Patterns to strip before lookup
_STRIP_SUFFIXES = re.compile(
    r'\b(pvt\.?\s*ltd\.?|private\s+limited|limited|ltd\.?|llc|inc\.?|plc|corp\.?|'
    r'corporation|technologies|technology|solutions|services|india|group|global|'
    r'consulting|advisors|associates)\b',
    re.IGNORECASE
)


@functools.lru_cache(maxsize=4096)
def normalize_company(raw: str) -> str:
    """
    Normalize a raw company name to its canonical form.
    Returns the canonical name if found, otherwise returns the cleaned raw name.
    """
    if not raw:
        return raw or ""

    # Exact lookup first (lowercase)
    key = raw.strip().lower()
    if key in COMPANY_CANONICAL:
        return COMPANY_CANONICAL[key]

    # Strip common suffixes and try again
    stripped = _STRIP_SUFFIXES.sub("", key).strip().strip(",").strip()
    stripped = re.sub(r'\s+', ' ', stripped).strip()
    if stripped and stripped in COMPANY_CANONICAL:
        return COMPANY_CANONICAL[stripped]

    # Return original with title casing if not found
    return raw.strip()


def run_company_normalization(db: Session) -> dict:
    """
    Batch-update all opportunities with normalized company names.
    Returns stats about how many were updated.
    """
    from app.models import Opportunity
    updated = 0
    unchanged = 0

    try:
        # Only fetch distinct non-null company names to minimize DB load
        companies = (
            db.query(Opportunity.company)
            .filter(Opportunity.company != None)
            .distinct()
            .all()
        )

        for (company,) in companies:
            canonical = normalize_company(company)
            if canonical != company:
                db.query(Opportunity).filter(
                    Opportunity.company == company
                ).update({"company": canonical}, synchronize_session=False)
                updated += 1
            else:
                unchanged += 1

        db.commit()
        logger.info(f"Company normalization: {updated} companies normalized, {unchanged} unchanged.")
    except Exception as e:
        db.rollback()
        logger.error(f"Company normalization error: {e}")

    return {"updated": updated, "unchanged": unchanged, "total": updated + unchanged}


def get_company_alias_count() -> int:
    """Return total number of aliases in the dictionary."""
    return len(COMPANY_CANONICAL)
