# Use prompt templates and variables - Anthropic

**Source:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables

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

  + [Overview](/en/docs/build-with-claude/prompt-engineering/overview)
  + [Claude 4 best practices](/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
  + [Prompt generator](/en/docs/build-with-claude/prompt-engineering/prompt-generator)
  + [Use prompt templates](/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables)
  + [Prompt improver](/en/docs/build-with-claude/prompt-engineering/prompt-improver)
  + [Be clear and direct](/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct)
  + [Use examples (multishot prompting)](/en/docs/build-with-claude/prompt-engineering/multishot-prompting)
  + [Let Claude think (CoT)](/en/docs/build-with-claude/prompt-engineering/chain-of-thought)
  + [Use XML tags](/en/docs/build-with-claude/prompt-engineering/use-xml-tags)
  + [Give Claude a role (system prompts)](/en/docs/build-with-claude/prompt-engineering/system-prompts)
  + [Prefill Claude's response](/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response)
  + [Chain complex prompts](/en/docs/build-with-claude/prompt-engineering/chain-prompts)
  + [Long context tips](/en/docs/build-with-claude/prompt-engineering/long-context-tips)
  + [Extended thinking tips](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips)

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

When deploying an LLM-based application with Claude, your API calls will typically consist of two types of content:

* **Fixed content:** Static instructions or context that remain constant across multiple interactions
* **Variable content:** Dynamic elements that change with each request or conversation, such as:
  + User inputs
  + Retrieved content for Retrieval-Augmented Generation (RAG)
  + Conversation context such as user account history
  + System-generated data such as tool use results fed in from other independent calls to Claude

A **prompt template** combines these fixed and variable parts, using placeholders for the dynamic content. In the [Anthropic Console](https://console.anthropic.com/), these placeholders are denoted with **{{double brackets}}**, making them easily identifiable and allowing for quick testing of different values.

# [​](#when-to-use-prompt-templates-and-variables) When to use prompt templates and variables

You should always use prompt templates and variables when you expect any part of your prompt to be repeated in another call to Claude (only via the API or the [Anthropic Console](https://console.anthropic.com/). [claude.ai](https://claude.ai/) currently does not support prompt templates or variables).

Prompt templates offer several benefits:

* **Consistency:** Ensure a consistent structure for your prompts across multiple interactions
* **Efficiency:** Easily swap out variable content without rewriting the entire prompt
* **Testability:** Quickly test different inputs and edge cases by changing only the variable portion
* **Scalability:** Simplify prompt management as your application grows in complexity
* **Version control:** Easily track changes to your prompt structure over time by keeping tabs only on the core part of your prompt, separate from dynamic inputs

The [Anthropic Console](https://console.anthropic.com/) heavily uses prompt templates and variables in order to support features and tooling for all the above, such as with the:

* **[Prompt generator](/en/docs/build-with-claude/prompt-engineering/prompt-generator):** Decides what variables your prompt needs and includes them in the template it outputs
* **[Prompt improver](/en/docs/build-with-claude/prompt-engineering/prompt-improver):** Takes your existing template, including all variables, and maintains them in the improved template it outputs
* **[Evaluation tool](/en/docs/test-and-evaluate/eval-tool):** Allows you to easily test, scale, and track versions of your prompts by separating the variable and fixed portions of your prompt template

# [​](#example-prompt-template) Example prompt template

Let’s consider a simple application that translates English text to Spanish. The translated text would be variable since you would expect this text to change between users or calls to Claude. This translated text could be dynamically retrieved from databases or the user’s input.

Thus, for your translation app, you might use this simple prompt template:

```
Translate this text from English to Spanish: {{text}}

```

# [​](#next-steps) Next steps

## Generate a prompt

Learn about the prompt generator in the Anthropic Console and try your hand at getting Claude to generate a prompt for you.## Apply XML tags

If you want to level up your prompt variable game, wrap them in XML tags.[## Anthropic Console

Check out the myriad prompt development tools available in the Anthropic Console.](https://console.anthropic.com/)

Was this page helpful?

YesNo

Prompt generator[Prompt improver](/en/docs/build-with-claude/prompt-engineering/prompt-improver)

On this page
