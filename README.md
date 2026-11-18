# WanderAI: AI Agent for Tourism Guide and Trip Planner
TY Group TYAIEC124, MIT School of Computing, Pune.

## Architecture
Browser UI -> FastAPI (`app/main.py`) -> Agent modules:
- `rag.py`     TF-IDF retrieval over attractions and tips (RAG knowledge base, JSON data)
- `planner.py` ranks attractions by interests, packs them into days (7 h/day), groups by area, estimates budget
- `weather.py` live forecast from Open-Meteo (no key); skipped gracefully if offline
- `llm.py`     optional LLM answers grounded in retrieved context; extractive fallback without a key
- `chat.py`    question -> detect destination -> retrieve -> answer

## Run
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload
Open http://127.0.0.1:8000 (API docs at /docs).

Optional LLM answers: set `ANTHROPIC_API_KEY` (and `WANDERAI_MODEL` to override the model name).

## Test
    python -m unittest discover -s tests -v

## Extend (future scope from synopsis)
Add destinations in `app/data/destinations.json`; swap TF-IDF for embeddings + FAISS/ChromaDB in `rag.py`; add Google Maps/OSM routing in `planner.py`.
