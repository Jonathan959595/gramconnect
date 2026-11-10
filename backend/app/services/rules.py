import re
from uuid import uuid4

ROUTES = {
    "Drainage": "Panchayat sanitation desk", "Electricity": "Electricity service desk",
    "Water": "Water supply desk", "Roads": "Roads & engineering",
    "Streetlight": "Electrical maintenance", "Sanitation": "Panchayat sanitation desk",
    "Other": "Village coordinator",
}

def classify_issue(text: str) -> str:
    value = text.lower()
    tests = {
        "Electricity": r"power|electric|current|కరెంట్|విద్యుత్",
        "Water": r"water|supply|నీరు",
        "Roads": r"road|pothole|రోడ్డు|గుంత",
        "Streetlight": r"street.?light|లైట్",
        "Sanitation": r"garbage|waste|చెత్త",
        "Drainage": r"drain|overflow|stagnant|డ్రైనేజీ|కాలువ",
    }
    return next((category for category, pattern in tests.items() if re.search(pattern, value)), "Other")

def priority_for(category: str) -> str:
    return "High" if category in {"Drainage", "Electricity"} else "Normal"

def reference(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8].upper()}"

def entity_id() -> str:
    return str(uuid4())
