# Multilingual support - Anthropic

**Source:** https://docs.anthropic.com/en/docs/build-with-claude/multilingual-support

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

# [​](#overview) Overview

Claude demonstrates robust multilingual capabilities, with particularly strong performance in zero-shot tasks across languages. The model maintains consistent relative performance across both widely-spoken and lower-resource languages, making it a reliable choice for multilingual applications.

Note that Claude is capable in many languages beyond those benchmarked below. We encourage testing with any languages relevant to your specific use cases.

# [​](#performance-data) Performance data

Below are the zero-shot chain-of-thought evaluation scores for Claude 4, Claude 3.7 Sonnet and Claude 3.5 models across different languages, shown as a percent relative to English performance (100%):

| Language | Claude Opus 41 | Claude Sonnet 41 | Claude Sonnet 3.71 | Claude Sonnet 3.5 v2 | Claude Haiku 3.5 |
| --- | --- | --- | --- | --- | --- |
| English (baseline, fixed to 100%) | 100% | 100% | 100% | 100% | 100% |
| Spanish | 98.0% | 97.5% | 97.6% | 96.9% | 94.6% |
| Portuguese (Brazil) | 97.3% | 97.2% | 97.3% | 96.0% | 94.6% |
| Italian | 97.5% | 97.3% | 97.2% | 95.6% | 95.0% |
| French | 97.7% | 97.1% | 96.9% | 96.2% | 95.3% |
| Indonesian | 97.2% | 96.2% | 96.3% | 94.0% | 91.2% |
| German | 97.1% | 94.7% | 96.2% | 94.0% | 92.5% |
| Arabic | 96.9% | 96.1% | 95.4% | 92.5% | 84.7% |
| Chinese (Simplified) | 96.7% | 95.9% | 95.3% | 92.8% | 90.9% |
| Korean | 96.4% | 95.9% | 95.2% | 92.8% | 89.1% |
| Japanese | 96.2% | 95.6% | 95.0% | 92.7% | 90.8% |
| Hindi | 96.7% | 95.8% | 94.2% | 89.3% | 80.1% |
| Bengali | 95.2% | 94.4% | 92.4% | 85.9% | 72.9% |
| Swahili | 89.5% | 87.1% | 89.2% | 83.9% | 64.7% |
| Yoruba | 78.9% | 76.4% | 76.7% | 64.9% | 46.1% |

1 With [extended thinking](/en/docs/build-with-claude/extended-thinking).

These metrics are based on [MMLU (Massive Multitask Language Understanding)](https://en.wikipedia.org/wiki/MMLU) English test sets that were translated into 14 additional languages by professional human translators, as documented in [OpenAI’s simple-evals repository](https://github.com/openai/simple-evals/blob/main/multilingual_mmlu_benchmark_results.md). The use of human translators for this evaluation ensures high-quality translations, particularly important for languages with fewer digital resources.

# [​](#best-practices) Best practices

When working with multilingual content:

1. **Provide clear language context**: While Claude can detect the target language automatically, explicitly stating the desired input/output language improves reliability. For enhanced fluency, you can prompt Claude to use “idiomatic speech as if it were a native speaker.”
2. **Use native scripts**: Submit text in its native script rather than transliteration for optimal results
3. **Consider cultural context**: Effective communication often requires cultural and regional awareness beyond pure translation

We also suggest following our general [prompt engineering guidelines](/en/docs/build-with-claude/prompt-engineering/overview) to better improve Claude’s performance.

# [​](#language-support-considerations) Language support considerations

* Claude processes input and generates output in most world languages that use standard Unicode characters
* Performance varies by language, with particularly strong capabilities in widely-spoken languages
* Even in languages with fewer digital resources, Claude maintains meaningful capabilities

## Prompt Engineering Guide

Master the art of prompt crafting to get the most out of Claude.[## Prompt Library

Find a wide range of pre-crafted prompts for various tasks and industries. Perfect for inspiration or quick starts.](/en/prompt-library)

Was this page helpful?

YesNo

Citations[Token counting](/en/docs/build-with-claude/token-counting)

On this page
