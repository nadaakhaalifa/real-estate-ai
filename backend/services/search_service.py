# calculate how well a unit matches the search query
def calculate_score(
    unit,
    target_bedrooms=None,
    max_price=None,
    min_area=None,
    max_area=None,
    location=None,
    project_name=None,
    unit_type=None,
    stage=None,
    developer_name=None,
):
    score = 0

    # bedroom match
    if target_bedrooms is not None and unit.get("bedrooms") is not None:
        if unit["bedrooms"] == target_bedrooms:
            score += 3
        else:
            score += 1

    # price closeness
    if max_price is not None and unit.get("price_total") is not None and max_price > 0:
        diff = abs(max_price - unit["price_total"])
        score += max(0, 3 - (diff / max_price))

    # area bonus
    if min_area is not None and unit.get("area_m2") is not None:
        if unit["area_m2"] >= min_area:
            score += 1

    if max_area is not None and unit.get("area_m2") is not None:
        if unit["area_m2"] <= max_area:
            score += 1

    # text match bonus
    if location and unit.get("location"):
        if location.lower() in unit["location"].lower():
            score += 2

    if project_name and unit.get("project_name"):
        if project_name.lower() in unit["project_name"].lower():
            score += 2

    if unit_type and unit.get("unit_type"):
        if unit_type.lower() in unit["unit_type"].lower():
            score += 2

    if stage and unit.get("stage"):
        if stage.lower() in unit["stage"].lower():
            score += 2

    if developer_name and unit.get("developer_name"):
        if developer_name.lower() in unit["developer_name"].lower():
            score += 2

    return score


def filter_units(
    units,
    min_price=None,
    max_price=None,
    min_bedrooms=None,
    max_bedrooms=None,
    min_area=None,
    max_area=None,
    project_name=None,
    location=None,
    unit_type=None,
    stage=None,
    developer_name=None,
):
    filtered_units = []

    for unit in units:
        # skip if price is below minimum
        if min_price is not None:
            if unit.get("price_total") is None or unit["price_total"] < min_price:
                continue

        # skip if price is above maximum
        if max_price is not None:
            if unit.get("price_total") is None or unit["price_total"] > max_price:
                continue

        # skip if bedrooms are below minimum
        if min_bedrooms is not None:
            if unit.get("bedrooms") is None or unit["bedrooms"] < min_bedrooms:
                continue

        # skip if bedrooms are above maximum
        if max_bedrooms is not None:
            if unit.get("bedrooms") is None or unit["bedrooms"] > max_bedrooms:
                continue

        # skip if area is below minimum
        if min_area is not None:
            if unit.get("area_m2") is None or unit["area_m2"] < min_area:
                continue

        # skip if area is above maximum
        if max_area is not None:
            if unit.get("area_m2") is None or unit["area_m2"] > max_area:
                continue

        # skip if project name does not match
        if project_name:
            if not unit.get("project_name") or project_name.lower() not in unit["project_name"].lower():
                continue

        # skip if location does not match
        if location:
            if not unit.get("location") or location.lower() not in unit["location"].lower():
                continue

        # skip if unit type does not match
        if unit_type:
            if not unit.get("unit_type") or unit_type.lower() not in unit["unit_type"].lower():
                continue

        # skip if stage does not match
        if stage:
            if not unit.get("stage") or stage.lower() not in unit["stage"].lower():
                continue

        # skip if developer name does not match
        if developer_name:
            if not unit.get("developer_name") or developer_name.lower() not in unit["developer_name"].lower():
                continue

        filtered_units.append(unit.copy())

    # calculate score for each filtered unit
    for unit in filtered_units:
        unit["score"] = calculate_score(
            unit,
            target_bedrooms=min_bedrooms,
            max_price=max_price,
            min_area=min_area,
            max_area=max_area,
            location=location,
            project_name=project_name,
            unit_type=unit_type,
            stage=stage,
            developer_name=developer_name,
        )

    # sort units by highest score first
    filtered_units.sort(key=lambda unit: unit["score"], reverse=True)

    return filtered_units