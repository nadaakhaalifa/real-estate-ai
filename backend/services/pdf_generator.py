from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def format_price(value):
    if value is None:
        return "-"
    return f"{value:,.0f} EGP"


def format_area(value):
    if value is None:
        return "-"
    return f"{value:,.2f} m²"


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

def calculate_dynamic_col_widths(table_data, usable_width, min_width=1.6 * cm, max_width=5.0 * cm):
    # estimate width from the longest text in each column
    col_count = len(table_data[0])
    max_lengths = [0] * col_count

    for row in table_data:
        for i, cell in enumerate(row):
            cell_text = str(cell) if cell is not None else ""
            max_lengths[i] = max(max_lengths[i], len(cell_text))

    # convert text lengths to proportional widths
    total_length = sum(max_lengths) if sum(max_lengths) > 0 else col_count
    raw_widths = [(usable_width * length / total_length) for length in max_lengths]

    # clamp widths to avoid too small / too large columns
    clamped_widths = [
        max(min_width, min(width, max_width))
        for width in raw_widths
    ]

    # normalize again so final widths fit the page exactly
    total_width = sum(clamped_widths)
    scale = usable_width / total_width if total_width > 0 else 1

    final_widths = [width * scale for width in clamped_widths]
    return final_widths


# build summary pdf from grouped rows
def generate_summary_pdf(summary_rows):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.0 * cm,
        rightMargin=1.0 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=colors.HexColor("#1F4E78"),
        spaceAfter=8,
    )

    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=12,
    )

    elements = []

    report_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    elements.append(Paragraph("Real Estate Starting Price Report", title_style))
    elements.append(
        Paragraph(
            f"Generated on {report_date} | Total summary rows: {len(summary_rows)}",
            meta_style,
        )
    )
    elements.append(Spacer(1, 0.3 * cm))

    table_data = [[
        "Developer",
        "Project",
        "Category",
        "Starting Price",
        "Starting Area",
        "Unit Code",
        "Building",
        "Floor",
    ]]

    for row in summary_rows:
        table_data.append([
            row.get("developer_name") or "-",
            row.get("project_name") or "-",
            format_category(row.get("category_type"), row.get("category_value")),
            format_price(row.get("starting_price")),
            format_area(row.get("starting_area_m2")),
            row.get("unit_code") or "-",
            row.get("building") or "-",
            row.get("floor_number") or "-",
        ])
    usable_width = 27 * cm
    col_widths = calculate_dynamic_col_widths(table_data, usable_width)
    
    table = Table(
        table_data,
        repeatRows=1,
        colWidths=col_widths
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#F7F9FC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer