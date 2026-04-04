import os
import asyncio
import threading
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from config import settings
from agents_bridge import AgentsBridge
from data_loader import load_playbook
from pathlib import Path

# Initialize Slack app based on environment
if settings.is_development and not settings.has_slack_credentials:
    # Development mode: Use mock credentials and disable token verification
    print("🔧 Running in DEVELOPMENT mode with mock Slack credentials")
    app = App(
        token="xoxb-mock-token-for-development",
        signing_secret="mock-secret-for-development",
        token_verification_enabled=False
    )
else:
    # Production mode or development with real credentials
    if settings.is_production:
        settings.validate_production()
        print("🚀 Running in PRODUCTION mode with real Slack credentials")
    else:
        print("🔧 Running in DEVELOPMENT mode with real Slack credentials")
    
    app = App(
        token=settings.SLACK_BOT_TOKEN,
        signing_secret=settings.SLACK_SIGNING_SECRET
    )

# Initialize agents bridge
agents_bridge = AgentsBridge()

@app.command("/playbookpulse")
def handle_playbook_command(ack, respond, command, client):
    # 1. Acknowledge the Slack request immediately (Required within 3 seconds)
    ack()

    channel_id = command.get("channel_id")
    user_id = command.get("user_id")
    
    # Extract repository name from command text (e.g., "username/repo-name")
    repo_name = command.get("text", "").strip()
    
    # Validate repository name format
    if not repo_name:
        respond(
            text="⚠️ Please provide a repository name!\n\nUsage: `/playbookpulse username/repo-name`\n\nExample: `/playbookpulse octocat/security-playbooks`"
        )
        return
    
    if "/" not in repo_name:
        respond(
            text=f"⚠️ Invalid repository format: `{repo_name}`\n\nPlease use: `username/repo-name`\n\nExample: `/playbookpulse octocat/security-playbooks`"
        )
        return

    # 2. Respond with initial status message
    respond(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🚀 *PlaybookPulse* is analyzing the incident context in <#{channel_id}>..."
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"📦 *Target Repository:* `{repo_name}`"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Triggered by <@{user_id}> | _Agents running: Playbook Parser ⏳ • Incident Trail ⏳ • Adherence Checker ⏳ • Compliance Mapper ⏳_"
                    }
                ]
            }
        ]
    )
    
    # 3. Run analysis in background thread (Slack commands need quick responses)
    def run_analysis():
        try:
            # Load playbook (use comprehensive one for demo)
            playbook_path = Path(__file__).parent / "fixtures" / "playbook_comprehensive.md"
            if playbook_path.exists():
                with open(playbook_path) as f:
                    playbook_content = f.read()
            else:
                playbook_content = load_playbook()  # Fallback to v1
            
            # Try to get Slack thread context (if in a thread)
            slack_data = None
            thread_ts = command.get("thread_ts")
            if thread_ts and settings.has_slack_credentials:
                try:
                    result = client.conversations_replies(
                        channel=channel_id,
                        ts=thread_ts
                    )
                    slack_data = {
                        "messages": result.get("messages", []),
                        "channel_id": channel_id,
                        "thread_ts": thread_ts
                    }
                except Exception as e:
                    print(f"Could not fetch thread context: {e}")
            
            # Run the multi-agent analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                agents_bridge.analyze_incident(
                    playbook_content=playbook_content,
                    slack_thread_data=slack_data,
                    compliance_frameworks=["nist_sp_800_61", "soc2_cc7"]
                )
            )
            loop.close()
            
            # 4. Post results back to channel
            if result.get("status") == "error":
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"❌ *Analysis Failed*\n\nError: {result.get('error', 'Unknown error')}",
                    thread_ts=thread_ts
                )
                return
            
            # Format successful result
            adherence = result.get("adherence", {})
            score = adherence.get("overall_score", 0)
            full = adherence.get("full_adherence", 0)
            partial = adherence.get("partial_adherence", 0)
            none_count = adherence.get("no_adherence", 0)
            
            # Determine score emoji
            if score >= 80:
                score_emoji = "🟢"
            elif score >= 60:
                score_emoji = "🟡"
            else:
                score_emoji = "🔴"
            
            # Build recommendations section
            recommendations = result.get("recommendations", [])
            rec_text = "\n".join([f"• {r}" for r in recommendations[:5]])
            
            # Build compliance section
            compliance = result.get("compliance", {})
            frameworks = compliance.get("frameworks_analyzed", [])
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 PlaybookPulse Analysis Complete",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Compliance Score:*\n{score_emoji} {score:.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Repository:*\n`{repo_name}`"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Steps Followed:* ✅ {full}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Steps Partially Followed:* ⚠️ {partial}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Steps Missed:* ❌ {none_count}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Frameworks Analyzed:* {len(frameworks)}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📋 Recommendations:*\n{rec_text if rec_text else '_No specific recommendations_'}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Analysis completed at {result.get('timestamp', 'N/A')} | Frameworks: {', '.join(frameworks)}"
                        }
                    ]
                }
            ]
            
            # Add action buttons if GitHub is configured
            if settings.has_github_credentials:
                blocks.append({
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🔧 Create Remediation PR",
                                "emoji": True
                            },
                            "style": "primary",
                            "action_id": "create_pr",
                            "value": repo_name
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📄 Download Report",
                                "emoji": True
                            },
                            "action_id": "download_report"
                        }
                    ]
                })
            
            client.chat_postMessage(
                channel=channel_id,
                blocks=blocks,
                text=f"PlaybookPulse Analysis Complete - Score: {score:.1f}%",
                thread_ts=thread_ts
            )
            
        except Exception as e:
            import traceback
            print(f"Analysis error: {e}")
            traceback.print_exc()
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ *Analysis Failed*\n\nError: {str(e)}",
                thread_ts=command.get("thread_ts")
            )
    
    # Start analysis in background thread
    thread = threading.Thread(target=run_analysis)
    thread.start()

# Create the handler that FastAPI will use to route traffic to Bolt
slack_handler = SlackRequestHandler(app)


# Button action handlers
@app.action("create_pr")
def handle_create_pr(ack, body, client, respond):
    """Handle the Create PR button click"""
    ack()
    
    repo_name = body.get("actions", [{}])[0].get("value", "")
    channel_id = body.get("channel", {}).get("id")
    user_id = body.get("user", {}).get("id")
    
    respond(
        text=f"🔧 Creating remediation PR for `{repo_name}`...",
        replace_original=False
    )
    
    # TODO: Implement actual PR creation using github_integration
    # For now, post a placeholder message
    def create_pr():
        try:
            from github_integration import open_playbook_pr
            from datetime import datetime
            
            if not settings.has_github_credentials:
                client.chat_postMessage(
                    channel=channel_id,
                    text="⚠️ GitHub credentials not configured. Cannot create PR."
                )
                return
            
            # Load the improved playbook (for now, use the comprehensive one)
            playbook_path = Path(__file__).parent / "fixtures" / "playbook_comprehensive.md"
            with open(playbook_path) as f:
                improved_content = f.read()
            
            branch_name = f"playbookpulse-remediation-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            pr_url = open_playbook_pr(
                repo_name=repo_name,
                branch_name=branch_name,
                file_path="incident_response_playbook.md",
                new_content=improved_content,
                pr_title="🔒 Playbook Improvements (Auto-Generated by PlaybookPulse)",
                pr_body="## PlaybookPulse Auto-Generated Improvements\n\nThis PR contains improvements to the incident response playbook based on compliance analysis.\n\n---\n_Generated by PlaybookPulse AI Orchestrator_ 🤖"
            )
            
            client.chat_postMessage(
                channel=channel_id,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"✅ *Pull Request Created!*\n\n<{pr_url}|View PR on GitHub>"
                        }
                    }
                ],
                text=f"PR Created: {pr_url}"
            )
            
        except Exception as e:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Failed to create PR: {str(e)}"
            )
    
    thread = threading.Thread(target=create_pr)
    thread.start()


@app.action("download_report")
def handle_download_report(ack, body, client, respond):
    """Handle the Download Report button click"""
    ack()
    
    channel_id = body.get("channel", {}).get("id")
    
    # For now, just acknowledge - full report generation would need the agents API
    respond(
        text="📄 Report generation is being prepared. This feature will be available in the next version.",
        replace_original=False
    )
