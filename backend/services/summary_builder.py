# build grouped summary rows from extracted units
def build_summary(units):
    grouped = {}

    for unit in units:
        developer = unit.get("developer_name")
        project = unit.get("project_name")
        bedrooms = unit.get("bedrooms")
        unit_type = unit.get("unit_type")
        price = unit.get("price_total")

        # skip rows with no project
        if project is None:
            continue

        # use bedrooms first, otherwise fallback to unit_type
        category_type = "bedrooms" if bedrooms is not None else "unit_type"
        category_value = bedrooms if bedrooms is not None else unit_type

        # skip rows with no grouping value
        if category_value is None:
            continue

        # skip rows with no price because we want a real starting unit
        if price is None:
            continue

        key = (developer, project, category_type, category_value)

        if key not in grouped:
            grouped[key] = {
                "developer_name": developer,
                "project_name": project,
                "category_type": category_type,
                "category_value": category_value,
                "units": [],
            }

        grouped[key]["units"].append(unit)

    summary_rows = []

    for group in grouped.values():
        units_in_group = group["units"]

        if not units_in_group:
            continue

        # choose one real connected row = lowest price row
        starting_unit = min(units_in_group, key=lambda x: x["price_total"])

        summary_rows.append({
            "developer_name": group["developer_name"],
            "project_name": group["project_name"],
            "category_type": group["category_type"],
            "category_value": group["category_value"],

            # all values below come from the SAME row
            "starting_price": round(starting_unit["price_total"], 2) if starting_unit.get("price_total") is not None else None,
            "starting_area_m2": round(starting_unit["area_m2"], 2) if starting_unit.get("area_m2") is not None else None,
            "unit_code": starting_unit.get("unit_code"),
            "building": starting_unit.get("building"),
            "floor_number": starting_unit.get("floor_number"),
            "unit_type": starting_unit.get("unit_type"),
        })

    summary_rows = sorted(
        summary_rows,
        key=lambda x: (
            x["project_name"] or "",
            x["category_type"] or "",
            str(x["category_value"])
        )
    )

    return summary_rows