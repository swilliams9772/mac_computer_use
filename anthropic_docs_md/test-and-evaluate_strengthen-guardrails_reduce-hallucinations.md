# Reduce hallucinations - Anthropic

**Source:** https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations

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

Even the most advanced language models, like Claude, can sometimes generate text that is factually incorrect or inconsistent with the given context. This phenomenon, known as “hallucination,” can undermine the reliability of your AI-driven solutions.
This guide will explore techniques to minimize hallucinations and ensure Claude’s outputs are accurate and trustworthy.

# [​](#basic-hallucination-minimization-strategies) Basic hallucination minimization strategies

* **Allow Claude to say “I don’t know”:** Explicitly give Claude permission to admit uncertainty. This simple technique can drastically reduce false information.

Example: Analyzing a merger & acquisition report

| Role | Content |
| --- | --- |
| User | As our M&A advisor, analyze this report on the potential acquisition of AcmeCo by ExampleCorp.<report>{{REPORT}}</report>Focus on financial projections, integration risks, and regulatory hurdles. If you’re unsure about any aspect or if the report lacks necessary information, say “I don’t have enough information to confidently assess this.” |

* **Use direct quotes for factual grounding:** For tasks involving long documents (>20K tokens), ask Claude to extract word-for-word quotes first before performing its task. This grounds its responses in the actual text, reducing hallucinations.

Example: Auditing a data privacy policy

| Role | Content |
| --- | --- |
| User | As our Data Protection Officer, review this updated privacy policy for GDPR and CCPA compliance.<policy>{{POLICY}}</policy>1. Extract exact quotes from the policy that are most relevant to GDPR and CCPA compliance. If you can’t find relevant quotes, state “No relevant quotes found.”2. Use the quotes to analyze the compliance of these policy sections, referencing the quotes by number. Only base your analysis on the extracted quotes. |

* **Verify with citations**: Make Claude’s response auditable by having it cite quotes and sources for each of its claims. You can also have Claude verify each claim by finding a supporting quote after it generates a response. If it can’t find a quote, it must retract the claim.

Example: Drafting a press release on a product launch

| Role | Content |
| --- | --- |
| User | Draft a press release for our new cybersecurity product, AcmeSecurity Pro, using only information from these product briefs and market reports.<documents>{{DOCUMENTS}}</documents>After drafting, review each claim in your press release. For each claim, find a direct quote from the documents that supports it. If you can’t find a supporting quote for a claim, remove that claim from the press release and mark where it was removed with empty [] brackets. |

# [​](#advanced-techniques) Advanced techniques

* **Chain-of-thought verification**: Ask Claude to explain its reasoning step-by-step before giving a final answer. This can reveal faulty logic or assumptions.
* **Best-of-N verficiation**: Run Claude through the same prompt multiple times and compare the outputs. Inconsistencies across outputs could indicate hallucinations.
* **Iterative refinement**: Use Claude’s outputs as inputs for follow-up prompts, asking it to verify or expand on previous statements. This can catch and correct inconsistencies.
* **External knowledge restriction**: Explicitly instruct Claude to only use information from provided documents and not its general knowledge.

Remember, while these techniques significantly reduce hallucinations, they don’t eliminate them entirely. Always validate critical information, especially for high-stakes decisions.

Was this page helpful?

YesNo

Develop test cases[Increase output consistency](/en/docs/test-and-evaluate/strengthen-guardrails/increase-consistency)

On this page
