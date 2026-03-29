from chains.summariser import summarise_article
from chains.formatter import format_newsletter

from langgraph.graph import StateGraph, END
from agents.state import NewsletterState
from chains.quality_check import check_quality
from chains.narrative import generate_narrative
from chains.relevance import score_article
from chains.category import classify_article
from chains.sentiment import get_article_sentiment
from chains.verifier import verify_summary

from bs4 import BeautifulSoup
import re

import time
import difflib

def find_best_url(title, summary_map):
    titles = list(summary_map.keys())

    # 1. Exact match
    if title in summary_map:
        return summary_map[title]

    # 2. Fuzzy match
    match = difflib.get_close_matches(title, titles, n=1, cutoff=0.5)

    if match:
        return summary_map[match[0]]

    # 3. Partial match fallback
    for t in titles:
        if title.lower() in t.lower() or t.lower() in title.lower():
            return summary_map[t]

    return ""


def clean_content(raw_html):
    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove unwanted tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Optional: limit length (prevents huge prompts)
    return text[:3000]


# -------------------------------
# 1. SUMMARISE NODE
# -------------------------------

def summarise_node(state):
    summaries = []

    for article in state["raw_articles"]:
        try:
            title = article["title"]
            content = article["content"]

            # 🔁 Try max 2 attempts
            for attempt in range(2):

                summary = summarise_article(title, content)

                is_valid = verify_summary(content, summary)

                if is_valid:
                    print(f"✅ Verified (attempt {attempt+1})")
                    break
                else:
                    print(f"⚠️ Hallucination detected. Retrying: {title}")

            summaries.append({
                "title": title,
                "url": article.get("url"),
                "summary": summary,
                "category": article.get("category"),
                "score": article.get("score"),
                "sentiment": article.get("sentiment")
            })

        except Exception as e:
            print(f"Error summarising: {article['title']}")
            continue

    return {
        **state,
        "summaries": summaries
    }


# -------------------------------
# 2. FORMAT NODE (UPDATED)
# -------------------------------
def format_node(state):
    newsletter = format_newsletter(state["summaries"])

    if newsletter is None:
        return {
            **state,
            "error": "Formatter failed",
            "newsletter_draft": None
        }

    summary_map = {
        item["title"]: item.get("url", "")
        for item in state["summaries"]
    }

    for section in newsletter.get("sections", []):
        title = section.get("title", "")
        section["url"] = find_best_url(title, summary_map)

    return {
        **state,
        "newsletter_draft": newsletter
    }

# -------------------------------
# 3. QUALITY NODE
# -------------------------------
def quality_node(state):
    if not state.get("newsletter_draft"):
        return {
            **state,
            "quality_passed": False,
            "quality_reason": "Formatter failed",
            "final_newsletter": None
        }

    result = check_quality(state["newsletter_draft"])

    return {
        **state,
        "quality_passed": result.startswith("APPROVED"),
        "quality_reason": result,
        "final_newsletter": state["newsletter_draft"]
    }


def narrative_node(state):
    summaries = state.get("summaries", [])

    if not summaries:
        return state

    narrative = generate_narrative(summaries)

    newsletter_draft = state.get("newsletter_draft")
    if newsletter_draft is not None:
        newsletter_draft = {
            **newsletter_draft,
            "intro": narrative
        }
    else:
        newsletter_draft = {
            "intro": narrative
        }

    return {
        **state,
        "intro": narrative,  # 🔥 important
        "newsletter_draft": newsletter_draft
    }

def relevance_node(state):
    scored = []

    for article in state["raw_articles"]:
        try:
            score = score_article(article["title"], article["content"])

            if score >= 6:  # 🔥 FILTER THRESHOLD
                scored.append({
                    **article,
                    "score": score
                })

        except Exception as e:
            continue

    if scored:
        # Sort first
        scored = sorted(scored, key=lambda x: x["score"], reverse=True)

        # Assign strict hierarchy
        for i, article in enumerate(scored):
            if i == 0:
                article["score"] = 9   # ONLY ONE top story
            elif i == 1:
                article["score"] = 8
            elif i == 2:
                article["score"] = 7
            else:
                article["score"] = 6

    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    return {
        **state,
        "raw_articles": scored
    }



def categorise_node(state):
    categorized = []

    for article in state["raw_articles"]:
        try:
            category = classify_article(
                article["title"],
                article["content"]
            )

            categorized.append({
                **article,
                "category": category
            })

        except:
            categorized.append({
                **article,
                "category": "Advancements"
            })
    # Ensure top story is Major News
    if categorized:
        top_article = max(categorized, key=lambda x: x["score"])

        for article in categorized:
            if article == top_article:
                article["category"] = "Major News"

    return {
        **state,
        "raw_articles": categorized
    }



def sentiment_node(state):
    summaries = state.get("summaries", [])

    updated = []

    for item in summaries:
        try:
            sentiment = get_article_sentiment(
                item["title"],
                item["summary"]
            )

            item["sentiment"] = sentiment

            updated.append(item)

        except Exception as e:
            item["sentiment"] = "Neutral"
            updated.append(item)

    return {
        **state,
        "summaries": updated
    }

# -------------------------------
# 4. BUILD GRAPH
# -------------------------------
def build_processor_graph():
    builder = StateGraph(NewsletterState)

    # Nodes
    builder.add_node("summarise", summarise_node)
    builder.add_node("format", format_node)
    builder.add_node("quality", quality_node)
    builder.add_node("narrative", narrative_node)
    builder.add_node("relevance", relevance_node)
    builder.add_node("categorise", categorise_node)
    builder.add_node("sentiment", sentiment_node)

    builder.set_entry_point("relevance")

    builder.add_edge("relevance", "categorise")
    builder.add_edge("categorise", "summarise")
    builder.add_edge("summarise", "sentiment")
    builder.add_edge("sentiment", "format")
    builder.add_edge("format", "narrative")
    builder.add_edge("narrative", "quality")
    builder.add_edge("quality", END)

    return builder.compile()