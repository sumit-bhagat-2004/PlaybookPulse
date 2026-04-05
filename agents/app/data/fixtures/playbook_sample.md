# Incident Response Playbook - Database Outage

## 1. Detection & Alert (Within 5 minutes)

**Objective:** Identify and confirm the database outage

**Steps:**
1. Monitoring system alerts on database availability (IMMEDIATE)
2. Verify alerts through manual checks (Within 2 minutes)
3. Assess scope of impact - which services affected (Within 3 minutes)
4. Classify incident severity P0-P3 (Within 5 minutes)

**Responsible:** On-call Engineer, SRE Team
**Timeline:** 0-5 minutes from alert

## 2. Initial Response (Within 10 minutes)

**Objective:** Contain the issue and establish communication

**Steps:**
1. Create Jira ticket with incident details (Within 5 minutes)
2. Start Slack thread in #incidents channel (Within 5 minutes)
3. Notify stakeholders - Engineering, Product, Support (Within 8 minutes)
4. Establish incident commander role (Within 10 minutes)
5. Begin timeline documentation (Within 10 minutes)

**Responsible:** Incident Commander, Communications Lead
**Timeline:** 5-10 minutes from alert

## 3. Investigation (10-20 minutes)

**Objective:** Identify root cause

**Steps:**
1. Check database logs for errors (Within 12 minutes)
2. Review recent deployments and changes (Within 15 minutes)
3. Analyze resource utilization - CPU, Memory, Disk (Within 18 minutes)
4. Check network connectivity (Within 15 minutes)
5. Verify backup systems status (Within 20 minutes)

**Responsible:** Database Team, SRE Team
**Timeline:** 10-20 minutes from alert

## 4. Mitigation (Within 30 minutes)

**Objective:** Restore service - CRITICAL TIMELINE

**Steps:**
1. Attempt failover to replica if available (Within 25 minutes - CRITICAL)
2. Increase database connection timeout if needed (Within 25 minutes)
3. Roll back recent changes if identified as cause (Within 28 minutes)
4. Implement temporary workarounds (Within 30 minutes)
5. Monitor recovery progress (Ongoing)

**Responsible:** Database Team, DevOps Team
**Timeline:** 20-30 minutes from alert
**SLA:** Service must be restored within 30 minutes for P0 incidents

## 5. Recovery (30-45 minutes)

**Objective:** Fully restore normal operations

**Steps:**
1. Verify all services are operational (Within 35 minutes)
2. Confirm data integrity (Within 40 minutes)
3. Test critical user workflows (Within 45 minutes)
4. Add monitoring for connection pool metrics (Within 60 minutes)
5. Monitor for recurrence (Ongoing)

**Responsible:** QA Team, SRE Team
**Timeline:** 30-60 minutes from alert

## 6. Post-Incident Review (Within 48 hours)

**Objective:** Learn and improve

**Steps:**
1. Document complete timeline in Jira (Within 2 hours of resolution)
2. Schedule post-mortem meeting within 48 hours (REQUIRED)
3. Identify action items for prevention (During post-mortem)
4. Update runbooks and documentation (Within 72 hours)
5. Create GitHub issues for follow-up work (Within 72 hours)
6. Share incident report with stakeholders (Within 72 hours)
7. Notify legal/compliance if customer data affected (IMMEDIATE if applicable)

**Responsible:** Incident Commander, All Teams
**Timeline:** 0-72 hours post-resolution

## Compliance Notes

This playbook addresses:
- NIST SP 800-61: Incident Handling (IR-4)
- SOC 2 CC7.2: Response to Security Incidents
- ISO 27001 A.16.1.5: Response to information security incidents
