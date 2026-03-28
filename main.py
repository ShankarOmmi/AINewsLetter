from fastapi import FastAPI
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from db.database import create_tables, get_connection
from api.router import router

from agents.collector import build_collector_graph
from agents.processor import build_processor_graph

from jinja2 import Environment, FileSystemLoader
from emailer.send import send_email

from apscheduler.schedulers.background import BackgroundScheduler

import time
import json


# -------------------------------
# 1. EMAIL RENDER FUNCTION
# -------------------------------
def render_email(newsletter, unsubscribe_url="http://example.com"):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("newsletter.html")

    return template.render(
        subject=newsletter["subject"],
        intro=newsletter["intro"],
        sections=newsletter["sections"],
        closing=newsletter["closing"],
        unsubscribe_url=unsubscribe_url
    )


# -------------------------------
# 2. SAVE EDITION (NEW)
# -------------------------------
def save_edition(newsletter):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO editions (subject, content, status)
        VALUES (?, ?, ?)
    """, (
        newsletter["subject"],
        json.dumps(newsletter),
        "pending"
    ))

    conn.commit()
    edition_id = cursor.lastrowid
    conn.close()

    return edition_id


# -------------------------------
# 3. SEND APPROVAL EMAIL (NEW)
# -------------------------------
def send_approval_email(newsletter, edition_id):
    approve_link = f"http://localhost:8000/approve?id={edition_id}"
    reject_link = f"http://localhost:8000/reject?id={edition_id}"

    # Render full newsletter HTML
    html = render_email(newsletter)

    # Add approval buttons on top
    approval_section = f"""
    <div style="padding: 15px; border: 2px solid #ccc; margin-bottom: 20px;">
        <h3>Approval Required</h3>
        <a href="{approve_link}" style="color: green; font-size: 18px;">✅ Approve</a>
        &nbsp;&nbsp;&nbsp;
        <a href="{reject_link}" style="color: red; font-size: 18px;">❌ Reject</a>
    </div>
    """

    # Combine
    final_html = approval_section + html

    send_email(
        to_email="n200179@rguktn.ac.in",
        subject="Approval Required - Newsletter",
        html_content=final_html
    )

    print(" Approval email sent!")

# -------------------------------
# 4. NEWSLETTER JOB (UPDATED)
# -------------------------------
def run_newsletter_job():
    print("\n🚀 Running newsletter job...")

    collector = build_collector_graph()
    processor = build_processor_graph()

    state = {
        "topic": "latest AI news",
        "raw_articles": [],
        "filtered_articles": [],
        "summaries": [],
        "newsletter_draft": "",
        "quality_passed": False,
        "final_newsletter": "",
        "error": None
    }

    # Run pipeline
    state = collector.invoke(state)
    state = processor.invoke(state)

    newsletter = state["final_newsletter"]

    if not newsletter or isinstance(newsletter, str):
        print("❌ Newsletter generation failed")
        return

    print("✅ Newsletter generated")

    # Save edition
    edition_id = save_edition(newsletter)
    print(f"💾 Saved edition {edition_id} (pending approval)")

    # Generate preview HTML (optional debug)
    html = render_email(newsletter)
    with open("test_email.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("📝 Preview saved as test_email.html")

    # Send approval email
    send_approval_email(newsletter, edition_id)


# -------------------------------
# 5. LIFESPAN (Startup/Shutdown)
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("Database initialised")

    # Scheduler
    scheduler = BackgroundScheduler()

    # Weekly (Monday 8 AM)
    scheduler.add_job(run_newsletter_job, "cron", day_of_week="mon", hour=8, minute=0)

    # TEST MODE (comment later)
    scheduler.add_job(run_newsletter_job, "interval", minutes=2)

    scheduler.start()
    print("Scheduler started")

    yield

    scheduler.shutdown()
    print("Shutting down")


# -------------------------------
# 6. FASTAPI APP
# -------------------------------
app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.get("/")
def home():
    return FileResponse("static/signup.html")


# -------------------------------
# 7. MANUAL RUN
# -------------------------------
if __name__ == "__main__":
    print("\n🧪 Running manual test...\n")

    # 🔥 IMPORTANT FIX
    create_tables()

    run_newsletter_job()