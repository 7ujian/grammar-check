/grammar-check <mode>

Switch the grammar-check plugin mode. Modes:

- `off` — disable grammar checking entirely
- `basic` — only flag grammar and spelling errors (skip style suggestions)
- `conversational` — check errors and suggest more natural, colloquial expressions
- `formal` — stricter checks with suggestions for professional / academic tone
- `standard` — default balanced mode (reset)

To apply the mode, write a JSON file to `~/.grammar-check-mode`:

```json
{"mode": "<mode>"}
```

Use `echo '{"mode": "<mode>"}' > ~/.grammar-check-mode` or the Write tool.

After writing, confirm the mode switch to the user in one short line. For example:
- off → "Grammar check disabled."
- basic → "Grammar check set to basic mode (grammar + spelling only)."
- conversational → "Grammar check set to conversational mode."
- formal → "Grammar check set to formal mode."
- standard → "Grammar check reset to standard mode."

If the user typed an unrecognized mode, list the valid modes and ask them to retry.
