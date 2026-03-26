from tavily import TavilyClient
from config import TAVILY_API_KEY
import feedparser

client = TavilyClient(api_key = TAVILY_API_KEY)

def search_node(state):
    topic = state["topic"]
    
    response = client.search(
        query = topic,
        search_depth = "advanced",
        max_results = 10
    )

    articles = []

    for r in response["results"]:
        articles.append({
            "title" : r["title"],
            "url" : r["url"],
            "content" : r["content"]
        })

    return {**state, "raw_articles":articles}


RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theguardian.com/technology/artificial-intelligence/rss",
    "https://www.wired.com/feed/tag/artificial-intelligence/latest/rss",
    "https://news.mit.edu/rss/topic/artificial-intelligence"
]


def rss_node(state):
    articles = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:  # limit per feed
            articles.append({
                "title": entry.title,
                "url": entry.link,
                "content": entry.summary if "summary" in entry else ""
            })

    return {
        **state,
        "raw_articles": state["raw_articles"] + articles
    }

def merge_node(state):
    seen = set()
    unique_articles = []

    for article in state["raw_articles"]:
        if article["url"] not in seen:
            seen.add(article["url"])
            unique_articles.append(article)

    return {
        **state,
        "raw_articles": unique_articles
    }

def filter_node(state):
    filtered = []

    for article in state["raw_articles"]:
        url = article["url"]
        title = article["title"].lower()

        # Remove category / generic pages
        if any(x in url for x in [
            "/tag/",
            "/category/",
            "/topics/",
            "/latest",
        ]):
            continue

        # Remove homepage-like domains (no article slug)
        if url.count("/") < 4:
            continue

        # Remove generic titles
        if any(x in title for x in [
            "latest news",
            "ai news",
            "home",
            "updates"
        ]):
            continue

        # Ensure content exists
        if len(article.get("content", "")) < 80:
            continue

        filtered.append(article)

    return {
        **state,
        "raw_articles": filtered
    }


from langgraph.graph import StateGraph, END
from agents.state import NewsletterState


def build_collector_graph():
    builder = StateGraph(NewsletterState)

    # Add nodes
    builder.add_node("search", search_node)
    builder.add_node("rss", rss_node)
    builder.add_node("merge", merge_node)
    builder.add_node("filter", filter_node)

    # Define flow
    builder.set_entry_point("search")
    builder.add_edge("search", "rss")
    builder.add_edge("rss", "merge")
    builder.add_edge("merge", "filter")
    builder.add_edge("filter", END)

    return builder.compile()