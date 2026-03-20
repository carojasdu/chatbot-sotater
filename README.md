# chatbot-sotater

**State-of-the-art-er** (Sotater for friends) is an agentic research assistant that helps you explore any topic in depth. You ask a question — it searches the web, downloads and indexes relevant sources into a local vector database, and answers using the content it collected. Ask follow-up questions and it builds on what it already knows.

---

## What it does

1. You ask: *"What are the latest advances in protein folding prediction?"*
2. The agent searches the web via Tavily and finds relevant articles and papers
3. It downloads each source, extracts the text, and indexes it into a per-project ChromaDB vector store
4. It retrieves the most relevant chunks and synthesizes a cited answer
5. Your next question queries the knowledge base first — no redundant searches

All indexed documents are saved locally as `.md` files with the original source URL embedded, so you can always trace content back to its origin.

---

## Features

- **Agentic workflow** — A LangGraph ReAct agent autonomously decides when to search, scrape, or query the knowledge base
- **RAG pipeline** — Local embeddings (sentence-transformers) + ChromaDB for fast, persistent retrieval
- **Project-based organization** — Each research project has its own document folder and vector store; switch between projects from the sidebar
- **Persistent knowledge base** — Indexed documents survive across sessions; the more you use a project, the richer its knowledge base gets
- **Document management** — Browse all indexed documents with source URLs, download dates, and chunk counts; delete any document and it's removed from the vector index too
- **Source attribution** — Every answer cites the original URLs

---

## Architecture

```
chatbot-sotater/
├── app.py                  Streamlit entry point
│
├── agent/
│   ├── graph.py            LangGraph ReAct agent (create_react_agent + system prompt)
│   ├── tools.py            Three tools: web_search, scrape_and_index, rag_query
│   └── state.py            AgentState TypedDict (messages + project_name)
│
├── rag/
│   ├── chunking.py         RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
│   ├── embeddings.py       sentence-transformers/all-MiniLM-L6-v2 (local, cached)
│   └── vectorstore.py      ChromaDB per-project: add, query, delete
│
├── scraper/
│   └── extract.py          Fetch URL → BeautifulSoup → save as .md with frontmatter
│
├── projects/
│   └── manager.py          Create/list/delete projects; document registry CRUD
│
├── ui/
│   ├── sidebar.py          Project selector, create-project form, document count
│   ├── chat.py             Chat interface wired to the agent, live tool-use display
│   └── documents.py        Document browser with delete functionality
│
└── data/                   Runtime data (gitignored)
    └── projects/
        └── <project-name>/
            ├── metadata.json       Project name, creation date, description
            ├── doc_registry.json   Index of all downloaded documents with source URLs
            ├── documents/          Raw .md files (one per indexed source)
            └── chroma_db/          ChromaDB persistent vector store
```

### Agent flow

```
User message
     │
     ▼
  [agent] ──── has tool calls? ──── yes ──── [tools] ────┐
     │                                                     │
     no                                                    │
     │                                                     └──► back to [agent]
     ▼
Final response
```

The agent uses Claude as the backbone LLM. On each turn it decides whether to call a tool or respond. Tool results feed back into the next agent step, enabling multi-step reasoning (e.g. search → pick best result → scrape it → answer).

### The three tools

| Tool | What it does |
|------|-------------|
| `web_search(query)` | Calls Tavily, returns top 5 results with title, URL, and snippet |
| `scrape_and_index(url, project_name)` | Downloads the page, strips boilerplate with BeautifulSoup, saves as `.md`, chunks it, embeds it, and stores it in ChromaDB |
| `rag_query(question, project_name)` | Runs cosine similarity search (k=5) against the project's ChromaDB collection, returns chunks with source URLs |

### RAG pipeline details

- **Chunking:** `RecursiveCharacterTextSplitter` — chunk size 1000 characters, overlap 200, splitting on paragraph → line → sentence → word boundaries in that order
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` — 80MB model, runs locally, no API call required. Loaded once and cached for the session.
- **Vector store:** ChromaDB with cosine distance. Each project has a completely isolated collection stored at `data/projects/<name>/chroma_db/`
- **Metadata per chunk:** `source_url`, `document_id`, `chunk_index` — used for attribution and for targeted deletion when a document is removed

---

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- An [Anthropic API key](https://console.anthropic.com/)
- A [Tavily API key](https://tavily.com/) (free tier: 1000 searches/month)

### Install

```bash
git clone git@github.com:carojasdu/chatbot-sotater.git
cd chatbot-sotater
uv sync
```

### Configure

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

```
ANTHROPIC_API_KEY=your-anthropic-key
TAVILY_API_KEY=your-tavily-key
```

### Run

```bash
uv run streamlit run app.py
```

---

## Running tests

```bash
uv sync --extra dev
uv run pytest -v
```

Tests cover: project management (create, list, delete, registry CRUD), web content extraction (mocked HTTP), and text chunking behavior.
