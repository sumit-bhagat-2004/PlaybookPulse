"""Sample test data for testing agents and orchestrator"""

# Sample incident response playbook
SAMPLE_PLAYBOOK = """# Incident Response Playbook - Database Corruption

## Overview
This playbook describes the process for responding to database corruption incidents.

## Detection
1. Monitor database integrity checks every hour
2. Alert on DBCC CheckDB failures
3. Check transaction logs for unusual patterns
4. Monitor application error logs for data access anomalies

### Success Criteria
- Detection within 15 minutes of occurrence
- Error rate < 1% false positives

## Containment
1. Isolate affected database from production traffic
2. Stop all write operations to corrupt tables
3. Enable read-only mode for non-affected tables
4. Notify DBA team immediately

### Escalation
- P1 if > 100GB affected
- P2 if 10-100GB affected
- P3 if < 10GB affected

## Investigation
1. Backup the corrupted database immediately
2. Run detailed DBCC CheckDB analysis
3. Identify scope of corruption (tables, indexes, LOB data)
4. Determine root cause (hardware, software, configuration)
5. Check recent changes (schema modifications, updates, backups)

## Recovery
1. Restore from latest clean backup
2. Rerun transactions from transaction log
3. Verify data integrity post-recovery
4. Run production validation suite
5. Document recovery time and impact

## Post-Incident
1. Root cause analysis
2. Implement preventive measures
3. Update backup procedures if needed
4. Schedule hardware diagnostics if hardware failure detected
5. Update runbooks based on lessons learned

## Roles and Responsibilities
- **Incident Commander**: Coordinates response, communicates status
- **DBA**: Leads technical investigation and recovery
- **Security**: Verifies no data exfiltration occurred
- **Communications**: Updates stakeholders

## Communication Plan
- Internal stakeholders: Every 30 minutes
- Customers: Only if > 1 hour downtime
- Executive leadership: Escalations only

## Success Metrics
- Time to Detection (TTD): Target < 15 minutes
- Time to Recovery (TTR): Target < 2 hours
- Data Loss: Target = 0 (RPO)
- System Availability: Target 99.9%

## Tools and Access
- Database admin tools: Available on ADMIN-DB-01
- Backup systems: Accessible via VPN
- Monitoring dashboard: prod-monitoring.internal
- Escalation contacts: See runbook page X
"""

# Sample incident data without external integrations
SAMPLE_INCIDENT_DATA = {
    "incident_id": "INC-2024-001",
    "title": "Database Corruption - Customer Transactions",
    "description": "Detected data corruption in transactions table affecting last 2 hours of data",
    "detected_at": "2024-01-15T14:30:00Z",
    "severity": "high",
    "affected_systems": ["prod-db-primary", "prod-db-replica"],
    "timeline": [
        {
            "timestamp": "2024-01-15T14:30:00Z",
            "event": "Database integrity check failed",
            "source": "monitoring"
        },
        {
            "timestamp": "2024-01-15T14:32:00Z",
            "event": "DBA team alerted",
            "source": "alerting_system"
        },
        {
            "timestamp": "2024-01-15T14:35:00Z",
            "event": "Database isolated from traffic",
            "source": "manual"
        }
    ],
    "initial_symptoms": [
        "DBCC CheckDB showing corruption in transactions table",
        "Application experiencing connection timeouts",
        "Monitoring alerts on error rate spike"
    ],
    "preliminary_scope": "~500GB data in 5 tables"
}

# Sample analysis results for testing
SAMPLE_ANALYSIS_RESULT = {
    "playbook_structure": {
        "has_detection": True,
        "has_containment": True,
        "has_investigation": True,
        "has_recovery": True,
        "has_post_incident": True,
        "completeness_score": 95
    },
    "adherence_checks": [
        {
            "step_id": "detection",
            "framework": "NIST_SP_800_61",
            "adherence_level": "full",
            "score": 90,
            "findings": [
                "Clear detection triggers defined",
                "Success criteria specified",
                "Escalation procedures documented"
            ],
            "recommendations": [
                "Add specific alert thresholds (DBCC return codes)"
            ]
        },
        {
            "step_id": "containment",
            "framework": "NIST_SP_800_61",
            "adherence_level": "full",
            "score": 85,
            "findings": [
                "Isolation procedures clear",
                "Escalation matrix defined"
            ],
            "recommendations": [
                "Add timeouts for containment actions",
                "Specify backup verification procedures"
            ]
        },
        {
            "step_id": "investigation",
            "framework": "NIST_SP_800_61",
            "adherence_level": "partial",
            "score": 70,
            "findings": [
                "Investigation steps defined",
                "Tools referenced"
            ],
            "recommendations": [
                "Add forensic data collection procedures",
                "Include chain of custody for evidence",
                "Define data retention for investigation"
            ]
        },
        {
            "step_id": "recovery",
            "framework": "NIST_SP_800_61",
            "adherence_level": "full",
            "score": 92,
            "findings": [
                "Recovery steps detailed",
                "Validation procedures included"
            ],
            "recommendations": []
        },
        {
            "step_id": "post_incident",
            "framework": "NIST_SP_800_61",
            "adherence_level": "partial",
            "score": 65,
            "findings": [
                "Basic review steps listed"
            ],
            "recommendations": [
                "Add post-mortem meeting agenda template",
                "Include metrics tracking",
                "Add timeline for preventive measures"
            ]
        }
    ],
    "overall_score": 80,
    "critical_gaps": [
        "Forensic procedures not documented",
        "Evidence handling not specified",
        "No preventive maintenance schedule"
    ],
    "recommendations": [
        "Document forensic investigation procedures aligned with NIST 800-86",
        "Add evidence handling procedures per legal requirements",
        "Include preventive monitoring thresholds based on NIST guidelines",
        "Consider adding recovery time objectives (RTO) and RPO targets"
    ]
}

# Test playbook with minimal sections
MINIMAL_PLAYBOOK = """# Simple Playbook

## Detection
Monitor for errors

## Response
Fix the issue

## Recovery
Restart services
"""

# Test playbook that's incomplete (for testing gaps)
INCOMPLETE_PLAYBOOK = """# Incomplete Playbook

## Detection Only
This playbook only has detection steps

1. Check logs
2. Verify issue
"""
