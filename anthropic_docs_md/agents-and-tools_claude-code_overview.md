# Claude Code overview - Anthropic

**Source:** https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview

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

Claude Code is an agentic coding tool that lives in your terminal, understands your codebase, and helps you code faster through natural language commands. By integrating directly with your development environment, Claude Code streamlines your workflow without requiring additional servers or complex setup.

```
npm install -g @anthropic-ai/claude-code

```

Claude Code’s key capabilities include:

* Editing files and fixing bugs across your codebase
* Answering questions about your code’s architecture and logic
* Executing and fixing tests, linting, and other commands
* Searching through git history, resolving merge conflicts, and creating commits and PRs
* Browsing documentation and resources from the internet using web search
* Works with [Amazon Bedrock and Google Vertex AI](/en/docs/claude-code/bedrock-vertex-proxies) for enterprise deployments

# [​](#why-claude-code%3F) Why Claude Code?

Claude Code operates directly in your terminal, understanding your project context and taking real actions. No need to manually add files to context - Claude will explore your codebase as needed.

# [​](#enterprise-integration) Enterprise integration

Claude Code seamlessly integrates with enterprise AI platforms. You can connect to [Amazon Bedrock or Google Vertex AI](/en/docs/claude-code/bedrock-vertex-proxies) for secure, compliant deployments that meet your organization’s requirements.

# [​](#security-and-privacy-by-design) Security and privacy by design

Your code’s security is paramount. Claude Code’s architecture ensures:

* **Direct API connection**: Your queries go straight to Anthropic’s API without intermediate servers
* **Works where you work**: Operates directly in your terminal
* **Understands context**: Maintains awareness of your entire project structure
* **Takes action**: Performs real operations like editing files and creating commits

# [​](#getting-started) Getting started

To get started with Claude Code, follow our [installation guide](/en/docs/claude-code/getting-started) which covers system requirements, installation steps, and authentication process.

# [​](#quick-tour) Quick tour

Here’s what you can accomplish with Claude Code:

# [​](#from-questions-to-solutions-in-seconds) From questions to solutions in seconds

```
# Ask questions about your codebase

claude
> how does our authentication system work?

# Create a commit with one command

claude commit

# Fix issues across multiple files

claude "fix the type errors in the auth module"

```

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

# [​](#next-steps) Next steps

## Getting started

Install Claude Code and get up and running## Core features

Explore what Claude Code can do for you## Commands

Learn about CLI commands and controls[## Configuration

Customize Claude Code for your workflow](/en/docs/claude-code/settings)

# [​](#additional-resources) Additional resources

## Claude Code tutorials

Step-by-step guides for common tasks## Troubleshooting

Solutions for common issues with Claude Code## Bedrock & Vertex integrations

Configure Claude Code with Amazon Bedrock or Google Vertex AI[## Reference implementation

Clone our development container reference implementation.](https://github.com/anthropics/claude-code/tree/main/.devcontainer)

# [​](#license-and-data-usage) License and data usage

Claude Code is provided under Anthropic’s [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms).

# [​](#how-we-use-your-data) How we use your data

We aim to be fully transparent about how we use your data. We may use feedback to improve our products and services, but we will not train generative models using your feedback from Claude Code. Given their potentially sensitive nature, we store user feedback transcripts for only 30 days.

# [​](#feedback-transcripts) Feedback transcripts

If you choose to send us feedback about Claude Code, such as transcripts of your usage, Anthropic may use that feedback to debug related issues and improve Claude Code’s functionality (e.g., to reduce the risk of similar bugs occurring in the future). We will not train generative models using this feedback.

# [​](#privacy-safeguards) Privacy safeguards

We have implemented several safeguards to protect your data, including limited retention periods for sensitive information, restricted access to user session data, and clear policies against using feedback for model training.

For full details, please review our [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms) and [Privacy Policy](https://www.anthropic.com/legal/privacy).

# [​](#license) License

© Anthropic PBC. All rights reserved. Use is subject to Anthropic’s [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms).

Was this page helpful?

YesNo

[Getting started](/en/docs/claude-code/getting-started)

On this page
