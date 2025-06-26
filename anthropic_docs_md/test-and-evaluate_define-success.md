# Define your success criteria - Anthropic

**Source:** https://docs.anthropic.com/en/docs/test-and-evaluate/define-success

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

Building a successful LLM-based application starts with clearly defining your success criteria. How will you know when your application is good enough to publish?

Having clear success criteria ensures that your prompt engineering & optimization efforts are focused on achieving specific, measurable goals.

# [​](#building-strong-criteria) Building strong criteria

Good success criteria are:

* **Specific**: Clearly define what you want to achieve. Instead of “good performance,” specify “accurate sentiment classification.”
* **Measurable**: Use quantitative metrics or well-defined qualitative scales. Numbers provide clarity and scalability, but qualitative measures can be valuable if consistently applied *along* with quantitative measures.

  + Even “hazy” topics such as ethics and safety can be quantified:

    | Safety criteria |
    | --- |
    | Bad | Safe outputs |
    | Good | Less than 0.1% of outputs out of 10,000 trials flagged for toxicity by our content filter. |

  Example metrics and measurement methods

  **Quantitative metrics**:

  + Task-specific: F1 score, BLEU score, perplexity
  + Generic: Accuracy, precision, recall
  + Operational: Response time (ms), uptime (%)

  **Quantitative methods**:

  + A/B testing: Compare performance against a baseline model or earlier version.
  + User feedback: Implicit measures like task completion rates.
  + Edge case analysis: Percentage of edge cases handled without errors.

  **Qualitative scales**:

  + Likert scales: “Rate coherence from 1 (nonsensical) to 5 (perfectly logical)”
  + Expert rubrics: Linguists rating translation quality on defined criteria
* **Achievable**: Base your targets on industry benchmarks, prior experiments, AI research, or expert knowledge. Your success metrics should not be unrealistic to current frontier model capabilities.
* **Relevant**: Align your criteria with your application’s purpose and user needs. Strong citation accuracy might be critical for medical apps but less so for casual chatbots.

Example task fidelity criteria for sentiment analysis

| Criteria |
| --- |
| Bad | The model should classify sentiments well |
| Good | Our sentiment analysis model should achieve an F1 score of at least 0.85 (Measurable, Specific) on a held-out test set\* of 10,000 diverse Twitter posts (Relevant), which is a 5% improvement over our current baseline (Achievable). |

\**More on held-out test sets in the next section*

# [​](#common-success-criteria-to-consider) Common success criteria to consider

Here are some criteria that might be important for your use case. This list is non-exhaustive.

Task fidelity

How well does the model need to perform on the task? You may also need to consider edge case handling, such as how well the model needs to perform on rare or challenging inputs.

Consistency

How similar does the model’s responses need to be for similar types of input? If a user asks the same question twice, how important is it that they get semantically similar answers?

Relevance and coherence

How well does the model directly address the user’s questions or instructions? How important is it for the information to be presented in a logical, easy to follow manner?

Tone and style

How well does the model’s output style match expectations? How appropriate is its language for the target audience?

Privacy preservation

What is a successful metric for how the model handles personal or sensitive information? Can it follow instructions not to use or share certain details?

Context utilization

How effectively does the model use provided context? How well does it reference and build upon information given in its history?

Latency

What is the acceptable response time for the model? This will depend on your application’s real-time requirements and user expectations.

Price

What is your budget for running the model? Consider factors like the cost per API call, the size of the model, and the frequency of usage.

Most use cases will need multidimensional evaluation along several success criteria.

Example multidimensional criteria for sentiment analysis

| Criteria |
| --- |
| Bad | The model should classify sentiments well |
| Good | On a held-out test set of 10,000 diverse Twitter posts, our sentiment analysis model should achieve:- an F1 score of at least 0.85- 99.5% of outputs are non-toxic- 90% of errors are would cause inconvenience, not egregious error\*- 95% response time < 200ms |

\**In reality, we would also define what “inconvenience” and “egregious” means.*

# [​](#next-steps) Next steps

[## Brainstorm criteria

Brainstorm success criteria for your use case with Claude on claude.ai.**Tip**: Drop this page into the chat as guidance for Claude!](https://claude.ai/)[## Design evaluations

Learn to build strong test sets to gauge Claude’s performance against your criteria.](/en/docs/be-clear-direct)

Was this page helpful?

YesNo

Google Sheets add-on[Develop test cases](/en/docs/test-and-evaluate/develop-tests)

On this page
