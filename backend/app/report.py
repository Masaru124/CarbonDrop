from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile, os
from sqlalchemy.orm import Session
from . import models, auth, database

router = APIRouter()

@router.get("/pdf")
def generate_report(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Carbon Footprint Report for {current_user.username}", styles["Heading1"]))
    story.append(Spacer(1, 20))

    # Get user's receipts
    receipts = db.query(models.Receipt).filter(models.Receipt.user_id == current_user.id).order_by(models.Receipt.date.desc()).all()
    total_footprint = sum(r.total_footprint for r in receipts)

    story.append(Paragraph(f"Total Carbon Footprint: {round(total_footprint, 2)} kg CO₂", styles["Heading2"]))
    story.append(Spacer(1, 10))

    if receipts:
        story.append(Paragraph("Receipt Details:", styles["Heading3"]))
        story.append(Spacer(1, 10))
        for r in receipts:
            story.append(Paragraph(f"Date: {r.date.strftime('%Y-%m-%d')}, Footprint: {round(r.total_footprint, 2)} kg CO₂", styles["Normal"]))
            story.append(Spacer(1, 5))
    else:
        story.append(Paragraph("No receipts found.", styles["Normal"]))

    doc.build(story)
    return FileResponse(tmp.name, filename="footprint_report.pdf", media_type="application/pdf")
