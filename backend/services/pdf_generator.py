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
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph("Real Estate Summary Report", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 0.4 * cm))

    table_data = [[
        "Developer",
        "Project",
        "Category Type",
        "Category Value",
        "Min Area (m2)",
        "Max Area (m2)",
        "Min Price",
        "Max Price",
    ]]

    for row in summary_rows:
        table_data.append([
            row.get("developer_name") or "-",
            row.get("project_name") or "-",
            row.get("category_type") or "-",
            str(row.get("category_value")) if row.get("category_value") is not None else "-",
            row.get("min_area_m2") if row.get("min_area_m2") is not None else "-",
            row.get("max_area_m2") if row.get("max_area_m2") is not None else "-",
            row.get("min_price") if row.get("min_price") is not None else "-",
            row.get("max_price") if row.get("max_price") is not None else "-",
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[3.2 * cm, 4.0 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm, 3.0 * cm, 3.5 * cm, 3.5 * cm],
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer