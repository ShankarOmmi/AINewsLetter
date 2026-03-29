from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import GROQ_API_KEY
import json
import re

from utils.logger import logger


llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)


prompt = ChatPromptTemplate.from_template("""
You are writing a weekly AI newsletter.

Given these article summaries:
{summaries}

Organize them into EXACTLY 3 sections:

1. Major News
2. Advancements
3. Fun & Interesting

Return JSON in this EXACT format:

{{
  "subject": "...",
  "intro": "...",
  "sections": [
    {{
      "category": "Major News",
      "articles": [
        {{ "title": "...", "summary": "..." }}
      ]
    }},
    {{
      "category": "Advancements",
      "articles": [
        {{ "title": "...", "summary": "..." }}
      ]
    }},
    {{
      "category": "Fun & Interesting",
      "articles": [
        {{ "title": "...", "summary": "..." }}
      ]
    }}
  ],
  "closing": "..."
}}

STRICT:
- Always include all 3 categories
- Return ONLY JSON
""")


def extract_json(text: str):
    # Remove ```json ... ``` wrapper if present
    text = text.strip()

    # Remove triple backticks
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text)  # remove ```json
        text = text.rstrip("```")

    return text.strip()


def normalize_newsletter(data, original_summaries):
    normalized_sections = []

    # 🔥 Create lookup by title
    lookup = {item["title"]: item for item in original_summaries}

    for section in data.get("sections", []):
        category = section.get("category", "Other")

        for article in section.get("articles", []):
            title = article.get("title", "")
            summary = article.get("summary", "")

            # 🔥 Fetch original data
            original = lookup.get(title, {})

            normalized_sections.append({
                "category": category,
                "title": title,
                "summary": summary,
                "url": original.get("url"),                  # ✅ FIX
                "score": original.get("score", 0),           # ✅ FIX
                "sentiment": original.get("sentiment", "Neutral")  # ✅ FIX
            })

    return {
        "subject": data.get("subject", ""),
        "intro": data.get("intro", ""),
        "sections": normalized_sections,
        "closing": data.get("closing", "")
    }




def format_newsletter(summaries):
    chain = prompt | llm

    for attempt in range(10):  # retry once
        response = chain.invoke({
            "summaries": summaries
        })

        cleaned = extract_json(response.content)

        try:
            parsed = json.loads(cleaned)
            return normalize_newsletter(parsed, summaries)

        except Exception as e:
            logger.warning(f"JSON failed (attempt {attempt + 1})")

    #  If still failing
    print("\n FINAL JSON FAILURE")
    return None