from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import GROQ_API_KEY

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)

prompt = ChatPromptTemplate.from_template("""
You are an expert news editor.

Determine whether the following two article titles refer to the EXACT SAME news event.

TITLE 1:
{title1}

TITLE 2:
{title2}

IMPORTANT RULES:

- Answer YES ONLY if both titles describe the SAME specific event or announcement
  (e.g., same company, same deal, same product launch, same incident)

- Answer NO if they are:
  - General trends or predictions
  - Different reports about the same topic (e.g., "AI in 2026")
  - Broad discussions in the same domain
  - Different companies or different events

Examples:

Same story → YES:
- "SoftBank secures $40B loan"
- "SoftBank raises $40B from banks"

Different → NO:
- "AI trends in 2026"
- "Future of AI industry"

Respond ONLY with:
YES or NO
""")


def is_same_story(title1, title2):
    chain = prompt | llm

    response = chain.invoke({
        "title1": title1,
        "title2": title2
    })

    return response.content.strip().upper() == "YES"


def cluster_articles(state):
    articles = state["raw_articles"]
    clusters = []

    for article in articles:
        placed = False

        for cluster in clusters:
            # Compare with first article in cluster
            if is_same_story(article["title"], cluster[0]["title"]):
                cluster.append(article)
                placed = True
                break

        if not placed:
            clusters.append([article])

    return {
        **state,
        "clusters": clusters
    }


def merge_clusters(state):
    clusters = state.get("clusters", [])
    merged_articles = []

    for cluster in clusters:
        # Combine titles + content
        combined_content = "\n\n".join([a["content"] for a in cluster])

        merged_articles.append({
            "title": cluster[0]["title"],  # representative title
            "url": cluster[0]["url"],      # primary source
            "content": combined_content
        })

    return {
        **state,
        "raw_articles": merged_articles
    }