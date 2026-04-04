# Incident Response Playbook: Database Credential Compromise

**Version:** 2.0  
**Last Updated:** 2024-01-15  
**Owner:** Security Operations Team  
**Compliance:** NIST SP 800-61, SOC 2 CC7, ISO 27001 A.16

---

## 1. Overview

This playbook defines the response procedure when database credentials are suspected or confirmed to be compromised. All steps must be documented in the incident ticket and Slack channel.

---

## 2. Detection Phase

### Step 1: Alert Acknowledgment
**Timeline:** Within 5 minutes of alert  
**Responsible:** On-Call SRE  
**Compliance:** NIST SP 800-61 §3.2.1

- [ ] Acknowledge the alert in PagerDuty/OpsGenie
- [ ] Create incident Slack channel: `#incident-YYYY-MM-DD-credential-leak`
- [ ] Post initial incident summary to channel
- [ ] Assign incident commander

### Step 2: Initial Triage
**Timeline:** Within 15 minutes  
**Responsible:** Security Engineer  
**Compliance:** SOC 2 CC7.1, NIST SP 800-61 §3.2.2

- [ ] Identify the source of credential exposure (logs, code repo, third-party breach)
- [ ] Determine which databases/systems are affected
- [ ] Classify severity (P1/P2/P3/P4)
- [ ] Update incident ticket with findings

---

## 3. Containment Phase

### Step 3: Immediate Access Revocation
**Timeline:** Within 30 minutes of detection  
**Responsible:** DBA Team  
**Compliance:** NIST SP 800-61 §3.3.1, SOC 2 CC7.2

- [ ] Disable compromised database accounts
- [ ] Revoke API keys/tokens associated with the credentials
- [ ] Block suspicious IP addresses if identified
- [ ] Document all revoked credentials in incident ticket

### Step 4: Network Isolation (if needed)
**Timeline:** Within 45 minutes  
**Responsible:** Infrastructure Team  
**Compliance:** ISO 27001 A.16.1.5

- [ ] Assess if network segmentation is required
- [ ] Implement firewall rules to isolate affected systems
- [ ] Verify containment is effective
- [ ] Update status in Slack channel

---

## 4. Investigation Phase

### Step 5: Log Analysis
**Timeline:** Within 2 hours  
**Responsible:** Security Analyst  
**Compliance:** NIST SP 800-61 §3.3.2, SOC 2 CC7.3

- [ ] Pull database access logs for the past 30 days
- [ ] Identify any unauthorized access patterns
- [ ] Check for data exfiltration indicators
- [ ] Document timeline of suspicious activities

### Step 6: Impact Assessment
**Timeline:** Within 4 hours  
**Responsible:** Security Lead  
**Compliance:** ISO 27001 A.16.1.4, SOC 2 CC7.4

- [ ] Determine what data may have been accessed
- [ ] Assess if PII/PHI/PCI data was exposed
- [ ] Calculate number of affected records
- [ ] Prepare preliminary impact report

---

## 5. Eradication Phase

### Step 7: Credential Rotation
**Timeline:** Within 1 hour of containment  
**Responsible:** DBA Team + DevOps  
**Compliance:** NIST SP 800-61 §3.4.1

- [ ] Generate new database credentials
- [ ] Update all applications with new credentials
- [ ] Test connectivity from all dependent services
- [ ] Remove old credentials from any exposed locations

### Step 8: Vulnerability Remediation
**Timeline:** Within 24 hours  
**Responsible:** Development Team  
**Compliance:** SOC 2 CC7.5

- [ ] Fix the root cause of credential exposure
- [ ] Deploy security patches if applicable
- [ ] Implement additional safeguards (secrets manager, etc.)
- [ ] Verify fix with security team

---

## 6. Recovery Phase

### Step 9: Service Restoration
**Timeline:** Based on severity  
**Responsible:** SRE Team  
**Compliance:** NIST SP 800-61 §3.5.1

- [ ] Gradually restore database access
- [ ] Monitor for anomalies during restoration
- [ ] Verify all systems are operational
- [ ] Communicate status to stakeholders

### Step 10: Monitoring Enhancement
**Timeline:** Within 48 hours  
**Responsible:** Security Operations  
**Compliance:** SOC 2 CC7.3

- [ ] Implement additional monitoring alerts
- [ ] Enable enhanced logging for affected systems
- [ ] Set up anomaly detection rules
- [ ] Document new monitoring in runbook

---

## 7. Post-Incident Phase

### Step 11: Legal/Compliance Notification
**Timeline:** Within 24 hours (or as required by regulation)  
**Responsible:** Security Lead + Legal  
**Compliance:** ISO 27001 A.16.1.2, GDPR Art. 33 (if applicable)

- [ ] Notify Legal team of incident
- [ ] Determine if regulatory notification is required
- [ ] Prepare breach notification if needed
- [ ] Document all communications

### Step 12: Post-Incident Review
**Timeline:** Within 5 business days  
**Responsible:** Incident Commander  
**Compliance:** NIST SP 800-61 §3.6.1

- [ ] Schedule post-mortem meeting
- [ ] Document lessons learned
- [ ] Identify process improvements
- [ ] Update this playbook with findings
- [ ] Close incident ticket

---

## 8. Escalation Matrix

| Severity | Response Time | Escalation Path |
|----------|--------------|-----------------|
| P1 (Critical) | Immediate | VP Engineering → CISO → CEO |
| P2 (High) | 15 minutes | Engineering Manager → Security Lead |
| P3 (Medium) | 1 hour | Team Lead → Engineering Manager |
| P4 (Low) | Next business day | Team Lead |

---

## 9. Contact List

- **Security Operations:** security@company.com, #security-ops
- **DBA Team:** dba@company.com, #database-ops  
- **Legal:** legal@company.com
- **Compliance:** compliance@company.com
- **On-Call SRE:** PagerDuty escalation policy

---

## 10. Compliance Framework References

| Framework | Control | Description |
|-----------|---------|-------------|
| NIST SP 800-61 | §3.2-3.6 | Incident Handling Process |
| SOC 2 | CC7.1-CC7.5 | System Operations |
| ISO 27001 | A.16.1.1-A.16.1.7 | Information Security Incident Management |
| GDPR | Art. 33-34 | Breach Notification |

---

**Document History:**
- v2.0 (2024-01-15): Added compliance mappings and enhanced timelines
- v1.0 (2023-06-01): Initial version
