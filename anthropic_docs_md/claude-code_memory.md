# Manage Claude's memory - Anthropic

**Source:** https://docs.anthropic.com/en/docs/claude-code/memory

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

Claude Code can remember your preferences across sessions, like style guidelines and common commands in your workflow.

# [​](#determine-memory-type) Determine memory type

Claude Code offers three memory locations, each serving a different purpose:

| Memory Type | Location | Purpose | Use Case Examples |
| --- | --- | --- | --- |
| **Project memory** | `./CLAUDE.md` | Team-shared instructions for the project | Project architecture, coding standards, common workflows |
| **User memory** | `~/.claude/CLAUDE.md` | Personal preferences for all projects | Code styling preferences, personal tooling shortcuts |
| **Project memory (local)** | `./CLAUDE.local.md` | Personal project-specific preferences | *(Deprecated, see below)* Your sandbox URLs, preferred test data |

All memory files are automatically loaded into Claude Code’s context when launched.

# [​](#claude-md-imports) CLAUDE.md imports

CLAUDE.md files can import additional files using `@path/to/import` syntax. The following example imports 3 files:

```
See @README for project overview and @package.json for available npm commands for this project.

# Additional Instructions

- git workflow @docs/git-instructions.md

```

Both relative and absolute paths are allowed. In particular, importing files in user’s home dir is a convenient way for your team members to provide individual instructions that are not checked into the repository. Previously CLAUDE.local.md served a similar purpose, but is now deprecated in favor of imports since they work better across multiple git worktrees.

```
# Individual Preferences

- @~/.claude/my-project-instructions.md

```

To avoid potential collisions, imports are not evaluated inside markdown code spans and code blocks.

```
This code span will not be treated as an import: `@anthropic-ai/claude-code`

```

Imported files can recursively import additional files, with a max-depth of 5 hops. You can see what memory files are loaded by running `/memory` command.

# [​](#how-claude-looks-up-memories) How Claude looks up memories

Claude Code reads memories recursively: starting in the cwd, Claude Code recurses up to */* and reads any CLAUDE.md or CLAUDE.local.md files it finds. This is especially convenient when working in large repositories where you run Claude Code in *foo/bar/*, and have memories in both *foo/CLAUDE.md* and *foo/bar/CLAUDE.md*.

Claude will also discover CLAUDE.md nested in subtrees under your current working directory. Instead of loading them at launch, they are only included when Claude reads files in those subtrees.

# [​](#quickly-add-memories-with-the-%23-shortcut) Quickly add memories with the `#` shortcut

The fastest way to add a memory is to start your input with the `#` character:

```
# Always use descriptive variable names

```

You’ll be prompted to select which memory file to store this in.

# [​](#directly-edit-memories-with-%2Fmemory) Directly edit memories with `/memory`

Use the `/memory` slash command during a session to open any memory file in your system editor for more extensive additions or organization.

# [​](#memory-best-practices) Memory best practices

* **Be specific**: “Use 2-space indentation” is better than “Format code properly”.
* **Use structure to organize**: Format each individual memory as a bullet point and group related memories under descriptive markdown headings.
* **Review periodically**: Update memories as your project evolves to ensure Claude is always using the most up to date information and context.

Was this page helpful?

YesNo

IDE integrations[Settings](/en/docs/claude-code/settings)

On this page
