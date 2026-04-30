from collections import defaultdict


def build_summary(units):
    groups = defaultdict(list)

    for unit in units:
        bedrooms = unit.get("bedrooms")
        unit_type = unit.get("unit_type")
        unit_type_text = str(unit_type).strip() if unit_type else ""

        # Group all bedrooms together, ignoring project/zone/type
        if bedrooms is not None:
            category_type = "bedrooms"
            category_value = int(bedrooms)

        # Only use unit type when bedrooms is missing
        elif unit_type_text:
            category_type = "unit_type"
            category_value = unit_type_text.lower()

        else:
            category_type = "unit_type"
            category_value = "unit"

        key = (
            category_type,
            category_value,
        )

        groups[key].append(unit)

    summary_rows = []

    for (category_type, category_value), group_units in groups.items():
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

        if category_type == "bedrooms":
            label = f"All {category_value} Bedroom"
            if category_value > 1:
                label += "s"
        else:
            label = f"All {str(category_value).title()}s"

        summary_rows.append({
            "source_file": "All Files",
            "project_name": "All Projects",
            "category_type": category_type,
            "category_value": label,
            "starting_price": cheapest_unit.get("price_total"),
            "starting_area_m2": cheapest_unit.get("area_m2"),
        })

    return summary_rows