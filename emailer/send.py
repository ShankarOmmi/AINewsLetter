import resend
from config import RESEND_API_KEY
from utils.logger import logger

resend.api_key = RESEND_API_KEY


def send_email(to_email, subject, html_content):
    try:
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",  # use this for testing
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        })

        logger.info(f"Email sent to {to_email}")
        return response

    except Exception as e:
        logger.error(f"Email failed for {to_email}: {str(e)}")
        return None