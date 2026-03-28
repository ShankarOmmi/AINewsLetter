from fastapi import APIRouter, HTTPException
from api.schemas import SubscribeRequest
from db.models import add_subscriber, unsubscribe
from db.database import get_connection
from emailer.send import send_email

from jinja2 import Environment, FileSystemLoader

import json
import time

router = APIRouter()


# -------------------------------
# TEMPLATE RENDER
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
# SUBSCRIBE
# -------------------------------
@router.post("/subscribe")
def subscribe(data: SubscribeRequest):
    result = add_subscriber(data.email)

    if not result["success"]:
        if "UNIQUE constraint failed" in result["error"]:
            return {"message": "Email already subscribed"}

        raise HTTPException(status_code=400, detail=result["error"])

    return {"message": "Subscribed successfully"}


# -------------------------------
# UNSUBSCRIBE
# -------------------------------
@router.get("/unsubscribe")
def unsubscribe_user(token: str):
    success = unsubscribe(token)

    if not success:
        raise HTTPException(status_code=404, detail="Invalid token")

    return {"message": "You have been unsubscribed"}


# -------------------------------
# APPROVE NEWSLETTER
# -------------------------------
@router.get("/approve")
def approve_newsletter(id: int):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch edition
    cursor.execute("SELECT content, status FROM editions WHERE id=?", (id,))
    row = cursor.fetchone()

    if not row:
        return {"error": "Edition not found"}

    content, status = row

    # Prevent double sending
    if status == "approved":
        return {"message": "Already approved"}

    newsletter = json.loads(content)

    # Mark approved
    cursor.execute("UPDATE editions SET status='approved' WHERE id=?", (id,))
    conn.commit()

    # Fetch subscribers
    cursor.execute("SELECT email, unsubscribe_token FROM subscribers WHERE status='active'")
    subscribers = cursor.fetchall()

    print(f"📬 Sending to {len(subscribers)} subscribers...")

    for email, token in subscribers:
        try:
            unsubscribe_url = f"http://localhost:8000/unsubscribe?token={token}"

            html = render_email(newsletter, unsubscribe_url)

            send_email(
                to_email=email,
                subject=newsletter["subject"],
                html_content=html
            )

            time.sleep(0.2)  # rate limiting

        except Exception as e:
            print(f"❌ Failed for {email}: {str(e)}")

    conn.close()

    return {"message": "✅ Newsletter approved and sent!"}


# -------------------------------
# REJECT NEWSLETTER
# -------------------------------
@router.get("/reject")
def reject_newsletter(id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE editions SET status='rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return {"message": "❌ Newsletter rejected"}