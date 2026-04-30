from collections import defaultdict


def build_summary(units):
    groups = defaultdict(list)

    for unit in units:
        project_name = unit.get("project_name") or "Unknown Project"
        source_file = unit.get("source_file") or "Unknown File"

        bedrooms = unit.get("bedrooms")
        unit_type = unit.get("unit_type")
        unit_type_text = str(unit_type).strip() if unit_type else ""
        unit_type_lower = unit_type_text.lower()

        # Villas / Offices / Town Houses / Studios, etc.
        # Check these BEFORE bedrooms because names like Villa B1 or Studio A2
        # can wrongly be parsed as bedroom numbers.
        if "villa" in unit_type_lower:
            category_type = "unit_type"
            category_value = "Villa"

        elif "studio" in unit_type_lower:
            category_type = "unit_type"
            category_value = "Studio"

        elif "office" in unit_type_lower:
            category_type = "unit_type"
            category_value = "Office"

        elif (
            "town house" in unit_type_lower
            or "townhouse" in unit_type_lower
            or unit_type_lower.startswith("tw")
            or unit_type_lower.startswith("th")
        ):
            category_type = "unit_type"
            category_value = "Town House"

        elif "duplex" in unit_type_lower:
            category_type = "unit_type"
            category_value = "Duplex"

        elif "penthouse" in unit_type_lower:
            category_type = "unit_type"
            category_value = "Penthouse"

        # Bedrooms should be grouped by number only:
        # 1 Bedroom, 2 Bedrooms, 3 Bedrooms
        elif bedrooms is not None:
            category_type = "bedrooms"
            category_value = int(bedrooms)

        # Other unit types
        elif unit_type_text:
            category_type = "unit_type"
            category_value = unit_type_text.title()

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

        if category_type == "bedrooms":
            if category_value == 1:
                category_label = "1 Bedroom"
            else:
                category_label = f"{category_value} Bedrooms"
        else:
            category_label = str(category_value)

        summary_rows.append({
            "source_file": source_file,
            "project_name": project_name,
            "category_type": category_type,
            "category_value": category_label,
            "starting_price": cheapest_unit.get("price_total"),
            "starting_area_m2": cheapest_unit.get("area_m2"),
        })

    return summary_rows