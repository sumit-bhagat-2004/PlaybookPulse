import os
import asyncio
import threading
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from config import settings
from agents_bridge import AgentsBridge
from data_loader import load_playbook, load_slack_thread, load_jira_ticket, load_github_commits
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

# Store recent analysis results (keyed by channel_id + timestamp)
# In production, use Redis or a database
ANALYSIS_CACHE = {}

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
                    print(f"Could not fetch live thread context: {e}")
            
            # 🚨 FIX: Inject Fixture Data for the Demo if live data is missing
            jira_data = None
            github_data = None
            
            if not slack_data:
                print("💉 Injecting fixture data for demo...")
                try:
                    # Convert Pydantic models back to dictionaries for the agents
                    slack_messages = load_slack_thread()
                    slack_data = {
                        "messages": [msg.dict() if hasattr(msg, 'dict') else msg.__dict__ for msg in slack_messages],
                        "channel_id": channel_id,
                        "thread_ts": "demo_thread"
                    }
                    
                    jira_ticket = load_jira_ticket()
                    jira_data = jira_ticket.dict() if hasattr(jira_ticket, 'dict') else jira_ticket.__dict__
                    
                    github_commits = load_github_commits()
                    github_data = [commit.dict() if hasattr(commit, 'dict') else commit.__dict__ for commit in github_commits]
                    
                    print(f"✓ Loaded {len(slack_data['messages'])} Slack messages")
                    print(f"✓ Loaded JIRA ticket: {jira_data.get('key', 'N/A')}")
                    print(f"✓ Loaded {len(github_data)} GitHub commits")
                except Exception as e:
                    import traceback
                    print(f"⚠️ Failed to load fixtures: {e}")
                    traceback.print_exc()
            
            # Run the multi-agent analysis (CIS ONLY)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(
                agents_bridge.analyze_incident(
                    playbook_content=playbook_content,
                    slack_thread_data=slack_data,
                    jira_ticket_data=jira_data,
                    github_events=github_data,
                    compliance_frameworks=["cis_controls_v8"]  # CIS ONLY
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
            
            # Store result for button handlers
            cache_key = f"{channel_id}_{thread_ts or 'main'}"
            ANALYSIS_CACHE[cache_key] = result
            
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
            
            # Add note if score is 0 due to lack of incident data
            incident_data = result.get("incident_data", {})
            has_data = (
                incident_data.get("slack_available") or
                incident_data.get("jira_available") or
                incident_data.get("github_available")
            )
            
            if score == 0 and not has_data:
                rec_text = "⚠️ *Note:* Score is 0% because no incident data was found to compare against the playbook. To get accurate compliance scores, run this command on a Slack thread with incident discussion, or provide JIRA ticket and GitHub event data.\n\n" + rec_text
            
            # Get CIS compliance details
            cis_compliance = result.get("cis_compliance", {})
            cis_score = 0
            sla_status = "N/A"
            
            if cis_compliance:
                dynamic = cis_compliance.get("dynamic_analysis", {})
                if dynamic:
                    cis_score = dynamic.get("compliance_score", 0)
                    sla = dynamic.get("sla_compliance", {})
                    sla_violations = sla.get("violations", 0)
                    sla_status = "✅ Met" if sla_violations == 0 else f"⚠️ {sla_violations} violation(s)"
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 CIS Controls v8 Compliance Analysis",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Playbook Adherence:*\n{score_emoji} {score:.1f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*CIS Control 17 Score:*\n{cis_score:.1f}%"
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
                            "text": f"*Steps Partial:* ⚠️ {partial}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Steps Missed:* ❌ {none_count}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*SLA Status:* {sla_status}"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"🎯 Framework: *CIS Controls v8* (Control 17 - Incident Response) | Repository: `{repo_name}`"
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
                            "text": f"Analysis completed at {result.get('timestamp', 'N/A')}"
                        }
                    ]
                }
            ]
            
            # Add action buttons
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
                            "text": "📄 Download CIS Report",
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


# Import PDF generator
from pdf_generator import generate_compliance_pdf, generate_quick_summary_pdf, generate_cis_compliance_pdf


# Button action handlers
@app.action("create_pr")
def handle_create_pr(ack, body, client):
    """Handle the Create PR button click"""
    print("[BUTTON] ✓ create_pr button clicked")
    # CRITICAL: Acknowledge immediately (within 3 seconds)
    ack()
    print("[BUTTON] ✓ Acknowledged")
    
    try:
        repo_name = body.get("actions", [{}])[0].get("value", "").strip()
        # Remove backticks if present (from Slack formatting)
        repo_name = repo_name.replace("`", "").strip()
        
        channel_id = body.get("channel", {}).get("id")
        user_id = body.get("user", {}).get("id")
        print(f"[BUTTON] Raw repo: {body.get('actions', [{}])[0].get('value', '')}")
        print(f"[BUTTON] Cleaned repo: {repo_name}, Channel: {channel_id}")
        
        # Send immediate feedback
        print("[BUTTON] Sending feedback message...")
        client.chat_postMessage(
            channel=channel_id,
            text=f"🔧 Creating remediation PR for `{repo_name}`..."
        )
        print("[BUTTON] Feedback sent, starting background thread...")
        
        # Create PR in background thread
        def create_pr():
            print("[PR-THREAD] Starting PR creation...")
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
                import traceback
                print(f"PR creation error: {e}")
                traceback.print_exc()
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"❌ Failed to create PR: {str(e)}"
                )
        
        thread = threading.Thread(target=create_pr)
        thread.start()
        
    except Exception as e:
        import traceback
        print(f"Button handler error: {e}")
        traceback.print_exc()
        # Send error to user
        try:
            client.chat_postMessage(
                channel=body.get("channel", {}).get("id"),
                text=f"❌ Button error: {str(e)}"
            )
        except:
            pass


@app.action("download_report")
def handle_download_report(ack, body, client):
    """Handle the Download Report button click"""
    print("[BUTTON] ✓ download_report button clicked")
    # CRITICAL: Acknowledge immediately
    ack()
    print("[BUTTON] ✓ Acknowledged")
    
    try:
        channel_id = body.get("channel", {}).get("id")
        user_id = body.get("user", {}).get("id")
        message_ts = body.get("message", {}).get("ts")
        print(f"[BUTTON] Channel: {channel_id}, User: {user_id}")
        
        # Send immediate feedback
        print("[BUTTON] Sending feedback message...")
        client.chat_postMessage(
            channel=channel_id,
            text="📄 Generating compliance report..."
        )
        print("[BUTTON] Feedback sent, starting PDF generation...")
        
        def generate_and_upload():
            print("[PDF] Starting PDF generation thread...")
            try:
                from datetime import datetime
                incident_id = f"INC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                print(f"[PDF] Incident ID: {incident_id}")
                
                # Try to get cached analysis result
                cache_key = f"{channel_id}_main"  # Try main thread
                print(f"[PDF] Looking for cache: {cache_key}")
                analysis_result = ANALYSIS_CACHE.get(cache_key)
                print(f"[PDF] Cache hit: {analysis_result is not None}")
                
                if analysis_result:
                    # Generate CIS-specific PDF with actual data
                    pdf_path = generate_cis_compliance_pdf(
                        analysis_result=analysis_result,
                        incident_id=incident_id
                    )
                else:
                    # Fallback: Generate quick summary
                    pdf_path = generate_quick_summary_pdf(
                        score=0.0,
                        full=0,
                        partial=0,
                        missed=10,
                        recommendations=[
                            "No analysis data found. Run /playbookpulse first.",
                            "CIS Control 17.3: Initial response SLA may not be met.",
                            "CIS Control 17.5: Ensure incident commander is assigned within 15 minutes.",
                            "CIS Control 17.8: Schedule post-incident review within 48 hours."
                        ],
                        incident_id=incident_id,
                        output_filename=f"playbookpulse_cis_report_{incident_id}.pdf"
                    )
                
                # Upload PDF to Slack
                with open(pdf_path, 'rb') as f:
                    client.files_upload_v2(
                        channel=channel_id,
                        file=f,
                        filename=f"PlaybookPulse_CIS_Report_{incident_id}.pdf",
                        title="PlaybookPulse CIS Controls v8 Compliance Report",
                        initial_comment=f"📄 Here's your CIS Controls v8 compliance report for incident {incident_id}"
                    )
                
                # Clean up the file
                import os
                os.remove(pdf_path)
                
            except Exception as e:
                import traceback
                print(f"Report generation error: {e}")
                traceback.print_exc()
                client.chat_postMessage(
                    channel=channel_id,
                    text=f"❌ Failed to generate report: {str(e)}"
                )
        
        thread = threading.Thread(target=generate_and_upload)
        thread.start()
        
    except Exception as e:
        import traceback
        print(f"Button handler error: {e}")
        traceback.print_exc()
        # Send error to user
        try:
            client.chat_postMessage(
                channel=body.get("channel", {}).get("id"),
                text=f"❌ Button error: {str(e)}"
            )
        except:
            pass
