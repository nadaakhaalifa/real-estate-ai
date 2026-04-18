from io import BytesIO

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment


def format_category(category_type, category_value):
    if category_value is None:
        return "-"

    if category_type == "bedrooms":
        if category_value == 0:
            return "Studio"
        if category_value == 1:
            return "1 Bedroom"
        return f"{category_value} Bedrooms"

    return str(category_value)


# build excel report from summary rows
def generate_summary_excel(summary_rows):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Summary"

    headers = [
        "Developer",
        "Project",
        "Category",
        "Starting Price",
        "Starting Area (m2)",
        "Unit Code",
        "Building",
        "Floor",
    ]

    sheet.append(headers)

    # style header row
    header_fill = PatternFill(fill_type="solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)

    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # add data rows
    for row in summary_rows:
        sheet.append([
            row.get("developer_name") or "-",
            row.get("project_name") or "-",
            format_category(row.get("category_type"), row.get("category_value")),
            row.get("starting_price"),
            row.get("starting_area_m2"),
            row.get("unit_code") or "-",
            row.get("building") or "-",
            row.get("floor_number") or "-",
        ])

    # set column widths
    widths = {
        "A": 18,
        "B": 24,
        "C": 18,
        "D": 18,
        "E": 18,
        "F": 16,
        "G": 14,
        "H": 12,
    }

    for col, width in widths.items():
        sheet.column_dimensions[col].width = width

    # center align everything
    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(horizontal="center", vertical="center")

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer