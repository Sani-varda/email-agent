# ML Arc — Marcus Outreach Agent

This repository contains the **Marcus Outreach Engine**, a specialised AI sub-agent used by **ML Arc** to automate personalised ROI-driven outreach for local businesses.

## How it Works
1. **Lead Discovery** — Pulls leads marked `Ready` from your Notion CRM (supports separate USA and India databases).
2. **Pain Point Classification** — Detects missing website, low review score (< 4.0), or defaults to general automation pitch.
3. **Outreach** — Sends a personalised branded HTML email with ROI-focused messaging via Gmail SMTP.
4. **CRM Sync** — Updates lead status to `Contacted` in Notion after a successful send.
5. **Failure Logging** — Any failed sends or Notion update errors are written to `failed_leads.json` for manual review and retry.

## Technology Stack
- **Notion API** — CRM and lead management
- **Gmail SMTP** — High-deliverability email outreach
- **Python 3.10+** — Core automation logic

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set environment variables
Create a `.env` file (never commit it — it\'s in `.gitignore`):
```bash
NOTION_TOKEN=your_notion_integration_token
DB_USA_ID=your_usa_notion_database_id
DB_INDIA_ID=your_india_notion_database_id
SMTP_USER=your_gmail_address@gmail.com
SMTP_PASS=your_gmail_app_password
SMTP_HOST=smtp.gmail.com    # optional, default: smtp.gmail.com
SMTP_PORT=465               # optional, default: 465
```

> ℹ️ **Gmail App Password**: Go to Google Account → Security → 2-Step Verification → App Passwords.

### 3. Optional — add `Review Score` to your Notion database
If your Notion CRM has a **Number** property called `Review Score`, Marcus will send the `low reviews` pitch to any lead scoring below 4.0 stars. Without it, all leads with a website fall back to the general automation pitch.

### 4. Run
```bash
python marcus_outreach.py
```

## Output
```
🚀 Marcus Outreach Cycle started at 2026-03-16T00:00:00 UTC

[🌍 USA] Found 12 ready leads.
  📧 Sending to Bright Smiles Dental (hello@brightsmiles.com) — pain point: missing website
  ✅ Sent and CRM updated.
  ...

📊 Run complete:
   ✅ Sent:    11
   ❌ Failed:  1
   ⏭️  Skipped: 0

   Failed leads saved to → failed_leads.json
```

## Retrying Failed Leads
Failed leads are saved to `failed_leads.json` with a reason and timestamp:
```json
[
  {
    "id": "notion-page-id",
    "email": "owner@example.com",
    "name": "Example Business",
    "pain_point": "low reviews",
    "reason": "smtp_send_failed",
    "timestamp": "2026-03-16T00:05:12.000000"
  }
]
```
Fix the issue (e.g. re-set `Outreach Status` to `Ready` in Notion), then re-run Marcus.

---
Built with ⚡ by **ML Arc** | [mlarc.vercel.app](https://mlarc.vercel.app/)
