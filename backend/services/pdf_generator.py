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

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[2.8 * cm, 4.0 * cm, 3.0 * cm, 3.2 * cm, 3.0 * cm, 2.8 * cm, 2.5 * cm, 2.0 * cm],
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#F7F9FC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer