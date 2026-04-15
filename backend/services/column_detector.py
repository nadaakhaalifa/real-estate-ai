import re


# score how likely a column matches a target field
def score_column(column_name, sample_values, target_field):
    name = str(column_name).lower()
    values_text = " ".join([str(v).lower() for v in sample_values if v is not None])

    score = 0

    if target_field == "price_total":
        keywords = ["price", "amount", "cost", "value", "inventory"]
        for keyword in keywords:
            if keyword in name:
                score += 2

        numeric_count = sum(1 for v in sample_values if _looks_numeric(v))
        score += numeric_count

    elif target_field == "area_m2":
        keywords = ["area", "bua", "sqm", "sq m", "size", "built up", "m2"]
        for keyword in keywords:
            if keyword in name:
                score += 2

        numeric_count = sum(1 for v in sample_values if _looks_numeric(v))
        score += numeric_count

    elif target_field == "bedrooms":
        keywords = ["bed", "bedroom", "br", "room", "unit type", "type", "layout"]
        for keyword in keywords:
            if keyword in name:
                score += 2

        bedroom_pattern_count = sum(1 for v in sample_values if _looks_like_bedroom_value(v))
        score += bedroom_pattern_count

    return score


# detect the best matching column using name + sample values
def detect_column(df, target_field):
    best_column = None
    best_score = -1

    for column in df.columns:
        sample_values = df[column].dropna().head(10).tolist()
        score = score_column(column, sample_values, target_field)

        if score > best_score:
            best_score = score
            best_column = column

    # avoid returning weak random matches
    if best_score <= 0:
        return None

    print(f"BEST COLUMN FOR {target_field}: {best_column} (score={best_score})")
    return best_column


# check if a value looks numeric
def _looks_numeric(value):
    if value is None:
        return False

    text = str(value).replace(",", "").strip()
    return bool(re.fullmatch(r"\d+(\.\d+)?", text))


# check if a value looks like bedroom text
def _looks_like_bedroom_value(value):
    if value is None:
        return False

    text = str(value).lower().strip()

    if "studio" in text:
        return True

    return bool(re.search(r"\d+\s*(bed|bedroom|bedrooms|br|bd|room)", text))