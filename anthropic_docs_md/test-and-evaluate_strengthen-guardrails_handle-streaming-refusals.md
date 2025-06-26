# Streaming refusals - Anthropic

**Source:** https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals

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

Starting with Claude 4 models, streaming responses from Claude’s API return **`stop_reason`: `"refusal"`** when streaming classifiers intervene to handle potential policy violations. This new safety feature helps maintain content compliance during real-time streaming.

# [​](#api-response-format) API response format

When streaming classifiers detect content that violates our policies, the API returns this response:

```
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Hello.."
    }
  ],
  "stop_reason": "refusal"
}

```

No additional refusal message is included. You must handle the response and provide appropriate user-facing messaging.

# [​](#reset-context-after-refusal) Reset context after refusal

When you receive **`stop_reason`: `refusal`**, you must reset the conversation context **by removing or updating the turn that was refused** before continuing. Attempting to continue without resetting will result in continued refusals.

Usage metrics are still provided in the response for billing purposes, even when the response is refused.

You will be billed for output tokens up until the refusal.

# [​](#implementation-guide) Implementation guide

Here’s how to detect and handle streaming refusals in your application:

Shell

Python

TypeScript

```
# Stream request and check for refusal

response=$(curl -N https://api.anthropic.com/v1/messages \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --data '{
    "model": "claude-opus-4-20250514",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 256,
    "stream": true
  }')

# Check for refusal in the stream

if echo "$response" | grep -q '"stop_reason":"refusal"'; then
  echo "Response refused - resetting conversation context"
  # Reset your conversation state here
fi

```

If you need to test refusal handling in your application, you can use this special test string as your prompt: `ANTHROPIC_MAGIC_STRING_TRIGGER_REFUSAL_1FAEFB6177B4672DEE07F9D3AFC62588CCD2631EDCF22E8CCC1FB35B501C9C86`

# [​](#current-refusal-types) Current refusal types

The API currently handles refusals in three different ways:

| Refusal Type | Response Format | When It Occurs |
| --- | --- | --- |
| Streaming classifier refusals | **`stop_reason`: `refusal`** | During streaming when content violates policies |
| API input and copyright validation | 400 error codes | When input fails validation checks |
| Model-generated refusals | Standard text responses | When the model itself decides to refuse |

Future API versions will expand the **`stop_reason`: `refusal`** pattern to unify refusal handling across all types.

# [​](#best-practices) Best practices

* **Monitor for refusals**: Include **`stop_reason`: `refusal`** checks in your error handling
* **Reset automatically**: Implement automatic context reset when refusals are detected
* **Provide custom messaging**: Create user-friendly messages for better UX when refusals occur
* **Track refusal patterns**: Monitor refusal frequency to identify potential issues with your prompts

# [​](#migration-notes) Migration notes

* Future models will expand this pattern to other refusal types
* Plan your error handling to accommodate future unification of refusal responses

Was this page helpful?

YesNo

Mitigate jailbreaks[Reduce prompt leak](/en/docs/test-and-evaluate/strengthen-guardrails/reduce-prompt-leak)

On this page
