# Remote MCP servers - Anthropic

**Source:** https://docs.anthropic.com/en/docs/agents-and-tools/remote-mcp-servers

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# First steps

* [Intro to Claude](/en/docs/welcome)
* [Get started](/en/docs/get-started)

# Models & pricing

* [Models overview](/en/docs/about-claude/models/overview)
* [Choosing a model](/en/docs/about-claude/models/choosing-a-model)
* [Migrating to Claude 4](/en/docs/about-claude/models/migrating-to-claude-4)
* [Model deprecations](/en/docs/about-claude/model-deprecations)
* [Pricing](/en/docs/about-claude/pricing)

# Learn about Claude

* [Building with Claude](/en/docs/overview)
* Use cases
* [Context windows](/en/docs/build-with-claude/context-windows)
* [Glossary](/en/docs/about-claude/glossary)
* Prompt engineering

# Explore features

* [Features overview](/en/docs/build-with-claude/overview)
* [Prompt caching](/en/docs/build-with-claude/prompt-caching)
* [Extended thinking](/en/docs/build-with-claude/extended-thinking)
* [Streaming Messages](/en/docs/build-with-claude/streaming)
* [Batch processing](/en/docs/build-with-claude/batch-processing)
* [Citations](/en/docs/build-with-claude/citations)
* [Multilingual support](/en/docs/build-with-claude/multilingual-support)
* [Token counting](/en/docs/build-with-claude/token-counting)
* [Embeddings](/en/docs/build-with-claude/embeddings)
* [Vision](/en/docs/build-with-claude/vision)
* [PDF support](/en/docs/build-with-claude/pdf-support)

# Agent components

* Tools
* Model Context Protocol (MCP)

  + [MCP overview](/en/docs/agents-and-tools/mcp)
  + [MCP connector (beta)](/en/docs/agents-and-tools/mcp-connector)
  + [Remote MCP servers](/en/docs/agents-and-tools/remote-mcp-servers)
* [Computer use (beta)](/en/docs/agents-and-tools/computer-use)
* [Google Sheets add-on](/en/docs/agents-and-tools/claude-for-sheets)

# Test & evaluate

* [Define success criteria](/en/docs/test-and-evaluate/define-success)
* [Develop test cases](/en/docs/test-and-evaluate/develop-tests)
* Strengthen guardrails
* [Using the Evaluation Tool](/en/docs/test-and-evaluate/eval-tool)

# Legal center

* [Anthropic Privacy Policy](https://www.anthropic.com/legal/privacy)
* [Security and compliance](https://trust.anthropic.com/)

Several companies have deployed remote MCP servers that developers can connect to via the Anthropic MCP connector API. These servers expand the capabilities available to developers and end users by providing remote access to various services and tools through the MCP protocol.

The remote MCP servers listed below are third-party services designed to work with the Anthropic API. These servers are not owned, operated, or endorsed by Anthropic. Users should only connect to remote MCP servers they trust and should review each server’s security practices and terms before connecting.

# [​](#connecting-to-remote-mcp-servers) Connecting to remote MCP servers

To connect to a remote MCP server:

1. Review the documentation for the specific server you want to use.
2. Ensure you have the necessary authentication credentials.
3. Follow the server-specific connection instructions provided by each company.

For more information about using remote MCP servers with the Anthropic API, see the [MCP connector docs](/en/docs/agents-and-tools/mcp-connector).

# [​](#remote-mcp-server-examples) Remote MCP server examples

| **Company** | **Description** | **Server URL** |
| --- | --- | --- |
| **[Asana](https://developers.asana.com/docs/using-asanas-model-control-protocol-mcp-server)** | Interact with your Asana workspace through AI tools to keep projects on track. | `https://mcp.asana.com/sse` |
| **[Atlassian](https://www.atlassian.com/platform/remote-mcp-server)** | Access Atlassian’s collaboration and productivity tools. | `https://mcp.atlassian.com/v1/sse` |
| **[Cloudflare](https://github.com/cloudflare/mcp-server-cloudflare/tree/main)** | Build applications, analyze traffic, monitor performance, and manage security settings through Cloudflare. | See [`mcp-server-cloudflare` repo](https://github.com/cloudflare/mcp-server-cloudflare/tree/main) for server URLs |
| **[Intercom](https://developers.intercom.com/docs/guides/mcp)** | Access real-time customer conversations, tickets, and user data—from Intercom. | `https://mcp.intercom.com/sse` |
| **[invideo](https://invideo.io/ai/mcp)** | Build video creation capabilities into your applications. | `https://mcp.invideo.io/sse` |
| **[Linear](https://linear.app/docs/mcp)** | Integrate with Linear’s issue tracking and project management system. | `https://mcp.linear.app/sse` |
| **[PayPal](https://www.paypal.ai/)** | Integrate PayPal commerce capabilities. | `https://mcp.paypal.com/sse` |
| **[Plaid](https://plaid.com/blog/plaid-mcp-ai-assistant-claude/)** | Analyze, troubleshoot, and optimize Plaid integrations. | `https://api.dashboard.plaid.com/mcp/sse` |
| **[Square](https://developer.squareup.com/docs/mcp)** | Use an agent to build on Square APIs. Payments, inventory, orders, and more. | `https://mcp.squareup.com/sse` |
| **[Workato](https://docs.workato.com/mcp.html)** | Access any application, workflows or data via Workato, made accessible for AI | MCP servers are programmatically generated. |
| **[Zapier](https://zapier.com/mcp)** | Connect to nearly 8,000 apps through Zapier’s automation platform. | `https://mcp.zapier.com/` |

Was this page helpful?

YesNo

MCP connector (beta)[Computer use (beta)](/en/docs/agents-and-tools/computer-use)

On this page
