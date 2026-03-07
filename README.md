# MoonLIT Arc — Marcus Outreach Agent

This repository contains the **Marcus Outreach Engine**, a specialized AI sub-agent used by **MoonLIT Arc** to automate personalized ROI-driven outreach for local businesses.

## How it Works
1. **Lead Discovery:** Identifies high-probability leads (businesses with missing websites or low review scores) from our Notion CRM.
2. **Personalization:** Analyzes business data to identify specific pain points.
3. **Outreach:** Sends highly personalized HTML emails with ROI-focused value propositions.
4. **CRM Sync:** Automatically updates lead status in Notion after successful outreach.

## Technology Stack
- **Notion API:** For CRM and lead management.
- **Gmail SMTP:** For high-deliverability outreach.
- **Python:** Core automation logic.

## Setup
1. Clone this repository.
2. Set the following environment variables:
   - `NOTION_TOKEN`: Your Notion integration token.
   - `DB_USA_ID`: The Notion database ID for USA leads.
   - `DB_INDIA_ID`: The Notion database ID for India leads.
   - `SMTP_USER`: Your Gmail address.
   - `SMTP_PASS`: Your Gmail App Password.
3. Install dependencies: `pip install requests`.
4. Run the agent: `python marcus_outreach.py`.

---
Built with ⚡ by **MoonLIT Arc** | [moonlitarc.com](https://moonlitarc.vercel.app/)
