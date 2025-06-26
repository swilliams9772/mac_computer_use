# Prompt engineering overview - Anthropic

**Source:** https://docs.anthropic.com/en/docs/intro-to-prompting

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

While these tips apply broadly to all Claude models, you can find prompting tips specific to extended thinking models [here](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips).

# [​](#before-prompt-engineering) Before prompt engineering

This guide assumes that you have:

1. A clear definition of the success criteria for your use case
2. Some ways to empirically test against those criteria
3. A first draft prompt you want to improve

If not, we highly suggest you spend time establishing that first. Check out [Define your success criteria](/en/docs/build-with-claude/define-success) and [Create strong empirical evaluations](/en/docs/build-with-claude/develop-tests) for tips and guidance.

[## Prompt generator

Don’t have a first draft prompt? Try the prompt generator in the Anthropic Console!](https://console.anthropic.com/dashboard)

# [​](#when-to-prompt-engineer) When to prompt engineer

This guide focuses on success criteria that are controllable through prompt engineering.
Not every success criteria or failing eval is best solved by prompt engineering. For example, latency and cost can be sometimes more easily improved by selecting a different model.

Prompting vs. finetuning

Prompt engineering is far faster than other methods of model behavior control, such as finetuning, and can often yield leaps in performance in far less time. Here are some reasons to consider prompt engineering over finetuning:

* **Resource efficiency**: Fine-tuning requires high-end GPUs and large memory, while prompt engineering only needs text input, making it much more resource-friendly.
* **Cost-effectiveness**: For cloud-based AI services, fine-tuning incurs significant costs. Prompt engineering uses the base model, which is typically cheaper.
* **Maintaining model updates**: When providers update models, fine-tuned versions might need retraining. Prompts usually work across versions without changes.
* **Time-saving**: Fine-tuning can take hours or even days. In contrast, prompt engineering provides nearly instantaneous results, allowing for quick problem-solving.
* **Minimal data needs**: Fine-tuning needs substantial task-specific, labeled data, which can be scarce or expensive. Prompt engineering works with few-shot or even zero-shot learning.
* **Flexibility & rapid iteration**: Quickly try various approaches, tweak prompts, and see immediate results. This rapid experimentation is difficult with fine-tuning.
* **Domain adaptation**: Easily adapt models to new domains by providing domain-specific context in prompts, without retraining.
* **Comprehension improvements**: Prompt engineering is far more effective than finetuning at helping models better understand and utilize external content such as retrieved documents
* **Preserves general knowledge**: Fine-tuning risks catastrophic forgetting, where the model loses general knowledge. Prompt engineering maintains the model’s broad capabilities.
* **Transparency**: Prompts are human-readable, showing exactly what information the model receives. This transparency aids in understanding and debugging.

# [​](#how-to-prompt-engineer) How to prompt engineer

The prompt engineering pages in this section have been organized from most broadly effective techniques to more specialized techniques. When troubleshooting performance, we suggest you try these techniques in order, although the actual impact of each technique will depend on your use case.

1. [Prompt generator](/en/docs/build-with-claude/prompt-engineering/prompt-generator)
2. [Be clear and direct](/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct)
3. [Use examples (multishot)](/en/docs/build-with-claude/prompt-engineering/multishot-prompting)
4. [Let Claude think (chain of thought)](/en/docs/build-with-claude/prompt-engineering/chain-of-thought)
5. [Use XML tags](/en/docs/build-with-claude/prompt-engineering/use-xml-tags)
6. [Give Claude a role (system prompts)](/en/docs/build-with-claude/prompt-engineering/system-prompts)
7. [Prefill Claude’s response](/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response)
8. [Chain complex prompts](/en/docs/build-with-claude/prompt-engineering/chain-prompts)
9. [Long context tips](/en/docs/build-with-claude/prompt-engineering/long-context-tips)

# [​](#prompt-engineering-tutorial) Prompt engineering tutorial

If you’re an interactive learner, you can dive into our interactive tutorials instead!

[## GitHub prompting tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)[## Google Sheets prompting tutorial

A lighter weight version of our prompt engineering tutorial via an interactive spreadsheet.](https://docs.google.com/spreadsheets/d/19jzLgRruG9kjUQNKtCg1ZjdD6l6weA6qRXG5zLIAhC8)

Was this page helpful?

YesNo

Glossary[Claude 4 best practices](/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)

On this page
