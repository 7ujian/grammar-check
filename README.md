# grammar-check

Claude Code plugin that checks your English for grammar and style issues, then politely suggests corrections before answering your question.

## How it works

When you submit a prompt in English, this plugin calls the free [LanguageTool API](https://languagetool.org) to check for grammar, spelling, and style issues. If problems are found, Claude first gives you a quick correction, then addresses your actual request.

No API key required. Uses only Python standard library.

## Install

```bash
# Clone and launch
git clone https://github.com/7ujian/grammar-check.git
cc --plugin-dir /path/to/grammar-check

# Or add an alias for convenience
alias cc='cc --plugin-dir /path/to/grammar-check'
```

## Structure

```
grammar-check/
├── .claude-plugin/plugin.json    # Plugin manifest
├── hooks/hooks.json              # UserPromptSubmit hook
└── scripts/grammar-check.py      # Grammar checker (calls LanguageTool API)
```

## License

MIT
