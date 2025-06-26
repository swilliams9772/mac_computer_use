# Choosing the right model - Anthropic

**Source:** https://docs.anthropic.com/en/docs/about-claude/models/choosing-a-model

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

# [​](#establish-key-criteria) Establish key criteria

When choosing a Claude model, we recommend first evaluating these factors:

* **Capabilities:** What specific features or capabilities will you need the model to have in order to meet your needs?
* **Speed:** How quickly does the model need to respond in your application?
* **Cost:** What’s your budget for both development and production usage?

Knowing these answers in advance will make narrowing down and deciding which model to use much easier.

# [​](#choose-the-best-model-to-start-with) Choose the best model to start with

There are two general approaches you can use to start testing which Claude model best works for your needs.

# [​](#option-1%3A-start-with-a-fast%2C-cost-effective-model) Option 1: Start with a fast, cost-effective model

For many applications, starting with a faster, more cost-effective model like Claude 3.5 Haiku can be the optimal approach:

1. Begin implementation with Claude 3.5 Haiku
2. Test your use case thoroughly
3. Evaluate if performance meets your requirements
4. Upgrade only if necessary for specific capability gaps

This approach allows for quick iteration, lower development costs, and is often sufficient for many common applications. This approach is best for:

* Initial prototyping and development
* Applications with tight latency requirements
* Cost-sensitive implementations
* High-volume, straightforward tasks

# [​](#option-2%3A-start-with-the-most-capable-model) Option 2: Start with the most capable model

For complex tasks where intelligence and advanced capabilities are paramount, you may want to start with the most capable model and then consider optimizing to more efficient models down the line:

1. Implement with Claude Opus 4 or Claude Sonnet 4
2. Optimize your prompts for these models
3. Evaluate if performance meets your requirements
4. Consider increasing efficiency by downgrading intelligence over time with greater workflow optimization

This approach is best for:

* Complex reasoning tasks
* Scientific or mathematical applications
* Tasks requiring nuanced understanding
* Applications where accuracy outweighs cost considerations
* Advanced coding

# [​](#model-selection-matrix) Model selection matrix

| When you need… | We recommend starting with… | Example use cases |
| --- | --- | --- |
| Highest intelligence and reasoning, superior capabilities for the most complex tasks, such as multi agent coding | Claude Opus 4 | Multi agent frameworks, complex codebase refactoring, nuanced creative writing, complex financial or scientific analysis |
| Balance of intelligence and speed, strong performance but with faster response times | Claude Sonnet 4 | Complex customer chatbot inquiries, complex code generation, straightforward agentic loops, data analysis |
| Fast responses at lower cost, optimized for high volume, straightforward appications with no need for extended thinking | Claude 3.5 Haiku | Basic customer support, high volume formulaic content generation, straightforward data extraction |

# [​](#decide-whether-to-upgrade-or-change-models) Decide whether to upgrade or change models

To determine if you need to upgrade or change models, you should:

1. [Create benchmark tests](en/docs/build-with-claude/develop-tests.mdx) specific to your use case - having a good evaluation set is the most important step in the process
2. Test with your actual prompts and data
3. Compare performance across models for:
   * Accuracy of responses
   * Response quality
   * Handling of edge cases
4. Weigh performance and cost tradeoffs

# [​](#next-steps) Next steps

## Model comparison chart

See detailed specifications and pricing for the latest Claude models[## Migrate to Claude 4

Follow the checklist for an easy migration to Claude 4](/en/docs/about-claude/models/migrating-to-claude-4)

Was this page helpful?

YesNo

Models overview[Migrating to Claude 4](/en/docs/about-claude/models/migrating-to-claude-4)

On this page
