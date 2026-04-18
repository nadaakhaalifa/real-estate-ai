import re
from collections import Counter


def score_column(column_name, sample_values, target_field):
    name = str(column_name).lower().strip()
    clean_values = [v for v in sample_values if v is not None]
    text_values = [str(v).lower().strip() for v in clean_values if str(v).strip()]

    score = 0

    if target_field == "price_total":
        score += _score_name_keywords(name,["price", "original price", "selling price", "sale price", "total price", "unit price", "price per m2"], 4)
        score += sum(1 for v in clean_values if _looks_numeric(v))

        score -= sum(3 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_short_code(v))
        score -= sum(2 for v in clean_values if _looks_like_building_value(v))

    elif target_field == "area_m2":
        score += _score_name_keywords(name, ["area", "bua", "sqm", "sq m", "size", "built up","builtup", "m2"], 4)
        score += sum(1 for v in clean_values if _looks_numeric(v))

        score -= sum(3 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_short_code(v))
        score -= sum(2 for v in clean_values if _looks_like_building_value(v))
        

    elif target_field == "bedrooms":
        score += _score_name_keywords(name, ["bed", "bedroom", "br", "room"], 2)
        score += sum(1 for v in clean_values if _looks_like_bedroom_value(v))

    elif target_field == "developer_name":
        score += _score_name_keywords(name, ["developer", "company", "builder", "brand"], 5)
        score += sum(2 for v in clean_values if _looks_like_company_name(v))
        score += _repetition_score(text_values)

        score -= sum(4 for v in clean_values if _looks_like_unit_type_value(v))
        score -= sum(4 for v in clean_values if _looks_like_building_value(v))
        score -= sum(4 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_short_code(v))
        score -= sum(3 for v in clean_values if _looks_like_project_name(v))
        score -= sum(2 for v in clean_values if _looks_numeric(v))
    
    elif target_field == "unit_type":
        score += _score_name_keywords(name, ["unit type", "type", "layout", "model", "unit"], 5)
        score += sum(3 for v in clean_values if _looks_like_unit_type_value(v))

        score -= sum(4 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_short_code(v))
        score -= sum(2 for v in clean_values if _looks_numeric(v))
    elif target_field == "location":
       score += _score_name_keywords(name, ["location", "district", "area", "city", "community", "sub area"], 5)

       score += sum(2 for v in clean_values if _looks_like_location_value(v))

       score -= sum(4 for v in clean_values if _looks_like_unit_code_value(v))
       score -= sum(3 for v in clean_values if _looks_like_short_code(v))
       score -= sum(3 for v in clean_values if _looks_like_building_value(v))
       score -= sum(3 for v in clean_values if _looks_numeric(v))

    elif target_field == "stage":
        score += _score_name_keywords(name, ["stage", "phase", "delivery", "delivery status"], 6)
        score += sum(2 for v in clean_values if _looks_like_stage_value(v))
        
        score -= sum(5 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_building_value(v))
        score -= sum(3 for v in clean_values if _looks_numeric(v))
        score -= sum(2 for v in clean_values if _looks_like_short_code(v))
    elif target_field == "building":
        score += _score_name_keywords(name, ["building", "building name", "block", "tower", "cluster", "bldg"], 6)

        score += sum(4 for v in clean_values if _looks_like_building_value(v))
        score += sum(2 for v in clean_values if _looks_like_short_code(v))

        score -= sum(3 for v in clean_values if _looks_like_zone_value(v))
        score -= sum(3 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(2 for v in clean_values if _looks_like_project_name(v))
    
    elif target_field == "project_name":
        score += _score_name_keywords(name, ["project", "compound", "development"], 6)
        score += sum(2 for v in clean_values if _looks_like_project_name(v))
        score += _repetition_score(text_values)

        score -= sum(3 for v in clean_values if _looks_like_unit_type_value(v))
        score -= sum(3 for v in clean_values if _looks_like_building_value(v))
        score -= sum(4 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_numeric(v))

    elif target_field == "unit_code":
        score += _score_name_keywords(name, ["unit code", "unit id", "unit", "code", "record"], 5)
        score += sum(5 for v in clean_values if _looks_like_unit_code_value(v))
        score += sum(1 for v in clean_values if _looks_like_text(v))
        score -= sum(2 for v in clean_values if _looks_like_unit_type_value(v))

    return score


def detect_column(df, target_field, excluded_columns=None):
    if excluded_columns is None:
        excluded_columns = set()

    best_column = None
    best_score = -1

    for column in df.columns:
        if column in excluded_columns:
            continue

        sample_values = df[column].dropna().head(20).tolist()
        score = score_column(column, sample_values, target_field)

        if score > best_score:
            best_score = score
            best_column = column

    # field-specific confidence thresholds
    min_score_by_field = {
        "developer_name": 7,
        "project_name": 7,
        "building": 6,
        "location": 8,
        "stage": 7,
        "unit_code": 5,
        "unit_type": 4,
        "price_total": 5,
        "area_m2": 5,
        "bedrooms": 4,
    }

    min_score = min_score_by_field.get(target_field, 1)

    if best_column is None or best_score < min_score:
        print(f"NO STRONG MATCH FOR {target_field} (best_score={best_score})")
        return None

    print(f"BEST COLUMN FOR {target_field}: {best_column} (score={best_score})")
    return best_column





def _score_name_keywords(column_name, keywords, weight=2):
    score = 0
    for keyword in keywords:
        if keyword in column_name:
            score += weight
    return score


def _looks_numeric(value):
    if value is None:
        return False

    text = str(value).replace(",", "").strip()
    return bool(re.fullmatch(r"\d+(\.\d+)?", text))


def _looks_like_text(value):
    if value is None:
        return False

    text = str(value).strip()
    if not text:
        return False

    return not _looks_numeric(text)


def _looks_like_bedroom_value(value):
    if value is None:
        return False

    text = str(value).lower().strip()

    if "studio" in text:
        return True

    return bool(re.search(r"\d+\s*(bed|bedroom|bedrooms|br|bd|room)", text))


def _looks_like_unit_type_value(value):
    if value is None:
        return False

    text = str(value).lower().strip()
    if not text:
        return False

    patterns = [
        r"\bstudio\b",
        r"\bapartment\b",
        r"\bflat\b",
        r"\bloft\b",
        r"\bduplex\b",
        r"\bpenthouse\b",
        r"\bvilla\b",
        r"\btownhouse\b",
        r"\btwin house\b",
        r"\bchalet\b",
        r"\b\d+\s*(bed|bedroom|bedrooms|br)\b",
        r"\btype\s*[a-z0-9]+\b",
        r"\blayout\b",
        r"\bunit\b",
    ]

    return any(re.search(pattern, text) for pattern in patterns)


def _looks_like_location_value(value):
    if value is None:
        return False

    text = str(value).lower().strip()
    if not text:
        return False

    if _looks_numeric(text):
        return False

    if _looks_like_unit_code_value(text):
        return False

    if _looks_like_short_code(text):
        return False

    if _looks_like_building_value(text):
        return False

    # real locations are words, not codes
    return len(text.split()) >= 1 and not bool(re.search(r"\d{2,}", text))

def _looks_like_stage_value(value):
    if value is None:
        return False

    text = str(value).lower().strip()
    if not text:
        return False

    patterns = [
        r"\bphase\b",
        r"\bstage\b",
        r"\bready\b",
        r"\bunder construction\b",
        r"\bfinished\b",
        r"\bsemi finished\b",
        r"\bcore and shell\b",
        r"\b\d{4}\b",
    ]

    return any(re.search(pattern, text) for pattern in patterns)


def _repetition_score(text_values):
    if not text_values:
        return 0

    counts = Counter(text_values)
    repeated_values = sum(1 for _, count in counts.items() if count > 1)
    return repeated_values

def _looks_like_project_name(value):
    if value is None:
        return False

    text = str(value).strip()
    if not text:
        return False

    text_lower = text.lower()

    if _looks_numeric(text):
        return False

    if _looks_like_unit_code_value(text):
        return False

    if _looks_like_building_value(text):
        return False

    if _looks_like_unit_type_value(text):
        return False

    if re.search(r"\d{4}-\d{2}-\d{2}", text_lower):
        return False

    if "do not modify" in text_lower:
        return False

    words = text_lower.split()
    return 1 <= len(words) <= 5

def _looks_like_building_value(value):
    if value is None:
        return False

    text = str(value).strip().lower()
    if not text:
        return False

    patterns = [
        r"\bbuilding\b",
        r"\bblock\b",
        r"\btower\b",
        r"\bcluster\b",
        r"\bbldg\b",
        r"^[a-z]$",
        r"^[a-z]\d+$",
        r"^\d+[a-z]$",
        r"^[a-z0-9]+-[a-z0-9]+$",
    ]

    return any(re.search(pattern, text) for pattern in patterns)



def _looks_like_short_code(value):
    if value is None:
        return False

    text = str(value).strip().lower()
    if not text:
        return False

    return bool(re.fullmatch(r"[a-z]\d*", text))

def _looks_like_company_name(value):
    if value is None:
        return False

    text = str(value).strip()
    if not text:
        return False

    text_lower = text.lower()

    if _looks_numeric(text):
        return False

    if _looks_like_short_code(text):
        return False

    if _looks_like_unit_code_value(text):
        return False

    if _looks_like_building_value(text):
        return False

    if _looks_like_unit_type_value(text):
        return False
    
    if re.search(r"\d{4}-\d{2}-\d{2}", text_lower):
        return False

    if "do not modify" in text_lower:
        return False

    return len(text_lower.split()) <= 4 and len(text_lower) > 2

def _looks_like_zone_value(value):
    if value is None:
        return False

    text = str(value).strip().lower()
    if not text:
        return False

    patterns = [
        r"^[a-z]\d+\s?[a-z]$",
        r"^[a-z]{1,2}\d+$",
        r"^[a-z]\d+\s\d+$",
    ]

    return any(re.fullmatch(pattern, text) for pattern in patterns)

def _looks_like_unit_code_value(value):
    if value is None:
        return False

    text = str(value).strip().lower()
    if not text:
        return False

    patterns = [
        r"^[a-z0-9]+(?:-[a-z0-9]+)+$",
        r"^[a-z0-9]{2,}-[a-z0-9]{1,}-[a-z0-9]{1,}$",
        r"^[a-z]\d+-[a-z0-9]+-\d+$",
    ]

    return any(re.fullmatch(pattern, text) for pattern in patterns)