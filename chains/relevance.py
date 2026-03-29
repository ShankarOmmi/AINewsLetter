from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import GROQ_API_KEY

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_template("""
You are a senior AI newsletter editor selecting the TOP story of the week.

ARTICLE:
Title: {title}
Content: {content}

Score from 1 to 10.

STRICT RULES:

9 → ONLY if this is a real-world, high-impact development
     (user growth, revenue, adoption, major product launch)

7 to 8 → Important but not dominant

5 to 6 → Background / trends / analysis

1 to 4 → Ignore

CRITICAL INSTRUCTION:

- DO NOT overrate predictions, opinions, or forecasts
- Prefer REAL events over speculation
- Prefer ACTUAL adoption over future possibilities

Examples:
- "Users doubled" → HIGH score
- "Report predicts future breakthrough" → LOWER score

Respond ONLY with a number.
""")

def score_article(title, content):
    chain = prompt | llm

    response = chain.invoke({
        "title": title,
        "content": content[:2000]  # limit size
    })

    try:
        return int(response.content.strip())
    except:
        return 5  # fallback