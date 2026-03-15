import requests
import json
import os
import time
from datetime import datetime
from send_email import send_sales_email

# ─── Configuration ───
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_USA       = os.getenv("DB_USA_ID")
DB_INDIA     = os.getenv("DB_INDIA_ID")

FAILED_LOG_PATH = "failed_leads.json"
SEND_DELAY_SECS = 2  # throttle between sends to respect Gmail rate limits


def _notion_headers() -> dict:
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }


def get_leads_to_email(database_id: str) -> list:
    """Fetch leads from Notion marked as 'Ready' for outreach."""
    if not NOTION_TOKEN or not database_id:
        print("[ERROR] Missing Notion configuration (NOTION_TOKEN / database_id).")
        return []

    payload = {
        "filter": {
            "and": [
                {"property": "Email Address", "email": {"is_not_empty": True}},
                {"property": "Outreach Status", "select": {"equals": "Ready"}},
            ]
        }
    }

    try:
        res = requests.post(
            f"https://api.notion.com/v1/databases/{database_id}/query",
            headers=_notion_headers(),
            json=payload,
            timeout=10,
        )
        if res.ok:
            return res.json().get("results", [])
        print(f"[ERROR] Notion query failed ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"[ERROR] Exception fetching leads: {e}")
    return []


def update_notion_status(page_id: str, status: str = "Contacted") -> bool:
    """Update lead status in Notion. Returns True on success."""
    try:
        res = requests.patch(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=_notion_headers(),
            json={"properties": {"Outreach Status": {"select": {"name": status}}}},
            timeout=10,
        )
        if not res.ok:
            print(f"[WARN] Failed to update Notion page {page_id} ({res.status_code}): {res.text}")
            return False
        return True
    except Exception as e:
        print(f"[WARN] Exception updating Notion page {page_id}: {e}")
        return False


def classify_pain_point(props: dict) -> str:
    """
    Derive pain point from lead properties.
    Priority: missing website > low reviews > default automation pitch.
    """
    website = props.get("Website", {}).get("url")
    review_score = props.get("Review Score", {}).get("number")  # optional field

    if not website:
        return "missing website"
    if review_score is not None and review_score < 4.0:
        return "low reviews"
    return "general automation"


def extract_lead(page: dict) -> dict | None:
    """
    Safely extract email and name from a Notion page.
    Returns None if required fields are missing or malformed.
    """
    try:
        props = page["properties"]
        email = props.get("Email Address", {}).get("email")
        title_arr = props.get("Name", {}).get("title", [])
        name = title_arr[0]["text"]["content"] if title_arr else None

        if not email or not name:
            print(f"[SKIP] Lead {page['id']} missing email or name — skipping.")
            return None

        return {
            "id": page["id"],
            "email": email,
            "name": name,
            "pain_point": classify_pain_point(props),
        }
    except (KeyError, IndexError, TypeError) as e:
        print(f"[SKIP] Malformed lead {page.get('id', 'unknown')}: {e}")
        return None


def log_failed_lead(lead: dict, reason: str) -> None:
    """Append a failed lead to failed_leads.json for review and retry."""
    entry = {**lead, "reason": reason, "timestamp": datetime.utcnow().isoformat()}
    existing = []
    try:
        with open(FAILED_LOG_PATH, "r") as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    existing.append(entry)
    with open(FAILED_LOG_PATH, "w") as f:
        json.dump(existing, f, indent=2)


def main():
    if not NOTION_TOKEN:
        print("[ERROR] NOTION_TOKEN is not set. Exiting.")
        return

    print(f"\n🚀 Marcus Outreach Cycle started at {datetime.utcnow().isoformat()} UTC")

    databases = [(db_id, label) for db_id, label in [(DB_USA, "USA"), (DB_INDIA, "India")] if db_id]

    if not databases:
        print("[ERROR] No databases configured (DB_USA_ID / DB_INDIA_ID). Exiting.")
        return

    total_sent = 0
    total_failed = 0
    total_skipped = 0

    for db_id, label in databases:
        pages = get_leads_to_email(db_id)
        print(f"\n[🌍 {label}] Found {len(pages)} ready leads.")

        for page in pages:
            lead = extract_lead(page)
            if not lead:
                total_skipped += 1
                continue

            print(f"  📧 Sending to {lead['name']} ({lead['email']}) — pain point: {lead['pain_point']}")

            sent = send_sales_email(lead["email"], lead["name"], lead["pain_point"])

            if sent:
                notion_updated = update_notion_status(lead["id"])
                if not notion_updated:
                    # Email sent but CRM not updated — log so we can manually fix
                    log_failed_lead(lead, "email_sent_but_notion_update_failed")
                    print(f"  ⚠️  Email sent but Notion update failed for {lead['name']} — logged to {FAILED_LOG_PATH}")
                else:
                    print(f"  ✅ Sent and CRM updated.")
                total_sent += 1
            else:
                log_failed_lead(lead, "smtp_send_failed")
                print(f"  ❌ Send failed for {lead['name']} — logged to {FAILED_LOG_PATH}")
                total_failed += 1

            time.sleep(SEND_DELAY_SECS)

    print(f"""
📊 Run complete:
   ✅ Sent:    {total_sent}
   ❌ Failed:  {total_failed}
   ⏭️  Skipped: {total_skipped}
""")
    if total_failed > 0:
        print(f"   Failed leads saved to → {FAILED_LOG_PATH}")


if __name__ == "__main__":
    main()
