from agents.collector import build_collector_graph
from agents.processor import (
    summarise_node,
    relevance_node,
    categorise_node,
    sentiment_node   # ✅ NEW
)
from chains.narrative import generate_narrative


def main():
    print("\n🔍 Running pipeline test (with clustering + scoring + sentiment + narrative)...\n")

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
    # 1. RUN COLLECTOR
    # -------------------------------
    collector = build_collector_graph()

    print("📡 Fetching + filtering + clustering articles...\n")
    state = collector.invoke(state)

    # -------------------------------
    # DEBUG: CLUSTER INFO
    # -------------------------------
    clusters = state.get("clusters", [])

    print(f"🧩 Total clusters formed: {len(clusters)}\n")

    for i, cluster in enumerate(clusters, 1):
        print(f"Cluster {i} ({len(cluster)} articles):")
        for art in cluster:
            print(f" - {art['title']}")
        print()

    print(f"📰 Articles AFTER clustering: {len(state['raw_articles'])}\n")

    # -------------------------------
    # 2. RELEVANCE SCORING
    # -------------------------------
    print("📊 Scoring articles...\n")

    state = relevance_node(state)

    print("📊 AFTER SCORING:\n")
    for art in state["raw_articles"]:
        print(f"[{art['score']}] {art['title']}")

    print("\n")

    # -------------------------------
    # 3. CATEGORISATION
    # -------------------------------
    print("🗂️ Categorising articles...\n")

    state = categorise_node(state)

    print("📂 AFTER CATEGORISATION:\n")
    for art in state["raw_articles"]:
        print(f"[{art['score']}] {art['category']} → {art['title']}")

    print("\n")

    # -------------------------------
    # 4. SUMMARIZE
    # -------------------------------
    print("🧠 Generating summaries...\n")

    state = summarise_node(state)
    summaries = state.get("summaries", [])

    print(f"✅ Summaries generated: {len(summaries)}\n")

    # -------------------------------
    # 5. SENTIMENT (🔥 NEW)
    # -------------------------------
    print("💡 Detecting sentiment per article...\n")

    state = sentiment_node(state)
    summaries = state.get("summaries", [])

    print("📊 SENTIMENT RESULTS:\n")
    for item in summaries:
        print(f"[{item['sentiment']}] {item['title']}")

    print("\n")

    # -------------------------------
    # 6. GENERATE NARRATIVE
    # -------------------------------
    print("🧠 Generating weekly narrative...\n")

    narrative = generate_narrative(summaries)

    print("📝 WEEKLY NARRATIVE:\n")
    print(narrative)
    print("\n" + "=" * 80 + "\n")

    # -------------------------------
    # 7. FINAL OUTPUT (WITH SENTIMENT)
    # -------------------------------
    for i, item in enumerate(summaries, 1):
        print("=" * 80)
        print(f"📰 {i}. [{item['sentiment']}] {item['title']}\n")
        print(item["summary"])
        print("\n🔗 Source:", item["url"])
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()