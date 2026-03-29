from chains.summariser import summarise_article
from chains.formatter import format_newsletter

from langgraph.graph import StateGraph, END
from agents.state import NewsletterState
from chains.quality_check import check_quality

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
            cleaned_content = clean_content(article.get("content", ""))

            # Skip useless content
            if len(cleaned_content) < 50:
                continue

            summary = summarise_article(
                article.get("title", ""),
                cleaned_content
            )

            summaries.append({
                "title": article.get("title", "No title"),
                "url": article.get("url", ""),
                "summary": summary
            })

            time.sleep(1)

        except Exception as e:
            print(f"Error summarising: {article.get('title')}")
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



# -------------------------------
# 4. BUILD GRAPH
# -------------------------------
def build_processor_graph():
    builder = StateGraph(NewsletterState)

    # Nodes
    builder.add_node("summarise", summarise_node)
    builder.add_node("format", format_node)
    builder.add_node("quality", quality_node)

    # Flow
    builder.set_entry_point("summarise")

    builder.add_edge("summarise", "format")
    builder.add_edge("format", "quality")
    builder.add_edge("quality", END)

    return builder.compile()