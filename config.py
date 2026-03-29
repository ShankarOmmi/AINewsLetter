import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Deployment
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///newsletter.db")

# Email Configuration
EMAIL_FROM = os.getenv("EMAIL_FROM", "newsletter@shankarommi.in")
APPROVAL_EMAIL = os.getenv("APPROVAL_EMAIL", "n200179@rguktn.ac.in")

# Server
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")