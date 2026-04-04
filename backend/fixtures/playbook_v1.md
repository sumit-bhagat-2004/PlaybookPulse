# Security Incident Playbook: Credential Leak

1. **Acknowledge & Triage:** On-call engineer acknowledges the alert.
2. **Identify Scope:** Determine which credentials were leaked and what systems they access.
3. **Revoke Access:** Immediately disable the compromised accounts or API keys.
4. **Rotate Credentials:** Generate new credentials and update affected services. (Expected: within 30 minutes of detection) [NIST SP 800-61 §3.3.1, SOC 2 CC7.3]
5. **Investigate Impact:** Review access logs to determine if the leaked credentials were used maliciously.
6. **Notify Legal/Compliance:** Inform internal legal counsel of the breach. [ISO 27001 A.16]
7. **Post-Mortem:** Document the incident and update this playbook.
