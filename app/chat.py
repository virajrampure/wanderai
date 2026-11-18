from .rag import KnowledgeBase
from . import llm


def chat(kb: KnowledgeBase, question, destination=None):
    dest = destination or kb.detect_destination(question)
    hits = [(s, d) for s, d in kb.search(question, dest=dest, k=4) if s > 0.05]
    snippets = [(d["item"] if d["kind"] == "tip" else f'{d["item"]["name"]} ({d["item"]["area"]}): {d["item"]["desc"]}')
                for _, d in hits]
    text, mode = llm.answer(question, snippets)
    return {"answer": text, "destination": dest, "mode": mode, "sources": snippets}
