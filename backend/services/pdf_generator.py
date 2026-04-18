from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


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
    elements = []

    elements.append(Paragraph("Real Estate Summary Report", styles["Title"]))
    elements.append(Spacer(1, 0.4 * cm))

    table_data = [[
        "Developer",
        "Project",
        "Category Type",
        "Category Value",
        "Starting Price",
        "Starting Area (m2)",
        "Unit Code",
        "Building",
        "Floor",
    ]]

    for row in summary_rows:
        table_data.append([
            row.get("developer_name") or "-",
            row.get("project_name") or "-",
            row.get("category_type") or "-",
            str(row.get("category_value")) if row.get("category_value") is not None else "-",
            row.get("starting_price") if row.get("starting_price") is not None else "-",
            row.get("starting_area_m2") if row.get("starting_area_m2") is not None else "-",
            row.get("unit_code") or "-",
            row.get("building") or "-",
            row.get("floor_number") or "-",
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[2.3 * cm, 3.3 * cm, 2.4 * cm, 2.4 * cm, 3.0 * cm, 3.0 * cm, 2.8 * cm, 2.2 * cm, 2.0 * cm],
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer