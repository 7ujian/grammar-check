# grammar-check

Claude Code plugin that checks your English for grammar and style issues using Claude, then politely suggests corrections before answering your question.

## How it works

When you submit a prompt in English, this plugin calls the Claude API to check for grammar, spelling, and style issues. If problems are found, Claude first gives you a quick correction, then addresses your actual request.

Uses your configured Haiku-equivalent model for fast, cost-effective grammar checking. No external services required.

## Install

### Option A — per-session (quick test)

```bash
git clone https://github.com/7ujian/grammar-check.git
claude --plugin-dir /path/to/grammar-check
```

### Option B — permanent install (recommended)

```bash
# Clone and copy to cache
git clone https://github.com/7ujian/grammar-check.git /tmp/grammar-check
mkdir -p ~/.claude/plugins/cache/local/grammar-check/2.0.0
cp -r /tmp/grammar-check/{.claude-plugin,commands,hooks,scripts} ~/.claude/plugins/cache/local/grammar-check/2.0.0/
```

Then add this entry to `~/.claude/plugins/installed_plugins.json` under `"plugins"`:

```json
"grammar-check@local": [{
  "scope": "user",
  "installPath": "~/.claude/plugins/cache/local/grammar-check/2.0.0",
  "version": "2.0.0"
}]
```

And enable it in `~/.claude/settings.json`:

```json
"enabledPlugins": {
  "grammar-check@local": true
}
```

Restart Claude Code.

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
