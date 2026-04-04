"""PDF Report Generator for PlaybookPulse compliance reports"""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_compliance_pdf(
    analysis_result: Dict[str, Any],
    output_filename: str = "compliance_report.pdf",
    incident_id: str = "UNKNOWN"
) -> str:
    """
    Generates an auditor-ready PDF from the AI's analysis result.
    
    Args:
        analysis_result: The full analysis result from agents_bridge
        output_filename: Name of the PDF file to generate
        incident_id: Incident identifier
        
    Returns:
        Absolute path to the generated PDF
    """
    # Ensure output directory exists
    output_dir = Path(__file__).parent / "reports"
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / output_filename
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor("#374151"),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Build document content
    story = []
    
    # Title
    story.append(Paragraph("PlaybookPulse", title_style))
    story.append(Paragraph("Incident Response Compliance Report", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    
    # Metadata section
    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    adherence = analysis_result.get("adherence", {})
    score = adherence.get("overall_score", 0)
    
    metadata_data = [
        ["Incident ID:", incident_id],
        ["Report Generated:", generated_time],
        ["Compliance Score:", f"{score:.1f}%"],
        ["Analysis Timestamp:", analysis_result.get("timestamp", "N/A")],
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f3f4f6")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(metadata_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    
    full = adherence.get("full_adherence", 0)
    partial = adherence.get("partial_adherence", 0)
    none_count = adherence.get("no_adherence", 0)
    
    summary_text = f"""
    This report presents the compliance analysis for incident {incident_id}. 
    The analysis was performed by PlaybookPulse's multi-agent AI system, which evaluated 
    adherence to established incident response playbooks and mapped findings to compliance frameworks.
    <br/><br/>
    <b>Key Findings:</b><br/>
    • Steps Fully Followed: {full}<br/>
    • Steps Partially Followed: {partial}<br/>
    • Steps Not Followed: {none_count}<br/>
    • Overall Compliance Score: {score:.1f}%
    """
    
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Playbook Information
    playbook = analysis_result.get("playbook", {})
    story.append(Paragraph("Playbook Information", heading_style))
    
    playbook_text = f"""
    <b>Title:</b> {playbook.get('title', 'Unknown')}<br/>
    <b>Total Steps:</b> {playbook.get('total_steps', 0)}<br/>
    <b>Phases:</b> {', '.join(playbook.get('phases', [])) if playbook.get('phases') else 'Not specified'}
    """
    
    story.append(Paragraph(playbook_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Adherence Details Table
    story.append(Paragraph("Detailed Adherence Analysis", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    # Build adherence table
    table_data = [
        ["Step", "Phase", "Description", "Adherence", "Evidence"]
    ]
    
    # Table style commands
    table_style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    
    adherence_checks = adherence.get("checks", [])
    
    for i, check in enumerate(adherence_checks):
        row_idx = i + 1
        adherence_level = check.get("adherence_level", "unknown")
        
        # Format evidence
        evidence_list = check.get("evidence", [])
        if evidence_list:
            evidence_text = evidence_list[0] if len(evidence_list) == 1 else f"{len(evidence_list)} items found"
        else:
            evidence_text = "No evidence"
        
        # Wrap long text
        description = check.get("description", "N/A")
        if len(description) > 60:
            description = description[:57] + "..."
        
        row = [
            str(check.get("step_number", i+1)),
            check.get("phase", "N/A"),
            Paragraph(description, styles['Normal']),
            adherence_level.upper(),
            Paragraph(evidence_text, styles['Normal'])
        ]
        table_data.append(row)
        
        # Color-code based on adherence
        if adherence_level == "full":
            bg_color = colors.HexColor("#dcfce7")  # Light green
        elif adherence_level == "partial":
            bg_color = colors.HexColor("#fef08a")  # Light yellow
        else:  # none
            bg_color = colors.HexColor("#fee2e2")  # Light red
        
        table_style_commands.append(
            ('BACKGROUND', (0, row_idx), (-1, row_idx), bg_color)
        )
    
    # Create table
    adherence_table = Table(
        table_data,
        colWidths=[0.5*inch, 1*inch, 2*inch, 1*inch, 2*inch]
    )
    adherence_table.setStyle(TableStyle(table_style_commands))
    story.append(adherence_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    story.append(Paragraph("Recommendations", heading_style))
    recommendations = analysis_result.get("recommendations", [])
    
    if recommendations:
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))
    else:
        story.append(Paragraph("No specific recommendations at this time.", styles['Normal']))
    
    story.append(Spacer(1, 0.2*inch))
    
    # Compliance Framework Mappings
    compliance = analysis_result.get("compliance", {})
    frameworks = compliance.get("frameworks_analyzed", [])
    
    if frameworks:
        story.append(Paragraph("Compliance Framework Mappings", heading_style))
        
        frameworks_text = f"<b>Frameworks Analyzed:</b> {', '.join(frameworks)}"
        story.append(Paragraph(frameworks_text, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        mappings = compliance.get("mappings", [])
        if mappings:
            mapping_text = f"Total compliance mappings identified: {len(mappings)}"
            story.append(Paragraph(mapping_text, styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        "This report was automatically generated by PlaybookPulse AI Compliance Auditor",
        footer_style
    ))
    
    # Build PDF
    doc.build(story)
    
    return str(output_path.absolute())


def generate_quick_summary_pdf(
    score: float,
    full: int,
    partial: int,
    missed: int,
    recommendations: List[str],
    incident_id: str = "UNKNOWN",
    output_filename: str = "quick_summary.pdf"
) -> str:
    """
    Generates a quick 1-page summary PDF (for Slack quick downloads).
    
    Args:
        score: Overall compliance score
        full: Number of steps fully followed
        partial: Number of steps partially followed
        missed: Number of steps missed
        recommendations: List of recommendation strings
        incident_id: Incident identifier
        output_filename: Name of the PDF file
        
    Returns:
        Absolute path to the generated PDF
    """
    output_dir = Path(__file__).parent / "reports"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / output_filename
    
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=20
    )
    story.append(Paragraph("PlaybookPulse Compliance Summary", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Score box
    score_data = [
        ["Compliance Score", f"{score:.1f}%"],
        ["Steps Followed", str(full)],
        ["Steps Partial", str(partial)],
        ["Steps Missed", str(missed)]
    ]
    
    score_table = Table(score_data, colWidths=[3*inch, 2*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f3f4f6")),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(score_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    story.append(Paragraph("Key Recommendations", styles['Heading2']))
    story.append(Spacer(1, 0.1*inch))
    
    for rec in recommendations[:5]:  # Top 5
        story.append(Paragraph(f"• {rec}", styles['Normal']))
        story.append(Spacer(1, 0.05*inch))
    
    doc.build(story)
    return str(output_path.absolute())
