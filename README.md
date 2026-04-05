<div align="center">

```
   ██████╗ ██╗      █████╗ ██╗   ██╗██████╗  ██████╗  ██████╗ ██╗  ██╗
   ██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔═══██╗██╔═══██╗██║ ██╔╝
   ██████╔╝██║     ███████║ ╚████╔╝ ██████╔╝██║   ██║██║   ██║█████╔╝ 
   ██╔═══╝ ██║     ██╔══██║  ╚██╔╝  ██╔══██╗██║   ██║██║   ██║██╔═██╗ 
   ██║     ███████╗██║  ██║   ██║   ██████╔╝╚██████╔╝╚██████╔╝██║  ██╗
   ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
   
        ██████╗ ██╗   ██╗██╗     ███████╗███████╗
        ██╔══██╗██║   ██║██║     ██╔════╝██╔════╝
        ██████╔╝██║   ██║██║     ███████╗█████╗  
        ██╔═══╝ ██║   ██║██║     ╚════██║██╔══╝  
        ██║     ╚██████╔╝███████╗███████║███████╗
        ╚═╝      ╚═════╝ ╚══════╝╚══════╝╚══════╝
```

### 🤖 AI-Powered Incident Response Compliance Auditing

**Stop guessing. Start proving compliance.**

[![CIS Controls v8](https://img.shields.io/badge/CIS_Controls-v8-blue?style=for-the-badge&logo=security&logoColor=white)](https://www.cisecurity.org/)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Slack](https://img.shields.io/badge/Slack-Integrated-4A154B?style=for-the-badge&logo=slack&logoColor=white)](https://slack.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[🚀 Quick Start](#-quick-start) • [📖 Documentation](#-documentation) • [🎯 Features](#-features) • [🏗️ Architecture](#️-architecture) • [🤝 Contributing](#-contributing)

---

</div>

## 🎯 What is PlaybookPulse?

**PlaybookPulse** is an AI-powered compliance auditing system that automatically validates your incident response against **CIS Controls v8**. 

Instead of manual compliance reviews, PlaybookPulse:
- 🔍 **Analyzes** your incident response playbooks
- ⏱️ **Validates** SLA compliance in real-time
- 📊 **Scores** your response against 9 CIS Control 17 safeguards
- 📄 **Generates** executive-ready PDF reports
- 💬 **Integrates** directly with Slack for seamless workflows

<div align="center">

### 🎬 See It In Action

```bash
# One command to analyze your incident response
python cli.py
```

<img src="docs/images/demo.gif" alt="PlaybookPulse Demo" width="600" />

*Analyze incidents, validate compliance, generate reports — all from your terminal or Slack.*

</div>

---

## 🌟 Features

<table>
<tr>
<td width="50%">

### 🔒 CIS Controls v8 Compliance
✅ **9 Safeguards Validated**
- Personnel Management (17.1)
- Contact Information (17.2)
- Reporting Process (17.3)
- IR Process Execution (17.4)
- Key Roles Assignment (17.5)
- Communication Channels (17.6)
- IR Exercises (17.7)
- Post-Incident Reviews (17.8)
- Incident Thresholds (17.9)

</td>
<td width="50%">

### ⚡ Real-Time Analysis
⏱️ **SLA Validation**
- Initial Response: 15 minutes
- Assessment: 30 minutes
- Containment Start: 60 minutes
- Complete Containment: 4 hours
- Eradication: 8 hours

🎯 **Automatic Scoring**
- Pre-PR static checks
- Post-merge dynamic validation
- Timeline extraction from Slack

</td>
</tr>
</table>

### 🚀 Three Ways to Analyze

<div align="center">

| Method | Use Case | Command |
|--------|----------|---------|
| 🖥️ **Interactive CLI** | Development, Testing | `python cli.py` |
| 💬 **Slack Integration** | Team Collaboration | `/playbookpulse analyze` |
| 🔌 **REST API** | CI/CD, Automation | `POST /compliance/pre-pr` |

</div>

---

## 🚀 Quick Start

### 📦 Prerequisites

- Python 3.13+
- Git
- (Optional) Slack workspace for team integration

### ⚡ 60-Second Setup

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/PlaybookPulse.git
cd PlaybookPulse

# 2. Set up environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# 3. Install dependencies
cd backend
pip install -r requirements.txt

# 4. Run your first analysis!
python cli.py
```

<details>
<summary><b>🎥 Watch: First Analysis Walkthrough</b></summary>

```bash
$ python cli.py

╔═══════════════════════════════════════════════════════════════╗
║             PlaybookPulse - CIS Compliance CLI                ║
╚═══════════════════════════════════════════════════════════════╝

📋 What would you like to do?

  1️⃣  Pre-PR Check (validate playbook structure)
  2️⃣  Post-Merge Check (validate incident response)
  3️⃣  Full Analysis (complete pipeline)
  4️⃣  Run All Checks
  5️⃣  Exit

Your choice (1-5): 2

📄 Playbook Input Options:
  1. Load from file
  2. Use sample playbook
  3. Paste content

Your choice (1-3): 2

✅ Loaded sample playbook (2847 characters)

🔍 POST-MERGE DYNAMIC COMPLIANCE CHECK
════════════════════════════════════════

✅ Status: NON_COMPLIANT
📊 Compliance Score: 58.3%
🔍 Controls Checked: 6
🚫 Violations: 1

⏱️  SLA Compliance:
   ✅ Status: COMPLIANT
   Violations: 0

💾 Results saved to: analysis_20260405_123456.json
```

</details>

---

## 📖 Documentation

### 📚 Complete Guides

| Guide | Description | Read Time |
|-------|-------------|-----------|
| [**INDEX.md**](INDEX.md) | 🗺️ Start here - Complete documentation map | 5 min |
| [**QUICK_START.md**](QUICK_START.md) | ⚡ Run your first analysis in 2 minutes | 2 min |
| [**START_ANALYSIS_GUIDE.md**](START_ANALYSIS_GUIDE.md) | 🎯 All analysis methods explained | 15 min |
| [**HOW_TO_START_ANALYSIS.md**](HOW_TO_START_ANALYSIS.md) | 📖 Full API reference & examples | 30 min |
| [**IMPLEMENTATION_SUMMARY.md**](IMPLEMENTATION_SUMMARY.md) | 🏗️ System architecture & status | 10 min |

### 🎓 Quick Reference

<details>
<summary><b>🔧 API Endpoints</b></summary>

```bash
# Pre-PR Static Check (before merge)
POST http://localhost:8000/compliance/pre-pr
Content-Type: application/json
{
  "playbook_content": "# Incident Response\n## Detection\n- Monitor alerts"
}

# Post-Merge Dynamic Check (after incident)
POST http://localhost:8000/compliance/post-merge
Content-Type: application/json
{
  "playbook_content": "...",
  "slack_channel_id": "C0123456789",
  "slack_thread_id": "1234567890.123456"
}

# Generate PDF Report
POST http://localhost:8000/report/generate
GET  http://localhost:8000/report/{incident_id}/pdf
```

</details>

<details>
<summary><b>💬 Slack Commands</b></summary>

```
# Start backend server
uvicorn main:app --reload --port 8000

# In Slack
/playbookpulse analyze

# Bot responds with:
# - 📊 Compliance score
# - 🔍 CIS Controls validation
# - 💡 Recommendations
# - 🔧 Button to create remediation PR
# - 📄 Button to download PDF report
```

</details>

<details>
<summary><b>🐍 Python Integration</b></summary>

```python
import asyncio
from agents_bridge import AgentsBridge

async def analyze_playbook():
    bridge = AgentsBridge()
    
    # Pre-PR check
    result = await bridge.check_pre_pr(
        playbook_content=open("playbook.md").read()
    )
    
    print(f"Compliance Score: {result['compliance_score']}%")
    print(f"Status: {result['overall_status']}")
    
    # Post-merge check with Slack data
    result = await bridge.check_post_merge(
        playbook_content=open("playbook.md").read(),
        slack_thread_data={"messages": [...]}
    )
    
    return result

asyncio.run(analyze_playbook())
```

</details>

---

## 🏗️ Architecture

<div align="center">

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Slack Integration] --> B[Backend API]
        C[CLI Interface] --> B
        D[REST API] --> B
    end
    
    subgraph "Backend Layer"
        B --> E[AgentsBridge]
        E --> F[StaticCISAgent]
        E --> G[DynamicCISAgent]
        F --> H[ComplianceLogger]
        G --> H
        H --> I[AlertSystem]
    end
    
    subgraph "Data Layer"
        B --> J[Slack API]
        B --> K[Jira API]
        B --> L[GitHub API]
    end
    
    subgraph "Output Layer"
        B --> M[PDF Generator]
        B --> N[Slack Notifications]
        I --> O[Alert Webhooks]
    end
    
    style A fill:#4A154B
    style B fill:#009688
    style E fill:#3776AB
    style F fill:#2196F3
    style G fill:#2196F3
    style M fill:#FF9800
```

</div>

### 🔄 Compliance Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Pre-PR Phase (Static)                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Parse playbook structure                                    │
│  2. Validate CIS Control 17 requirements                        │
│  3. Check SLA definitions                                       │
│  4. Verify role assignments                                     │
│  5. Return compliance score (blocking if < 60%)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 Post-Merge Phase (Dynamic)                      │
├─────────────────────────────────────────────────────────────────┤
│  1. Fetch incident data (Slack/Jira/GitHub)                     │
│  2. Extract timeline and activities                             │
│  3. Validate SLA compliance                                     │
│  4. Check role execution                                        │
│  5. Generate compliance report + PDF                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Alert & Reporting                            │
├─────────────────────────────────────────────────────────────────┤
│  • Trigger alerts on violations                                 │
│  • Send Slack notifications                                     │
│  • Generate executive PDF report                                │
│  • Create remediation PR (optional)                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

<div align="center">

| Category | Technologies |
|----------|-------------|
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white) ![Python](https://img.shields.io/badge/Python_3.13-3776AB?style=flat&logo=python&logoColor=white) |
| **AI/LLM** | ![Gemini](https://img.shields.io/badge/Google_Gemini-4285F4?style=flat&logo=google&logoColor=white) ![Anthropic](https://img.shields.io/badge/Claude-191919?style=flat) |
| **Integrations** | ![Slack](https://img.shields.io/badge/Slack-4A154B?style=flat&logo=slack&logoColor=white) ![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white) ![Jira](https://img.shields.io/badge/Jira-0052CC?style=flat&logo=jira&logoColor=white) |
| **Reporting** | ![ReportLab](https://img.shields.io/badge/ReportLab-PDF-red?style=flat) |
| **Compliance** | ![CIS](https://img.shields.io/badge/CIS_Controls_v8-007ACC?style=flat) |

</div>

---

## 📁 Project Structure

```
PlaybookPulse/
├── 📂 backend/                  # Main backend application
│   ├── main.py                  # FastAPI server
│   ├── agents_bridge.py         # CIS compliance orchestration
│   ├── slack_app.py             # Slack integration
│   ├── cli.py                   # Interactive CLI
│   ├── quick_start_analysis.py  # Demo script
│   ├── pdf_generator.py         # PDF report generation
│   ├── 📂 compliance/           # CIS agents
│   │   ├── static_cis_agent.py  # Pre-PR checks
│   │   ├── dynamic_cis_agent.py # Post-merge validation
│   │   ├── compliance_logger.py # Structured logging
│   │   └── alert_system.py      # Alert notifications
│   └── 📂 fixtures/             # Test data
│
├── 📂 agents/                   # Multi-agent system (optional)
│   ├── 📂 app/
│   │   ├── 📂 agents/           # Agent implementations
│   │   ├── 📂 integrations/     # LLM clients
│   │   └── 📂 services/         # Analysis services
│   └── requirements.txt
│
├── 📂 docs/                     # Documentation
│   ├── INDEX.md                 # Documentation index
│   ├── QUICK_START.md           # Quick start guide
│   ├── START_ANALYSIS_GUIDE.md  # Analysis methods
│   └── HOW_TO_START_ANALYSIS.md # API reference
│
├── .env.example                 # Environment template
├── README.md                    # This file!
└── requirements.txt             # Python dependencies
```

---

## 🎯 Use Cases

<table>
<tr>
<td width="50%">

### 🔍 Pre-PR Compliance Check

**Scenario**: Before merging playbook changes

```bash
# Run compliance check
python cli.py check playbook.md

# If score >= 80%, merge is approved
# If score < 80%, review recommendations
```

**Benefits**:
- ✅ Catch compliance issues early
- ✅ Prevent non-compliant merges
- ✅ Maintain high standards

</td>
<td width="50%">

### 📊 Post-Incident Analysis

**Scenario**: After resolving a security incident

```
# In Slack
/playbookpulse analyze

# Bot analyzes the thread and returns:
# - Compliance score
# - SLA violations
# - Recommendations
# - PDF report
```

**Benefits**:
- ✅ Automated post-mortems
- ✅ SLA validation
- ✅ Evidence for audits

</td>
</tr>
<tr>
<td width="50%">

### 🔄 CI/CD Integration

**Scenario**: Automated compliance in pipelines

```yaml
# .github/workflows/compliance.yml
- name: CIS Compliance Check
  run: |
    python cli.py check playbook.md
    score=$(jq '.compliance_score' result.json)
    if [ $score -lt 80 ]; then exit 1; fi
```

**Benefits**:
- ✅ Shift-left compliance
- ✅ Automated enforcement
- ✅ Fast feedback loops

</td>
<td width="50%">

### 📈 Quarterly Audits

**Scenario**: Executive compliance reporting

```bash
# Generate comprehensive report
python quick_start_analysis.py

# Outputs:
# - JSON results
# - PDF executive summary
# - Compliance trends
```

**Benefits**:
- ✅ Audit-ready reports
- ✅ Compliance tracking
- ✅ Executive visibility

</td>
</tr>
</table>

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Core Settings
ENVIRONMENT=development           # or 'production'
API_HOST=0.0.0.0
API_PORT=8000

# LLM Provider (choose one)
LLM_PROVIDER=gemini              # or 'anthropic'
GEMINI_API_KEY=your_key_here     # Get from https://aistudio.google.com/
ANTHROPIC_API_KEY=sk-ant-xxx     # Get from https://console.anthropic.com/

# Slack Integration (optional)
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
SLACK_SIGNING_SECRET=your-secret

# GitHub Integration (optional)
GITHUB_TOKEN=ghp_your_token
GITHUB_ORG=your-org

# Alert System (optional)
SLACK_ALERT_WEBHOOK=https://hooks.slack.com/services/xxx
PAGERDUTY_API_KEY=your_key
```

<details>
<summary><b>🔐 Getting API Keys</b></summary>

**Gemini API** (Recommended for best results):
1. Visit https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy and add to `.env`

**Anthropic Claude** (Alternative):
1. Visit https://console.anthropic.com/
2. Create account and navigate to API Keys
3. Generate new key
4. Copy and add to `.env`

**Slack Bot**:
1. Visit https://api.slack.com/apps
2. Create new app or select existing
3. Enable Socket Mode
4. Install app to workspace
5. Copy tokens to `.env`

</details>

---

## 📊 Example Results

### Pre-PR Check Output

```bash
════════════════════════════════════════
🔍 PRE-PR STATIC COMPLIANCE CHECK
════════════════════════════════════════

✅ Status: PASS
📊 Compliance Score: 88.9%
🔍 Controls Checked: 9
⚠️  Warnings: 1

📋 Control Status:
   ✅ 17.1: Designate Personnel
   ✅ 17.2: Contact Information
   ✅ 17.3: Reporting Process
   ✅ 17.4: IR Process
   ✅ 17.5: Key Roles
   ⚠️  17.6: Communication Mechanisms
   ✅ 17.7: IR Exercises
   ✅ 17.8: Post-Incident Reviews
   ✅ 17.9: Incident Thresholds

⚠️  Warnings:
   • 17.6: Secure communication channels should be specified

💡 Recommendations:
   • Define encrypted communication channels (Signal, Wire)
   • Document secure file transfer procedures
   • Add backup communication methods
```

### Post-Merge Analysis

```bash
════════════════════════════════════════
🔍 POST-MERGE DYNAMIC COMPLIANCE CHECK
════════════════════════════════════════

⚠️  Status: NON_COMPLIANT
📊 Compliance Score: 75.0%
🚫 Violations: 2

⏱️  SLA Compliance:
   ✅ Status: COMPLIANT
   ✅ Initial Response: 5 min (required: 15 min)
   ✅ Containment: 45 min (required: 60 min)
   ⚠️  Post-Mortem: Not scheduled (required within 48h)

🚫 Violations Found:
   • Control 17.1: No incident commander assigned
   • Control 17.8: Post-incident review not scheduled

💡 Recommendations:
   • Explicitly assign incident commander in first 15 minutes
   • Schedule post-mortem within 48 hours
   • Document lessons learned process
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

```bash
# 1. Fork the repository
# 2. Create a feature branch
git checkout -b feature/amazing-feature

# 3. Make your changes
# 4. Run tests
pytest tests/ -v

# 5. Commit with conventional commits
git commit -m "feat: add amazing feature"

# 6. Push and create PR
git push origin feature/amazing-feature
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linters
flake8 backend/
black backend/

# Run tests with coverage
pytest --cov=backend tests/
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **CIS Controls v8** - Center for Internet Security
- **FastAPI** - Modern web framework
- **Anthropic Claude** & **Google Gemini** - AI capabilities
- **Slack** - Team collaboration platform
- **Community** - All contributors and users

---

## 📞 Support

<div align="center">

### Need Help?

| Resource | Link |
|----------|------|
| 📖 **Documentation** | [INDEX.md](INDEX.md) |
| 🐛 **Bug Reports** | [GitHub Issues](https://github.com/yourusername/PlaybookPulse/issues) |
| 💬 **Discussions** | [GitHub Discussions](https://github.com/yourusername/PlaybookPulse/discussions) |
| 📧 **Email** | support@playbookpulse.io |

---

### ⭐ Star Us on GitHub!

If PlaybookPulse helped your team, please ⭐ star the repository!

[![GitHub stars](https://img.shields.io/github/stars/yourusername/PlaybookPulse?style=social)](https://github.com/yourusername/PlaybookPulse)

---

**Made with ❤️ by the PlaybookPulse Team**

*Securing incidents, one playbook at a time.*

</div>
