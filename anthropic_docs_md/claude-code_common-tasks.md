# Core tasks and workflows - Anthropic

**Source:** https://docs.anthropic.com/en/docs/claude-code/common-tasks

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

Claude Code operates directly in your terminal, understanding your project
context and taking real actions. No need to manually add files to context -
Claude will explore your codebase as needed.

# [​](#understand-unfamiliar-code) Understand unfamiliar code

```
> what does the payment processing system do?
> find where user permissions are checked
> explain how the caching layer works

```

# [​](#automate-git-operations) Automate Git operations

```
> commit my changes
> create a pr
> which commit added tests for markdown back in December?
> rebase on main and resolve any merge conflicts

```

# [​](#edit-code-intelligently) Edit code intelligently

```
> add input validation to the signup form
> refactor the logger to use the new API
> fix the race condition in the worker queue

```

# [​](#test-and-debug-your-code) Test and debug your code

```
> run tests for the auth module and fix failures
> find and fix security vulnerabilities
> explain why this test is failing

```

# [​](#encourage-deeper-thinking) Encourage deeper thinking

For complex problems, explicitly ask Claude to think more deeply:

```
> think about how we should architect the new payment service
> think hard about the edge cases in our authentication flow

```

Claude Code will show when the model is using extended thinking. You can
proactively prompt Claude to “think” or “think deeply” for more
planning-intensive tasks. We suggest that you first tell Claude about your task
and let it gather context from your project. Then, ask it to “think” to create a
plan.

Claude will think more based on the words you use. For example, “think hard” will trigger more extended thinking than saying “think” alone.

For more tips, see
[Extended thinking tips](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips).

# [​](#automate-ci-and-infra-workflows) Automate CI and infra workflows

Claude Code comes with a non-interactive mode for headless execution. This is
especially useful for running Claude Code in non-interactive contexts like
scripts, pipelines, and Github Actions.

Use `--print` (`-p`) to run Claude in non-interactive mode. In this mode, you
can set the `ANTHROPIC_API_KEY` environment variable to provide a custom API
key.

Non-interactive mode is especially useful when you pre-configure the set of
commands Claude is allowed to use:

```
export ANTHROPIC_API_KEY=sk_...
claude -p "update the README with the latest changes" --allowedTools "Bash(git diff:*)" "Bash(git log:*)" Write --disallowedTools ...

```

Was this page helpful?

YesNo

Getting started[CLI usage](/en/docs/claude-code/cli-usage)

On this page
