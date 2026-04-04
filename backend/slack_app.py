import os
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from backend.config import settings

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

@app.command("/playbookpulse")
def handle_playbook_command(ack, respond, command):
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

    # 2. Respond with a rich Block Kit message to set the demo stage
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
                        "text": f"Triggered by <@{user_id}> | _Agents running: Playbook Parser ⏳ • Incident Trail ⏳ • Adherence Checker ⏳_"
                    }
                ]
            }
        ]
    )

    # TODO: Integration point for Gemini orchestrator
    # This is where we'll:
    # 1. Load incident data (fixtures or real APIs)
    # 2. Run Gemini agents to detect compliance gaps
    # 3. Generate improved playbook if gaps found
    # 4. Create GitHub PR with open_playbook_pr(repo_name=repo_name, ...)
    # 5. Post PR link back to this channel

# Create the handler that FastAPI will use to route traffic to Bolt
slack_handler = SlackRequestHandler(app)
