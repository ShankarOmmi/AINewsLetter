from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import GROQ_API_KEY

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_template("""
You are a sentiment classifier for an AI newsletter. Your only job is to label each article as Positive, Negative, or Neutral.

ARTICLE:
Title: {title}
Summary: {summary}

THE SINGLE MOST IMPORTANT RULE:
Ask yourself — "Has something good or bad ALREADY HAPPENED and been CONFIRMED?"
If YES → Positive or Negative
If NO (it is a prediction, trend, opinion, analysis, or plan) → Neutral

---

POSITIVE — only when ALL of these are true:
  - Something beneficial has already happened (not predicted, not planned)
  - It is confirmed, not speculative
  - The outcome is clearly good for the field, users, or society
  ✓ "Claude paid subscriptions double" → confirmed growth → Positive
  ✓ "New model beats benchmark" → confirmed achievement → Positive
  ✗ "AI will transform healthcare in 2026" → future prediction → Neutral
  ✗ "Trends that will shape AI" → analysis/opinion → Neutral

NEGATIVE — only when ALL of these are true:
  - Something harmful has already happened and is confirmed
  - Some negative prediction that might be harmful and is presented as more likely than not like some dangers of AI
  - It is not just a warning or theoretical risk
  ✓ "Study confirms AI chatbots give dangerous personal advice" → confirmed harm → Negative
  ✓ "Company fined for AI data misuse" → confirmed bad outcome → Negative
  ✗ "Experts warn AI could cause job losses" → warning, not confirmed → Neutral

NEUTRAL — use this for:
  - Predictions and forecasts that are mostly uncertain("will", "could", "expected to", "next year")
  - Trend reports and analysis ("trends to watch", "what's next", "7 things")
  - Opinions and commentary without confirmed outcomes
  - Mixed articles with both positives and negatives
  - Announcements of plans not yet executed
  ✓ "What's next for AI in 2026" → prediction/analysis → Neutral
  ✓ "Morgan Stanley warns of AI breakthrough coming" → warning/forecast → Neutral
  ✓ "Trends that will shape AI and tech in 2026" → trend analysis → Neutral

---

Now classify this article. Think step by step:
Step 1 — What is the single core fact of this article?
Step 2 — Has this thing ALREADY HAPPENED (confirmed), or is it predicted/discussed/warned about?
Step 3 — If already happened: is the outcome good (Positive) or bad (Negative)?
Step 4 — If not confirmed or mixed: Neutral

Respond with your answer in EXACTLY one word:
Positive
Negative
Neutral
""")


def get_article_sentiment(title, summary):
    chain = prompt | llm

    response = chain.invoke({
        "title": title,
        "summary": summary
    })

    return response.content.strip()