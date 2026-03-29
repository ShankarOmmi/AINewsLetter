from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import GROQ_API_KEY

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)


prompt = ChatPromptTemplate.from_template("""
You are a strict fact-checking AI.

Given:

ORIGINAL ARTICLE:
{content}

GENERATED SUMMARY:
{summary}

TASK:
Check whether the summary is factually consistent with the article.

RULES:
- Do NOT assume anything
- Only check if summary claims are supported by the article
- If even ONE major claim is unsupported → FAIL

Respond with ONLY ONE WORD:

PASS → if summary is accurate
FAIL → if summary has hallucinations or unsupported claims
""")


def verify_summary(content, summary):
    chain = prompt | llm

    response = chain.invoke({
        "content": content,
        "summary": summary
    })

    result = response.content.strip().upper()

    if "PASS" in result:
        return True
    else:
        return False