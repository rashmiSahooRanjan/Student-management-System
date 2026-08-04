# utils/pdf_reports.py — PDF generation with ReportLab

import io
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    )
    RL = True
except ImportError:
    RL = False


def _hdr():
    styles = getSampleStyleSheet()
    return ParagraphStyle("H", parent=styles["Heading1"], fontSize=20,
                          textColor=colors.HexColor("#1a1f35"), spaceAfter=4)

def _sub():
    styles = getSampleStyleSheet()
    return ParagraphStyle("S", parent=styles["Normal"], fontSize=10,
                          textColor=colors.HexColor("#555"))


def generate_marksheet(student, marks):
    if not RL:
        return None
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    els    = []
    styles = getSampleStyleSheet()

    els.append(Paragraph("EduNova School", _hdr()))
    els.append(Paragraph("Student Academic Marksheet", _sub()))
    els.append(Spacer(1, 0.3*cm))
    els.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#38bdf8")))
    els.append(Spacer(1, 0.4*cm))

    info = [
        ["Student Name", student.get("name","")],
        ["Student ID",   student.get("student_id","")],
        ["Class",        f"Class {student.get('class','')} – {student.get('section','')}"],
        ["Gender",       student.get("gender","")],
        ["Issue Date",   datetime.now().strftime("%d %B %Y")],
    ]
    it = Table(info, colWidths=[4.5*cm, 11*cm])
    it.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("TEXTCOLOR",     (0,0),(0,-1), colors.HexColor("#555")),
    ]))
    els += [it, Spacer(1, 0.5*cm)]

    if marks:
        hdr  = ["#", "Subject", "Exam Type", "Obtained", "Total", "Percentage", "Grade"]
        rows = [hdr] + [
            [str(i+1), m.get("subject",""), (m.get("exam_type","")).replace("_"," ").title(),
             str(int(m.get("marks_obtained",0))), str(int(m.get("total_marks",100))),
             f"{m.get('percentage',0):.1f}%", m.get("grade","")]
            for i, m in enumerate(marks)
        ]
        t = Table(rows, colWidths=[0.8*cm, 4.5*cm, 3.2*cm, 2*cm, 2*cm, 2.8*cm, 2*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,0),  colors.HexColor("#1a1f35")),
            ("TEXTCOLOR",     (0,0),(-1,0),  colors.white),
            ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0),(-1,-1), 9),
            ("ALIGN",         (3,0),(-1,-1), "CENTER"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#f4f6ff")]),
            ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#cccccc")),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ]))
        els.append(t)

        avg = sum(m.get("percentage",0) for m in marks) / len(marks)
        gpa = round(avg / 100 * 4, 2)
        els += [Spacer(1, 0.4*cm),
                Paragraph(f"<b>Overall Average: {avg:.1f}%</b>  &nbsp;&nbsp; <b>GPA (4.0): {gpa}</b>",
                          styles["Normal"])]
    else:
        els.append(Paragraph("No marks recorded.", styles["Normal"]))

    els += [Spacer(1, 1*cm),
            Paragraph("___________________________", styles["Normal"]),
            Paragraph("Authorised Signature", _sub())]

    doc.build(els)
    buf.seek(0)
    return buf.read()


def generate_fee_receipt(student, fee):
    if not RL:
        return None
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    els    = []
    styles = getSampleStyleSheet()

    els.append(Paragraph("EduNova School", _hdr()))
    els.append(Paragraph("Official Fee Payment Receipt", _sub()))
    els.append(Spacer(1, 0.3*cm))
    els.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#38bdf8")))
    els.append(Spacer(1, 0.5*cm))

    rows = [
        ["Receipt No",  fee.get("receipt_no", "—")],
        ["Student",     student.get("name","")],
        ["Student ID",  student.get("student_id","")],
        ["Class",       f"Class {student.get('class','')} – {student.get('section','')}"],
        ["Fee Type",    fee.get("fee_type","").title()],
        ["Amount",      f"INR {fee.get('amount',0):,.2f}"],
        ["Paid On",     (fee.get("paid_date","")[:10] if fee.get("paid_date") else "—")],
        ["Status",      "PAID"],
    ]
    t = Table(rows, colWidths=[4.5*cm, 11*cm])
    t.setStyle(TableStyle([
        ("FONTNAME",      (0,0),(0,-1),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 11),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("TEXTCOLOR",     (0,0),(0,-1),  colors.HexColor("#555")),
        ("TEXTCOLOR",     (1,7),(1,7),   colors.HexColor("#16a34a")),
        ("FONTNAME",      (1,7),(1,7),   "Helvetica-Bold"),
        ("FONTSIZE",      (1,7),(1,7),   13),
    ]))
    els += [t, Spacer(1, 1.2*cm),
            Paragraph("Thank you for your payment.", styles["Italic"]),
            Spacer(1, 0.8*cm),
            Paragraph("___________________________", styles["Normal"]),
            Paragraph("Cashier / Accounts Office", _sub())]

    doc.build(els)
    buf.seek(0)
    return buf.read()
