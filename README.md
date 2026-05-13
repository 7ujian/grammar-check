# grammar-check

Claude Code plugin that checks your English for grammar and style issues, then politely suggests corrections before answering your question.

## How it works

When you submit a prompt in English, this plugin calls the free [LanguageTool API](https://languagetool.org) to check for grammar, spelling, and style issues. If problems are found, Claude first gives you a quick correction, then addresses your actual request.

No API key required. Uses only Python standard library.

## Install

```bash
git clone https://github.com/7ujian/grammar-check.git
cc --plugin-dir /path/to/grammar-check
```

## Modes

Switch modes anytime with `/grammar-check <mode>`:

| Command | Mode | Behavior |
|---|---|---|
| `/grammar-check off` | Off | Disable grammar checking |
| `/grammar-check basic` | Basic | Grammar + spelling only |
| `/grammar-check conversational` | Conversational | Errors + colloquial phrasing suggestions |
| `/grammar-check formal` | Formal | Stricter checks + professional/academic tone |
| `/grammar-check standard` | Standard | Default balanced mode |

## Structure

```
grammar-check/
├── .claude-plugin/plugin.json    # Plugin manifest
├── commands/grammar-check.md     # Slash command for mode switching
├── hooks/hooks.json              # UserPromptSubmit hook
└── scripts/grammar-check.py      # Grammar checker (calls LanguageTool API)
```

## License

MIT
