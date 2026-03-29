from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config import GROQ_API_KEY

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0.3
)

prompt = ChatPromptTemplate.from_template("""
You are a senior AI newsletter editor writing for a high-quality weekly briefing.

Your goal is to produce a sharp, information-dense, and insightful summary.

ARTICLE TITLE:
{title}

ARTICLE CONTENT:
{content}

INSTRUCTIONS:

Write EXACTLY TWO paragraphs:

Paragraph 1 (2 to 3 sentences):
- Clearly explain what happened
- Focus only on the core event (avoid overload)
- Include key facts (companies, numbers, actions)

Paragraph 2 (1 to 2 sentences):
- Explain WHY this matters
- Focus on implications, industry shifts, or future consequences
- Be analytical and confident

STYLE RULES:
- Write like a professional human editor
- Use varied analytical phrasing such as:
  "This signals...", "This suggests...", "This reflects...", "This highlights..." 
    these are just examples - be creative with your language and never repeat the
    same phrase across summaries  
- DO NOT repeat the same opening phrase across summaries
- Vary sentence structure naturally
- Avoid generic phrases like:
  "growing trend", "this is important", "this could be useful"
- Each sentence must add new information

STRICT RULES:
- MUST be exactly TWO paragraphs (with one blank line between them)
- Do NOT repeat the title
- Do NOT hallucinate anything not in the article
- Keep total length between 70 to 110 words
- No headings, no bullet points, no markdown

OUTPUT:
Return only the final summary text.
""")

def summarise_article(title, content):
    chain = prompt | llm

    try:
        response = chain.invoke({
            "title": title,
            "content": content[:2000]  # prevent overload
        })

        summary = response.content.strip()

        # ✅ Basic quality filter (intelligence layer)
        if len(summary) < 50:
            return None

        return summary

    except Exception as e:
        print("Summarisation failed:", str(e))
        return None