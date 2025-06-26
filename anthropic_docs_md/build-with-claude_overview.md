# Features overview - Anthropic

**Source:** https://docs.anthropic.com/en/docs/build-with-claude/overview

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

# [​](#batch-processing) Batch processing

Process large volumes of requests asynchronously for cost savings. Send batches with a large number of queries per batch. Each batch is processed in less than 24 hours and costs 50% less than standard API calls. [Learn more](/en/api/creating-message-batches).

**Available on:**

# [​](#citations) Citations

Ground Claude’s responses in source documents. With Citations, Claude can provide detailed references to the exact sentences and passages it uses to generate responses, leading to more verifiable, trustworthy outputs. [Learn more](/en/docs/build-with-claude/citations).

**Available on:**

# [​](#computer-use-public-beta) Computer use (public beta)

Computer use is Claude’s ability to perform tasks by interpreting screenshots and automatically generating the necessary computer commands (like mouse movements and keystrokes). [Learn more](/en/docs/agents-and-tools/computer-use).

**Available on:**

# [​](#pdf-support) PDF support

Process and analyze text and visual content from PDF documents. [Learn more](/en/docs/build-with-claude/pdf-support).

**Available on:**

# [​](#mcp-connector-public-beta) MCP connector (public beta)

Connect to Model Context Protocol (MCP) servers directly from the Messages API. The Remote MCP connector allows Claude to access external tools and services without requiring you to build an MCP client. [Learn more](/en/docs/agents-and-tools/mcp-connector).

**Available on:**

# [​](#prompt-caching) Prompt caching

Provide Claude with more background knowledge and example outputs to reduce costs by up to 90% and latency by up to 85% for long prompts. [Learn more](/en/docs/build-with-claude/prompt-caching).

**Available on:**

# [​](#1-hour-cache-duration-beta) 1-hour cache duration (beta)

Anthropic offers a 1-hour cache duration for prompt caching.

To use the extended cache, add `extended-cache-ttl-2025-04-11` as a [beta header](/en/api/beta-headers) to your request.

**Available on:**

# [​](#token-counting) Token counting

Token counting enables you to determine the number of tokens in a message before sending it to Claude, helping you make informed decisions about your prompts and usage. [Learn more](/en/api/messages-count-tokens).

**Available on:**

# [​](#tool-use) Tool use

Enable Claude to interact with external tools and APIs to perform a wider variety of tasks. [Learn more](/en/docs/build-with-claude/tool-use/overview).

**Available on:**

# [​](#web-search) Web search

Augment Claude’s comprehensive knowledge with current, real-world data from across the web. [Learn more](/en/docs/build-with-claude/tool-use/web-search-tool).

**Available on:**

# [​](#files-api-public-beta) Files API (public beta)

Upload and manage files to use with Claude without re-uploading content with each request. Supports PDFs, images, and text files up to 32 MB per file. [Learn more](/en/docs/build-with-claude/files).

**Available on:**

# [​](#code-execution-public-beta) Code execution (public beta)

Run Python code in a sandboxed environment for advanced data analysis. [Learn more](/en/docs/agents-and-tools/tool-use/code-execution-tool).

**Available on:**

Was this page helpful?

YesNo

Extended thinking tips[Prompt caching](/en/docs/build-with-claude/prompt-caching)

On this page
