from agents.collector import build_collector_graph
from agents.processor import (
    summarise_node,
    relevance_node,
    categorise_node,
    sentiment_node
)
from chains.narrative import generate_narrative


def main():
    print("\n🔍 Running pipeline test (FULL AI SYSTEM)...\n")

    # -------------------------------
    # INITIAL STATE
    # -------------------------------
    state = {
        "topic": "latest AI news",
        "raw_articles": [],
        "filtered_articles": [],
        "clusters": [],
        "summaries": [],
        "newsletter_draft": None,
        "quality_passed": False,
        "final_newsletter": None,
        "error": None
    }

    # -------------------------------
    # 1. COLLECT
    # -------------------------------
    collector = build_collector_graph()

    print("📡 Fetching + filtering + clustering articles...\n")
    state = collector.invoke(state)

    print(f"📰 Articles AFTER clustering: {len(state['raw_articles'])}\n")

    # -------------------------------
    # 2. RELEVANCE
    # -------------------------------
    print("📊 Scoring articles...\n")
    state = relevance_node(state)

    for art in state["raw_articles"]:
        print(f"[{art['score']}] {art['title']}")
    print()

    # -------------------------------
    # 3. CATEGORY
    # -------------------------------
    print("🗂️ Categorising articles...\n")
    state = categorise_node(state)

    for art in state["raw_articles"]:
        print(f"[{art['score']}] {art['category']} → {art['title']}")
    print()

    # -------------------------------
    # 4. SUMMARISE + VERIFY 🔥
    # -------------------------------
    print("\n🧠 Generating + VERIFYING summaries...\n")

    state = summarise_node(state)
    summaries = state.get("summaries", [])

    print(f"\n✅ Final summaries count: {len(summaries)}\n")

    # -------------------------------
    # 5. SENTIMENT
    # -------------------------------
    print("💡 Detecting sentiment...\n")

    state = sentiment_node(state)
    summaries = state.get("summaries", [])

    for item in summaries:
        print(f"[{item['sentiment']}] {item['title']}")
    print()

    # -------------------------------
    # 6. NARRATIVE
    # -------------------------------
    print("🧠 Generating weekly narrative...\n")

    narrative = generate_narrative(summaries)

    print("📝 WEEKLY NARRATIVE:\n")
    print(narrative)
    print("\n" + "=" * 80 + "\n")

    # -------------------------------
    # 7. FINAL OUTPUT
    # -------------------------------
    for i, item in enumerate(summaries, 1):
        print("=" * 80)
        print(f"📰 {i}. [{item['sentiment']}] {item['title']}\n")
        print(item["summary"])
        print("\n🔗 Source:", item["url"])
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()