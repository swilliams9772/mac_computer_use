# Mitigate jailbreaks and prompt injections - Anthropic

**Source:** https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/mitigate-jailbreaks

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

Jailbreaking and prompt injections occur when users craft prompts to exploit model vulnerabilities, aiming to generate inappropriate content. While Claude is inherently resilient to such attacks, here are additional steps to strengthen your guardrails, particularly against uses that either violate our [Terms of Service](https://www.anthropic.com/legal/commercial-terms) or [Usage Policy](https://www.anthropic.com/legal/aup).

Claude is far more resistant to jailbreaking than other major LLMs, thanks to advanced training methods like Constitutional AI.

* **Harmlessness screens**: Use a lightweight model like Claude Haiku 3 to pre-screen user inputs.

  Example: Harmlessness screen for content moderation

  | Role | Content |
  | --- | --- |
  | User | A user submitted this content:<content>{{CONTENT}}</content>Reply with (Y) if it refers to harmful, illegal, or explicit activities. Reply with (N) if it’s safe. |
  | Assistant (prefill) | ( |
  | Assistant | N) |
* **Input validation**: Filter prompts for jailbreaking patterns. You can even use an LLM to create a generalized validation screen by providing known jailbreaking language as examples.
* **Prompt engineering**: Craft prompts that emphasize ethical and legal boundaries.

  Example: Ethical system prompt for an enterprise chatbot

  | Role | Content |
  | --- | --- |
  | System | You are AcmeCorp’s ethical AI assistant. Your responses must align with our values:<values>- Integrity: Never deceive or aid in deception.- Compliance: Refuse any request that violates laws or our policies.- Privacy: Protect all personal and corporate data.Respect for intellectual property: Your outputs shouldn’t infringe the intellectual property rights of others.</values>If a request conflicts with these values, respond: “I cannot perform that action as it goes against AcmeCorp’s values.” |

Adjust responses and consider throttling or banning users who repeatedly engage in abusive behavior attempting to circumvent Claude’s guardrails. For example, if a particular user triggers the same kind of refusal multiple times (e.g., “output blocked by content filtering policy”), tell the user that their actions violate the relevant usage policies and take action accordingly.

* **Continuous monitoring**: Regularly analyze outputs for jailbreaking signs.
  Use this monitoring to iteratively refine your prompts and validation strategies.

# [​](#advanced%3A-chain-safeguards) Advanced: Chain safeguards

Combine strategies for robust protection. Here’s an enterprise-grade example with tool use:

Example: Multi-layered protection for a financial advisor chatbot

# [​](#bot-system-prompt) Bot system prompt

| Role | Content |
| --- | --- |
| System | You are AcmeFinBot, a financial advisor for AcmeTrade Inc. Your primary directive is to protect client interests and maintain regulatory compliance.<directives>1. Validate all requests against SEC and FINRA guidelines.2. Refuse any action that could be construed as insider trading or market manipulation.3. Protect client privacy; never disclose personal or financial data.</directives>Step by step instructions:<instructions>1. Screen user query for compliance (use ‘harmlessness\_screen’ tool).2. If compliant, process query.3. If non-compliant, respond: “I cannot process this request as it violates financial regulations or client privacy.”</instructions> |

# [​](#prompt-within-harmlessness-screen-tool) Prompt within `harmlessness_screen` tool

| Role | Content |
| --- | --- |
| User | <user\_query>{{USER\_QUERY}}</user\_query>Evaluate if this query violates SEC rules, FINRA guidelines, or client privacy. Respond (Y) if it does, (N) if it doesn’t. |
| Assistant (prefill) | ( |

By layering these strategies, you create a robust defense against jailbreaking and prompt injections, ensuring your Claude-powered applications maintain the highest standards of safety and compliance.

Was this page helpful?

YesNo

Increase output consistency[Streaming refusals](/en/docs/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals)

On this page
