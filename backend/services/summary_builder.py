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

        # skip invalid rows (no project = useless data)
        if project is None:
            continue

        # choose grouping: bedrooms first, otherwise fallback to unit_type
        category_type = "bedrooms" if bedrooms is not None else "unit_type"
        category_value = bedrooms if bedrooms is not None else unit_type

        # skip if no grouping value found
        if category_value is None:
            continue

        # unique key per group
        key = (developer, project, category_type, category_value)

        # initialize group
        if key not in grouped:
            grouped[key] = {
                "developer_name": developer,
                "project_name": project,
                "category_type": category_type,
                "category_value": category_value,
                "areas": [],
                "prices": [],
            }

        # collect values
        if area is not None:
            grouped[key]["areas"].append(area)

        if price is not None:
            grouped[key]["prices"].append(price)

    summary_rows = []

    # build final summary rows
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

    # sort output for consistency (important for frontend/PDF)
    summary_rows = sorted(
        summary_rows,
        key=lambda x: (
            x["project_name"] or "",
            x["category_type"],
            str(x["category_value"])
        )
    )

    # round numbers for cleaner display
    for row in summary_rows:
        if row["min_price"] is not None:
            row["min_price"] = round(row["min_price"], 2)
        if row["max_price"] is not None:
            row["max_price"] = round(row["max_price"], 2)
        if row["min_area_m2"] is not None:
            row["min_area_m2"] = round(row["min_area_m2"], 2)
        if row["max_area_m2"] is not None:
            row["max_area_m2"] = round(row["max_area_m2"], 2)

    return summary_rows