import re


def normalize_skill(raw: str) -> str:
    
    if not raw:
        return ""
    # Insert space between a lowercase->uppercase boundary (AndroidDeveloper -> Android Developer)
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", raw)
    return re.sub(r"\s+", " ", spaced).strip().lower()


def parse_experience_range(raw: str | None) -> tuple[float, float] | None:
   
    if not raw or not raw.strip():
        return None

    text = raw.lower().strip()

    # Range: "2-4 years" or "2 - 4 years"
    range_match = re.search(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*year", text)
    if range_match:
        return float(range_match.group(1)), float(range_match.group(2))

    # Plus: "3+ years"
    plus_match = re.search(r"(\d+(?:\.\d+)?)\s*\+\s*year", text)
    if plus_match:
        return float(plus_match.group(1)), 99.0

    # Years + months: "2 years 6 months"
    years_months = re.search(
        r"(\d+(?:\.\d+)?)\s*year[s]?\s*(?:(\d+)\s*month)?", text
    )
    if years_months and years_months.group(1):
        years = float(years_months.group(1))
        months = float(years_months.group(2)) if years_months.group(2) else 0.0
        total = years + (months / 12)
        return total, total

    # Months only: "6 months"
    months_only = re.search(r"(\d+(?:\.\d+)?)\s*month", text)
    if months_only:
        val = float(months_only.group(1)) / 12
        return val, val

    # Bare number: "5"
    bare_number = re.search(r"^(\d+(?:\.\d+)?)$", text)
    if bare_number:
        val = float(bare_number.group(1))
        return val, val

    return None


def parse_candidate_total_experience(key_experience: str | None, key_experience_in_month: str | None) -> float:
    
    total_years = 0.0

    if key_experience:
        parsed = parse_experience_range(key_experience)
        if parsed:
            total_years += parsed[0]

    if key_experience_in_month:
        month_match = re.search(r"(\d+(?:\.\d+)?)", key_experience_in_month)
        if month_match:
            total_years += float(month_match.group(1)) / 12

    return round(total_years, 2)