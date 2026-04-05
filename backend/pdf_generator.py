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


def generate_cis_compliance_pdf(
    analysis_result: Dict[str, Any],
    incident_id: str = "UNKNOWN",
    output_filename: str = None
) -> str:
    """
    Generates CIS Controls v8 specific compliance report PDF.
    
    Args:
        analysis_result: The full CIS analysis result
        incident_id: Incident identifier
        output_filename: Name of the PDF file (auto-generated if not provided)
        
    Returns:
        Absolute path to the generated PDF
    """
    output_dir = Path(__file__).parent / "reports"
    output_dir.mkdir(exist_ok=True)
    
    if not output_filename:
        output_filename = f"cis_compliance_report_{incident_id}.pdf"
    
    output_path = output_dir / output_filename
    
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CISTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#1e3a5f"),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CISHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor("#1e3a5f"),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'CISSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor("#374151"),
        spaceAfter=8
    )
    
    story = []
    
    # ============ TITLE PAGE ============
    story.append(Paragraph("CIS Controls v8", title_style))
    story.append(Paragraph("Incident Response Compliance Report", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Control 17: Incident Response Management", subheading_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Metadata
    generated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    adherence = analysis_result.get("adherence", {})
    score = adherence.get("overall_score", 0)
    
    cis_compliance = analysis_result.get("cis_compliance", {})
    cis_score = 0
    if cis_compliance:
        dynamic = cis_compliance.get("dynamic_analysis", {})
        cis_score = dynamic.get("compliance_score", 0) if dynamic else 0
    
    metadata = [
        ["Incident ID:", incident_id],
        ["Report Generated:", generated_time],
        ["Framework:", "CIS Controls v8 (Control 17)"],
        ["Playbook Adherence Score:", f"{score:.1f}%"],
        ["CIS Compliance Score:", f"{cis_score:.1f}%"],
    ]
    
    meta_table = Table(metadata, colWidths=[2.5*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f0f4f8")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 0.4*inch))
    
    # ============ EXECUTIVE SUMMARY ============
    story.append(Paragraph("Executive Summary", heading_style))
    
    full = adherence.get("full_adherence", 0)
    partial = adherence.get("partial_adherence", 0)
    none_count = adherence.get("no_adherence", 0)
    
    if score >= 80:
        score_status = "COMPLIANT"
        score_color = "#22c55e"
    elif score >= 60:
        score_status = "PARTIALLY COMPLIANT"
        score_color = "#f59e0b"
    else:
        score_status = "NON-COMPLIANT"
        score_color = "#ef4444"
    
    summary = f"""
    <b>Overall Status: <font color="{score_color}">{score_status}</font></b><br/><br/>
    This CIS Controls v8 compliance report evaluates incident response activities 
    against Control 17 (Incident Response Management) safeguards. The analysis 
    was performed by PlaybookPulse's AI-powered compliance engine.<br/><br/>
    <b>Key Metrics:</b><br/>
    • Steps Fully Followed: {full}<br/>
    • Steps Partially Followed: {partial}<br/>
    • Steps Not Followed: {none_count}<br/>
    • Overall Playbook Adherence: {score:.1f}%<br/>
    • CIS Control 17 Compliance: {cis_score:.1f}%
    """
    
    story.append(Paragraph(summary, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # ============ CIS CONTROL 17 ANALYSIS ============
    story.append(Paragraph("CIS Control 17 Safeguard Analysis", heading_style))
    
    if cis_compliance:
        mappings = cis_compliance.get("mappings", [])
        
        if mappings:
            control_data = [["Control ID", "Title", "Status", "SLA"]]
            control_styles = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]
            
            for i, mapping in enumerate(mappings):
                row_idx = i + 1
                level = mapping.get("adherence_level", "unknown")
                sla = mapping.get("sla_status", "N/A")
                
                # Truncate title if needed
                title = mapping.get("control_title", "N/A")
                if len(title) > 40:
                    title = title[:37] + "..."
                
                control_data.append([
                    mapping.get("control_id", "?"),
                    title,
                    level.upper(),
                    sla.upper()
                ])
                
                # Color code rows
                if level == "full":
                    bg = colors.HexColor("#dcfce7")
                elif level == "partial":
                    bg = colors.HexColor("#fef3c7")
                else:
                    bg = colors.HexColor("#fee2e2")
                
                control_styles.append(('BACKGROUND', (0, row_idx), (-1, row_idx), bg))
            
            control_table = Table(control_data, colWidths=[1*inch, 2.8*inch, 1.2*inch, 1*inch])
            control_table.setStyle(TableStyle(control_styles))
            story.append(control_table)
        else:
            story.append(Paragraph("No CIS control mappings available.", styles['Normal']))
        
        # SLA Compliance Section
        dynamic = cis_compliance.get("dynamic_analysis", {})
        if dynamic:
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("SLA Compliance", heading_style))
            
            sla_data = dynamic.get("sla_compliance", {})
            sla_checks = sla_data.get("checks", [])
            
            if sla_checks:
                sla_table_data = [["SLA", "Required (min)", "Actual (min)", "Status"]]
                sla_styles = [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]
                
                for i, check in enumerate(sla_checks):
                    row_idx = i + 1
                    status = check.get("status", "unknown")
                    
                    sla_table_data.append([
                        check.get("sla", "N/A"),
                        str(check.get("required_minutes", "N/A")),
                        str(check.get("actual_minutes", "N/A")),
                        status.upper()
                    ])
                    
                    if status == "met":
                        bg = colors.HexColor("#dcfce7")
                    else:
                        bg = colors.HexColor("#fee2e2")
                    
                    sla_styles.append(('BACKGROUND', (0, row_idx), (-1, row_idx), bg))
                
                sla_table = Table(sla_table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1*inch])
                sla_table.setStyle(TableStyle(sla_styles))
                story.append(sla_table)
            else:
                story.append(Paragraph("Insufficient timeline data for SLA analysis.", styles['Normal']))
    
    story.append(Spacer(1, 0.3*inch))
    
    # ============ RECOMMENDATIONS ============
    story.append(Paragraph("Recommendations", heading_style))
    recommendations = analysis_result.get("recommendations", [])
    
    if recommendations:
        for rec in recommendations[:10]:
            # Color code by type
            if "CRITICAL" in rec or "VIOLATION" in rec:
                rec_text = f'<font color="#ef4444">⚠ {rec}</font>'
            elif "WARNING" in rec:
                rec_text = f'<font color="#f59e0b">⚡ {rec}</font>'
            else:
                rec_text = f"• {rec}"
            
            story.append(Paragraph(rec_text, styles['Normal']))
            story.append(Spacer(1, 0.05*inch))
    else:
        story.append(Paragraph("No recommendations at this time.", styles['Normal']))
    
    # ============ FOOTER ============
    story.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'CISFooter',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph(
        "Generated by PlaybookPulse | CIS Controls v8 Compliance Engine | " + generated_time,
        footer_style
    ))
    
    # Build PDF
    doc.build(story)
    
    return str(output_path.absolute())
