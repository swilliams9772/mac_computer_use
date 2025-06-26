# Building with extended thinking - Anthropic

**Source:** https://docs.anthropic.com/en/docs/about-claude/models/extended-thinking-models#getting-started-with-extended-thinking-models

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

Extended thinking gives Claude enhanced reasoning capabilities for complex tasks, while providing varying levels of transparency into its step-by-step thought process before it delivers its final answer.

# [​](#supported-models) Supported models

Extended thinking is supported in the following models:

* Claude Opus 4 (`claude-opus-4-20250514`)
* Claude Sonnet 4 (`claude-sonnet-4-20250514`)
* Claude Sonnet 3.7 (`claude-3-7-sonnet-20250219`)

API behavior differs across Claude 3.7 and Claude 4 models, but the API shapes remain exactly the same.

For more information, see [Differences in thinking across model versions](/_sites/docs.anthropic.com/en/docs/build-with-claude/extended-thinking#differences-in-thinking-across-model-versions).

# [​](#how-extended-thinking-works) How extended thinking works

When extended thinking is turned on, Claude creates `thinking` content blocks where it outputs its internal reasoning. Claude incorporates insights from this reasoning before crafting a final response.

The API response will include `thinking` content blocks, followed by `text` content blocks.

Here’s an example of the default response format:

```
{
  "content": [
    {
      "type": "thinking",
      "thinking": "Let me analyze this step by step...",
      "signature": "WaUjzkypQ2mUEVM36O2TxuC06KN8xyfbJwyem2dw3URve/op91XWHOEBLLqIOMfFG/UvLEczmEsUjavL...."
    },
    {
      "type": "text",
      "text": "Based on my analysis..."
    }
  ]
}

```

For more information about the response format of extended thinking, see the [Messages API Reference](/en/api/messages).

# [​](#how-to-use-extended-thinking) How to use extended thinking

Here is an example of using extended thinking in the Messages API:

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
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 16000,
    "thinking": {
        "type": "enabled",
        "budget_tokens": 10000
    },
    "messages": [
        {
            "role": "user",
            "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?"
        }
    ]
}'

```

To turn on extended thinking, add a `thinking` object, with the `thinking` parameter set to `enabled` and the `budget_tokens` to a specified token budget for extended thinking.

The `budget_tokens` parameter determines the maximum number of tokens Claude is allowed to use for its internal reasoning process. In Claude 4 models, this limit applies to full thinking tokens, and not to [the summarized output](/_sites/docs.anthropic.com/en/docs/build-with-claude/extended-thinking#summarized-thinking). Larger budgets can improve response quality by enabling more thorough analysis for complex problems, although Claude may not use the entire budget allocated, especially at ranges above 32k.

`budget_tokens` must be set to a value less than `max_tokens`. However, when using [interleaved thinking with tools](/_sites/docs.anthropic.com/en/docs/build-with-claude/extended-thinking#interleaved-thinking), you can exceed this limit as the token limit becomes your entire context window (200k tokens).

# [​](#summarized-thinking) Summarized thinking

With extended thinking enabled, the Messages API for Claude 4 models returns a summary of Claude’s full thinking process. Summarized thinking provides the full intelligence benefits of extended thinking, while preventing misuse.

Here are some important considerations for summarized thinking:

* You’re charged for the full thinking tokens generated by the original request, not the summary tokens.
* The billed output token count will **not match** the count of tokens you see in the response.
* The first few lines of thinking output are more verbose, providing detailed reasoning that’s particularly helpful for prompt engineering purposes.
* As Anthropic seeks to improve the extended thinking feature, summarization behavior is subject to change.
* Summarization preserves the key ideas of Claude’s thinking process with minimal added latency, enabling a streamable user experience and easy migration from Claude 3.7 models to Claude 4 models.
* Summarization is processed by a different model than the one you target in your requests. The thinking model does not see the summarized output.

Claude Sonnet 3.7 continues to return full thinking output.

In rare cases where you need access to full thinking output for Claude 4 models, [contact our sales team](mailto:sales@anthropic.com).

# [​](#streaming-thinking) Streaming thinking

You can stream extended thinking responses using [server-sent events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent%5Fevents/Using%5Fserver-sent%5Fevents).

When streaming is enabled for extended thinking, you receive thinking content via `thinking_delta` events.

For more documention on streaming via the Messages API, see [Streaming Messages](/en/api/messages-streaming).

Here’s how to handle streaming with thinking:

Shell

Python

TypeScript

Java

[Try in Console](https://console.anthropic.com/workbench/new?user=What+is+27+*+453%3F&thinking.budget_tokens=16000)

```
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data \
'{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 16000,
    "stream": true,
    "thinking": {
        "type": "enabled",
        "budget_tokens": 10000
    },
    "messages": [
        {
            "role": "user",
            "content": "What is 27 * 453?"
        }
    ]
}'

```

Example streaming output:

```
event: message_start
data: {"type": "message_start", "message": {"id": "msg_01...", "type": "message", "role": "assistant", "content": [], "model": "claude-sonnet-4-20250514", "stop_reason": null, "stop_sequence": null}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "thinking", "thinking": ""}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "Let me solve this step by step:\n\n1. First break down 27 * 453"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "thinking_delta", "thinking": "\n2. 453 = 400 + 50 + 3"}}

// Additional thinking deltas...

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "signature_delta", "signature": "EqQBCgIYAhIM1gbcDa9GJwZA2b3hGgxBdjrkzLoky3dl1pkiMOYds..."}}

event: content_block_stop
data: {"type": "content_block_stop", "index": 0}

event: content_block_start
data: {"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": ""}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 1, "delta": {"type": "text_delta", "text": "27 * 453 = 12,231"}}

// Additional text deltas...

event: content_block_stop
data: {"type": "content_block_stop", "index": 1}

event: message_delta
data: {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": null}}

event: message_stop
data: {"type": "message_stop"}

```

When using streaming with thinking enabled, you might notice that text sometimes arrives in larger chunks alternating with smaller, token-by-token delivery. This is expected behavior, especially for thinking content.

The streaming system needs to process content in batches for optimal performance, which can result in this “chunky” delivery pattern, with possible delays between streaming events. We’re continuously working to improve this experience, with future updates focused on making thinking content stream more smoothly.

# [​](#extended-thinking-with-tool-use) Extended thinking with tool use

Extended thinking can be used alongside [tool use](/en/docs/build-with-claude/tool-use), allowing Claude to reason through tool selection and results processing.

When using extended thinking with tool use, be aware of the following limitations:

1. **Tool choice limitation**: Tool use with thinking only supports `tool_choice: {"type": "auto"}` (the default) or `tool_choice: {"type": "none"}`. Using `tool_choice: {"type": "any"}` or `tool_choice: {"type": "tool", "name": "..."}` will result in an error because these options force tool use, which is incompatible with extended thinking.
2. **Preserving thinking blocks**: During tool use, you must pass `thinking` blocks back to the API for the last assistant message. Include the complete unmodified block back to the API to maintain reasoning continuity.

Example: Passing thinking blocks with tool results

Here’s a practical example showing how to preserve thinking blocks when providing tool results:

Python

TypeScript

Java

```
weather_tool = {
    "name": "get_weather",
    "description": "Get current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}

# First request - Claude responds with thinking and tool request

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[weather_tool],
    messages=[
        {"role": "user", "content": "What's the weather in Paris?"}
    ]
)

```

The API response will include thinking, text, and tool\_use blocks:

```
{
    "content": [
        {
            "type": "thinking",
            "thinking": "The user wants to know the current weather in Paris. I have access to a function `get_weather`...",
            "signature": "BDaL4VrbR2Oj0hO4XpJxT28J5TILnCrrUXoKiiNBZW9P+nr8XSj1zuZzAl4egiCCpQNvfyUuFFJP5CncdYZEQPPmLxYsNrcs...."
        },
        {
            "type": "text",
            "text": "I can help you get the current weather information for Paris. Let me check that for you"
        },
        {
            "type": "tool_use",
            "id": "toolu_01CswdEQBMshySk6Y9DFKrfq",
            "name": "get_weather",
            "input": {
                "location": "Paris"
            }
        }
    ]
}

```

Now let’s continue the conversation and use the tool

Python

TypeScript

Java

```
# Extract thinking block and tool use block

thinking_block = next((block for block in response.content
                      if block.type == 'thinking'), None)
tool_use_block = next((block for block in response.content
                      if block.type == 'tool_use'), None)

# Call your actual weather API, here is where your actual API call would go

# let's pretend this is what we get back
weather_data = {"temperature": 88}

# Second request - Include thinking block and tool result

# No new thinking blocks will be generated in the response
continuation = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[weather_tool],
    messages=[
        {"role": "user", "content": "What's the weather in Paris?"},
        # notice that the thinking_block is passed in as well as the tool_use_block
        # if this is not passed in, an error is raised
        {"role": "assistant", "content": [thinking_block, tool_use_block]},
        {"role": "user", "content": [{
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": f"Current temperature: {weather_data['temperature']}°F"
        }]}
    ]
)

```

The API response will now **only** include text

```
{
    "content": [
        {
            "type": "text",
            "text": "Currently in Paris, the temperature is 88°F (31°C)"
        }
    ]
}

```

# [​](#preserving-thinking-blocks) Preserving thinking blocks

During tool use, you must pass `thinking` blocks back to the API, and you must include the complete unmodified block back to the API. This is critical for maintaining the model’s reasoning flow and conversation integrity.

While you can omit `thinking` blocks from prior `assistant` role turns, we suggest always passing back all thinking blocks to the API for any multi-turn conversation. The API will:

* Automatically filter the provided thinking blocks
* Use the relevant thinking blocks necessary to preserve the model’s reasoning
* Only bill for the input tokens for the blocks shown to Claude

When Claude invokes tools, it is pausing its construction of a response to await external information. When tool results are returned, Claude will continue building that existing response. This necessitates preserving thinking blocks during tool use, for a couple of reasons:

1. **Reasoning continuity**: The thinking blocks capture Claude’s step-by-step reasoning that led to tool requests. When you post tool results, including the original thinking ensures Claude can continue its reasoning from where it left off.
2. **Context maintenance**: While tool results appear as user messages in the API structure, they’re part of a continuous reasoning flow. Preserving thinking blocks maintains this conceptual flow across multiple API calls. For more information on context management, see our [guide on context windows](/en/docs/context-windows).

**Important**: When providing `thinking` blocks, the entire sequence of consecutive `thinking` blocks must match the outputs generated by the model during the original request; you cannot rearrange or modify the sequence of these blocks.

# [​](#interleaved-thinking) Interleaved thinking

Extended thinking with tool use in Claude 4 models supports interleaved thinking, which enables Claude to think between tool calls and make more sophisticated reasoning after receiving tool results.

With interleaved thinking, Claude can:

* Reason about the results of a tool call before deciding what to do next
* Chain multiple tool calls with reasoning steps in between
* Make more nuanced decisions based on intermediate results

To enable interleaved thinking, add [the beta header](/en/api/beta-headers) `interleaved-thinking-2025-05-14` to your API request.

Here are some important considerations for interleaved thinking:

* With interleaved thinking, the `budget_tokens` can exceed the `max_tokens` parameter, as it represents the total budget across all thinking blocks within one assistant turn.
* Interleaved thinking is only supported for [tools used via the Messages API](/en/docs/build-with-claude/tool-use/overview).
* Interleaved thinking is supported for Claude 4 models only, with the beta header `interleaved-thinking-2025-05-14`.
* Direct calls to Anthropic’s API allow you to pass `interleaved-thinking-2025-05-14` in requests to any model, with no effect.
* On 3rd-party platforms (e.g., [Amazon Bedrock](/en/api/claude-on-amazon-bedrock) and [Vertex AI](/en/api/claude-on-vertex-ai)), if you pass `interleaved-thinking-2025-05-14` to any model aside from Claude Opus 4 or Sonnet 4, your request will fail.

Tool use without interleaved thinking

Python

TypeScript

Java

```
import anthropic

client = anthropic.Anthropic()

# Define tools

calculator_tool = {
    "name": "calculator",
    "description": "Perform mathematical calculations",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    }
}

database_tool = {
    "name": "database_query",
    "description": "Query product database",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute"
            }
        },
        "required": ["query"]
    }
}

# First request - Claude thinks once before all tool calls

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[calculator_tool, database_tool],
    messages=[{
        "role": "user",
        "content": "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
    }]
)

# Response includes thinking followed by tool uses

# Note: Claude thinks once at the beginning, then makes all tool decisions
print("First response:")
for block in response.content:
    if block.type == "thinking":
        print(f"Thinking (summarized): {block.thinking}")
    elif block.type == "tool_use":
        print(f"Tool use: {block.name} with input {block.input}")
    elif block.type == "text":
        print(f"Text: {block.text}")

# You would execute the tools and return results...

# After getting both tool results back, Claude directly responds without additional thinking

```

In this example without interleaved thinking:

1. Claude thinks once at the beginning to understand the task
2. Makes all tool use decisions upfront
3. When tool results are returned, Claude immediately provides a response without additional thinking

Tool use with interleaved thinking

Python

TypeScript

Java

```
import anthropic

client = anthropic.Anthropic()

# Same tool definitions as before

calculator_tool = {
    "name": "calculator",
    "description": "Perform mathematical calculations",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    }
}

database_tool = {
    "name": "database_query",
    "description": "Query product database",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute"
            }
        },
        "required": ["query"]
    }
}

# First request with interleaved thinking enabled

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[calculator_tool, database_tool],
    # Enable interleaved thinking with beta header
    extra_headers={
        "anthropic-beta": "interleaved-thinking-2025-05-14"
    },
    messages=[{
        "role": "user",
        "content": "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
    }]
)

print("Initial response:")
thinking_blocks = []
tool_use_blocks = []

for block in response.content:
    if block.type == "thinking":
        thinking_blocks.append(block)
        print(f"Thinking: {block.thinking}")
    elif block.type == "tool_use":
        tool_use_blocks.append(block)
        print(f"Tool use: {block.name} with input {block.input}")
    elif block.type == "text":
        print(f"Text: {block.text}")

# First tool result (calculator)

calculator_result = "7500"  # 150 * 50

# Continue with first tool result

response2 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[calculator_tool, database_tool],
    extra_headers={
        "anthropic-beta": "interleaved-thinking-2025-05-14"
    },
    messages=[
        {
            "role": "user",
            "content": "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
        },
        {
            "role": "assistant",
            "content": [thinking_blocks[0], tool_use_blocks[0]]
        },
        {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_blocks[0].id,
                "content": calculator_result
            }]
        }
    ]
)

print("\nAfter calculator result:")
# With interleaved thinking, Claude can think about the calculator result

# before deciding to query the database
for block in response2.content:
    if block.type == "thinking":
        thinking_blocks.append(block)
        print(f"Interleaved thinking: {block.thinking}")
    elif block.type == "tool_use":
        tool_use_blocks.append(block)
        print(f"Tool use: {block.name} with input {block.input}")

# Second tool result (database)

database_result = "5200"  # Example average monthly revenue

# Continue with second tool result

response3 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    tools=[calculator_tool, database_tool],
    extra_headers={
        "anthropic-beta": "interleaved-thinking-2025-05-14"
    },
    messages=[
        {
            "role": "user",
            "content": "What's the total revenue if we sold 150 units of product A at $50 each, and how does this compare to our average monthly revenue from the database?"
        },
        {
            "role": "assistant",
            "content": [thinking_blocks[0], tool_use_blocks[0]]
        },
        {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_blocks[0].id,
                "content": calculator_result
            }]
        },
        {
            "role": "assistant",
            "content": thinking_blocks[1:] + tool_use_blocks[1:]
        },
        {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_blocks[1].id,
                "content": database_result
            }]
        }
    ]
)

print("\nAfter database result:")
# With interleaved thinking, Claude can think about both results

# before formulating the final response
for block in response3.content:
    if block.type == "thinking":
        print(f"Final thinking: {block.thinking}")
    elif block.type == "text":
        print(f"Final response: {block.text}")

```

In this example with interleaved thinking:

1. Claude thinks about the task initially
2. After receiving the calculator result, Claude can think again about what that result means
3. Claude then decides how to query the database based on the first result
4. After receiving the database result, Claude thinks once more about both results before formulating a final response
5. The thinking budget is distributed across all thinking blocks within the turn

This pattern allows for more sophisticated reasoning chains where each tool’s output informs the next decision.

# [​](#extended-thinking-with-prompt-caching) Extended thinking with prompt caching

[Prompt caching](/en/docs/build-with-claude/prompt-caching) with thinking has several important considerations:

**Thinking block context removal**

* Thinking blocks from previous turns are removed from context, which can affect cache breakpoints
* When continuing conversations with tool use, thinking blocks are cached and count as input tokens when read from cache
* This creates a tradeoff: while thinking blocks don’t consume context window space visually, they still count toward your input token usage when cached
* If thinking becomes disabled, requests will fail if you pass thinking content in the current tool use turn. In other contexts, thinking content passed to the API is simply ignored

**Cache invalidation patterns**

* Changes to thinking parameters (enabled/disabled or budget allocation) invalidate message cache breakpoints
* [Interleaved thinking](/_sites/docs.anthropic.com/en/docs/build-with-claude/extended-thinking#interleaved-thinking) amplifies cache invalidation, as thinking blocks can occur between multiple [tool calls](/_sites/docs.anthropic.com/en/docs/build-with-claude/extended-thinking#extended-thinking-with-tool-use)
* System prompts and tools remain cached despite thinking parameter changes or block removal

While thinking blocks are removed for caching and context calculations, they must be preserved when continuing conversations with [tool use](/_sites/docs.anthropic.com/en/docs/build-with-claude/extended-thinking#extended-thinking-with-tool-use), especially with [interleaved thinking](/_sites/docs.anthropic.com/en/docs/build-with-claude/extended-thinking#interleaved-thinking).

# [​](#understanding-thinking-block-caching-behavior) Understanding thinking block caching behavior

When using extended thinking with tool use, thinking blocks exhibit specific caching behavior that affects token counting:

**How it works:**

1. Caching only occurs when you make a subsequent request that includes tool results
2. When the subsequent request is made, the previous conversation history (including thinking blocks) can be cached
3. These cached thinking blocks count as input tokens in your usage metrics when read from the cache
4. When a non-tool-result user block is included, all previous thinking blocks are ignored and stripped from context

**Detailed example flow:**

**Request 1:**

```
User: "What's the weather in Paris?"

```

**Response 1:**

```
[thinking_block_1] + [tool_use block 1]

```

**Request 2:**

```
User: ["What's the weather in Paris?"],
Assistant: [thinking_block_1] + [tool_use block 1],
User: [tool_result_1, cache=True]

```

**Response 2:**

```
[thinking_block_2] + [text block 2]

```

Request 2 writes a cache of the request content (not the response). The cache includes the original user message, the first thinking block, tool use block, and the tool result.

**Request 3:**

```
User: ["What's the weather in Paris?"],
Assistant: [thinking_block_1] + [tool_use block 1],
User: [tool_result_1, cache=True],
Assistant: [thinking_block_2] + [text block 2],
User: [Text response, cache=True]

```

Because a non-tool-result user block was included, all previous thinking blocks are ignored. This request will be processed the same as:

```
User: ["What's the weather in Paris?"],
Assistant: [tool_use block 1],
User: [tool_result_1, cache=True],
Assistant: [text block 2],
User: [Text response, cache=True]

```

**Key points:**

* This caching behavior happens automatically, even without explicit `cache_control` markers
* This behavior is consistent whether using regular thinking or interleaved thinking

System prompt caching (preserved when thinking changes)

Python

TypeScript

```
from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup

client = Anthropic()

def fetch_article_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

# Fetch the content of the article

book_url = "https://www.gutenberg.org/cache/epub/1342/pg1342.txt"
book_content = fetch_article_content(book_url)
# Use just enough text for caching (first few chapters)

LARGE_TEXT = book_content[:5000]

SYSTEM_PROMPT=[
    {
        "type": "text",
        "text": "You are an AI assistant that is tasked with literary analysis. Analyze the following text carefully.",
    },
    {
        "type": "text",
        "text": LARGE_TEXT,
        "cache_control": {"type": "ephemeral"}
    }
]

MESSAGES = [
    {
        "role": "user",
        "content": "Analyze the tone of this passage."
    }
]

# First request - establish cache

print("First request - establishing cache")
response1 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 4000
    },
    system=SYSTEM_PROMPT,
    messages=MESSAGES
)

print(f"First response usage: {response1.usage}")

MESSAGES.append({
    "role": "assistant",
    "content": response1.content
})
MESSAGES.append({
    "role": "user",
    "content": "Analyze the characters in this passage."
})
# Second request - same thinking parameters (cache hit expected)

print("\nSecond request - same thinking parameters (cache hit expected)")
response2 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 4000
    },
    system=SYSTEM_PROMPT,
    messages=MESSAGES
)

print(f"Second response usage: {response2.usage}")

# Third request - different thinking parameters (cache miss for messages)

print("\nThird request - different thinking parameters (cache miss for messages)")
response3 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 8000  # Changed thinking budget
    },
    system=SYSTEM_PROMPT,  # System prompt remains cached
    messages=MESSAGES  # Messages cache is invalidated
)

print(f"Third response usage: {response3.usage}")

```

Messages caching (invalidated when thinking changes)

Python

TypeScript

Java

```
from anthropic import Anthropic
import requests
from bs4 import BeautifulSoup

client = Anthropic()

def fetch_article_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # Drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text

# Fetch the content of the article

book_url = "https://www.gutenberg.org/cache/epub/1342/pg1342.txt"
book_content = fetch_article_content(book_url)
# Use just enough text for caching (first few chapters)

LARGE_TEXT = book_content[:5000]

# No system prompt - caching in messages instead

MESSAGES = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": LARGE_TEXT,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": "Analyze the tone of this passage."
            }
        ]
    }
]

# First request - establish cache

print("First request - establishing cache")
response1 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 4000
    },
    messages=MESSAGES
)

print(f"First response usage: {response1.usage}")

MESSAGES.append({
    "role": "assistant",
    "content": response1.content
})
MESSAGES.append({
    "role": "user",
    "content": "Analyze the characters in this passage."
})
# Second request - same thinking parameters (cache hit expected)

print("\nSecond request - same thinking parameters (cache hit expected)")
response2 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 4000  # Same thinking budget
    },
    messages=MESSAGES
)

print(f"Second response usage: {response2.usage}")

MESSAGES.append({
    "role": "assistant",
    "content": response2.content
})
MESSAGES.append({
    "role": "user",
    "content": "Analyze the setting in this passage."
})

# Third request - different thinking budget (cache miss expected)

print("\nThird request - different thinking budget (cache miss expected)")
response3 = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=20000,
    thinking={
        "type": "enabled",
        "budget_tokens": 8000  # Different thinking budget breaks cache
    },
    messages=MESSAGES
)

print(f"Third response usage: {response3.usage}")

```

Here is the output of the script (you may see slightly different numbers)

```
First request - establishing cache
First response usage: { cache_creation_input_tokens: 1370, cache_read_input_tokens: 0, input_tokens: 17, output_tokens: 700 }

Second request - same thinking parameters (cache hit expected)

Second response usage: { cache_creation_input_tokens: 0, cache_read_input_tokens: 1370, input_tokens: 303, output_tokens: 874 }

Third request - different thinking budget (cache miss expected)
Third response usage: { cache_creation_input_tokens: 1370, cache_read_input_tokens: 0, input_tokens: 747, output_tokens: 619 }

```

This example demonstrates that when caching is set up in the messages array, changing the thinking parameters (budget\_tokens increased from 4000 to 8000) **invalidates the cache**. The third request shows no cache hit with `cache_creation_input_tokens=1370` and `cache_read_input_tokens=0`, proving that message-based caching is invalidated when thinking parameters change.

# [​](#max-tokens-and-context-window-size-with-extended-thinking) Max tokens and context window size with extended thinking

In older Claude models (prior to Claude Sonnet 3.7), if the sum of prompt tokens and `max_tokens` exceeded the model’s context window, the system would automatically adjust `max_tokens` to fit within the context limit. This meant you could set a large `max_tokens` value and the system would silently reduce it as needed.

With Claude 3.7 and 4 models, `max_tokens` (which includes your thinking budget when thinking is enabled) is enforced as a strict limit. The system will now return a validation error if prompt tokens + `max_tokens` exceeds the context window size.

You can read through our [guide on context windows](/en/docs/context-windows) for a more thorough deep dive.

# [​](#the-context-window-with-extended-thinking) The context window with extended thinking

When calculating context window usage with thinking enabled, there are some considerations to be aware of:

* Thinking blocks from previous turns are stripped and not counted towards your context window
* Current turn thinking counts towards your `max_tokens` limit for that turn

The diagram below demonstrates the specialized token management when extended thinking is enabled:

The effective context window is calculated as:

```
context window =
  (current input tokens - previous thinking tokens) +
  (thinking tokens + encrypted thinking tokens + text output tokens)

```

We recommend using the [token counting API](/en/docs/build-with-claude/token-counting) to get accurate token counts for your specific use case, especially when working with multi-turn conversations that include thinking.

# [​](#the-context-window-with-extended-thinking-and-tool-use) The context window with extended thinking and tool use

When using extended thinking with tool use, thinking blocks must be explicitly preserved and returned with the tool results.

The effective context window calculation for extended thinking with tool use becomes:

```
context window =
  (current input tokens + previous thinking tokens + tool use tokens) +
  (thinking tokens + encrypted thinking tokens + text output tokens)

```

The diagram below illustrates token management for extended thinking with tool use:

# [​](#managing-tokens-with-extended-thinking) Managing tokens with extended thinking

Given the context window and `max_tokens` behavior with extended thinking Claude 3.7 and 4 models, you may need to:

* More actively monitor and manage your token usage
* Adjust `max_tokens` values as your prompt length changes
* Potentially use the [token counting endpoints](/en/docs/build-with-claude/token-counting) more frequently
* Be aware that previous thinking blocks don’t accumulate in your context window

This change has been made to provide more predictable and transparent behavior, especially as maximum token limits have increased significantly.

# [​](#thinking-encryption) Thinking encryption

Full thinking content is encrypted and returned in the `signature` field. This field is used to verify that thinking blocks were generated by Claude when passed back to the API.

It is only strictly necessary to send back thinking blocks when using [tools with extended thinking](/_sites/docs.anthropic.com/en/docs/build-with-claude/extended-thinking#extended-thinking-with-tool-use). Otherwise you can omit thinking blocks from previous turns, or let the API strip them for you if you pass them back.

If sending back thinking blocks, we recommend passing everything back as you received it for consistency and to avoid potential issues.

Here are some important considerations on thinking encryption:

* When [streaming responses](/_sites/docs.anthropic.com/en/docs/build-with-claude/extended-thinking#streaming-extended-thinking), the signature is added via a `signature_delta` inside a `content_block_delta` event just before the `content_block_stop` event.
* `signature` values are significantly longer in Claude 4 than in previous models.
* The `signature` field is an opaque field and should not be interpreted or parsed - it exists solely for verification purposes.
* `signature` values are compatible across platforms (Anthropic APIs, [Amazon Bedrock](/en/api/claude-on-amazon-bedrock), and [Vertex AI](/en/api/claude-on-vertex-ai)). Values generated on one platform will be compatible with another.

# [​](#thinking-redaction) Thinking redaction

Occasionally Claude’s internal reasoning will be flagged by our safety systems. When this occurs, we encrypt some or all of the `thinking` block and return it to you as a `redacted_thinking` block. `redacted_thinking` blocks are decrypted when passed back to the API, allowing Claude to continue its response without losing context.

When building customer-facing applications that use extended thinking:

* Be aware that redacted thinking blocks contain encrypted content that isn’t human-readable
* Consider providing a simple explanation like: “Some of Claude’s internal reasoning has been automatically encrypted for safety reasons. This doesn’t affect the quality of responses.”
* If showing thinking blocks to users, you can filter out redacted blocks while preserving normal thinking blocks
* Be transparent that using extended thinking features may occasionally result in some reasoning being encrypted
* Implement appropriate error handling to gracefully manage redacted thinking without breaking your UI

Here’s an example showing both normal and redacted thinking blocks:

```
{
  "content": [
    {
      "type": "thinking",
      "thinking": "Let me analyze this step by step...",
      "signature": "WaUjzkypQ2mUEVM36O2TxuC06KN8xyfbJwyem2dw3URve/op91XWHOEBLLqIOMfFG/UvLEczmEsUjavL...."
    },
    {
      "type": "redacted_thinking",
      "data": "EmwKAhgBEgy3va3pzix/LafPsn4aDFIT2Xlxh0L5L8rLVyIwxtE3rAFBa8cr3qpPkNRj2YfWXGmKDxH4mPnZ5sQ7vB9URj2pLmN3kF8/dW5hR7xJ0aP1oLs9yTcMnKVf2wRpEGjH9XZaBt4UvDcPrQ..."
    },
    {
      "type": "text",
      "text": "Based on my analysis..."
    }
  ]
}

```

Seeing redacted thinking blocks in your output is expected behavior. The model can still use this redacted reasoning to inform its responses while maintaining safety guardrails.

If you need to test redacted thinking handling in your application, you can use this special test string as your prompt: `ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB`

When passing `thinking` and `redacted_thinking` blocks back to the API in a multi-turn conversation, you must include the complete unmodified block back to the API for the last assistant turn. This is critical for maintaining the model’s reasoning flow. We suggest always passing back all thinking blocks to the API. For more details, see the [Preserving thinking blocks](/_sites/docs.anthropic.com/en/docs/build-with-claude/extended-thinking#preserving-thinking-blocks) section above.

Example: Working with redacted thinking blocks

This example demonstrates how to handle `redacted_thinking` blocks that may appear in responses when Claude’s internal reasoning contains content flagged by safety systems:

Python

TypeScript

Java

[Try in Console](https://console.anthropic.com/workbench/new?user=ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB&thinking.budget_tokens=16000)

```
import anthropic

client = anthropic.Anthropic()

# Using a special prompt that triggers redacted thinking (for demonstration purposes only)

response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000
    },
    messages=[{
        "role": "user",
        "content": "ANTHROPIC_MAGIC_STRING_TRIGGER_REDACTED_THINKING_46C9A13E193C177646C7398A98432ECCCE4C1253D5E2D82641AC0E52CC2876CB"
    }]
)

# Identify redacted thinking blocks

has_redacted_thinking = any(
    block.type == "redacted_thinking" for block in response.content
)

if has_redacted_thinking:
    print("Response contains redacted thinking blocks")
    # These blocks are still usable in subsequent requests

    # Extract all blocks (both redacted and non-redacted)
    all_thinking_blocks = [
        block for block in response.content
        if block.type in ["thinking", "redacted_thinking"]
    ]

    # When passing to subsequent requests, include all blocks without modification
    # This preserves the integrity of Claude's reasoning

    print(f"Found {len(all_thinking_blocks)} thinking blocks total")
    print(f"These blocks are still billable as output tokens")

```

# [​](#differences-in-thinking-across-model-versions) Differences in thinking across model versions

The Messages API handles thinking differently across Claude Sonnet 3.7 and Claude 4 models, primarily in redaction and summarization behavior.

See the table below for a condensed comparison:

| Feature | Claude Sonnet 3.7 | Claude 4 Models |
| --- | --- | --- |
| **Thinking Output** | Returns full thinking output | Returns summarized thinking |
| **Interleaved Thinking** | Not supported | Supported with `interleaved-thinking-2025-05-14` beta header |

# [​](#pricing) Pricing

Extended thinking uses the standard token pricing scheme:

| Model | Base Input Tokens | Cache Writes | Cache Hits | Output Tokens |
| --- | --- | --- | --- | --- |
| Claude Opus 4 | $15 / MTok | $18.75 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Sonnet 4 | $3 / MTok | $3.75 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 3.7 | $3 / MTok | $3.75 / MTok | $0.30 / MTok | $15 / MTok |

The thinking process incurs charges for:

* Tokens used during thinking (output tokens)
* Thinking blocks from the last assistant turn included in subsequent requests (input tokens)
* Standard text output tokens

When extended thinking is enabled, a specialized system prompt is automatically included to support this feature.

When using summarized thinking:

* **Input tokens**: Tokens in your original request (excludes thinking tokens from previous turns)
* **Output tokens (billed)**: The original thinking tokens that Claude generated internally
* **Output tokens (visible)**: The summarized thinking tokens you see in the response
* **No charge**: Tokens used to generate the summary

The billed output token count will **not** match the visible token count in the response. You are billed for the full thinking process, not the summary you see.

# [​](#best-practices-and-considerations-for-extended-thinking) Best practices and considerations for extended thinking

# [​](#working-with-thinking-budgets) Working with thinking budgets

* **Budget optimization:** The minimum budget is 1,024 tokens. We suggest starting at the minimum and increasing the thinking budget incrementally to find the optimal range for your use case. Higher token counts enable more comprehensive reasoning but with diminishing returns depending on the task. Increasing the budget can improve response quality at the tradeoff of increased latency. For critical tasks, test different settings to find the optimal balance. Note that the thinking budget is a target rather than a strict limit—actual token usage may vary based on the task.
* **Starting points:** Start with larger thinking budgets (16k+ tokens) for complex tasks and adjust based on your needs.
* **Large budgets:** For thinking budgets above 32k, we recommend using [batch processing](/en/docs/build-with-claude/batch-processing) to avoid networking issues. Requests pushing the model to think above 32k tokens causes long running requests that might run up against system timeouts and open connection limits.
* **Token usage tracking:** Monitor thinking token usage to optimize costs and performance.

# [​](#performance-considerations) Performance considerations

* **Response times:** Be prepared for potentially longer response times due to the additional processing required for the reasoning process. Factor in that generating thinking blocks may increase overall response time.
* **Streaming requirements:** Streaming is required when `max_tokens` is greater than 21,333. When streaming, be prepared to handle both thinking and text content blocks as they arrive.

# [​](#feature-compatibility) Feature compatibility

* Thinking isn’t compatible with `temperature` or `top_k` modifications as well as [forced tool use](/en/docs/build-with-claude/tool-use#forcing-tool-use).
* When thinking is enabled, you can set `top_p` to values between 1 and 0.95.
* You cannot pre-fill responses when thinking is enabled.
* Changes to the thinking budget invalidate cached prompt prefixes that include messages. However, cached system prompts and tool definitions will continue to work when thinking parameters change.

# [​](#usage-guidelines) Usage guidelines

* **Task selection:** Use extended thinking for particularly complex tasks that benefit from step-by-step reasoning like math, coding, and analysis.
* **Context handling:** You do not need to remove previous thinking blocks yourself. The Anthropic API automatically ignores thinking blocks from previous turns and they are not included when calculating context usage.
* **Prompt engineering:** Review our [extended thinking prompting tips](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips) if you want to maximize Claude’s thinking capabilities.

# [​](#next-steps) Next steps

[## Try the extended thinking cookbook

Explore practical examples of thinking in our cookbook.](https://github.com/anthropics/anthropic-cookbook/tree/main/extended_thinking)[## Extended thinking prompting tips

Learn prompt engineering best practices for extended thinking.](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips)

Was this page helpful?

YesNo

Prompt caching[Streaming Messages](/en/docs/build-with-claude/streaming)

On this page
