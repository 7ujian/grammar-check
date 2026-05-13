# grammar-check

Claude Code plugin that checks your English for grammar and style issues using Claude, then politely suggests corrections before answering your question.

## How it works

When you submit a prompt in English, this plugin calls the Claude API to check for grammar, spelling, and style issues. If problems are found, Claude first gives you a quick correction, then addresses your actual request.

Uses your configured Haiku-equivalent model for fast, cost-effective grammar checking. No external services required.

## Install

### Option A — auto-load (recommended for personal use)

```bash
git clone https://github.com/7ujian/grammar-check.git ~/.claude/plugins/data/grammar-check-inline
```

Restart Claude Code. The plugin loads automatically from `~/.claude/plugins/data/`.

### Option B — per-session

```bash
git clone https://github.com/7ujian/grammar-check.git
claude --plugin-dir /path/to/grammar-check
```

### Option C — custom marketplace (for sharing with a team)

Add the repo as a custom marketplace, then install:

```bash
# One-time marketplace registration
claude plugins add marketplace https://github.com/7ujian/grammar-check

# Install the plugin
claude plugins install grammar-check@<marketplace-name>
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
├── commands/mode.md              # Slash command for mode switching
├── hooks/hooks.json              # UserPromptSubmit hook
└── scripts/grammar-check.py      # Grammar checker (calls Claude API)
```

## License

MIT
