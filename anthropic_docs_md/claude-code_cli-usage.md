# CLI usage and controls - Anthropic

**Source:** https://docs.anthropic.com/en/docs/claude-code/cli-usage

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# Claude Code

* [Overview](/en/docs/claude-code/overview)
* [Getting started](/en/docs/claude-code/getting-started)
* [Common tasks](/en/docs/claude-code/common-tasks)
* [CLI usage](/en/docs/claude-code/cli-usage)
* [IDE integrations](/en/docs/claude-code/ide-integrations)
* [Memory management](/en/docs/claude-code/memory)
* [Settings](/en/docs/claude-code/settings)
* [Security](/en/docs/claude-code/security)
* [Team setup](/en/docs/claude-code/team)
* [Monitoring usage](/en/docs/claude-code/monitoring-usage)
* [Costs](/en/docs/claude-code/costs)
* [Bedrock, Vertex, and proxies](/en/docs/claude-code/bedrock-vertex-proxies)
* [GitHub Actions](/en/docs/claude-code/github-actions)
* [SDK](/en/docs/claude-code/sdk)
* [Tutorials](/en/docs/claude-code/tutorials)
* [Troubleshooting](/en/docs/claude-code/troubleshooting)

# [​](#getting-started) Getting started

Claude Code provides two main ways to interact:

* **Interactive mode**: Run `claude` to start a REPL session
* **One-shot mode**: Use `claude -p "query"` for quick commands

```
# Start interactive mode

claude

# Start with an initial query

claude "explain this project"

# Run a single command and exit

claude -p "what does this function do?"

# Process piped content

cat logs.txt | claude -p "analyze these errors"

```

# [​](#cli-commands) CLI commands

| Command | Description | Example |
| --- | --- | --- |
| `claude` | Start interactive REPL | `claude` |
| `claude "query"` | Start REPL with initial prompt | `claude "explain this project"` |
| `claude -p "query"` | Run one-off query, then exit | `claude -p "explain this function"` |
| `cat file | claude -p "query"` | Process piped content | `cat logs.txt | claude -p "explain"` |
| `claude -c` | Continue most recent conversation | `claude -c` |
| `claude -c -p "query"` | Continue in print mode | `claude -c -p "Check for type errors"` |
| `claude -r "<session-id>" "query"` | Resume session by ID | `claude -r "abc123" "Finish this PR"` |
| `claude config` | Configure settings | `claude config set --global theme dark` |
| `claude update` | Update to latest version | `claude update` |
| `claude mcp` | Configure Model Context Protocol servers | [See MCP section in tutorials](/en/docs/claude-code/tutorials#set-up-model-context-protocol-mcp) |

# [​](#cli-flags) CLI flags

Customize Claude Code’s behavior with these command-line flags:

| Flag | Description | Example |
| --- | --- | --- |
| `--print`, `-p` | Print response without interactive mode (see [SDK documentation](/en/docs/claude-code/sdk) for programmatic usage details) | `claude -p "query"` |
| `--output-format` | Specify output format for print mode (options: `text`, `json`, `stream-json`) | `claude -p "query" --output-format json` |
| `--verbose` | Enable verbose logging, shows full turn-by-turn output (helpful for debugging in both print and interactive modes) | `claude --verbose` |
| `--max-turns` | Limit the number of agentic turns in non-interactive mode | `claude -p --max-turns 3 "query"` |
| `--model` | Sets the model for the current session with an alias for the latest model (`sonnet` or `opus`) or a model’s full name | `claude --model claude-sonnet-4-20250514` |
| `--permission-prompt-tool` | Specify an MCP tool to handle permission prompts in non-interactive mode | `claude -p --permission-prompt-tool mcp_auth_tool "query"` |
| `--resume` | Resume a specific session by ID, or by choosing in interactive mode | `claude --resume abc123 "query"` |
| `--continue` | Load the most recent conversation in the current directory | `claude --continue` |
| `--dangerously-skip-permissions` | Skip permission prompts (use with caution) | `claude --dangerously-skip-permissions` |

The `--output-format json` flag is particularly useful for scripting and
automation, allowing you to parse Claude’s responses programmatically.

For detailed information about print mode (`-p`) including output formats,
streaming, verbose logging, and programmatic usage, see the
[SDK documentation](/en/docs/claude-code/sdk).

# [​](#slash-commands) Slash commands

Control Claude’s behavior during an interactive session:

| Command | Purpose |
| --- | --- |
| `/bug` | Report bugs (sends conversation to Anthropic) |
| `/clear` | Clear conversation history |
| `/compact [instructions]` | Compact conversation with optional focus instructions |
| `/config` | View/modify configuration |
| `/cost` | Show token usage statistics |
| `/doctor` | Checks the health of your Claude Code installation |
| `/help` | Get usage help |
| `/init` | Initialize project with CLAUDE.md guide |
| `/login` | Switch Anthropic accounts |
| `/logout` | Sign out from your Anthropic account |
| `/memory` | Edit CLAUDE.md memory files |
| `/model` | Select or change the AI model |
| `/pr_comments` | View pull request comments |
| `/review` | Request code review |
| `/status` | View account and system statuses |
| `/terminal-setup` | Install Shift+Enter key binding for newlines (iTerm2 and VSCode only) |
| `/vim` | Enter vim mode for alternating insert and command modes |

# [​](#special-shortcuts) Special shortcuts

# [​](#quick-memory-with-%23) Quick memory with `#`

Add memories instantly by starting your input with `#`:

```
# Always use descriptive variable names

```

You’ll be prompted to select which memory file to store this in.

# [​](#line-breaks-in-terminal) Line breaks in terminal

Enter multiline commands using:

* **Quick escape**: Type `\` followed by Enter
* **Keyboard shortcut**: Option+Enter (or Shift+Enter if configured)

To set up Option+Enter in your terminal:

**For Mac Terminal.app:**

1. Open Settings → Profiles → Keyboard
2. Check “Use Option as Meta Key”

**For iTerm2 and VSCode terminal:**

1. Open Settings → Profiles → Keys
2. Under General, set Left/Right Option key to “Esc+”

**Tip for iTerm2 and VSCode users**: Run `/terminal-setup` within Claude Code to
automatically configure Shift+Enter as a more intuitive alternative.

See [terminal setup in settings](/en/docs/claude-code/settings#line-breaks) for
configuration details.

# [​](#vim-mode) Vim Mode

Claude Code supports a subset of Vim keybindings that can be enabled with `/vim`
or configured via `/config`.

The supported subset includes:

* Mode switching: `Esc` (to NORMAL), `i`/`I`, `a`/`A`, `o`/`O` (to INSERT)
* Navigation: `h`/`j`/`k`/`l`, `w`/`e`/`b`, `0`/`$`/`^`, `gg`/`G`
* Editing: `x`, `dw`/`de`/`db`/`dd`/`D`, `cw`/`ce`/`cb`/`cc`/`C`, `.` (repeat)

Was this page helpful?

YesNo

Common tasks[IDE integrations](/en/docs/claude-code/ide-integrations)

On this page
