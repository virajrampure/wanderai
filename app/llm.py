"""Optional LLM layer. Uses the Anthropic API if ANTHROPIC_API_KEY is set, else an extractive fallback."""
import os
import requests

SYSTEM = ("You are WanderAI, a friendly tourism guide for India. Answer ONLY using the provided context. "
          "If the context is insufficient, say so briefly. Keep answers under 120 words.")


def answer(question, context_snippets):
    key = os.getenv("ANTHROPIC_API_KEY")
    if key and context_snippets:
        try:
            r = requests.post("https://api.anthropic.com/v1/messages", timeout=30, headers={
                "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
                json={"model": os.getenv("WANDERAI_MODEL", "claude-sonnet-4-5"), "max_tokens": 400,
                      "system": SYSTEM, "messages": [{"role": "user", "content":
                      "Context:\n- " + "\n- ".join(context_snippets) + f"\n\nQuestion: {question}"}]})
            r.raise_for_status()
            return r.json()["content"][0]["text"], "llm"
        except Exception:
            pass  # fall through to extractive answer
    if not context_snippets:
        return "I don't have information on that yet. Try asking about Goa, Jaipur, Manali, Kerala, Varanasi, Udaipur, Pune or Hampi.", "fallback"
    return "Here is what I found:\n- " + "\n- ".join(context_snippets[:3]), "extractive"
