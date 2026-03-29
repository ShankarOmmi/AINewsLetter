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

from utils.logger import logger


# -------------------------------
# 1. EMAIL RENDER FUNCTION
# -------------------------------
from collections import defaultdict
import datetime

COLORS = ["#0a0a0a", "#1a73e8", "#2e7d32", "#8e24aa"]

def render_email(newsletter, edition_number, unsubscribe_url="http://example.com"):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("newsletter.html")

    # GROUP SECTIONS (IMPORTANT FIX)
    grouped_sections = defaultdict(list)
    for item in newsletter["sections"]:
        grouped_sections[item["category"]].append(item)

    # COLOR ROTATION
    header_color = COLORS[edition_number % 4]

    return template.render(
        subject=newsletter["subject"],
        intro=newsletter["intro"],
        grouped_sections=grouped_sections,  
        closing=newsletter["closing"],
        unsubscribe_url=unsubscribe_url,
        edition_number=edition_number,
        date=datetime.datetime.now().strftime("%B %d, %Y"),
        header_color=header_color
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
    # ✅ Use localhost directly (no BASE_URL)
    approve_link = f"http://localhost:8000/approve?id={edition_id}"
    reject_link = f"http://localhost:8000/reject?id={edition_id}"

    # Full newsletter HTML
    html = render_email(newsletter, edition_number=edition_id)

    # Approval UI
    approval_section = f"""
    <div style="padding:15px; border:2px solid #e5e7eb; margin-bottom:20px; text-align:center;">
        <h3 style="margin:0 0 10px 0;">Approval Required</h3>

        <a href="{approve_link}" style="background:#16a34a; color:white; padding:10px 16px; text-decoration:none; border-radius:6px;">
            Approve
        </a>

        &nbsp;&nbsp;

        <a href="{reject_link}" style="background:#dc2626; color:white; padding:10px 16px; text-decoration:none; border-radius:6px;">
            Reject
        </a>
    </div>
    """

    final_html = approval_section + html

    send_email(
        to_email="n200179@rguktn.ac.in",
        subject=f"Approval Required - Edition #{edition_id}",
        html_content=final_html
    )

    logger.info("Approval email sent")

# -------------------------------
# 4. NEWSLETTER JOB (UPDATED)
# -------------------------------
def run_newsletter_job():
    logger.info("Running newsletter job...")

    try:
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

        state = collector.invoke(state)
        state = processor.invoke(state)

        newsletter = state["final_newsletter"]

        if not newsletter or isinstance(newsletter, str):
            logger.error("Newsletter generation failed")
            return

        logger.info("Newsletter generated")

        edition_id = save_edition(newsletter)
        logger.info(f"Saved edition {edition_id}")

        html = render_email(newsletter, edition_number=edition_id)
        with open("test_email.html", "w", encoding="utf-8") as f:
            f.write(html)

        logger.info("Preview saved")

        send_approval_email(newsletter, edition_id)

    except Exception as e:
        logger.exception(f"CRITICAL ERROR in newsletter job: {str(e)}")


# -------------------------------
# 5. LIFESPAN (Startup/Shutdown)
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    logger.info("Database initialised")

    # Scheduler
    scheduler = BackgroundScheduler()

    # Weekly (Monday 8 AM)
    scheduler.add_job(run_newsletter_job, "cron", day_of_week="mon", hour=8, minute=0)

    # TEST MODE (comment later)
    scheduler.add_job(run_newsletter_job, "interval", minutes=2)

    scheduler.start()
    logger.info("Scheduler started")

    yield

    scheduler.shutdown()
    logger.info("Shutting down")


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
    logger.info("\nRunning manual test...\n")

    # IMPORTANT FIX
    create_tables()

    run_newsletter_job()