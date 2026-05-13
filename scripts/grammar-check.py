#!/usr/bin/env python3
"""Check English via LanguageTool API and inject grammar corrections as additionalContext.

Supports modes: off, basic, conversational, formal, standard (default).
Mode is read from ~/.grammar-check-mode (set by /grammar-check slash command).
"""

import sys
import json
import os
import urllib.request
import urllib.parse
import urllib.error

API_URL = "https://api.languagetool.org/v2/check"
MIN_WORDS = 3
MAX_MATCHES = 5
TIMEOUT = 8
STATE_FILE = os.path.expanduser("~/.grammar-check-mode")

MODE_LABELS = {
    "basic": "Basic",
    "conversational": "Conversational",
    "formal": "Formal",
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


def check_grammar(text: str, mode: str) -> list | None:
    params = {"text": text, "language": "en-US"}
    if mode == "formal":
        params["level"] = "picky"

    payload = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(API_URL, data=payload)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8")).get("matches", [])
    except (urllib.error.URLError, urllib.error.HTTPError,
            json.JSONDecodeError, OSError):
        return None


def format_corrections(text: str, matches: list, mode: str) -> str:
    lines = []

    for m in matches:
        if len(lines) >= MAX_MATCHES:
            break

        issue_type = (m.get("rule", {}) or {}).get("issueType", "other")

        if mode == "basic" and issue_type not in ("misspelling", "grammar"):
            continue

        offset = m.get("offset", 0)
        length = m.get("length", 0)
        message = m.get("message", m.get("shortMessage", ""))
        replacements = [
            r.get("value", "")
            for r in (m.get("replacements") or [])[:3]
        ]

        error_text = text[offset:offset + length] if offset + length <= len(text) else "?"
        replacement_str = " / ".join(replacements) if replacements else "..."

        tag = {
            "misspelling": "Spelling", "grammar": "Grammar",
            "style": "Style", "typographical": "Typo",
        }.get(issue_type, issue_type.title())

        if replacement_str == "...":
            lines.append(f"- {tag}: \"{error_text}\" — {message}")
        else:
            lines.append(f"- {tag}: \"{error_text}\" → {replacement_str} ({message})")

    return "\n".join(lines)


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

    user_prompt = stdin_data.get("user_prompt", "").strip()
    if len(user_prompt.split()) < MIN_WORDS:
        print(json.dumps({}))
        return

    matches = check_grammar(user_prompt, mode)
    if matches is None or not matches:
        print(json.dumps({}))
        return

    corrections = format_corrections(user_prompt, matches, mode)
    if not corrections:
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
