from fastapi import APIRouter, HTTPException
from api.schemas import SubscribeRequest
from db.models import add_subscriber, unsubscribe, log_send
from db.database import get_connection
from emailer.send import send_email

from jinja2 import Environment, FileSystemLoader
from utils.logger import logger

import json
import time

router = APIRouter()

# CONFIG (change later for Railway)
BASE_URL = "http://localhost:8000"


# -------------------------------
# SUBSCRIBE
# -------------------------------
@router.post("/subscribe")
def subscribe(data: SubscribeRequest):
    result = add_subscriber(data.email)

    if not result["success"]:
        if "UNIQUE constraint failed" in result["error"]:
            logger.warning(f"Duplicate subscription attempt: {data.email}")
            return {"message": "Email already subscribed"}

        logger.error(f"Subscription failed: {result['error']}")
        raise HTTPException(status_code=400, detail=result["error"])

    logger.info(f"New subscriber added: {data.email}")
    return {"message": "Subscribed successfully"}

# -------------------------------
# UNSUBSCRIBE
# -------------------------------
@router.get("/unsubscribe")
def unsubscribe_user(token: str):
    success = unsubscribe(token)

    if not success:
        logger.warning(f"Invalid unsubscribe token: {token}")
        raise HTTPException(status_code=404, detail="Invalid token")

    logger.info(f"User unsubscribed with token: {token}")
    return {"message": "You have been unsubscribed"}

# -------------------------------
# APPROVE NEWSLETTER
# -------------------------------
@router.get("/approve")
def approve_newsletter(id: int):
    conn = get_connection()
    cursor = conn.cursor()

    logger.info(f"Approval requested for edition {id}")

    try:
        # -------------------------------
        # FETCH EDITION
        # -------------------------------
        cursor.execute("SELECT content, status FROM editions WHERE id=?", (id,))
        row = cursor.fetchone()

        if not row:
            logger.error(f"Edition {id} not found")
            return {"error": "Edition not found"}

        content, status = row

        if status == "approved":
            logger.warning(f"Edition {id} already approved")
            return {"message": "Already approved"}

        # -------------------------------
        # PARSE NEWSLETTER
        # -------------------------------
        try:
            newsletter = json.loads(content)
        except Exception as e:
            logger.error(f"JSON parse failed for edition {id}: {str(e)}")
            return {"error": "Invalid newsletter content"}

        # -------------------------------
        # MARK APPROVED
        # -------------------------------
        cursor.execute("UPDATE editions SET status='approved' WHERE id=?", (id,))
        conn.commit()

        logger.info(f"Edition {id} marked as approved")

        # -------------------------------
        # FETCH SUBSCRIBERS
        # -------------------------------
        cursor.execute(
            "SELECT email, unsubscribe_token FROM subscribers WHERE status='active'"
        )
        subscribers = cursor.fetchall()

        total_subscribers = len(subscribers)
        logger.info(f"Sending to {total_subscribers} subscribers")

        # -------------------------------
        # RATE LIMITING CONFIG
        # -------------------------------
        BATCH_SIZE = 10
        DELAY_BETWEEN_BATCHES = 2

        success_count = 0
        fail_count = 0

        # -------------------------------
        # SEND EMAILS (SAFE LOOP)
        # -------------------------------
        try:
            for i in range(0, total_subscribers, BATCH_SIZE):
                batch = subscribers[i:i + BATCH_SIZE]

                for email, token in batch:
                    try:
                        unsubscribe_url = f"{BASE_URL}/unsubscribe?token={token}"
                        html = render_email(newsletter, edition_number=id, unsubscribe_url=unsubscribe_url)

                        send_email(
                            to_email=email,
                            subject=newsletter["subject"],
                            html_content=html
                        )

                        success_count += 1

                    except Exception as e:
                        fail_count += 1
                        logger.error(f"Failed for {email}: {str(e)}")

                logger.info(f"Batch {i // BATCH_SIZE + 1} sent")

                time.sleep(DELAY_BETWEEN_BATCHES)

        except Exception as e:
            logger.exception(f"Critical sending failure for edition {id}: {str(e)}")

        # -------------------------------
        # DETERMINE STATUS
        # -------------------------------
        if success_count == 0:
            send_status = "fail"
        elif fail_count == 0:
            send_status = "success"
        else:
            send_status = "partial"

        # -------------------------------
        # LOG SEND TO DB
        # -------------------------------
        log_send(id, newsletter["subject"], total_subscribers, send_status)

        logger.info(
            f"Edition {id} completed | Success: {success_count} | Failed: {fail_count}"
        )

        return {
            "message": "Newsletter approved and sent!",
            "success": success_count,
            "failed": fail_count
        }

    finally:
        conn.close()

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

    logger.warning(f"Edition {id} rejected")

    return {"message": "Newsletter rejected"}