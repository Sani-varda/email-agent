import requests
import json
import os
import time
from send_resend_email import send_sales_email

# Environment Variables for Security
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_USA = os.getenv("DB_USA_ID")
DB_INDIA = os.getenv("DB_INDIA_ID")

def get_leads_to_email(database_id):
    """Fetch leads from Notion that are marked as 'Ready' for outreach."""
    if not NOTION_TOKEN or not database_id:
        print("Error: Missing Notion configuration.")
        return []

    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Filter: Email exists AND Outreach Status is 'Ready'
    payload = {
        "filter": {
            "and": [
                { "property": "Email Address", "email": { "is_not_empty": True } },
                { "property": "Outreach Status", "select": { "equals": "Ready" } }
            ]
        }
    }
    
    try:
        res = requests.post(f"https://api.notion.com/v1/databases/{database_id}/query", headers=headers, json=payload)
        if res.ok:
            return res.json().get("results", [])
    except Exception as e:
        print(f"Error fetching leads: {e}")
    return []

def update_notion_status(page_id, status="Contacted"):
    """Update lead status in Notion after successful outreach."""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "properties": {
            "Outreach Status": { "select": { "name": status } }
        }
    }
    requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json=payload)

def main():
    print("🚀 Starting Marcus Outreach Cycle...")
    
    databases = [db for db in [DB_USA, DB_INDIA] if db]
    
    for db_id in databases:
        leads = get_leads_to_email(db_id)
        print(f"Found {len(leads)} leads in database: {db_id}")
        
        for page in leads:
            props = page["properties"]
            email = props["Email Address"]["email"]
            name = props["Name"]["title"][0]["text"]["content"]
            
            website = props.get("Website", {}).get("url")
            pain_point = "missing website" if not website else "low reviews"
            
            print(f"📧 Sending ROI email to: {name} ({email})...")
            
            success = send_sales_email(email, name, pain_point)
            
            if success:
                update_notion_status(page["id"])
                print(f"✅ Status updated to 'Contacted'.")
            
            time.sleep(2)

if __name__ == "__main__":
    main()
