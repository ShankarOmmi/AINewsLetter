# AI Newsletter Agent

An autonomous, multi-agent AI system that collects, filters, scores, summarises, and delivers a weekly AI newsletter — fully hands-off, with a human-in-the-loop approval step before sending.

Built with **LangGraph**, **LangChain**, **FastAPI**, **Groq (Llama 3)**, **Tavily**, and **Resend**.

---

## What this project does

Every Monday at 8 AM, the system wakes up on its own and runs a complete editorial pipeline:

1. Searches the web and parses RSS feeds to collect fresh AI news articles
2. Deduplicates them by URL, then clusters semantically identical stories using an LLM
3. Scores every article for relevance using a Groq-powered chain
4. Classifies each article into one of three editorial categories
5. Summarises every article in a structured two-paragraph format
6. Verifies each summary against its source to catch hallucinations
7. Classifies the sentiment of each article as Positive, Negative, or Neutral
8. Generates a weekly narrative that connects all stories into a single insight
9. Formats everything into a structured newsletter and runs a quality check
10. Saves the edition to the database and emails a preview to the editor with Approve / Reject buttons
11. On approval, sends the newsletter to all active subscribers in rate-limited batches with personalised unsubscribe links

No human needs to write, curate, or format anything. The only human decision is whether to press Approve.

---

## Architecture overview

The system is built around two separate **LangGraph state graphs** that run in sequence:

```
Collector Graph → Processor Graph → FastAPI delivery layer
```

### Collector Graph

```
search_node → rss_node → merge_node → filter_node → cluster_articles → merge_clusters
```

- Fetches articles from Tavily search API and four RSS feeds in sequence
- Merges all results into a single list and deduplicates by URL
- Filters out aggregator pages, shallow URLs, weak titles, and thin content
- Uses an LLM to detect whether pairs of articles describe the same event, groups them into clusters, and merges each cluster into one representative article with combined content

### Processor Graph

```
relevance_node → categorise_node → summarise_node → sentiment_node → format_node → narrative_node → quality_node
```

- Scores every article for real-world relevance (1–10) and drops anything below 6
- Classifies each article into Major News, Advancements, or Fun & Interesting — and forces the highest-scored article to be Major News
- Summarises each article using a structured prompt with verification retry logic
- Classifies the sentiment of each summary as Positive, Negative, or Neutral
- Formats all summaries into a JSON newsletter structure with subject, intro, sections, and closing
- Generates a two-sentence narrative that finds the connecting thread across all stories
- Runs a final quality check and flags any issues

---

## Tech stack

| Component | Technology |
|---|---|
| Agent orchestration | LangGraph |
| LLM chains | LangChain + Groq (Llama 3.1 8B Instant) |
| Web search | Tavily API |
| RSS parsing | feedparser |
| HTML content cleaning | BeautifulSoup4 |
| API server | FastAPI |
| Database | SQLite (via sqlite3) |
| Email sending | Resend API |
| Email templating | Jinja2 |
| Scheduling | APScheduler |
| Logging | Python logging module |
| Config management | python-dotenv |

---

## Project structure

```
newsletter-agent/
├── agents/
│   ├── state.py          ← Shared TypedDict state schema for all graph nodes
│   ├── collector.py      ← Collector LangGraph: search + RSS + dedup + filter + cluster
│   ├── cluster.py        ← LLM-based semantic duplicate detection and cluster merging
│   └── processor.py      ← Processor LangGraph: relevance + category + summarise + sentiment + format + narrative + quality
│
├── chains/
│   ├── relevance.py      ← Scores articles 1–10 for real-world impact and recency
│   ├── category.py       ← Classifies articles into Major News / Advancements / Fun & Interesting
│   ├── summariser.py     ← Generates structured two-paragraph summaries with style rules
│   ├── verifier.py       ← Fact-checks summaries against source content (hallucination guard)
│   ├── sentiment.py      ← Classifies article sentiment as Positive / Negative / Neutral
│   ├── narrative.py      ← Generates a weekly connecting insight across all stories
│   ├── formatter.py      ← Structures all summaries into a JSON newsletter with retry logic
│   └── quality_check.py  ← Reviews the full newsletter for tone, clarity, and consistency
│
├── api/
│   ├── router.py         ← FastAPI routes: /subscribe, /unsubscribe, /approve, /reject
│   └── schemas.py        ← Pydantic request models with email validation
│
├── db/
│   ├── database.py       ← SQLite connection factory and table creation
│   └── models.py         ← CRUD operations for subscribers, editions, and send logs
│
├── emailer/
│   └── send.py           ← Resend API wrapper with error handling and logging
│
├── templates/
│   └── newsletter.html   ← Jinja2 email template with sentiment badges, category sections, and unsubscribe links
│
├── static/
│   └── signup.html       ← Public subscriber signup page
│
├── utils/
│   └── logger.py         ← Structured logger writing to both console and logs/app.log
│
├── config.py             ← Environment variable loading via dotenv
└── main.py               ← FastAPI app, scheduler, render/save/approve flow
```

---

## File-by-file breakdown

### `agents/state.py`

Defines the `NewsletterState` TypedDict — the single shared data structure that every LangGraph node reads from and writes to. Fields include `topic`, `raw_articles`, `filtered_articles`, `summaries`, `newsletter_draft`, `clusters`, `quality_passed`, `final_newsletter`, and `error`. Every node receives the full state and returns an updated copy, which is how LangGraph manages stateful pipelines without global variables.

### `agents/collector.py`

Builds and compiles the collector LangGraph graph. Contains four node functions:

- `search_node` — calls the Tavily API with `search_depth="advanced"` and collects up to 10 results, validating that each has a real HTTP URL and content
- `rss_node` — parses four RSS feeds (TechCrunch AI, The Guardian AI, Wired AI, MIT News AI) using feedparser, collecting the 5 most recent entries from each
- `merge_node` — deduplicates the combined article list using a URL-based seen-set
- `filter_node` — applies a multi-rule filter removing aggregator pages (URLs containing `/tag/`, `/category/`, `/topics/`), shallow URLs (fewer than 4 slashes), generic titles, very short titles (under 4 words), and articles with less than 120 characters of content

The graph runs all four nodes in sequence before handing off to the cluster nodes.

### `agents/cluster.py`

Contains the LLM-powered semantic clustering logic, which solves a problem URL deduplication cannot: multiple outlets covering the same story with different URLs.

- `is_same_story(title1, title2)` — calls Groq with a binary YES/NO prompt to determine whether two article titles refer to the exact same event, not just the same topic
- `cluster_articles(state)` — iterates through all articles and builds clusters by comparing each article against the first article in each existing cluster using `is_same_story`
- `merge_clusters(state)` — flattens each cluster into a single article, keeping the first title and URL as the representative and concatenating all content with double newlines for richer summarisation context

### `agents/processor.py`

Builds and compiles the processor LangGraph graph. Contains seven node functions:

- `relevance_node` — calls `score_article` for each article, drops anything scoring below 6, then reassigns scores in a strict hierarchy: rank 1 gets 9, rank 2 gets 8, rank 3 gets 7, everything else gets 6. This ensures a clear editorial hierarchy.
- `categorise_node` — calls `classify_article` for each article, then overrides: the article with the highest score is always forced to Major News regardless of the LLM's classification
- `summarise_node` — calls `summarise_article` for each article, then immediately calls `verify_summary` to check for hallucinations. Retries once if the first summary fails verification.
- `sentiment_node` — calls `get_article_sentiment` on the title and generated summary of each article, defaulting to Neutral on failure
- `format_node` — calls `format_newsletter` and then uses `find_best_url` to re-attach source URLs to each article in the formatted output using exact match, fuzzy match, and partial match fallback
- `narrative_node` — calls `generate_narrative` with all summaries and stores the result as the newsletter intro
- `quality_node` — calls `check_quality` on the full newsletter draft and stores the pass/fail result and reason

Also contains `clean_content` which strips HTML tags, navigation, footer, and script elements from raw scraped content before passing it to any LLM chain.

### `chains/relevance.py`

Prompts Groq to score an article from 1 to 10 based on real-world impact. The prompt explicitly instructs the model to score 9 only for confirmed events like user growth or major product launches, 7–8 for important but not dominant news, 5–6 for background analysis and trends, and 1–4 for low-signal content. Falls back to 5 if the model returns a non-integer response.

### `chains/category.py`

Classifies each article into one of three categories: Major News (reserved for high-impact industry events), Advancements (technical progress, new models, research), or Fun & Interesting (studies, insights, lighter reads). Passes the first 1500 characters of content to keep prompt size manageable.

### `chains/summariser.py`

The most carefully prompted chain in the system. Instructs Groq to write exactly two paragraphs: the first (2–3 sentences) explaining what happened with key facts, the second (1–2 sentences) explaining why it matters analytically. Style rules prohibit repeating opening phrases across summaries, ban generic filler phrases, and require varied analytical language ("This signals...", "This reflects...", etc.). Total length is constrained to 70–110 words. Uses `temperature=0.3` for controlled but not entirely deterministic output.

### `chains/verifier.py`

A dedicated hallucination guard. Takes the original article content and the generated summary, then asks Groq to check whether every factual claim in the summary is supported by the source. Responds with a single word: PASS or FAIL. If the result contains "PASS" the summary is accepted; otherwise the summarise node retries. This is one of the most production-relevant features in the codebase — it addresses a known LLM reliability problem with a concrete automated solution.

### `chains/sentiment.py`

Classifies each article's sentiment using a carefully structured prompt with a single decision-rule at the top: "Has something good or bad ALREADY HAPPENED and been CONFIRMED?" Positive requires a confirmed beneficial outcome. Negative requires confirmed harm that has occurred. Neutral covers predictions, forecasts, trend analysis, and opinions. The chain uses chain-of-thought reasoning (asking the model to reason through four steps) before producing the label. The label is extracted from the response and used to render a colour-coded badge in the email template.

### `chains/narrative.py`

Generates a two-sentence connecting narrative across all articles — the editorial voice of the newsletter. The prompt instructs the model to find a contrast, shift, or tension that connects the week's stories (e.g., capability vs control, growth vs risk, adoption vs trust) rather than simply listing what happened. It explicitly prohibits corporate and generic phrases and provides a worked example of a high-quality output.

### `chains/formatter.py`

Calls Groq to organise all summaries into a structured JSON newsletter with three sections (Major News, Advancements, Fun & Interesting), a subject line, intro paragraph, and closing. Retries up to 10 times on JSON parse failure, stripping markdown code fences between attempts. The `normalize_newsletter` function then re-enriches the LLM's output with URL, score, and sentiment fields by looking up each article title in the original summaries dictionary.

### `chains/quality_check.py`

Reviews the full newsletter for engaging intro, clear and factual summaries, consistent tone, and absence of repetition. Returns either "APPROVED" or "REJECTED: <reason>". The result is stored in the state but does not currently block sending — it serves as a diagnostic and logging signal.

### `api/router.py`

Four FastAPI endpoints:

- `POST /subscribe` — validates the email with Pydantic's `EmailStr`, checks for duplicates, creates a UUID unsubscribe token, and saves the subscriber. Returns a clear message for duplicates rather than an error.
- `GET /unsubscribe?token=<uuid>` — looks up the token and sets subscriber status to "unsubscribed" without deleting the record
- `GET /approve?id=<edition_id>` — fetches the pending edition from the database, parses its JSON content, marks it approved, fetches all active subscribers, renders the HTML email with a per-subscriber unsubscribe URL, sends in batches of 10 with a 2-second delay between batches, and logs the result to the sends table. Returns success/fail counts.
- `GET /reject?id=<edition_id>` — marks the edition as rejected in the database

### `api/schemas.py`

Defines `SubscribeRequest` as a Pydantic BaseModel with a single `EmailStr` field. Pydantic validates email format automatically before the endpoint logic runs, returning a 422 error for malformed addresses.

### `db/database.py`

Manages the SQLite connection. `get_connection()` returns a connection with `row_factory = sqlite3.Row` set, which allows accessing row columns by name rather than index. `create_tables()` creates three tables on startup if they do not exist: `subscribers`, `sends`, and `editions`.

### `db/models.py`

CRUD layer for all three tables:

- `add_subscriber(email)` — inserts with a generated UUID token, returns success/error dict
- `unsubscribe(token)` — updates status, returns True if a row was affected
- `get_active_subscribers()` — returns all active subscriber emails and tokens
- `log_send(edition_id, subject, total, status)` — records every send event with outcome

### `emailer/send.py`

Thin wrapper around the Resend SDK. Sends HTML emails from the configured sender address, logs success and failure per recipient, and returns None on failure (allowing the batch loop in the router to continue rather than crash).

### `templates/newsletter.html`

Jinja2 email template rendered server-side before sending. Key features:

- Rotating header colour based on edition number (cycles through 4 colours)
- Edition number and formatted date in the header
- Dynamic intro paragraph (generated by the narrative chain)
- Category sections rendered from `grouped_sections` dict — each category heading appears once regardless of how many articles it contains
- Per-article sentiment badge: green pill for Positive, red pill for Negative, grey pill for Neutral
- "Read more →" link rendered conditionally only when a URL is present
- Personalised unsubscribe link in the footer using the subscriber's unique token

### `static/signup.html`

A minimal single-page subscriber signup form. On submit, it POSTs the email to `/subscribe` via a fetch call and displays the server's response message. No frameworks, no dependencies — pure HTML, CSS, and vanilla JavaScript.

### `utils/logger.py`

Configures a named logger (`newsletter`) that writes to both the console and `logs/app.log` simultaneously. Creates the logs directory if it does not exist. Uses a guard against duplicate handlers so the logger can be safely imported from multiple modules. Format: `timestamp | level | message`.

### `config.py`

Loads `TAVILY_API_KEY`, `GROQ_API_KEY`, and `RESEND_API_KEY` from a `.env` file using python-dotenv. All other modules import keys from here — no key is hardcoded anywhere in the chain or agent files.

### `main.py`

The application entry point. Responsibilities:

- `render_email(newsletter, edition_number, unsubscribe_url)` — loads the Jinja2 template, groups sections by category using `defaultdict`, selects a header colour by rotating through 4 options, and renders the full HTML string
- `save_edition(newsletter)` — serialises the newsletter dict to JSON and inserts it into the editions table with status "pending", returning the auto-incremented edition ID
- `send_approval_email(newsletter, edition_id)` — renders the newsletter HTML, prepends an approval UI with green Approve and red Reject buttons linking to `/approve?id=` and `/reject?id=`, and emails it to the editor
- `run_newsletter_job()` — the full pipeline: initialise state → run collector graph → run processor graph → log sentiment distribution → save edition → write preview HTML → send approval email
- `lifespan` — FastAPI lifespan context manager that creates tables on startup, starts APScheduler with a weekly Monday 8 AM cron job, and shuts down cleanly on exit
- The FastAPI app mounts the router and serves `signup.html` at `/`

---

## Database schema

### `subscribers`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Auto-incremented identifier |
| email | TEXT UNIQUE | Subscriber email address |
| status | TEXT | `active` or `unsubscribed` |
| subscribed_at | TIMESTAMP | Subscription datetime |
| unsubscribe_token | TEXT UNIQUE | UUID used in unsubscribe links |

### `editions`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Edition number |
| subject | TEXT | Newsletter subject line |
| content | TEXT | Full newsletter JSON |
| status | TEXT | `pending`, `approved`, or `rejected` |
| created_at | TIMESTAMP | Generation datetime |

### `sends`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Send record identifier |
| edition_number | INTEGER | Foreign reference to editions.id |
| subject | TEXT | Subject line at time of send |
| sent_at | TIMESTAMP | Send datetime |
| total_recipients | INTEGER | Number of active subscribers at send time |
| status | TEXT | `success`, `partial`, or `fail` |

---

## Intelligence features

This project goes beyond basic automation through multiple AI-powered decision layers:

**Semantic duplicate clustering** — Instead of deduplicating only by URL, the system uses an LLM to compare article titles and detect whether different URLs describe the same event. Duplicate stories are merged into one, combining content from multiple sources for richer summarisation.

**Relevance scoring with editorial hierarchy** — Every article receives a 1–10 relevance score from a Groq chain before it enters the summarisation pipeline. Articles scoring below 6 are dropped. The remaining articles are reassigned to a strict score hierarchy (9, 8, 7, 6) to ensure a clear narrative order.

**Forced top story selection** — The highest-scored article is always promoted to Major News regardless of the category chain's decision. This ensures the most important story always leads.

**Hallucination verification** — After every summary is generated, a second LLM call checks whether the summary's factual claims are supported by the original article. If the check fails, summarisation retries once. This directly addresses one of the most common reliability problems in LLM-based content pipelines.

**Sentiment classification with chain-of-thought reasoning** — Each article is classified as Positive, Negative, or Neutral using a structured prompt with a primary decision rule (has this already happened and been confirmed?) and four explicit reasoning steps. The label drives colour-coded badges in the email.

**Narrative generation** — Rather than providing a generic intro, a dedicated chain reads all article summaries and finds the connecting thread — a contrast, tension, or shift — and writes it as an editorial insight. This gives the newsletter a voice rather than a list.

**Quality gating** — A final review chain evaluates the complete newsletter for tone consistency, summary quality, and repetition before it is sent to the editor for approval.

**Human-in-the-loop approval** — The newsletter is never sent automatically. The system emails a full preview to the editor with Approve and Reject buttons. Only after explicit approval does it send to subscribers. This is the correct architecture for any AI system that produces public-facing content.

---

## Setup and installation

### Prerequisites

- Python 3.10+
- A Groq account (free) — [console.groq.com](https://console.groq.com)
- A Tavily account (free tier) — [tavily.com](https://tavily.com)
- A Resend account (free tier) — [resend.com](https://resend.com)

### Installation

```bash
git clone https://github.com/yourusername/newsletter-agent.git
cd newsletter-agent
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
RESEND_API_KEY=your_resend_api_key
```

### Running locally

```bash
uvicorn main:app --reload
```

The application will:
- Create the SQLite database and tables on startup
- Serve the signup page at `http://localhost:8000`
- Start the weekly scheduler

To trigger the newsletter pipeline immediately without waiting for Monday, call `run_newsletter_job()` directly via `python main.py`.

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the subscriber signup page |
| POST | `/subscribe` | Adds a new subscriber |
| GET | `/unsubscribe?token=<uuid>` | Unsubscribes a user by token |
| GET | `/approve?id=<edition_id>` | Approves and sends an edition |
| GET | `/reject?id=<edition_id>` | Rejects an edition |

---

## Requirements

```
fastapi
uvicorn
python-dotenv
pydantic[email]
langchain-core
langchain-groq
langgraph
tavily-python
feedparser
requests
beautifulsoup4
jinja2
resend
apscheduler
```

---

## Known limitations

- The quality gate records pass/fail but does not currently block sending on failure — rejection is handled only by the human reviewer
- The system currently searches a single fixed topic ("latest AI news") — topic configuration requires a code change rather than a config value
- SQLite is suitable for development and low-scale production; a Postgres database would be needed for scale beyond a few thousand subscribers

---

## Deployment

The project is designed for deployment on [Railway](https://railway.app). Set all environment variables in the Railway dashboard, point the start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`, and update `BASE_URL` in `api/router.py` to your Railway domain before deploying.

---

## License

MIT
