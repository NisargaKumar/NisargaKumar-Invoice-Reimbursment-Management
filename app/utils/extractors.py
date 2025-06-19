import re

def extract_name(text: str) -> str:
    patterns = [
        r"Customer\s+Name[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"Passenger\s+Details\s*\([^)]+\):\s*([A-Z][a-z]+)",
        r"Name[:\-]?\s*([A-Z][a-z]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "Unknown"

def extract_date(text: str) -> str:
    patterns = [
        r"Invoice\s+Date[:\-]?\s*(\d{1,2}\s+\w+\s+\d{4})",
        r"Date[:\-]?\s*(\w+\s+\d{1,2},?\s+\d{4})",
        r"(\d{1,2}\s+\w+\s+\d{4})"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "Unknown"
