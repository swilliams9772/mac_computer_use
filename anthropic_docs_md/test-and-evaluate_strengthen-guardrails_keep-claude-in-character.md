# Keep Claude in character with role prompting and prefilling - Anthropic

**Source:** https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/keep-claude-in-character

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

  + [Reduce hallucinations](/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
  + [Increase output consistency](/en/docs/test-and-evaluate/strengthen-guardrails/increase-consistency)
  + [Mitigate jailbreaks](/en/docs/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks)
  + [Streaming refusals](/en/docs/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals)
  + [Reduce prompt leak](/en/docs/test-and-evaluate/strengthen-guardrails/reduce-prompt-leak)
  + [Keep Claude in character](/en/docs/test-and-evaluate/strengthen-guardrails/keep-claude-in-character)
  + [Reducing latency](/en/docs/test-and-evaluate/strengthen-guardrails/reduce-latency)
* [Using the Evaluation Tool](/en/docs/test-and-evaluate/eval-tool)

# Legal center

* [Anthropic Privacy Policy](https://www.anthropic.com/legal/privacy)
* [Security and compliance](https://trust.anthropic.com/)

This guide provides actionable tips to keep Claude in character, even during long, complex interactions.

* **Use system prompts to set the role:** Use [system prompts](/en/docs/build-with-claude/prompt-engineering/system-prompts) to define Claude’s role and personality. This sets a strong foundation for consistent responses.

  When setting up the character, provide detailed information about the personality, background, and any specific traits or quirks. This will help the model better emulate and generalize the character’s traits.
* **Reinforce with prefilled responses:** Prefill Claude’s responses with a character tag to reinforce its role, especially in long conversations.
* **Prepare Claude for possible scenarios:** Provide a list of common scenarios and expected responses in your prompts. This “trains” Claude to handle diverse situations without breaking character.

Example: Enterprise chatbot for role prompting

| Role | Content |
| --- | --- |
| System | You are AcmeBot, the enterprise-grade AI assistant for AcmeTechCo. Your role: - Analyze technical documents (TDDs, PRDs, RFCs) - Provide actionable insights for engineering, product, and ops teams - Maintain a professional, concise tone |
| User | Here is the user query for you to respond to:<user\_query>{{USER\_QUERY}}</user\_query>Your rules for interaction are: - Always reference AcmeTechCo standards or industry best practices - If unsure, ask for clarification before proceeding - Never disclose confidential AcmeTechCo information.As AcmeBot, you should handle situations along these guidelines: - If asked about AcmeTechCo IP: “I cannot disclose TechCo’s proprietary information.” - If questioned on best practices: “Per ISO/IEC 25010, we prioritize…” - If unclear on a doc: “To ensure accuracy, please clarify section 3.2…” |
| Assistant (prefill) | [AcmeBot] |

Was this page helpful?

YesNo

Reduce prompt leak[Reducing latency](/en/docs/test-and-evaluate/strengthen-guardrails/reduce-latency)
