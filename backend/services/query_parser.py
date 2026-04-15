import re

# translator between:
# what the user types (human language)
# what your backend understands (filters)

# extract simple filters from text query
def parse_search_query(query: str):
    result = {
        "min_price": None,
        "max_price": None,
        "bedrooms": None
    }

    if not query:
        return result

    text = query.strip().lower()
    
    # detect bedrooms like 3 bedroom, 3 bedrooms, 3 br, 3 bd
    bedroom_match = re.search(r"(\d+)\s*(bedroom|bedrooms|br|bd|bed)", text)
    if bedroom_match:
        result["bedrooms"] = int(bedroom_match.group(1))

    # detect max price like under 10m or max 8000000
    under_million_match = re.search(r"(under|max)\s*(\d+\.?\d*)\s*m", text)
    if under_million_match:
        result["max_price"] = float(under_million_match.group(2)) * 1_000_000

    under_plain_match = re.search(r"(under|max)\s*(\d+)", text)
    if under_plain_match and result["max_price"] is None:
        result["max_price"] = int(under_plain_match.group(2))

    return result