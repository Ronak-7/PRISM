import smtplib
import ssl
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# ── Configuration ─────────────────────────────────
EMAIL_SENDER = "prism.security.alerts@gmail.com"       # Replace with your Gmail
EMAIL_PASSWORD = "iajcywdfmotzruaw"   # Replace with your App Password
EMAIL_RECEIVER = "prism.security.alerts@gmail.com"     # Replace with alert recipient

REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

# ── Severity Classification ────────────────────────
def classify_severity(device, value):
    thresholds = {
        "sensor/temperature":     {"medium": 30,  "high": 40},
        "sensor/humidity":        {"medium": 20,  "high": 10},
        "sensor/cpu_load":        {"medium": 70,  "high": 90},
        "sensor/network_traffic": {"medium": 1000,"high": 2000},
        "sensor/power_consumption":{"medium": 300, "high": 400},
        "sensor/motion":          {"medium": 1,   "high": 1},
        "sensor/door_access":     {"medium": 5,   "high": 10},
        "sensor/packet_loss":     {"medium": 10,  "high": 20},
    }
    if device not in thresholds:
        return "LOW"
    t = thresholds[device]
    if value >= t["high"]:
        return "HIGH"
    elif value >= t["medium"]:
        return "MEDIUM"
    return "LOW"

# ── Email Alert ────────────────────────────────────
def send_email_alert(incident):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚨 PRISM Alert — {incident['severity']} Severity Anomaly Detected"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER

        body = f"""
PRISM — Predictive Real-time IoT Security Monitoring
=====================================================
⚠️  ANOMALY DETECTED

Device:       {incident['device']}
Value:        {incident['value']}
Severity:     {incident['severity']}
Timestamp:    {incident['timestamp']}
Report ID:    {incident['report_id']}
Anomaly Type: {incident['anomaly_type']}

RECOMMENDED ACTION:
{incident['recommended_action']}

— PRISM Automated Alert System
        """
        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print(f"✅ Email alert sent for {incident['report_id']}")
        return True

    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

# ── PDF Report ─────────────────────────────────────
def generate_pdf_report(incident):
    report_path = f"{REPORTS_DIR}/{incident['report_id']}.pdf"
    doc = SimpleDocTemplate(report_path, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontSize=20, alignment=TA_CENTER,
                                  textColor=colors.HexColor('#1F3864'),
                                  fontName='Helvetica-Bold', spaceAfter=6)
    subtitle_style = ParagraphStyle('subtitle', fontSize=11,
                                     alignment=TA_CENTER,
                                     textColor=colors.HexColor('#2E5C9E'),
                                     spaceAfter=4)
    heading_style = ParagraphStyle('heading', fontSize=13,
                                    textColor=colors.HexColor('#1F3864'),
                                    fontName='Helvetica-Bold', spaceAfter=6,
                                    spaceBefore=12)
    normal_style = styles['Normal']

    severity_colors = {
        "HIGH": colors.HexColor('#FF4444'),
        "MEDIUM": colors.HexColor('#FFA500'),
        "LOW": colors.HexColor('#28A745')
    }
    sev_color = severity_colors.get(incident['severity'], colors.grey)

    elements = []

    # Header
    elements.append(Paragraph("PRISM", title_style))
    elements.append(Paragraph("Predictive Real-time IoT Security Monitoring",
                               subtitle_style))
    elements.append(Paragraph("INCIDENT REPORT", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2,
                                color=colors.HexColor('#1F3864')))
    elements.append(Spacer(1, 0.3*cm))

    # Report Meta
    meta_data = [
        ["Report ID", incident['report_id']],
        ["Date & Time", incident['timestamp']],
        ["Status", "OPEN"],
    ]
    meta_table = Table(meta_data, colWidths=[5*cm, 12*cm])
    meta_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1F3864')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.3*cm))

    # Severity Badge
    sev_data = [["SEVERITY", incident['severity']]]
    sev_table = Table(sev_data, colWidths=[5*cm, 12*cm])
    sev_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TEXTCOLOR', (1, 0), (1, 0), sev_color),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#1F3864')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(sev_table)
    elements.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor('#CCCCCC')))

    # Incident Summary
    elements.append(Paragraph("INCIDENT SUMMARY", heading_style))
    summary_data = [
        ["Device", incident['device']],
        ["Anomaly Type", incident['anomaly_type']],
        ["Value Recorded", str(incident['value'])],
        ["Normal Range", incident['normal_range']],
        ["ML Model", incident['ml_model']],
        ["Anomaly Score", str(incident['anomaly_score'])],
    ]
    summary_table = Table(summary_data, colWidths=[5*cm, 12*cm])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2E5C9E')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1),
         [colors.HexColor('#F5F8FF'), colors.white]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
    ]))
    elements.append(summary_table)

    # Recommended Response
    elements.append(Paragraph("RECOMMENDED RESPONSE (NIST CSF)",
                               heading_style))
    elements.append(Paragraph(incident['recommended_action'], normal_style))
    elements.append(Spacer(1, 0.3*cm))

    # Footer
    elements.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor('#CCCCCC')))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        f"Generated by PRISM Automated Incident Response System | {incident['timestamp']}",
        ParagraphStyle('footer', fontSize=8, textColor=colors.grey,
                        alignment=TA_CENTER)))

    doc.build(elements)
    print(f"📄 PDF report generated: {report_path}")
    return report_path

# ── Main Incident Handler ──────────────────────────
def handle_incident(device, value, anomaly_score, ml_model="Isolation Forest"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    severity = classify_severity(device, value)

    normal_ranges = {
        "sensor/temperature": "20°C - 25°C",
        "sensor/humidity": "40% - 60%",
        "sensor/cpu_load": "10% - 50%",
        "sensor/network_traffic": "100 - 500 KB/s",
        "sensor/power_consumption": "50W - 150W",
        "sensor/motion": "0 (No Motion)",
        "sensor/door_access": "0 - 3 attempts/min",
        "sensor/packet_loss": "0% - 2%",
    }

    actions = {
        "HIGH": "IMMEDIATELY isolate the affected device. Investigate for cyberattack or critical failure. Escalate to security team. Log all activity.",
        "MEDIUM": "Monitor device closely. Review recent activity logs. Consider temporary isolation if behaviour persists.",
        "LOW": "Log the event for audit purposes. Continue monitoring. No immediate action required."
    }

    incident = {
        "report_id": report_id,
        "timestamp": timestamp,
        "device": device,
        "value": value,
        "severity": severity,
        "anomaly_type": "Sensor Anomaly — Value Outside Normal Range",
        "normal_range": normal_ranges.get(device, "Unknown"),
        "ml_model": ml_model,
        "anomaly_score": anomaly_score,
        "recommended_action": actions[severity]
    }

    print(f"\n{'='*50}")
    print(f"INCIDENT DETECTED — {report_id}")
    print(f"Device: {device} | Value: {value} | Severity: {severity}")
    print(f"{'='*50}")

    # Generate PDF
    generate_pdf_report(incident)

    # Send email only for HIGH severity
    if severity == "HIGH":
        send_email_alert(incident)

    return incident

# ── Test ───────────────────────────────────────────
if __name__ == "__main__":
    print("PRISM Incident Response System — Test")
    print("=" * 50)

    # Simulate a high severity anomaly
    handle_incident(
        device="sensor/cpu_load",
        value=97.3,
        anomaly_score=0.87,
        ml_model="Isolation Forest"
    )

    # Simulate a medium severity anomaly
    handle_incident(
        device="sensor/temperature",
        value=35.0,
        anomaly_score=0.45,
        ml_model="Autoencoder"
    )

    print("\nIncident response test complete!")
    print(f"Check the reports/ folder for generated PDFs")