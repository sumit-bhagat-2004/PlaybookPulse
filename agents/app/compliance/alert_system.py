"""
Alert System (Stub)

This module provides a stub implementation for alerting dev teams
when compliance checks fail.

TO BE IMPLEMENTED BY USER:
- Slack integration
- Email notifications  
- PagerDuty integration
- Custom webhooks

The methods here are intentionally left as stubs for the user to implement.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json


class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    SLACK = "slack"
    EMAIL = "email"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"


class AlertSystem:
    """
    Alert System for notifying dev team on compliance failures
    
    STUB IMPLEMENTATION - User should implement the actual integrations
    
    Features to implement:
    - Slack notifications (via webhook or API)
    - Email alerts
    - PagerDuty incidents
    - Custom webhook calls
    """
    
    def __init__(
        self,
        slack_webhook_url: Optional[str] = None,
        email_config: Optional[Dict[str, Any]] = None,
        pagerduty_api_key: Optional[str] = None,
        custom_webhook_url: Optional[str] = None
    ):
        """
        Initialize alert system with optional configurations
        
        Args:
            slack_webhook_url: Slack incoming webhook URL
            email_config: Email configuration (smtp_host, from_email, to_emails)
            pagerduty_api_key: PagerDuty API key for incident creation
            custom_webhook_url: Custom webhook URL for alerts
        """
        self.slack_webhook_url = slack_webhook_url
        self.email_config = email_config
        self.pagerduty_api_key = pagerduty_api_key
        self.custom_webhook_url = custom_webhook_url
        
        # Alert history
        self.alerts_sent: List[Dict[str, Any]] = []
        
        # Enabled channels
        self.enabled_channels: List[AlertChannel] = []
        if slack_webhook_url:
            self.enabled_channels.append(AlertChannel.SLACK)
        if email_config:
            self.enabled_channels.append(AlertChannel.EMAIL)
        if pagerduty_api_key:
            self.enabled_channels.append(AlertChannel.PAGERDUTY)
        if custom_webhook_url:
            self.enabled_channels.append(AlertChannel.WEBHOOK)
        
        print(f"[AlertSystem] Initialized with channels: {[c.value for c in self.enabled_channels]}")
        if not self.enabled_channels:
            print("[AlertSystem] WARNING: No alert channels configured!")
    
    def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "medium",
        event: Optional[Dict[str, Any]] = None,
        channels: Optional[List[AlertChannel]] = None
    ) -> Dict[str, Any]:
        """
        Send an alert to configured channels
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (low, medium, high, critical)
            event: Original compliance event that triggered the alert
            channels: Specific channels to use (defaults to all enabled)
            
        Returns:
            Alert result with status per channel
        """
        alert = {
            "id": f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
            "timestamp": datetime.utcnow().isoformat(),
            "title": title,
            "message": message,
            "severity": severity,
            "event": event,
            "results": {}
        }
        
        target_channels = channels or self.enabled_channels
        
        for channel in target_channels:
            try:
                if channel == AlertChannel.SLACK:
                    result = self._send_slack_alert(title, message, severity, event)
                elif channel == AlertChannel.EMAIL:
                    result = self._send_email_alert(title, message, severity, event)
                elif channel == AlertChannel.PAGERDUTY:
                    result = self._send_pagerduty_alert(title, message, severity, event)
                elif channel == AlertChannel.WEBHOOK:
                    result = self._send_webhook_alert(title, message, severity, event)
                else:
                    result = {"status": "skipped", "reason": "Unknown channel"}
                
                alert["results"][channel.value] = result
                
            except Exception as e:
                alert["results"][channel.value] = {
                    "status": "error",
                    "error": str(e)
                }
        
        self.alerts_sent.append(alert)
        
        return alert
    
    def _send_slack_alert(
        self,
        title: str,
        message: str,
        severity: str,
        event: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send alert to Slack
        
        TODO: Implement Slack webhook integration
        
        Example implementation:
        ```python
        import requests
        
        payload = {
            "text": f"*{title}*",
            "attachments": [{
                "color": self._severity_to_color(severity),
                "text": message,
                "fields": [
                    {"title": "Severity", "value": severity, "short": True},
                    {"title": "Time", "value": datetime.utcnow().isoformat(), "short": True}
                ]
            }]
        }
        
        response = requests.post(self.slack_webhook_url, json=payload)
        return {"status": "sent", "response_code": response.status_code}
        ```
        """
        # STUB - User should implement
        print(f"[AlertSystem] STUB: Would send Slack alert: {title}")
        return {
            "status": "stub",
            "message": "Slack integration not implemented. See code comments for example."
        }
    
    def _send_email_alert(
        self,
        title: str,
        message: str,
        severity: str,
        event: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send alert via email
        
        TODO: Implement email sending
        
        Example implementation:
        ```python
        import smtplib
        from email.mime.text import MIMEText
        
        msg = MIMEText(f"{message}\\n\\nSeverity: {severity}\\nEvent: {json.dumps(event)}")
        msg['Subject'] = f"[Compliance Alert] {title}"
        msg['From'] = self.email_config['from_email']
        msg['To'] = ', '.join(self.email_config['to_emails'])
        
        with smtplib.SMTP(self.email_config['smtp_host']) as server:
            server.send_message(msg)
        
        return {"status": "sent"}
        ```
        """
        # STUB - User should implement
        print(f"[AlertSystem] STUB: Would send email alert: {title}")
        return {
            "status": "stub", 
            "message": "Email integration not implemented. See code comments for example."
        }
    
    def _send_pagerduty_alert(
        self,
        title: str,
        message: str,
        severity: str,
        event: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create PagerDuty incident
        
        TODO: Implement PagerDuty integration
        
        Example implementation:
        ```python
        import requests
        
        pd_severity = {
            "low": "info",
            "medium": "warning", 
            "high": "error",
            "critical": "critical"
        }.get(severity, "warning")
        
        payload = {
            "routing_key": self.pagerduty_api_key,
            "event_action": "trigger",
            "payload": {
                "summary": f"{title}: {message}",
                "severity": pd_severity,
                "source": "PlaybookPulse Compliance"
            }
        }
        
        response = requests.post(
            "https://events.pagerduty.com/v2/enqueue",
            json=payload
        )
        return {"status": "sent", "dedup_key": response.json().get("dedup_key")}
        ```
        """
        # STUB - User should implement
        print(f"[AlertSystem] STUB: Would create PagerDuty incident: {title}")
        return {
            "status": "stub",
            "message": "PagerDuty integration not implemented. See code comments for example."
        }
    
    def _send_webhook_alert(
        self,
        title: str,
        message: str,
        severity: str,
        event: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Send alert to custom webhook
        
        TODO: Implement webhook call
        
        Example implementation:
        ```python
        import requests
        
        payload = {
            "title": title,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "event": event
        }
        
        response = requests.post(
            self.custom_webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        return {"status": "sent", "response_code": response.status_code}
        ```
        """
        # STUB - User should implement
        print(f"[AlertSystem] STUB: Would POST to webhook: {title}")
        return {
            "status": "stub",
            "message": "Webhook integration not implemented. See code comments for example."
        }
    
    def _severity_to_color(self, severity: str) -> str:
        """Convert severity to Slack color"""
        colors = {
            "low": "#36a64f",      # Green
            "medium": "#ffa500",   # Orange
            "high": "#ff6600",     # Dark orange
            "critical": "#ff0000"  # Red
        }
        return colors.get(severity, "#808080")
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """Get history of sent alerts"""
        return self.alerts_sent
    
    def get_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total = len(self.alerts_sent)
        by_severity = {}
        by_channel = {}
        
        for alert in self.alerts_sent:
            sev = alert.get("severity", "unknown")
            by_severity[sev] = by_severity.get(sev, 0) + 1
            
            for channel, result in alert.get("results", {}).items():
                by_channel[channel] = by_channel.get(channel, 0) + 1
        
        return {
            "total_alerts": total,
            "by_severity": by_severity,
            "by_channel": by_channel,
            "enabled_channels": [c.value for c in self.enabled_channels]
        }


# Convenience function to create configured alert system
def create_alert_system(
    slack_webhook: Optional[str] = None,
    email_host: Optional[str] = None,
    email_from: Optional[str] = None,
    email_to: Optional[List[str]] = None,
    pagerduty_key: Optional[str] = None,
    webhook_url: Optional[str] = None
) -> AlertSystem:
    """
    Create an AlertSystem with the provided configuration
    
    Pass environment variables or config values as needed.
    Channels without configuration will be disabled.
    """
    email_config = None
    if email_host and email_from and email_to:
        email_config = {
            "smtp_host": email_host,
            "from_email": email_from,
            "to_emails": email_to
        }
    
    return AlertSystem(
        slack_webhook_url=slack_webhook,
        email_config=email_config,
        pagerduty_api_key=pagerduty_key,
        custom_webhook_url=webhook_url
    )
