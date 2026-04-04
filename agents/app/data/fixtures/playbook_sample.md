# Incident Response Playbook - Database Outage

## 1. Detection & Alert

**Objective:** Identify and confirm the database outage

**Steps:**
1. Monitoring system alerts on database availability
2. Verify alerts through manual checks
3. Assess scope of impact (which services affected)
4. Classify incident severity (P0-P3)

**Responsible:** On-call Engineer, SRE Team

## 2. Initial Response

**Objective:** Contain the issue and establish communication

**Steps:**
1. Create Jira ticket with incident details
2. Start Slack thread in #incidents channel
3. Notify stakeholders (Engineering, Product, Support)
4. Establish incident commander role
5. Begin timeline documentation

**Responsible:** Incident Commander, Communications Lead

## 3. Investigation

**Objective:** Identify root cause

**Steps:**
1. Check database logs for errors
2. Review recent deployments and changes
3. Analyze resource utilization (CPU, Memory, Disk)
4. Check network connectivity
5. Verify backup systems status

**Responsible:** Database Team, SRE Team

## 4. Mitigation

**Objective:** Restore service

**Steps:**
1. Attempt failover to replica if available
2. Restart database service if appropriate
3. Roll back recent changes if identified as cause
4. Implement temporary workarounds
5. Monitor recovery progress

**Responsible:** Database Team, DevOps Team

## 5. Recovery

**Objective:** Fully restore normal operations

**Steps:**
1. Verify all services are operational
2. Confirm data integrity
3. Test critical user workflows
4. Monitor for recurrence

**Responsible:** QA Team, SRE Team

## 6. Post-Incident Review

**Objective:** Learn and improve

**Steps:**
1. Document timeline in Jira
2. Schedule post-mortem meeting within 48 hours
3. Identify action items for prevention
4. Update runbooks and documentation
5. Create GitHub issues for follow-up work
6. Share incident report with stakeholders

**Responsible:** Incident Commander, All Teams

## Compliance Notes

This playbook addresses:
- NIST SP 800-61: Incident Handling (IR-4)
- SOC 2 CC7.2: Response to Security Incidents
- ISO 27001 A.16.1.5: Response to information security incidents
