from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import GROQ_API_KEY

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_template("""
You are a sharp AI newsletter editor.

You are given summaries of this week's articles.

Your job is to extract ONE meaningful insight that connects them — ideally a contrast, shift, or tension.

SUMMARIES:
{summaries}

INSTRUCTIONS:

- Write EXACTLY 2 sentences
- First sentence → describe what is happening across the stories
- Second sentence → highlight a contrast, tension, or deeper implication

STRICT RULES:

- Base everything ONLY on the summaries
- Do NOT introduce new topics
- Avoid generic phrases like:
  "growing emphasis", "AI landscape", "innovation and security"
- Do NOT sound corporate or vague
- Focus on ONE sharp idea

STYLE:

- Think like an editor, not a summarizer
- Prefer contrast:
  - growth vs risk
  - adoption vs trust
  - capability vs control

GOOD EXAMPLE:

"This week’s developments show AI rapidly moving into real-world deployment, with both enterprises and consumers accelerating adoption. At the same time, rising concerns around reliability and over-reliance suggest that the next phase of AI will be defined as much by trust as by capability."

Return ONLY the paragraph.
""")


def generate_narrative(summaries):
    formatted = "\n\n".join([
        f"- {s['title']}: {s['summary']}"
        for s in summaries
    ])

    chain = prompt | llm

    response = chain.invoke({
        "summaries": formatted
    })

    return response.content.strip()