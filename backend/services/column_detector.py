import re
from collections import Counter


def score_column(column_name, sample_values, target_field):
    name = str(column_name).lower().strip()
    clean_values = [v for v in sample_values if v is not None]
    text_values = [str(v).lower().strip() for v in clean_values if str(v).strip()]

    score = 0

    if "do not modify" in name:
        score -= 20

    if target_field == "price_total":
        score += _score_name_keywords(
            name,
            [
                "price",
                "original price",
                "selling price",
                "sale price",
                "total price",
                "unit price",
                "inventory price",
                "asking price",
                "grand total",
                "pricing structure",
                "unit total",
                "total with finishing",
                "amount",
            ],
            4,
        )

        if "grand total" in name:
            score += 25
        if "pricing structure" in name:
            score += 15

        score += sum(1 for v in clean_values if _looks_numeric(v))
        score -= sum(3 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_short_code(v))
        score -= sum(2 for v in clean_values if _looks_like_building_value(v))

    elif target_field == "area_m2":
        score += _score_name_keywords(
            name,
            ["area", "bua", "sqm", "sq m", "size", "built up", "builtup", "m2", "built area"],
            4,
        )

        if "built area" in name or "builtup" in name or "built up" in name or "bua" in name:
            score += 30

        if "land area" in name or "garden" in name or "roof" in name or "terrace" in name:
            score -= 25

        score += sum(1 for v in clean_values if _looks_numeric(v))
        score -= sum(3 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_short_code(v))
        score -= sum(2 for v in clean_values if _looks_like_building_value(v))
        score -= sum(2 for v in clean_values if _looks_like_datetime_value(v))

    elif target_field == "bedrooms":
        score += _score_name_keywords(
            name,
            [
                "bed",
                "bedroom",
                "bedrooms",
                "br",
                "no of bedrooms",
                "no. of bedrooms",
                "number of bedrooms",
                "category",
            ],
            6,
        )

        score += sum(4 for v in clean_values if _looks_like_bedroom_value(v))
        score -= sum(3 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(2 for v in clean_values if _looks_like_datetime_value(v))

    elif target_field == "developer_name":
        score += _score_name_keywords(name, ["developer", "company", "builder", "brand"], 6)
        score += sum(2 for v in clean_values if _looks_like_company_name(v))
        score += _repetition_score(text_values)
        score += _organization_column_score(text_values)

        score -= _category_column_score(text_values)
        score -= sum(5 for v in clean_values if _looks_like_hash_value(v))
        score -= sum(4 for v in clean_values if _looks_like_unit_type_value(v))
        score -= sum(4 for v in clean_values if _looks_like_building_value(v))
        score -= sum(4 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_short_code(v))
        score -= sum(3 for v in clean_values if _looks_numeric(v))
        score -= sum(4 for v in clean_values if _looks_like_datetime_value(v))

    elif target_field == "unit_type":
        score += _score_name_keywords(
            name,
            ["unit type", "type", "layout", "model", "category", "usage type"],
            5,
        )

        if "unit type" in name:
            score += 25

        if "category" in name:
            score += 10

        score += sum(4 for v in clean_values if _looks_like_unit_type_value(v))
        score += _category_column_score(text_values)

        score -= sum(4 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_short_code(v))
        score -= sum(2 for v in clean_values if _looks_numeric(v))
        score -= sum(2 for v in clean_values if _looks_like_datetime_value(v))

    elif target_field == "location":
        score += _score_name_keywords(name, ["location", "district", "city", "community", "sub area"], 5)
        score += sum(2 for v in clean_values if _looks_like_location_value(v))

        score -= _category_column_score(text_values)
        score -= sum(4 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_short_code(v))
        score -= sum(3 for v in clean_values if _looks_like_building_value(v))
        score -= sum(3 for v in clean_values if _looks_numeric(v))
        score -= sum(4 for v in clean_values if _looks_like_datetime_value(v))

    elif target_field == "stage":
        score += _score_name_keywords(name, ["stage", "status", "delivery status", "finish"], 6)
        score += sum(2 for v in clean_values if _looks_like_stage_value(v))

        score -= sum(5 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(3 for v in clean_values if _looks_like_building_value(v))
        score -= sum(3 for v in clean_values if _looks_numeric(v))
        score -= sum(5 for v in clean_values if _looks_like_datetime_value(v))
        score -= sum(2 for v in clean_values if _looks_like_short_code(v))

    elif target_field == "building":
        score += _score_name_keywords(name, ["building", "building name", "block", "tower", "cluster", "bldg"], 6)
        score += sum(4 for v in clean_values if _looks_like_building_value(v))
        score += sum(2 for v in clean_values if _looks_like_short_code(v))

        score -= sum(3 for v in clean_values if _looks_like_zone_value(v))
        score -= sum(3 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(2 for v in clean_values if _looks_like_project_name(v))
        score -= sum(3 for v in clean_values if _looks_like_datetime_value(v))

    elif target_field == "project_name":
        score += _score_name_keywords(name, ["project", "project name", "compound", "development"], 6)

        if name == "project" or "project name" in name:
            score += 30

        score += sum(2 for v in clean_values if _looks_like_project_name(v))
        score += _project_like_column_score(text_values)
        score += _repetition_score(text_values)

        score -= _category_column_score(text_values)
        score -= sum(3 for v in clean_values if _looks_like_unit_type_value(v))
        score -= sum(3 for v in clean_values if _looks_like_building_value(v))
        score -= sum(4 for v in clean_values if _looks_like_unit_code_value(v))
        score -= sum(5 for v in clean_values if _looks_like_hash_value(v))
        score -= sum(3 for v in clean_values if _looks_numeric(v))
        score -= sum(4 for v in clean_values if _looks_like_datetime_value(v))

    elif target_field == "unit_code":
        score += _score_name_keywords(name, ["unit code", "unit id", "code", "record"], 6)
        score += sum(5 for v in clean_values if _looks_like_unit_code_value(v))
        score += sum(1 for v in clean_values if _looks_like_text(v))

        score -= sum(2 for v in clean_values if _looks_like_unit_type_value(v))
        score -= sum(2 for v in clean_values if _looks_like_datetime_value(v))

    return score


def detect_column(df, target_field, excluded_columns=None):
    if excluded_columns is None:
        excluded_columns = set()

    best_column = None
    best_score = -1

    for column in df.columns:
        if column in excluded_columns:
            continue

        sample_values = df[column].dropna().head(30).tolist()
        score = score_column(column, sample_values, target_field)

        if score > best_score:
            best_score = score
            best_column = column

    min_score_by_field = {
        "developer_name": 9,
        "project_name": 8,
        "building": 6,
        "location": 8,
        "stage": 8,
        "unit_code": 5,
        "unit_type": 5,
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
    column_name = str(column_name).lower()

    for keyword in keywords:
        keyword = str(keyword).lower()
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


def _looks_like_datetime_value(value):
    if value is None:
        return False

    text = str(value).strip().lower()
    if not text:
        return False

    patterns = [
        r"\d{4}-\d{2}-\d{2}",
        r"\d{2}/\d{2}/\d{4}",
        r"\d{4}/\d{2}/\d{2}",
        r"\d{2}:\d{2}:\d{2}",
    ]

    return any(re.search(pattern, text) for pattern in patterns)


def _looks_like_bedroom_value(value):
    if value is None:
        return False

    text = str(value).lower().strip()
    if not text:
        return False

    if "studio" in text:
        return True

    return bool(
        re.search(r"\b\d+\s*[- ]?\s*(bed|beds|bedroom|bedrooms|br|bd)\b", text)
    )

def _looks_like_unit_type_value(value):
    if value is None:
        return False

    text = str(value).lower().strip()
    if not text:
        return False

    if _looks_numeric(text):
        return False

    if _looks_like_datetime_value(text):
        return False

    if _looks_like_unit_code_value(text):
        return False

    patterns = [
        r"\bstudio\b",
        r"\bvilla\b",
        r"\bapartment\b",
        r"\bflat\b",
        r"\bloft\b",
        r"\bduplex\b",
        r"\bpenthouse\b",
        r"\bvilla\b",
        r"\btown\s*house\b",
        r"\btownhouse\b",
        r"\btwin\s*house\b",
        r"\bchalet\b",
        r"\bretail\b",
        r"\boffice\b",
        r"\bclinic\b",
        r"\bcommercial\b",
        r"\bf&b\b",
        r"\bfood\b",
        r"\badmin\b",
        r"\bmedical\b",
        r"\b\d+\s*(bed|beds|bedroom|bedrooms|br|bd)\b",
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

    if _looks_like_datetime_value(text):
        return False

    return len(text.split()) >= 1 and not bool(re.search(r"\d{2,}", text))


def _looks_like_stage_value(value):
    if value is None:
        return False

    text = str(value).lower().strip()
    if not text:
        return False

    if _looks_like_datetime_value(text):
        return False

    patterns = [
        r"\bphase\b",
        r"\bstage\b",
        r"\bready\b",
        r"\bunder construction\b",
        r"\bfinished\b",
        r"\bsemi finished\b",
        r"\bcore and shell\b",
        r"\bnot finished\b",
        r"\bdelivered\b",
    ]

    return any(re.search(pattern, text) for pattern in patterns)


def _repetition_score(text_values):
    if not text_values:
        return 0

    counts = Counter(text_values)
    return sum(1 for _, count in counts.items() if count > 1)


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

    if _looks_like_datetime_value(text_lower):
        return False

    if "do not modify" in text_lower:
        return False

    words = text_lower.split()
    return 1 <= len(words) <= 6


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

    if _looks_like_datetime_value(text_lower):
        return False

    if _looks_like_hash_value(text_lower):
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


def _category_column_score(text_values):
    if not text_values:
        return 0

    unique_values = set(text_values)
    if not unique_values:
        return 0

    if len(unique_values) <= 20:
        avg_words = sum(len(v.split()) for v in unique_values) / len(unique_values)
        if avg_words <= 6:
            return 5

    return 0


def _project_like_column_score(text_values):
    if not text_values:
        return 0

    unique_values = set(text_values)
    if not unique_values:
        return 0

    avg_words = sum(len(v.split()) for v in unique_values) / len(unique_values)

    score = 0

    if avg_words >= 2:
        score += 2

    if len(unique_values) >= 3:
        score += 2

    return score


def _organization_column_score(text_values):
    if not text_values:
        return 0

    unique_values = set(text_values)
    if not unique_values:
        return 0

    avg_words = sum(len(v.split()) for v in unique_values) / len(unique_values)

    score = 0

    if 1 <= avg_words <= 4:
        score += 1

    if len(unique_values) <= 12:
        score += 1

    return score


def _looks_like_hash_value(value):
    if value is None:
        return False

    text = str(value).strip().lower()

    if not text:
        return False

    if " " in text:
        return False

    if len(text) < 16:
        return False

    has_letters = bool(re.search(r"[a-z]", text))
    has_digits = bool(re.search(r"\d", text))

    return has_letters and has_digits