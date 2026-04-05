"""
CIS Compliance Module

This module provides CIS Controls v8 compliance checking:
- Static checks (pre-PR) via StaticCISAgent
- Dynamic checks (post-merge) via DynamicCISAgent
- Compliance logging via ComplianceLogger
- Alert system stub via AlertSystem
"""
from app.compliance.cis_framework import (
    CISControlV8,
    CISIRPhase,
    get_cis_requirements_for_step,
    get_all_cis_controls,
    calculate_sla_violation_severity,
    SLAViolationSeverity
)
from app.compliance.timestamp_analyzer import TimestampAnalyzer
from app.compliance.static_cis_agent import StaticCISAgent
from app.compliance.dynamic_cis_agent import DynamicCISAgent
from app.compliance.compliance_logger import ComplianceLogger, LogLevel, ComplianceEventType
from app.compliance.alert_system import AlertSystem, AlertSeverity, AlertChannel, create_alert_system

__all__ = [
    # CIS Framework
    'CISControlV8',
    'CISIRPhase',
    'get_cis_requirements_for_step',
    'get_all_cis_controls',
    'calculate_sla_violation_severity',
    'SLAViolationSeverity',
    
    # Agents
    'StaticCISAgent',      # Pre-PR static compliance checks
    'DynamicCISAgent',     # Post-merge dynamic compliance checks
    'TimestampAnalyzer',
    
    # Logging
    'ComplianceLogger',
    'LogLevel',
    'ComplianceEventType',
    
    # Alerts
    'AlertSystem',
    'AlertSeverity',
    'AlertChannel',
    'create_alert_system',
]
