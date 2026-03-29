from chains.summariser import summarise_article
from chains.formatter import format_newsletter

from langgraph.graph import StateGraph, END
from agents.state import NewsletterState
from chains.quality_check import check_quality

import time


# -------------------------------
# 1. SUMMARISE NODE
# -------------------------------
def summarise_node(state):
    summaries = []

    for article in state["raw_articles"]:
        try:
            summary = summarise_article(
                article["title"],
                article["content"]
            )

            summaries.append({
                "title": article.get("title", "No title"),
                "url": article.get("url", ""),   # ✅ SAFE URL
                "summary": summary
            })

            time.sleep(1)  # avoid rate limits

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

    # ✅ ENSURE URL IS PRESERVED
    # Sometimes LLM drops it → we reattach manually
    for i, section in enumerate(newsletter.get("sections", [])):
        if "url" not in section or not section["url"]:
            if i < len(state["summaries"]):
                section["url"] = state["summaries"][i].get("url", "")

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