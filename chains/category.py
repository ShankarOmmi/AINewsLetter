from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import GROQ_API_KEY

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_template("""
You are an AI newsletter editor.

Classify this article into ONE category:

1. Major News → ONLY if it is a major industry event
2. Advancements → technical progress, research, models
3. Fun & Interesting → lighter insights, studies

ARTICLE:
Title: {title}
Content: {content}

STRICT RULES:

- NOT everything is Major News
- Use Major News sparingly (only top stories)
- Any articles that provides news about any type of research or advancements
  or something that talks about new things must be categorised as Advancements
- Fun & Interesting is for anything that is not a major news or advancement 
  but is still interesting for readers (e.g., studies, insights, lighter news)

Respond ONLY with:
Major News OR Advancements OR Fun & Interesting
""")

def classify_article(title, content):
    chain = prompt | llm

    response = chain.invoke({
        "title": title,
        "content": content[:1500]
    })

    return response.content.strip()