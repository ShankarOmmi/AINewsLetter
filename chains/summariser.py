from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from config import GROQ_API_KEY

llm = ChatGroq(
    api_key = GROQ_API_KEY,
    model = "llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_template("""
You are writing for a professional AI newsletter.

Given:
Title: {title}
Content: {content}

Write a clean 2-3 sentence summary.

STRICT RULES:
- Do NOT include headings like "Summary" or "Key Takeaways"
- Do NOT use markdown formatting (**, #, etc.)
- Just write plain text
- Keep it concise and clear

Focus on:
1. What happened
2. Why it matters
""")

def summarise_article(title, content):
    chain = prompt | llm
    
    response = chain.invoke({
        "title" : title,
        "content" : content
    })

    return response.content.strip()