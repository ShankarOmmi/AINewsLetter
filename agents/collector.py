from tavily import TavilyClient
from config import TAVILY_API_KEY
import feedparser

from langgraph.graph import StateGraph, END
from agents.state import NewsletterState
from agents.cluster import cluster_articles, merge_clusters

client = TavilyClient(api_key=TAVILY_API_KEY)


# -------------------------------
# 1. SEARCH NODE
# -------------------------------
def search_node(state):
    topic = state["topic"]

    response = client.search(
        query=topic,
        search_depth="advanced",
        max_results=10
    )

    articles = []

    for r in response["results"]:
        url = r.get("url", "")

        # ✅ Ensure valid URL
        if not url.startswith("http"):
            continue

        articles.append({
            "title": r.get("title", "No title"),
            "url": url,
            "content": r.get("content", "") or ""
        })

    return {**state, "raw_articles": articles}


# -------------------------------
# 2. RSS NODE
# -------------------------------
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

        for entry in feed.entries[:5]:
            url = entry.get("link", "")

            # ✅ Ensure valid URL
            if not url.startswith("http"):
                continue

            articles.append({
                "title": entry.get("title", "No title"),
                "url": url,
                "content": entry.get("summary", "") or ""
            })

    return {
        **state,
        "raw_articles": state["raw_articles"] + articles
    }


# -------------------------------
# 3. MERGE NODE (DEDUP)
# -------------------------------
def merge_node(state):
    seen = set()
    unique_articles = []

    for article in state["raw_articles"]:
        url = article.get("url")

        if not url:
            continue

        if url not in seen:
            seen.add(url)
            unique_articles.append(article)

    return {
        **state,
        "raw_articles": unique_articles
    }


# -------------------------------
# 4. FILTER NODE (IMPROVED)
# -------------------------------
def filter_node(state):
    filtered = []

    for article in state["raw_articles"]:
        url = article.get("url", "")
        title = article.get("title", "").lower()
        content = article.get("content", "")

        # ❌ Skip invalid URL
        if not url.startswith("http"):
            continue

        # ❌ Remove category / aggregator pages
        if any(x in url for x in [
            "/tag/",
            "/category/",
            "/topics/",
            "/topic/",
            "/latest",
            "/section/",
            "artificialintelligence"
        ]):
            continue

        # ❌ Remove shallow URLs
        if url.count("/") < 4:
            continue

        # ❌ Remove generic titles
        if any(x in title for x in [
            "latest news",
            "ai news",
            "artificial intelligence",
            "ai (artificial intelligence)",
            "home",
            "updates"
        ]):
            continue

        # ❌ Remove weak titles
        if len(title.split()) < 4:
            continue

        # ❌ Ensure usable content
        if len(content) < 120:
            continue

        filtered.append({
            "title": article["title"],
            "url": article["url"],
            "content": content
        })

    return {
        **state,
        "raw_articles": filtered
    }


# -------------------------------
# GRAPH
# -------------------------------


def build_collector_graph():
    builder = StateGraph(NewsletterState)

    builder.add_node("search", search_node)
    builder.add_node("rss", rss_node)
    builder.add_node("merge", merge_node)
    builder.add_node("filter", filter_node)
    builder.add_node("cluster", cluster_articles)
    builder.add_node("merge_clusters", merge_clusters)

    builder.set_entry_point("search")

    builder.add_edge("search", "rss")
    builder.add_edge("rss", "merge")
    builder.add_edge("merge", "filter")
    builder.add_edge("filter", "cluster")
    builder.add_edge("cluster", "merge_clusters")

    builder.add_edge("merge_clusters", END)

    return builder.compile()