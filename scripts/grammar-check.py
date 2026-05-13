#!/usr/bin/env python3
"""Check English via LanguageTool public API and inject grammar corrections as additionalContext."""

import sys
import json
import urllib.request
import urllib.parse
import urllib.error

API_URL = "https://api.languagetool.org/v2/check"
MIN_WORDS = 3
MAX_MATCHES = 5
TIMEOUT = 8


def check_grammar(text: str) -> list | None:
    """Call LanguageTool API v2. Returns list of matches, or None on error."""
    payload = urllib.parse.urlencode({
        "text": text,
        "language": "en-US",
    }).encode("utf-8")

    req = urllib.request.Request(API_URL, data=payload)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("matches", [])
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, OSError):
        return None


def format_corrections(text: str, matches: list) -> str:
    """Format LanguageTool matches into concise correction lines."""
    lines = []

    for m in matches[:MAX_MATCHES]:
        offset = m.get("offset", 0)
        length = m.get("length", 0)
        message = m.get("message", m.get("shortMessage", ""))
        issue_type = (m.get("rule", {}) or {}).get("issueType", "other")
        replacements = [
            r.get("value", "")
            for r in (m.get("replacements") or [])[:3]
        ]

        error_text = text[offset:offset + length] if offset + length <= len(text) else "?"

        replacement_str = " / ".join(replacements) if replacements else "…"

        tag = {"misspelling": "Spelling", "grammar": "Grammar", "style": "Style",
               "typographical": "Typo"}.get(issue_type, issue_type.title())

        if replacement_str == "…":
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

    user_prompt = stdin_data.get("user_prompt", "").strip()

    if len(user_prompt.split()) < MIN_WORDS:
        print(json.dumps({}))
        return

    matches = check_grammar(user_prompt)

    if matches is None or not matches:
        print(json.dumps({}))
        return

    corrections = format_corrections(user_prompt, matches)

    if not corrections:
        print(json.dumps({}))
        return

    additional_context = (
        "## ⚠️ English Note\n\n"
        "The user's latest message contains these potential English issues:\n\n"
        f"{corrections}\n\n"
        "**Instruction:** Before addressing the user's actual request, "
        "concisely point out 2–3 of the most important corrections above. "
        "Be friendly and brief — one or two lines max. "
        "Then proceed to answer their actual question."
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context,
        }
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
