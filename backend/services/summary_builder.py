# build grouped summary rows from extracted units
def build_summary(units):
    grouped = {}

    for unit in units:
        developer = unit.get("developer_name")
        project = unit.get("project_name")
        bedrooms = unit.get("bedrooms")
        unit_type = unit.get("unit_type")
        area = unit.get("area_m2")
        price = unit.get("price_total")

        # skip rows with no project
        if project is None:
            continue

        # use bedrooms if available, otherwise fallback to unit_type
        category_type = "bedrooms" if bedrooms is not None else "unit_type"
        category_value = bedrooms if bedrooms is not None else unit_type

        if category_value is None:
            continue

        key = (developer, project, category_type, category_value)

        if key not in grouped:
            grouped[key] = {
                "developer_name": developer,
                "project_name": project,
                "category_type": category_type,
                "category_value": category_value,
                "areas": [],
                "prices": [],
            }

        if area is not None:
            grouped[key]["areas"].append(area)

        if price is not None:
            grouped[key]["prices"].append(price)

    summary_rows = []

    for group in grouped.values():
        areas = group["areas"]
        prices = group["prices"]

        summary_rows.append({
            "developer_name": group["developer_name"],
            "project_name": group["project_name"],
            "category_type": group["category_type"],
            "category_value": group["category_value"],
            "min_area_m2": min(areas) if areas else None,
            "max_area_m2": max(areas) if areas else None,
            "min_price": min(prices) if prices else None,
            "max_price": max(prices) if prices else None,
        })

    return summary_rows