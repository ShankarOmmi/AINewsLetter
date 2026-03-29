from typing import TypedDict, List, Dict, Optional

class NewsletterState(TypedDict):
    topic : str
    raw_articles : List[Dict]
    filtered_articles : List[Dict]
    summaries : List[Dict]
    newsletter_draft : str
    clusters : List[List[Dict]]
    quality_passed : bool
    final_newsletter : str
    error : Optional[str]