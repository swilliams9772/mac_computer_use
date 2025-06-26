# Use our prompt improver to optimize your prompts - Anthropic

**Source:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-improver

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

Our prompt improver is compatible with all Claude models, including those with extended thinking capabilities. For prompting tips specific to extended thinking models, see [here](/en/docs/build-with-claude/extended-thinking).

The prompt improver helps you quickly iterate and improve your prompts through automated analysis and enhancement. It excels at making prompts more robust for complex tasks that require high accuracy.

# [​](#before-you-begin) Before you begin

You’ll need:

* A [prompt template](/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables) to improve
* Feedback on current issues with Claude’s outputs (optional but recommended)
* Example inputs and ideal outputs (optional but recommended)

# [​](#how-the-prompt-improver-works) How the prompt improver works

The prompt improver enhances your prompts in 4 steps:

1. **Example identification**: Locates and extracts examples from your prompt template
2. **Initial draft**: Creates a structured template with clear sections and XML tags
3. **Chain of thought refinement**: Adds and refines detailed reasoning instructions
4. **Example enhancement**: Updates examples to demonstrate the new reasoning process

You can watch these steps happen in real-time in the improvement modal.

# [​](#what-you-get) What you get

The prompt improver generates templates with:

* Detailed chain-of-thought instructions that guide Claude’s reasoning process and typically improve its performance
* Clear organization using XML tags to separate different components
* Standardized example formatting that demonstrates step-by-step reasoning from input to output
* Strategic prefills that guide Claude’s initial responses

While examples appear separately in the Workbench UI, they’re included at the start of the first user message in the actual API call. View the raw format by clicking ”**</> Get Code**” or insert examples as raw text via the Examples box.

# [​](#how-to-use-the-prompt-improver) How to use the prompt improver

1. Submit your prompt template
2. Add any feedback about issues with Claude’s current outputs (e.g., “summaries are too basic for expert audiences”)
3. Include example inputs and ideal outputs
4. Review the improved prompt

# [​](#generate-test-examples) Generate test examples

Don’t have examples yet? Use our [Test Case Generator](/en/docs/test-and-evaluate/eval-tool#creating-test-cases) to:

1. Generate sample inputs
2. Get Claude’s responses
3. Edit the responses to match your ideal outputs
4. Add the polished examples to your prompt

# [​](#when-to-use-the-prompt-improver) When to use the prompt improver

The prompt improver works best for:

* Complex tasks requiring detailed reasoning
* Situations where accuracy is more important than speed
* Problems where Claude’s current outputs need significant improvement

For latency or cost-sensitive applications, consider using simpler prompts. The prompt improver creates templates that produce longer, more thorough, but slower responses.

# [​](#example-improvement) Example improvement

Here’s how the prompt improver enhances a basic classification prompt:

Original prompt

```
From the following list of Wikipedia article titles, identify which article this sentence came from.
Respond with just the article title and nothing else.

Article titles:
{{titles}}

Sentence to classify:
{{sentence}}

```

Improved prompt

```
You are an intelligent text classification system specialized in matching sentences to Wikipedia article titles. Your task is to identify which Wikipedia article a given sentence most likely belongs to, based on a provided list of article titles.

First, review the following list of Wikipedia article titles:
<article_titles>
{{titles}}
</article_titles>

Now, consider this sentence that needs to be classified:
<sentence_to_classify>
{{sentence}}
</sentence_to_classify>

Your goal is to determine which article title from the provided list best matches the given sentence. Follow these steps:

1. List the key concepts from the sentence
2. Compare each key concept with the article titles
3. Rank the top 3 most relevant titles and explain why they are relevant
4. Select the most appropriate article title that best encompasses or relates to the sentence's content

Wrap your analysis in <analysis> tags. Include the following:
- List of key concepts from the sentence
- Comparison of each key concept with the article titles
- Ranking of top 3 most relevant titles with explanations
- Your final choice and reasoning

After your analysis, provide your final answer: the single most appropriate Wikipedia article title from the list.

Output only the chosen article title, without any additional text or explanation.

```

Notice how the improved prompt:

* Adds clear step-by-step reasoning instructions
* Uses XML tags to organize content
* Provides explicit output formatting requirements
* Guides Claude through the analysis process

# [​](#troubleshooting) Troubleshooting

Common issues and solutions:

* **Examples not appearing in output**: Check that examples are properly formatted with XML tags and appear at the start of the first user message
* **Chain of thought too verbose**: Add specific instructions about desired output length and level of detail
* **Reasoning steps don’t match your needs**: Modify the steps section to match your specific use case

# [​](#next-steps) Next steps

## Prompt library

Get inspired by example prompts for various tasks.[## GitHub prompting tutorial

Learn prompting best practices with our interactive tutorial.](https://github.com/anthropics/prompt-eng-interactive-tutorial)[## Test your prompts

Use our evaluation tool to test your improved prompts.](/en/docs/test-and-evaluate/eval-tool)

Was this page helpful?

YesNo

Use prompt templates[Be clear and direct](/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct)

On this page
