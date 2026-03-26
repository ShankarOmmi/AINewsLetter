import resend
from config import RESEND_API_KEY

resend.api_key = RESEND_API_KEY


def send_email(to_email, subject, html_content):
    try:
        response = resend.Emails.send({
            "from": "onboarding@resend.dev",  # use this for testing
            "to": [to_email],
            "subject": subject,
            "html": html_content,
        })

        print(f"✅ Email sent to {to_email}")
        return response

    except Exception as e:
        print(f"❌ Email failed: {str(e)}")
        return None