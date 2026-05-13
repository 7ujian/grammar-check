#!/usr/bin/env python3
"""Check English via Claude API and inject grammar corrections as additionalContext.

Supports modes: off, basic, conversational, formal, standard (default).
Mode is read from ~/.grammar-check-mode (set by /grammar-check slash command).
"""

import sys
import json
import os
import urllib.request
import urllib.error

MIN_WORDS = 3
TIMEOUT = 15
STATE_FILE = os.path.expanduser("~/.grammar-check-mode")

BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
API_KEY = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
MODEL = os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL", "claude-haiku-4-5-20251001")

MODE_LABELS = {
    "basic": "Basic",
    "conversational": "Conversational",
    "formal": "Formal",
}

SYSTEM_PROMPTS = {
    "basic": (
        "Check the following text ONLY for spelling mistakes and grammar errors. "
        "Do NOT comment on style, word choice, tone, or phrasing.\n\n"
        "For each issue, output one line in this exact format:\n"
        '- TYPE: "original text" → "correction" (brief reason)\n\n'
        "If no issues are found, output exactly: No issues."
    ),
    "conversational": (
        "Check the following text for spelling/grammar errors AND unnatural or "
        "awkward phrasing. Suggest more natural, colloquial, native-sounding alternatives.\n\n"
        "For each issue, output one line in this exact format:\n"
        '- TYPE: "original text" → "correction" (brief reason)\n\n'
        "If no issues are found, output exactly: No issues."
    ),
    "formal": (
        "Check the following text strictly for: spelling/grammar errors, informal "
        "language, slang, contractions, casual expressions, wordiness, weak phrasing, "
        "passive voice overuse. Suggest polished, professional, academic alternatives.\n\n"
        "For each issue, output one line in this exact format:\n"
        '- TYPE: "original text" → "correction" (brief reason)\n\n'
        "If no issues are found, output exactly: No issues."
    ),
    "standard": (
        "Check the following text for spelling/grammar errors and style issues "
        "(wordiness, awkward phrasing, unclear expression).\n\n"
        "For each issue, output one line in this exact format:\n"
        '- TYPE: "original text" → "correction" (brief reason)\n\n'
        "If no issues are found, output exactly: No issues."
    ),
}

TONE_INSTRUCTIONS = {
    "standard": (
        "concisely point out 2-3 of the most important corrections above. "
        "Be friendly and brief — one or two lines max."
    ),
    "basic": (
        "concisely point out 2-3 grammar or spelling errors above. "
        "Be brief and direct."
    ),
    "conversational": (
        "concisely point out 2-3 corrections above, and suggest a more natural, "
        "colloquial way to express the idea. Sound like a native speaker giving friendly advice."
    ),
    "formal": (
        "concisely point out 2-3 corrections above, and suggest a more polished, "
        "formal way to express the idea. Focus on professional or academic tone."
    ),
}


def read_mode() -> str:
    try:
        with open(STATE_FILE) as f:
            data = json.load(f)
            return data.get("mode", "standard")
    except Exception:
        return "standard"


def check_grammar(text: str, mode: str) -> str | None:
    """Call Claude API to grammar-check the text. Returns the response text or None."""
    system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["standard"])

    body = {
        "model": MODEL,
        "max_tokens": 600,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": text}
        ],
    }

    req = urllib.request.Request(
        f"{BASE_URL}/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            for block in result.get("content", []):
                if block.get("type") == "text":
                    return block.get("text", "").strip()
            return None
    except (urllib.error.URLError, urllib.error.HTTPError,
            json.JSONDecodeError, OSError, KeyError, IndexError):
        return None


def main() -> None:
    try:
        stdin_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({}))
        return

    mode = read_mode()
    if mode == "off":
        print(json.dumps({}))
        return

    prompt = stdin_data.get("prompt", "").strip()
    if len(prompt.split()) < MIN_WORDS:
        print(json.dumps({}))
        return

    corrections = check_grammar(prompt, mode)
    if corrections is None:
        print(json.dumps({}))
        return

    if corrections in ("No issues.", "No issues"):
        print(json.dumps({}))
        return

    label = MODE_LABELS.get(mode, "")
    instruction = TONE_INSTRUCTIONS.get(mode, TONE_INSTRUCTIONS["standard"])

    additional_context = (
        "## ⚠️ English Note\n\n"
        + (f"**Mode:** {label}\n\n" if label else "")
        + "The user's latest message contains these potential English issues:\n\n"
        f"{corrections}\n\n"
        f"**Instruction:** Before addressing the user's actual request, {instruction} "
        "Then proceed to answer their actual question."
    )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context,
        }
    }))


if __name__ == "__main__":
    main()
