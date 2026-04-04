# PlaybookPulse

AI-powered incident response compliance auditing for security teams.

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate      # Linux/Mac
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and configure your settings
   ```

### Environment Configuration

The application supports two modes:

#### **Development Mode (Default)**
- Set `ENVIRONMENT=development` in `.env`
- Works without Slack credentials (uses mocks)
- Perfect for local testing and development

#### **Production Mode**
- Set `ENVIRONMENT=production` in `.env`
- **Requires** real Slack credentials
- Will fail to start without proper configuration

### Getting Slack Credentials

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Create a new app or select existing
3. Navigate to "OAuth & Permissions"
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)
   - Add to `.env` as `SLACK_BOT_TOKEN`
4. Navigate to "Basic Information"
   - Copy the "Signing Secret"
   - Add to `.env` as `SLACK_SIGNING_SECRET`
5. Add the slash command `/playbookpulse` pointing to your webhook URL

## Running the Server

Start the FastAPI server:
```bash
# Using uvicorn directly (if venv is activated)
uvicorn backend.main:api --reload --port 8000

# Or using venv Python directly
.\venv\Scripts\python.exe -m uvicorn backend.main:api --reload --port 8000
```

The server will be available at `http://127.0.0.1:8000`

### Endpoints

- `GET /` - API information and status
- `GET /health` - Health check endpoint with environment info
- `POST /slack/events` - Slack event handler (slash commands)

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
playbookpulse/
├── backend/
│   ├── main.py              # FastAPI server entry point
│   ├── slack_app.py         # Slack Bolt command logic
│   ├── config.py            # Environment configuration
│   ├── schemas.py           # Pydantic data models
│   ├── data_loader.py       # Fixture data loaders
│   └── fixtures/            # Mock data for testing
│       ├── playbook_v1.md
│       ├── slack_thread.json
│       ├── jira_ticket.json
│       └── github_commits.json
├── tests/
│   ├── test_data_loader.py  # Data validation tests
│   └── test_slack_app.py    # Slack integration tests
├── .env.example             # Environment template
└── requirements.txt
```

## Slack Integration

### Local Development with ngrok

1. Start the server locally (dev mode)
2. Expose it with ngrok:
   ```bash
   ngrok http 8000
   ```
3. Configure your Slack app's slash command URL:
   ```
   https://your-ngrok-url.ngrok.io/slack/events
   ```

### Slash Command

Use `/playbookpulse` in any Slack channel where the bot is installed to trigger an incident analysis.

The bot will respond with:
- Analysis status message
- Channel context
- Agent processing indicators

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `development` | Set to `production` or `development` |
| `SLACK_BOT_TOKEN` | Prod only | - | Bot User OAuth Token (xoxb-...) |
| `SLACK_SIGNING_SECRET` | Prod only | - | Signing secret for request verification |
| `SERVER_HOST` | No | `0.0.0.0` | Server bind address |
| `SERVER_PORT` | No | `8000` | Server port |
| `GOOGLE_API_KEY` | Coming soon | - | Gemini API key for AI orchestration |

## Development Workflow

1. **Local development**: Use default dev mode with mocks
2. **Testing with real Slack**: Add credentials to `.env` (still in dev mode)
3. **Production deployment**: Set `ENVIRONMENT=production` and deploy

## Next Steps

- [ ] Integrate Gemini API for AI orchestration
- [ ] Build playbook parser agent
- [ ] Build incident trail analyzer
- [ ] Build adherence checker
- [ ] Add PDF report generation
