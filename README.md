```
newsletter-agent/
├── main.py                  ← entry point, scheduler lives here
├── config.py                ← all API keys loaded from .env
├── .env                     ← your secrets (never commit this)
│
├── agents/
│   ├── collector.py         ← LangGraph graph for data collection
│   ├── processor.py         ← LangGraph graph for LLM processing
│   └── state.py             ← shared TypedDict state schema
│
├── chains/
│   ├── summariser.py        ← LangChain chain: raw text → summary
│   ├── formatter.py         ← LangChain chain: summaries newsletter draft
│   └── quality_check.py    ← LangChain chain: self-critique + rewrite
│
├── db/
│   ├── database.py          ← SQLite connection + table setup
│   └── models.py            ← Subscriber, Edition, Send models
│
├── api/
│   ├── router.py            ← FastAPI routes
│   └── schemas.py           ← Pydantic models for request/response
│
├── templates/
│   └── newsletter.html      ← Jinja2 email HTML template
│
├── static/
│   └── signup.html          ← the public signup page
│
└── requirements.txt
```
