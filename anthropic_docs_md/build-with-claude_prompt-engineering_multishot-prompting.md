# Use examples (multishot prompting) to guide Claude's behavior - Anthropic

**Source:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/multishot-prompting

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

Examples are your secret weapon shortcut for getting Claude to generate exactly what you need. By providing a few well-crafted examples in your prompt, you can dramatically improve the accuracy, consistency, and quality of Claude’s outputs.
This technique, known as few-shot or multishot prompting, is particularly effective for tasks that require structured outputs or adherence to specific formats.

**Power up your prompts**: Include 3-5 diverse, relevant examples to show Claude exactly what you want. More examples = better performance, especially for complex tasks.

# [​](#why-use-examples%3F) Why use examples?

* **Accuracy**: Examples reduce misinterpretation of instructions.
* **Consistency**: Examples enforce uniform structure and style.
* **Performance**: Well-chosen examples boost Claude’s ability to handle complex tasks.

# [​](#crafting-effective-examples) Crafting effective examples

For maximum effectiveness, make sure that your examples are:

* **Relevant**: Your examples mirror your actual use case.
* **Diverse**: Your examples cover edge cases and potential challenges, and vary enough that Claude doesn’t inadvertently pick up on unintended patterns.
* **Clear**: Your examples are wrapped in `<example>` tags (if multiple, nested within `<examples>` tags) for structure.

Ask Claude to evaluate your examples for relevance, diversity, or clarity. Or have Claude generate more examples based on your initial set.

Example: Analyzing customer feedback

Notice that in the “no examples” version, Claude does not list multiple options for each category, despite its written analysis indicating that there are multiple categories for certain feedback. It also includes a long explanation when we may not want it to.

| Role | No Examples | With Examples |
| --- | --- | --- |
| User | Analyze this customer feedback and categorize the issues. Use these categories: UI/UX, Performance, Feature Request, Integration, Pricing, and Other. Also rate the sentiment (Positive/Neutral/Negative) and priority (High/Medium/Low).Here is the feedback: {{FEEDBACK}} | Our CS team is overwhelmed with unstructured feedback. Your task is to analyze feedback and categorize issues for our product and engineering teams. Use these categories: UI/UX, Performance, Feature Request, Integration, Pricing, and Other. Also rate the sentiment (Positive/Neutral/Negative) and priority (High/Medium/Low). Here is an example:<example>Input: The new dashboard is a mess! It takes forever to load, and I can’t find the export button. Fix this ASAP!Category: UI/UX, PerformanceSentiment: NegativePriority: High</example>Now, analyze this feedback: {{FEEDBACK}} |
| Assistant (Claude’s response) | Here’s the analysis of the customer feedback:Issue: UI/UXSentiment: NegativePriority: HighThe customer is frustrated with the new dashboard design, which they find cluttered and slow to load. They specifically call out the missing “export” button, which is likely a critical feature. This issue needs to be addressed as a high priority.Issue: IntegrationSentiment: PositivePriority: MediumThe customer is pleased with the existing Salesforce integration but would like to see support for Hubspot as well. This is a feature request that could be considered for a future product update.Issue: PricingSentiment: NegativePriority: HighThe customer finds the pricing to be unreasonable, especially for the basic features. They are threatening to switch to a competitor, so this is a high-priority issue that needs to be reviewed.Issue: PerformanceSentiment NegativePriority: HighThe customer is experiencing critical issues with the mobile app, where large file uploads consistently result in crashes. This is a significant problem that impacts the customer’s ability to use the product effectively and should be addressed as a high priority.Issue: UI/UXSentiment: PositivePriority: LowThe customer is overall satisfied with the product, specifically calling out the intuitive UI and excellent customer support. This is a positive piece of feedback that does not require any immediate action. | Here’s the analysis of the customer feedback:1. The new dashboard is a mess! It takes forever to load, and I can’t find the export button. Fix this ASAP!Category: UI/UX, PerformanceSentiment: NegativePriority: High2. Love the Salesforce integration! But it’d be great if you could add Hubspot too.Category: Integration, Feature RequestSentiment: PositivePriority: Medium3. Your pricing is ridiculous! $99/mo for basic features? I’m switching to Competitor X.Category: PricingSentiment: NegativePriority: High4. The mobile app keeps crashing when I try to upload large files (>50MB). This is critical for our field agents.Category: PerformanceSentiment: NegativePriority: High5. Overall, I’m happy with the product. The UI is intuitive, and the customer support is top-notch. Keep it up!Category: UI/UX, Other (Customer Support)Sentiment: PositivePriority: Low |

## Prompt library

Get inspired by a curated selection of prompts for various tasks and use cases.[## GitHub prompting tutorial](https://github.com/anthropics/prompt-eng-interactive-tutorial)[## Google Sheets prompting tutorial

A lighter weight version of our prompt engineering tutorial via an interactive spreadsheet.](https://docs.google.com/spreadsheets/d/19jzLgRruG9kjUQNKtCg1ZjdD6l6weA6qRXG5zLIAhC8)

Was this page helpful?

YesNo

Be clear and direct[Let Claude think (CoT)](/en/docs/build-with-claude/prompt-engineering/chain-of-thought)

On this page
