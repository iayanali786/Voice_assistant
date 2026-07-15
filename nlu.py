"""
nlu.py
------
A small, dependency-free intent classifier.

Rather than matching one fixed keyword per command (e.g. only reacting to
the exact phrase "what time is it"), each intent is given a *set* of
keywords. Whichever intent scores the most keyword hits in the sentence
wins. This lets phrasing vary quite a bit ("can you tell me the time",
"what's the time right now", "do you know the time") while still being
simple enough to run instantly with no extra ML libraries.

For a production system you'd swap this scoring function out for
nltk's tokenizer + a proper classifier, or an intent model from
transformers -- the interface below (parse_intent -> intent name) would
stay the same, so the rest of the app wouldn't need to change.
"""

import re

INTENT_KEYWORDS = {
    "greet":         ["hello", "hi", "hey"],
    "time":          ["time", "clock"],
    "date":          ["date", "today", "day"],
    "search":        ["search", "google", "look up", "browse"],
    "email":         ["email", "mail", "send a message"],
    "reminder":      ["remind", "reminder", "alarm", "timer"],
    "weather":       ["weather", "temperature", "forecast", "rain"],
    "add_command":   ["add command", "new command", "teach you"],
    "exit":          ["exit", "quit", "stop", "goodbye", "bye"],
}


def _clean(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return text


def parse_intent(text: str) -> tuple[str, str]:
    """
    Returns a tuple of (intent_name, cleaned_text).
    intent_name is "unknown" if nothing scored above zero, and the
    knowledge-base / QA fallback in features.py takes over from there.
    """
    cleaned = _clean(text)
    scores = {}

    for intent, keywords in INTENT_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in cleaned)
        if hits:
            scores[intent] = hits

    if not scores:
        return "unknown", cleaned

    best_intent = max(scores, key=scores.get)
    return best_intent, cleaned
