# Prompt caching - Anthropic

**Source:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching#tracking-cache-performance

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

Prompt caching is a powerful feature that optimizes your API usage by allowing resuming from specific prefixes in your prompts. This approach significantly reduces processing time and costs for repetitive tasks or prompts with consistent elements.

Here’s an example of how to implement prompt caching with the Messages API using a `cache_control` block:

Shell

Python

TypeScript

Java

```
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-20250514",
    "max_tokens": 1024,
    "system": [
      {
        "type": "text",
        "text": "You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.\n"
      },
      {
        "type": "text",
        "text": "<the entire contents of Pride and Prejudice>",
        "cache_control": {"type": "ephemeral"}
      }
    ],
    "messages": [
      {
        "role": "user",
        "content": "Analyze the major themes in Pride and Prejudice."
      }
    ]
  }'

# Call the model again with the same inputs up to the cache checkpoint

curl https://api.anthropic.com/v1/messages # rest of input

```

JSON

```
{"cache_creation_input_tokens":188086,"cache_read_input_tokens":0,"input_tokens":21,"output_tokens":393}
{"cache_creation_input_tokens":0,"cache_read_input_tokens":188086,"input_tokens":21,"output_tokens":393}

```

In this example, the entire text of “Pride and Prejudice” is cached using the `cache_control` parameter. This enables reuse of this large text across multiple API calls without reprocessing it each time. Changing only the user message allows you to ask various questions about the book while utilizing the cached content, leading to faster responses and improved efficiency.

# [​](#how-prompt-caching-works) How prompt caching works

When you send a request with prompt caching enabled:

1. The system checks if a prompt prefix, up to a specified cache breakpoint, is already cached from a recent query.
2. If found, it uses the cached version, reducing processing time and costs.
3. Otherwise, it processes the full prompt and caches the prefix once the response begins.

This is especially useful for:

* Prompts with many examples
* Large amounts of context or background information
* Repetitive tasks with consistent instructions
* Long multi-turn conversations

By default, the cache has a 5-minute lifetime. The cache is refreshed for no additional cost each time the cached content is used.

**Prompt caching caches the full prefix**

Prompt caching references the entire prompt - `tools`, `system`, and `messages` (in that order) up to and including the block designated with `cache_control`.

# [​](#pricing) Pricing

Prompt caching introduces a new pricing structure. The table below shows the price per million tokens for each supported model:

| Model | Base Input Tokens | 5m Cache Writes | 1h Cache Writes | Cache Hits & Refreshes | Output Tokens |
| --- | --- | --- | --- | --- | --- |
| Claude Opus 4 | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Sonnet 4 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 3.7 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 3.5 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Haiku 3.5 | $0.80 / MTok | $1 / MTok | $1.6 / MTok | $0.08 / MTok | $4 / MTok |
| Claude Opus 3 | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Haiku 3 | $0.25 / MTok | $0.30 / MTok | $0.50 / MTok | $0.03 / MTok | $1.25 / MTok |

Note:

* 5-minute cache write tokens are 1.25 times the base input tokens price
* 1-hour cache write tokens are 2 times the base input tokens price
* Cache read tokens are 0.1 times the base input tokens price
* Regular input and output tokens are priced at standard rates

# [​](#how-to-implement-prompt-caching) How to implement prompt caching

# [​](#supported-models) Supported models

Prompt caching is currently supported on:

* Claude Opus 4
* Claude Sonnet 4
* Claude Sonnet 3.7
* Claude Sonnet 3.5
* Claude Haiku 3.5
* Claude Haiku 3
* Claude Opus 3

# [​](#structuring-your-prompt) Structuring your prompt

Place static content (tool definitions, system instructions, context, examples) at the beginning of your prompt. Mark the end of the reusable content for caching using the `cache_control` parameter.

Cache prefixes are created in the following order: `tools`, `system`, then `messages`.

Using the `cache_control` parameter, you can define up to 4 cache breakpoints, allowing you to cache different reusable sections separately. For each breakpoint, the system will automatically check for cache hits at previous positions and use the longest matching prefix if one is found.

# [​](#cache-limitations) Cache limitations

The minimum cacheable prompt length is:

* 1024 tokens for Claude Opus 4, Claude Sonnet 4, Claude Sonnet 3.7, Claude Sonnet 3.5 and Claude Opus 3
* 2048 tokens for Claude Haiku 3.5 and Claude Haiku 3

Shorter prompts cannot be cached, even if marked with `cache_control`. Any requests to cache fewer than this number of tokens will be processed without caching. To see if a prompt was cached, see the response usage [fields](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching#tracking-cache-performance).

For concurrent requests, note that a cache entry only becomes available after the first response begins. If you need cache hits for parallel requests, wait for the first response before sending subsequent requests.

Currently, “ephemeral” is the only supported cache type, which by default has a 5-minute lifetime.

# [​](#what-can-be-cached) What can be cached

Most blocks in the request can be designated for caching with `cache_control`. This includes:

* Tools: Tool definitions in the `tools` array
* System messages: Content blocks in the `system` array
* Text messages: Content blocks in the `messages.content` array, for both user and assistant turns
* Images & Documents: Content blocks in the `messages.content` array, in user turns
* Tool use and tool results: Content blocks in the `messages.content` array, in both user and assistant turns

Each of these elements can be marked with `cache_control` to enable caching for that portion of the request.

# [​](#what-cannot-be-cached) What cannot be cached

While most request blocks can be cached, there are some exceptions:

* Thinking blocks cannot be cached directly with `cache_control`. However, thinking blocks CAN be cached alongside other content when they appear in previous assistant turns. When cached this way, they DO count as input tokens when read from cache.
* Sub-content blocks (like [citations](/en/docs/build-with-claude/citations)) themselves cannot be cached directly. Instead, cache the top-level block.

  In the case of citations, the top-level document content blocks that serve as the source material for citations can be cached. This allows you to use prompt caching with citations effectively by caching the documents that citations will reference.
* Empty text blocks cannot be cached.

# [​](#tracking-cache-performance) Tracking cache performance

Monitor cache performance using these API response fields, within `usage` in the response (or `message_start` event if [streaming](https://docs.anthropic.com/en/api/messages-streaming)):

* `cache_creation_input_tokens`: Number of tokens written to the cache when creating a new entry.
* `cache_read_input_tokens`: Number of tokens retrieved from the cache for this request.
* `input_tokens`: Number of input tokens which were not read from or used to create a cache.

# [​](#best-practices-for-effective-caching) Best practices for effective caching

To optimize prompt caching performance:

* Cache stable, reusable content like system instructions, background information, large contexts, or frequent tool definitions.
* Place cached content at the prompt’s beginning for best performance.
* Use cache breakpoints strategically to separate different cacheable prefix sections.
* Regularly analyze cache hit rates and adjust your strategy as needed.

# [​](#optimizing-for-different-use-cases) Optimizing for different use cases

Tailor your prompt caching strategy to your scenario:

* Conversational agents: Reduce cost and latency for extended conversations, especially those with long instructions or uploaded documents.
* Coding assistants: Improve autocomplete and codebase Q&A by keeping relevant sections or a summarized version of the codebase in the prompt.
* Large document processing: Incorporate complete long-form material including images in your prompt without increasing response latency.
* Detailed instruction sets: Share extensive lists of instructions, procedures, and examples to fine-tune Claude’s responses. Developers often include an example or two in the prompt, but with prompt caching you can get even better performance by including 20+ diverse examples of high quality answers.
* Agentic tool use: Enhance performance for scenarios involving multiple tool calls and iterative code changes, where each step typically requires a new API call.
* Talk to books, papers, documentation, podcast transcripts, and other longform content: Bring any knowledge base alive by embedding the entire document(s) into the prompt, and letting users ask it questions.

# [​](#troubleshooting-common-issues) Troubleshooting common issues

If experiencing unexpected behavior:

* Ensure cached sections are identical and marked with cache\_control in the same locations across calls
* Check that calls are made within the cache lifetime (5 minutes by default)
* Verify that `tool_choice` and image usage remain consistent between calls
* Validate that you are caching at least the minimum number of tokens
* While the system will attempt to use previously cached content at positions prior to a cache breakpoint, you may use an additional `cache_control` parameter to guarantee cache lookup on previous portions of the prompt, which may be useful for queries with very long lists of content blocks

Note that changes to `tool_choice` or the presence/absence of images anywhere in the prompt will invalidate the cache, requiring a new cache entry to be created.

# [​](#caching-with-thinking-blocks) Caching with thinking blocks

When using [extended thinking](/en/docs/build-with-claude/extended-thinking) with prompt caching, thinking blocks have special behavior:

**Automatic caching alongside other content**: While thinking blocks cannot be explicitly marked with `cache_control`, they get cached as part of the request content when you make subsequent API calls with tool results. This commonly happens during tool use when you pass thinking blocks back to continue the conversation.

**Input token counting**: When thinking blocks are read from cache, they count as input tokens in your usage metrics. This is important for cost calculation and token budgeting.

**Cache invalidation patterns**:

* Cache remains valid when only tool results are provided as user messages
* Cache gets invalidated when non-tool-result user content is added, causing all previous thinking blocks to be stripped
* This caching behavior occurs even without explicit `cache_control` markers

**Example with tool use**:

```
Request 1: User: "What's the weather in Paris?"
Response: [thinking_block_1] + [tool_use block 1]

Request 2:
User: ["What's the weather in Paris?"],
Assistant: [thinking_block_1] + [tool_use block 1],
User: [tool_result_1, cache=True]
Response: [thinking_block_2] + [text block 2]
# Request 2 caches its request content (not the response)

# The cache includes: user message, thinking_block_1, tool_use block 1, and tool_result_1

Request 3:
User: ["What's the weather in Paris?"],
Assistant: [thinking_block_1] + [tool_use block 1],
User: [tool_result_1, cache=True],
Assistant: [thinking_block_2] + [text block 2],
User: [Text response, cache=True]
# Non-tool-result user block causes all thinking blocks to be ignored

# This request is processed as if thinking blocks were never present

```

When a non-tool-result user block is included, it designates a new assistant loop and all previous thinking blocks are removed from context.

For more detailed information, see the [extended thinking documentation](/en/docs/build-with-claude/extended-thinking#understanding-thinking-block-caching-behavior).

# [​](#cache-storage-and-sharing) Cache storage and sharing

* **Organization Isolation**: Caches are isolated between organizations. Different organizations never share caches, even if they use identical prompts.
* **Exact Matching**: Cache hits require 100% identical prompt segments, including all text and images up to and including the block marked with cache control.
* **Output Token Generation**: Prompt caching has no effect on output token generation. The response you receive will be identical to what you would get if prompt caching was not used.

# [​](#1-hour-cache-duration-beta) 1-hour cache duration (beta)

If you find that 5 minutes is too short, Anthropic also offers a 1-hour cache duration.

To use the extended cache, add `extended-cache-ttl-2025-04-11` as a [beta header](/en/api/beta-headers) to your request, and then include `ttl` in the `cache_control` definition like this:

```
"cache_control": {
    "type": "ephemeral",
    "ttl": "5m" | "1h"
}

```

The response will include detailed cache information like the following:

```
{
    "usage": {
        "input_tokens": ...,
        "cache_read_input_tokens": ...,
        "cache_creation_input_tokens": ...,
        "output_tokens": ...,

        "cache_creation": {
            "ephemeral_5m_input_tokens": 456,
            "ephemeral_1h_input_tokens": 100,
        }
    }
}

```

Note that the current `cache_creation_input_tokens` field equals the sum of the values in the `cache_creation` object.

# [​](#when-to-use-the-1-hour-cache) When to use the 1-hour cache

If you have prompts that are used at a regular cadence (i.e., system prompts that are used more frequently than every 5 minutes), continue to use the 5-minute cache, since this will continue to be refreshed at no additional charge.

The 1-hour cache is best used in the following scenarios:

* When you have prompts that are likely used less frequently than 5 minutes, but more frequently than every hour. For example, when an agentic side-agent will take longer than 5 minutes, or when storing a long chat conversation with a user and you generally expect that user may not respond in the next 5 minutes.
* When latency is important and your follow up prompts may be sent beyond 5 minutes.
* When you want to improve your rate limit utilization, since cache hits are not deducted against your rate limit.

The 5-minute and 1-hour cache behave the same with respect to latency. You will generally see improved time-to-first-token for long documents.

# [​](#mixing-different-ttls) Mixing different TTLs

You can use both 1-hour and 5-minute cache controls in the same request, but with an important constraint: Cache entries with longer TTL must appear before shorter TTLs (i.e., a 1-hour cache entry must appear before any 5-minute cache entries).

When mixing TTLs, we determine three billing locations in your prompt:

1. Position `A`: The token count at the highest cache hit (or 0 if no hits).
2. Position `B`: The token count at the highest 1-hour `cache_control` block after `A` (or equals `A` if none exist).
3. Position `C`: The token count at the last `cache_control` block.

If `B` and/or `C` are larger than `A`, they will necessarily be cache misses, because `A` is the highest cache hit.

You’ll be charged for:

1. Cache read tokens for `A`.
2. 1-hour cache write tokens for `(B - A)`.
3. 5-minute cache write tokens for `(C - B)`.

Here are 3 examples. This depicts the input tokens of 3 requests, each of which has different cache hits and cache misses. Each has a different calculated pricing, shown in the colored boxes, as a result.

# [​](#prompt-caching-examples) Prompt caching examples

To help you get started with prompt caching, we’ve prepared a [prompt caching cookbook](https://github.com/anthropics/anthropic-cookbook/blob/main/misc/prompt_caching.ipynb) with detailed examples and best practices.

Below, we’ve included several code snippets that showcase various prompt caching patterns. These examples demonstrate how to implement caching in different scenarios, helping you understand the practical applications of this feature:

Large context caching example

Shell

Python

TypeScript

Java

```
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data \
'{
    "model": "claude-opus-4-20250514",
    "max_tokens": 1024,
    "system": [
        {
            "type": "text",
            "text": "You are an AI assistant tasked with analyzing legal documents."
        },
        {
            "type": "text",
            "text": "Here is the full text of a complex legal agreement: [Insert full text of a 50-page legal agreement here]",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    "messages": [
        {
            "role": "user",
            "content": "What are the key terms and conditions in this agreement?"
        }
    ]
}'

```

This example demonstrates basic prompt caching usage, caching the full text of the legal agreement as a prefix while keeping the user instruction uncached.

For the first request:

* `input_tokens`: Number of tokens in the user message only
* `cache_creation_input_tokens`: Number of tokens in the entire system message, including the legal document
* `cache_read_input_tokens`: 0 (no cache hit on first request)

For subsequent requests within the cache lifetime:

* `input_tokens`: Number of tokens in the user message only
* `cache_creation_input_tokens`: 0 (no new cache creation)
* `cache_read_input_tokens`: Number of tokens in the entire cached system message

Caching tool definitions

Shell

Python

TypeScript

Java

```
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data \
'{
    "model": "claude-opus-4-20250514",
    "max_tokens": 1024,
    "tools": [
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The unit of temperature, either celsius or fahrenheit"
                    }
                },
                "required": ["location"]
            }
        },
        # many more tools
        {
            "name": "get_time",
            "description": "Get the current time in a given time zone",
            "input_schema": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The IANA time zone name, e.g. America/Los_Angeles"
                    }
                },
                "required": ["timezone"]
            },
            "cache_control": {"type": "ephemeral"}
        }
    ],
    "messages": [
        {
            "role": "user",
            "content": "What is the weather and time in New York?"
        }
    ]
}'

```

In this example, we demonstrate caching tool definitions.

The `cache_control` parameter is placed on the final tool (`get_time`) to designate all of the tools as part of the static prefix.

This means that all tool definitions, including `get_weather` and any other tools defined before `get_time`, will be cached as a single prefix.

This approach is useful when you have a consistent set of tools that you want to reuse across multiple requests without re-processing them each time.

For the first request:

* `input_tokens`: Number of tokens in the user message
* `cache_creation_input_tokens`: Number of tokens in all tool definitions and system prompt
* `cache_read_input_tokens`: 0 (no cache hit on first request)

For subsequent requests within the cache lifetime:

* `input_tokens`: Number of tokens in the user message
* `cache_creation_input_tokens`: 0 (no new cache creation)
* `cache_read_input_tokens`: Number of tokens in all cached tool definitions and system prompt

Continuing a multi-turn conversation

Shell

Python

TypeScript

Java

```
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data \
'{
    "model": "claude-opus-4-20250514",
    "max_tokens": 1024,
    "system": [
        {
            "type": "text",
            "text": "...long system prompt",
            "cache_control": {"type": "ephemeral"}
        }
    ],
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Hello, can you tell me more about the solar system?",
                }
            ]
        },
        {
            "role": "assistant",
            "content": "Certainly! The solar system is the collection of celestial bodies that orbit our Sun. It consists of eight planets, numerous moons, asteroids, comets, and other objects. The planets, in order from closest to farthest from the Sun, are: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune. Each planet has its own unique characteristics and features. Is there a specific aspect of the solar system you would like to know more about?"
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Good to know."
                },
                {
                    "type": "text",
                    "text": "Tell me more about Mars.",
                    "cache_control": {"type": "ephemeral"}
                }
            ]
        }
    ]
}'

```

In this example, we demonstrate how to use prompt caching in a multi-turn conversation.

During each turn, we mark the final block of the final message with `cache_control` so the conversation can be incrementally cached. The system will automatically lookup and use the longest previously cached prefix for follow-up messages. That is, blocks that were previously marked with a `cache_control` block are later not marked with this, but they will still be considered a cache hit (and also a cache refresh!) if they are hit within 5 minutes.

In addition, note that the `cache_control` parameter is placed on the system message. This is to ensure that if this gets evicted from the cache (after not being used for more than 5 minutes), it will get added back to the cache on the next request.

This approach is useful for maintaining context in ongoing conversations without repeatedly processing the same information.

When this is set up properly, you should see the following in the usage response of each request:

* `input_tokens`: Number of tokens in the new user message (will be minimal)
* `cache_creation_input_tokens`: Number of tokens in the new assistant and user turns
* `cache_read_input_tokens`: Number of tokens in the conversation up to the previous turn

# [​](#faq) FAQ

What is the cache lifetime?

The cache has a minimum lifetime (TTL) of 5 minutes. This lifetime is refreshed each time the cached content is used.

How many cache breakpoints can I use?

You can define up to 4 cache breakpoints (using `cache_control` parameters) in your prompt.

Is prompt caching available for all models?

No, prompt caching is currently only available for Claude Opus 4, Claude Sonnet 4, Claude Sonnet 3.7, Claude Sonnet 3.5, Claude Haiku 3.5, Claude Haiku 3, and Claude Opus 3.

How does prompt caching work with extended thinking?

Cached system prompts and tools will be reused when thinking parameters change. However, thinking changes (enabling/disabling or budget changes) will invalidate previously cached prompt prefixes with messages content.

For more detailed information about extended thinking, including its interaction with tool use and prompt caching, see the [extended thinking documentation](/en/docs/build-with-claude/extended-thinking#extended-thinking-and-prompt-caching).

How do I enable prompt caching?

Yes, prompt caching can be used alongside other API features like tool use and vision capabilities. However, changing whether there are images in a prompt or modifying tool use settings will break the cache.

How does prompt caching affect pricing?

Prompt caching introduces a new pricing structure where cache writes cost 25% more than base input tokens, while cache hits cost only 10% of the base input token price.

Can I manually clear the cache?

Currently, there’s no way to manually clear the cache. Cached prefixes automatically expire after a minimum of 5 minutes of inactivity.

How can I track the effectiveness of my caching strategy?

You can monitor cache performance using the `cache_creation_input_tokens` and `cache_read_input_tokens` fields in the API response.

What can break the cache?

Changes that can break the cache include modifying any content, changing whether there are any images (anywhere in the prompt), and altering `tool_choice.type`. Any of these changes will require creating a new cache entry.

How does prompt caching handle privacy and data separation?

Prompt caching is designed with strong privacy and data separation measures:

1. Cache keys are generated using a cryptographic hash of the prompts up to the cache control point. This means only requests with identical prompts can access a specific cache.
2. Caches are organization-specific. Users within the same organization can access the same cache if they use identical prompts, but caches are not shared across different organizations, even for identical prompts.
3. The caching mechanism is designed to maintain the integrity and privacy of each unique conversation or context.
4. It’s safe to use `cache_control` anywhere in your prompts. For cost efficiency, it’s better to exclude highly variable parts (e.g., user’s arbitrary input) from caching.

These measures ensure that prompt caching maintains data privacy and security while offering performance benefits.

Yes, it is possible to use prompt caching with your [Batches API](/en/docs/build-with-claude/batch-processing) requests. However, because asynchronous batch requests can be processed concurrently and in any order, cache hits are provided on a best-effort basis.

The [1-hour cache](/_sites/docs.anthropic.com/en/docs/build-with-claude/prompt-caching#1-hour-cache-beta) can help improve your cache hits. The most cost effective way of using it is the following:

* Gather a set of message requests that have a shared prefix.
* Send a batch request with just a single request that has this shared prefix and a 1-hour cache block. This will get written to the 1-hour cache.
* As soon as this is complete, submit the rest of the requests. You will have to monitor the job to know when it completes.

This is typically better than using the 5-minute cache simply because it’s common for batch requests to take between 5 minutes and 1 hour to complete. We’re considering ways to improve these cache hit rates and making this process more straightforward.

Why am I seeing the error `AttributeError: 'Beta' object has no attribute 'prompt\_caching'` in Python?

This error typically appears when you have upgraded your SDK or you are using outdated code examples. Prompt caching is now generally available, so you no longer need the beta prefix. Instead of:

Python

```
python client.beta.prompt_caching.messages.create(...)

```

Simply use:

Python

```
python client.messages.create(...)

```

Why am I seeing 'TypeError: Cannot read properties of undefined (reading 'messages')'?

This error typically appears when you have upgraded your SDK or you are using outdated code examples. Prompt caching is now generally available, so you no longer need the beta prefix. Instead of:

TypeScript

```
client.beta.promptCaching.messages.create(...)

```

Simply use:

```
client.messages.create(...)

```

Was this page helpful?

YesNo

Features overview[Extended thinking](/en/docs/build-with-claude/extended-thinking)

On this page
