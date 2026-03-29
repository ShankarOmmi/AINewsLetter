# 🧠 AI Newsletter Engine — Full Autonomous + Human-in-the-Loop System

---

## 🚀 Overview

This project is a **production-grade AI-powered newsletter system** that automatically collects, processes, verifies, and delivers high-quality AI news — with a **human approval layer** for safety.

It is NOT just an automation script.

It is a **multi-stage AI pipeline system** that combines:

* LLM orchestration
* Data pipelines
* Verification loops
* Email infrastructure
* Scheduling
* API backend
* Database persistence

---

## 🧩 What Makes This Project Special

Unlike basic automation tools, this system includes:

* 🧠 Multi-stage AI reasoning pipeline
* 🛡️ Hallucination detection & retry system
* 📊 Relevance scoring (ranking intelligence)
* 🗂️ Smart categorization (editorial structure)
* 😊 Per-article sentiment analysis
* 🧵 Weekly narrative generation (storytelling layer)
* 👨‍⚖️ Human approval before sending
* 📬 Batch email delivery to subscribers
* 🔄 Scheduled execution (fully autonomous)

👉 This is essentially a **mini AI media product**, not a script.

---

## 🏗️ Complete System Architecture

```
Scheduler (APScheduler)
        ↓
Collector Graph (LangGraph)
        ↓
Processor Graph (LangGraph)
        ↓
Formatter (LLM → JSON → Structured Data)
        ↓
Database (Store Edition)
        ↓
Approval Email (Human-in-the-loop)
        ↓
FastAPI Endpoint (/approve)
        ↓
Batch Email Sender
        ↓
Subscribers
```

---

## 🔄 End-to-End Pipeline Flow

### 1. 📰 Data Collection

* Fetches articles using:

  * Tavily API
  * RSS feeds
* Merges sources
* Removes duplicates

---

### 2. 🧹 Filtering

* Removes:

  * Low-quality articles
  * Category pages
  * Empty content
* Ensures only useful articles proceed

---

### 3. 🧩 Clustering

* Groups similar articles
* Prevents duplicate stories
* Keeps newsletter concise

---

### 4. 📊 Relevance Scoring

Each article gets a score (0–10):

* Importance
* Impact
* Novelty

Used for:

* Sorting
* Prioritization

---

### 5. 🗂️ Categorisation

Each article is classified into:

* **Major News**
* **Advancements**
* **Fun & Interesting**

---

### 6. 🧠 Summarization

* LLM generates structured summaries
* Clean + concise
* Context-aware

---

### 7. 🛡️ Hallucination Guard (CRITICAL)

This is one of the most important features.

For each summary:

* It is **verified against source**
* If incorrect:

  * 🔁 Regenerated
* Stops hallucinated content

---

### 8. 😊 Sentiment Analysis (Per Article)

Each article is labeled:

* Positive
* Neutral
* Risk

Stored inside:

```
section = {
  title,
  summary,
  url,
  category,
  score,
  sentiment
}
```

---

### 9. 🧵 Weekly Narrative

* Generates a high-level story:

  * “What happened this week in AI?”
* Adds editorial intelligence

---

### 10. 🧾 Formatting (LLM → Structured JSON)

* Converts summaries into:

```
{
  subject,
  intro,
  sections,
  closing
}
```

* Then normalized into flat structure

---

### 11. 💾 Save Newsletter

Stored in DB as:

* `pending`
* `approved`
* `rejected`

---

### 12. 📩 Approval Email

Sent to admin with:

* Full newsletter preview
* Approve button
* Reject button

---

### 13. 👨‍⚖️ Human-in-the-Loop

* Prevents bad AI output
* Adds safety layer

---

### 14. 📬 Final Delivery

After approval:

* Sent to all subscribers
* Batched sending (safe)
* Rate-limited

---

## 📁 Complete Project Structure

```
project/
│
├── main.py
├── agents/
│   ├── collector.py
│   ├── processor.py
│   ├── cluster.py
│   └── formatter.py
│
├── chains/
│   ├── narrative.py
│   └── sentiment.py
│
├── api/
│   └── router.py
│
├── db/
│   ├── database.py
│   └── models.py
│
├── emailer/
│   └── send.py
│
├── templates/
│   └── newsletter.html
│
├── utils/
│   └── logger.py
│
└── config.py
```

---

## 📌 File-by-File Explanation

---

### 🧠 `main.py`

**Central orchestration**

Responsibilities:

* Runs full pipeline
* Schedules execution
* Sends approval email
* Saves newsletter
* Renders HTML

Includes:

* APScheduler (cron + interval)
* Email preview generation

---

### 📰 `agents/collector.py`

Handles:

* Fetching articles
* Filtering
* Deduplication

---

### ⚙️ `agents/processor.py`

Core intelligence:

* relevance_node
* categorise_node
* summarise_node
* sentiment_node

Also includes:

* hallucination retry logic

---

### 🧩 `agents/cluster.py`

* Groups similar articles
* Avoids repetition

---

### 🧾 `agents/formatter.py`

* Converts summaries → structured newsletter
* Uses LLM
* Ensures strict JSON
* Normalizes output

---

### 🧠 `chains/narrative.py`

* Generates weekly theme

---

### 😊 `chains/sentiment.py`

* Classifies article tone

---

### 🌐 `api/router.py`

Endpoints:

#### `/subscribe`

Add user

#### `/unsubscribe`

Remove user

#### `/approve`

* Marks edition approved
* Sends newsletter to all users

#### `/reject`

Marks rejected

---

### 🗄️ `db/database.py`

* SQLite connection
* Table creation

---

### 🗄️ `db/models.py`

* Subscriber handling
* Send logging

---

### 📧 `emailer/send.py`

* Sends emails via SMTP / Resend

---

### 🎨 `templates/newsletter.html`

Features:

* Card UI
* Category grouping
* Sentiment badge
* Responsive design

---

### 🧰 `utils/logger.py`

Logs:

* Pipeline stages
* Errors
* Sentiment distribution
* Email sending

---

## ⚡ Features Summary

| Feature                 | Status |
| ----------------------- | ------ |
| Multi-source collection | ✅      |
| Filtering               | ✅      |
| Clustering              | ✅      |
| Scoring                 | ✅      |
| Categorisation          | ✅      |
| Summarization           | ✅      |
| Hallucination guard     | ✅      |
| Sentiment analysis      | ✅      |
| Narrative generation    | ✅      |
| Email rendering         | ✅      |
| Approval system         | ✅      |
| Scheduling              | ✅      |
| Database storage        | ✅      |
| Subscriber system       | ✅      |

---

## 🔐 Safety Systems

* Hallucination detection
* Human approval gate
* Rate-limited sending
* Unsubscribe system

---

## ⏰ Scheduler

Runs automatically:

### Weekly:

```
Monday 7:30 AM
```

### Test mode:

```
Every 2 minutes
```

---

## 🚀 How to Run

```
pip install -r requirements.txt
python main.py
```

---

## 🌍 Deployment Plan

1. Buy domain (GoDaddy safe)
2. Configure DNS
3. Connect with Resend
4. Deploy FastAPI (Railway/Render)
5. Run scheduler

---

## ⚠️ Notes on Domain

* No renewal → domain expires
* No fines
* Email stops working

---

## 📈 Why This Project Matters

This project demonstrates:

* Real AI system design
* LLM orchestration
* Reliability engineering
* Production thinking
* Safety-aware AI usage

---

## 🧠 Final Thought

This is not just a project.

It is a **complete AI product prototype** combining:

* Intelligence
* Automation
* Safety
* Scalability

---

## 👨‍💻 Author

Built using:

* LangGraph
* FastAPI
* Groq LLM
* APScheduler
* SMTP / Resend

---

## ⭐ Support

If you like this project:

* ⭐ Star the repo
* 🔁 Share it
* 🛠️ Build on it

---
