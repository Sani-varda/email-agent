import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load credentials from environment variables
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


def _validate_smtp_config() -> bool:
    """Fail fast if SMTP credentials are not set."""
    if not SMTP_USER or not SMTP_PASS:
        print("[ERROR] SMTP_USER and SMTP_PASS environment variables must be set.")
        return False
    return True


def send_sales_email(
    to_email: str,
    business_name: str,
    pain_point: str,
    sender_name: str = "Sani V.",
) -> bool:
    """
    Sends a personalized ROI-driven sales email via Gmail SMTP.
    Returns True on success, False on failure.
    """
    if not _validate_smtp_config():
        return False

    # ─── Pain point copy ───
    if pain_point == "low reviews":
        point_text = (
            "I noticed your business\'s online presence has significant room to grow in customer reviews. "
            "Our automated Reputation Engine doesn\'t just manage feedback—it actively converts happy "
            "customers into 5-star reviews on autopilot. For most clinics this directly translates to a "
            "20–30% lift in new patient inquiries within the first 60 days."
        )
    elif pain_point == "missing website":
        point_text = (
            "I couldn\'t locate a dedicated website for your business. Local businesses without a "
            "high-converting digital storefront lose nearly 40% of potential bookings to competitors "
            "who are easier to find online. We provide premium, one-time-ownership SaaS websites that "
            "act as your 24/7 sales team—capturing every lead that would otherwise be missed."
        )
    else:
        point_text = (
            "We specialise in eliminating operational inefficiencies through 24/7 AI assistance and "
            "workflow automation. Automating up to 70% of routine customer inquiries and internal "
            "reporting reduces overhead while increasing response speed—a combination that typically "
            "delivers an immediate positive ROI."
        )

    primary_blue = "#1e3a8a"
    light_blue_bg = "#f0f4ff"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ROI-Driven AI Automation for {business_name}</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; line-height: 1.6; color: #1a1a1a; background-color: #f4f4f4; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 0; border-radius: 6px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            .header {{ background-color: {primary_blue}; color: #ffffff; padding: 40px 20px; text-align: center; }}
            .header h1 {{ margin: 0; letter-spacing: 2px; text-transform: uppercase; font-size: 26px; }}
            .body-content {{ padding: 40px; }}
            .service-card {{ background-color: {light_blue_bg}; padding: 22px; margin-bottom: 20px; border-radius: 4px; border-left: 5px solid {primary_blue}; }}
            .service-title {{ font-weight: bold; color: {primary_blue}; display: block; margin-bottom: 6px; font-size: 16px; }}
            .cta {{ text-align: center; margin: 40px 0; }}
            .cta-button {{ background-color: {primary_blue}; color: #ffffff !important; padding: 18px 35px; text-decoration: none; font-weight: bold; display: inline-block; text-transform: uppercase; letter-spacing: 1px; font-size: 14px; border-radius: 4px; }}
            .footer-text {{ font-size: 11px; color: #666666; margin-top: 25px; text-align: center; line-height: 1.5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header"><h1>MoonLIT Arc</h1></div>
            <div class="body-content">
                <p>Dear Team at {business_name},</p>
                <p>I am reaching out from MoonLIT Arc. We help high-growth businesses eliminate manual bottlenecks and maximise revenue potential.</p>
                <p>{point_text}</p>
                <div class="service-card"><span class="service-title">24/7 AI Assistance</span>Instantly handle 70% of customer inquiries.</div>
                <div class="service-card"><span class="service-title">Reputation Management</span>Dominate local rankings on Google Maps.</div>
                <div class="service-card"><span class="service-title">Workflow Automation</span>Eliminate manual tasks with RAG-based AI solutions.</div>
                <p>Our &ldquo;One-Time Ownership&rdquo; model means you own the technology we build for you—delivering permanent ROI without monthly fees.</p>
                <div class="cta"><a href="https://moonlitarc.vercel.app/" class="cta-button">Schedule an ROI Consultation</a></div>
                <p>Best regards,<br>
                <strong>{sender_name}</strong><br>
                MoonLIT Arc Engineering</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} | MoonLIT Arc <{SMTP_USER}>"
    msg["To"] = to_email
    msg["Subject"] = f"ROI Analysis and AI Automation for {business_name}"
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
            return True
    except Exception as e:
        print(f"[ERROR] Failed to send email to {to_email}: {e}")
        return False
