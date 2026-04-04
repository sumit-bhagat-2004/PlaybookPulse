"""PDF Report Generator Service"""
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import io

from app.utils.logger import logger


class PDFGenerator:
    """Service for generating PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
    
    def generate_analysis_report(
        self,
        analysis_data: Dict[str, Any],
        include_recommendations: bool = True,
        include_evidence: bool = True
    ) -> bytes:
        """
        Generate a PDF report for an analysis
        
        Args:
            analysis_data: Complete analysis results
            include_recommendations: Include recommendations section
            include_evidence: Include evidence details
            
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        
        try:
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
            )
            
            story.append(Paragraph("Incident Response Analysis Report", title_style))
            story.append(Spacer(1, 0.3 * inch))
            
            # Summary
            story.append(Paragraph("Executive Summary", self.styles['Heading2']))
            
            summary_data = [
                ["Analysis ID", analysis_data.get("analysis_id", "N/A")],
                ["Status", analysis_data.get("status", "N/A")],
                ["Overall Score", f"{analysis_data.get('overall_score', 0)}%"],
                ["Completed At", analysis_data.get("completed_at", "N/A")]
            ]
            
            summary_table = Table(summary_data, colWidths=[2 * inch, 4 * inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.5 * inch))
            
            # Adherence Checks
            result = analysis_data.get("result", {})
            adherence_checks = result.get("adherence_checks", [])
            
            if adherence_checks:
                story.append(Paragraph("Adherence Results", self.styles['Heading2']))
                
                for check in adherence_checks:
                    story.append(Paragraph(
                        f"Step: {check.get('step_id')}",
                        self.styles['Heading3']
                    ))
                    story.append(Paragraph(
                        f"Adherence Level: {check.get('adherence_level')}",
                        self.styles['Normal']
                    ))
                    
                    if include_evidence and check.get('evidence'):
                        story.append(Paragraph("Evidence:", self.styles['Normal']))
                        for evidence in check.get('evidence', []):
                            story.append(Paragraph(f"• {evidence}", self.styles['Normal']))
                    
                    if include_recommendations and check.get('recommendations'):
                        story.append(Paragraph("Recommendations:", self.styles['Normal']))
                        for rec in check.get('recommendations', []):
                            story.append(Paragraph(f"• {rec}", self.styles['Normal']))
                    
                    story.append(Spacer(1, 0.2 * inch))
            
            # Build PDF
            doc.build(story)
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            logger.info(f"Generated PDF report ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            raise
