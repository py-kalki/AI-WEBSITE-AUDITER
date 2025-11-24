from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os

class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = self.styles['Heading1']
        self.heading_style = self.styles['Heading2']
        self.normal_style = self.styles['BodyText']
        
    def generate(self, lead_data, audit_data, suggestions, filename):
        """Generates a PDF report for the audit."""
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        
        # Title
        story.append(Paragraph(f"Website Audit Report: {lead_data.get('business_name')}", self.title_style))
        story.append(Spacer(1, 12))
        
        # Business Info
        story.append(Paragraph("Business Information", self.heading_style))
        info_data = [
            ["Business Name", lead_data.get('business_name', 'N/A')],
            ["Category", lead_data.get('category', 'N/A')],
            ["Website", lead_data.get('website', 'N/A')],
            ["Phone", lead_data.get('phone', 'N/A')],
            ["Address", lead_data.get('address', 'N/A')]
        ]
        t = Table(info_data, colWidths=[150, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # Audit Scores
        story.append(Paragraph("Audit Scores", self.heading_style))
        score_data = [
            ["Metric", "Score"],
            ["Performance", f"{audit_data.get('performance_score', 0)}/100"],
            ["SEO", f"{audit_data.get('seo_score', 0)}/100"],
            ["UX", f"{audit_data.get('ux_score', 0)}/100"],
            ["Mobile", f"{audit_data.get('mobile_score', 0)}/100"],
            ["Overall Score", f"{audit_data.get('overall_score', 0)}/100"]
        ]
        
        t_scores = Table(score_data, colWidths=[200, 100])
        t_scores.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t_scores)
        story.append(Spacer(1, 20))
        
        # Key Issues
        story.append(Paragraph("Key Issues Identified", self.heading_style))
        priorities = audit_data.get('priorities', [])
        if priorities:
            for p in priorities:
                text = f"<b>[{p.get('priority', 'Medium')}] {p.get('category', 'General')}:</b> {p.get('issue', 'Unknown issue')}"
                story.append(Paragraph(text, self.normal_style))
                story.append(Spacer(1, 6))
        else:
            story.append(Paragraph("No major issues found.", self.normal_style))
            
        story.append(Spacer(1, 20))
        
        # AI Suggestions
        story.append(Paragraph("AI Recommendations", self.heading_style))
        if suggestions:
            story.append(Paragraph(suggestions.replace("\n", "<br/>"), self.normal_style))
        else:
            story.append(Paragraph("No AI suggestions available.", self.normal_style))
            
        # Build PDF
        try:
            doc.build(story)
            print(f"Report generated: {filename}")
            return True
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False

if __name__ == "__main__":
    # Test
    gen = PDFReportGenerator()
    dummy_lead = {"business_name": "Test Biz", "category": "Test", "website": "example.com"}
    dummy_audit = {"performance_score": 80, "seo_score": 70, "ux_score": 90, "mobile_score": 60, "overall_score": 75, 
                   "priorities": [{"priority": "High", "category": "Mobile", "issue": "Horizontal scroll"}]}
    gen.generate(dummy_lead, dummy_audit, "Improve mobile responsiveness.", "test_report.pdf")
