from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config import GROQ_API_KEY


llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)


prompt = ChatPromptTemplate.from_template("""
You are reviewing a newsletter.

Check:
- Is the intro engaging?
- Are summaries clear and factual?
- Is tone consistent?
- Any repetition or awkward phrasing?

Respond with ONLY:

APPROVED

OR

REJECTED: <reason>
""")


def check_quality(newsletter):
    chain = prompt | llm

    response = chain.invoke({
        "newsletter": str(newsletter)
    })

    return response.content.strip()