from collections import defaultdict


def build_summary(units):
    groups = defaultdict(list)

    for unit in units:
        project_name = unit.get("project_name") or "Unknown Project"
        source_file = unit.get("source_file") or "Unknown File"

        bedrooms = unit.get("bedrooms")
        unit_type = unit.get("unit_type")

        if bedrooms is not None:
            category_type = "bedrooms"
            category_value = int(bedrooms)
        elif unit_type:
            category_type = "unit_type"
            category_value = str(unit_type).strip()
        else:
            category_type = "unit_type"
            category_value = "Unit"

        key = (
            source_file,
            project_name,
            category_type,
            category_value,
        )

        groups[key].append(unit)

    summary_rows = []

    for (source_file, project_name, category_type, category_value), group_units in groups.items():
        valid_price_units = [
            unit for unit in group_units
            if unit.get("price_total") is not None
        ]

        if not valid_price_units:
            continue

        cheapest_unit = min(
            valid_price_units,
            key=lambda unit: float(unit.get("price_total") or 0)
        )

        starting_price = cheapest_unit.get("price_total")
        starting_area = cheapest_unit.get("area_m2")

        summary_rows.append({
            "source_file": source_file,
            "project_name": project_name,
            "category_type": category_type,
            "category_value": category_value,
            "starting_price": starting_price,
            "starting_area_m2": starting_area,
        })

    return summary_rows