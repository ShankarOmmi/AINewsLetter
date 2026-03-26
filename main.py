from fastapi import FastAPI
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from db.database import create_tables
from api.router import router

from agents.collector import build_collector_graph
from agents.processor import build_processor_graph

from jinja2 import Environment, FileSystemLoader
from emailer.send import send_email

from apscheduler.schedulers.background import BackgroundScheduler


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
# 2. NEWSLETTER JOB (CORE LOGIC)
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

    html = render_email(newsletter)

    # Save locally (debug)
    with open("test_email.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ HTML generated")

    # 🔥 SEND EMAIL (currently only to yourself)
    send_email(
        to_email="n200179@rguktn.ac.in",
        subject=newsletter["subject"],
        html_content=html
    )

    print("✅ Email sent!")


# -------------------------------
# 3. LIFESPAN (Startup/Shutdown)
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("Database initialised")

    # 🔥 START SCHEDULER
    scheduler = BackgroundScheduler()

    # Weekly schedule (Monday 8 AM)
    scheduler.add_job(run_newsletter_job, "cron", day_of_week="mon", hour=8, minute=0)

    #TEST MODE (uncomment for quick testing)
    scheduler.add_job(run_newsletter_job, "interval", minutes=2)

    scheduler.start()
    print("Scheduler started")

    yield

    scheduler.shutdown()
    print("Shutting down")


# -------------------------------
# 4. FASTAPI APP
# -------------------------------
app = FastAPI(lifespan=lifespan)

app.include_router(router)


@app.get("/")
def home():
    return FileResponse("static/signup.html")


# -------------------------------
# 5. MANUAL RUN (FOR TESTING)
# -------------------------------
if __name__ == "__main__":
    print("\n🧪 Running manual test...\n")
    run_newsletter_job()