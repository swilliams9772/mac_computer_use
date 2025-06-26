# How to implement tool use - Anthropic

**Source:** https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use

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

  + [Overview](/en/docs/agents-and-tools/tool-use/overview)
  + [How to implement tool use](/en/docs/agents-and-tools/tool-use/implement-tool-use)
  + [Token-efficient tool use (beta)](/en/docs/agents-and-tools/tool-use/token-efficient-tool-use)
  + Client tools
  + Server tools
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

# [​](#choosing-a-model) Choosing a model

Generally, use Claude Opus 4, Claude Sonnet 4, Claude Sonnet 3.7, Claude Sonnet 3.5 or Claude Opus 3 for complex tools and ambiguous queries; they handle multiple tools better and seek clarification when needed.

Use Claude Haiku 3.5 or Claude Haiku 3 for straightforward tools, but note they may infer missing parameters.

If using Claude Sonnet 3.7 with tool use and extended thinking, refer to our guide [here](/en/docs/build-with-claude/extended-thinking) for more information.

# [​](#specifying-client-tools) Specifying client tools

Client tools (both Anthropic-defined and user-defined) are specified in the `tools` top-level parameter of the API request. Each tool definition includes:

| Parameter | Description |
| --- | --- |
| `name` | The name of the tool. Must match the regex `^[a-zA-Z0-9_-]{1,64}$`. |
| `description` | A detailed plaintext description of what the tool does, when it should be used, and how it behaves. |
| `input_schema` | A [JSON Schema](https://json-schema.org/) object defining the expected parameters for the tool. |

Example simple tool definition

JSON

```
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
        "description": "The unit of temperature, either 'celsius' or 'fahrenheit'"
      }
    },
    "required": ["location"]
  }
}

```

This tool, named `get_weather`, expects an input object with a required `location` string and an optional `unit` string that must be either “celsius” or “fahrenheit”.

# [​](#tool-use-system-prompt) Tool use system prompt

When you call the Anthropic API with the `tools` parameter, we construct a special system prompt from the tool definitions, tool configuration, and any user-specified system prompt. The constructed prompt is designed to instruct the model to use the specified tool(s) and provide the necessary context for the tool to operate properly:

```
In this environment you have access to a set of tools you can use to answer the user's question.
{{ FORMATTING INSTRUCTIONS }}
String and scalar parameters should be specified as is, while lists and objects should use JSON format. Note that spaces for string values are not stripped. The output is not expected to be valid XML and is parsed with regular expressions.
Here are the functions available in JSONSchema format:
{{ TOOL DEFINITIONS IN JSON SCHEMA }}
{{ USER SYSTEM PROMPT }}
{{ TOOL CONFIGURATION }}

```

# [​](#best-practices-for-tool-definitions) Best practices for tool definitions

To get the best performance out of Claude when using tools, follow these guidelines:

* **Provide extremely detailed descriptions.** This is by far the most important factor in tool performance. Your descriptions should explain every detail about the tool, including:
  + What the tool does
  + When it should be used (and when it shouldn’t)
  + What each parameter means and how it affects the tool’s behavior
  + Any important caveats or limitations, such as what information the tool does not return if the tool name is unclear. The more context you can give Claude about your tools, the better it will be at deciding when and how to use them. Aim for at least 3-4 sentences per tool description, more if the tool is complex.
* **Prioritize descriptions over examples.** While you can include examples of how to use a tool in its description or in the accompanying prompt, this is less important than having a clear and comprehensive explanation of the tool’s purpose and parameters. Only add examples after you’ve fully fleshed out the description.

Example of a good tool description

JSON

```
{
  "name": "get_stock_price",
  "description": "Retrieves the current stock price for a given ticker symbol. The ticker symbol must be a valid symbol for a publicly traded company on a major US stock exchange like NYSE or NASDAQ. The tool will return the latest trade price in USD. It should be used when the user asks about the current or most recent price of a specific stock. It will not provide any other information about the stock or company.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string",
        "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
      }
    },
    "required": ["ticker"]
  }
}

```

Example poor tool description

JSON

```
{
  "name": "get_stock_price",
  "description": "Gets the stock price for a ticker.",
  "input_schema": {
    "type": "object",
    "properties": {
      "ticker": {
        "type": "string"
      }
    },
    "required": ["ticker"]
  }
}

```

The good description clearly explains what the tool does, when to use it, what data it returns, and what the `ticker` parameter means. The poor description is too brief and leaves Claude with many open questions about the tool’s behavior and usage.

# [​](#controlling-claude%E2%80%99s-output) Controlling Claude’s output

# [​](#forcing-tool-use) Forcing tool use

In some cases, you may want Claude to use a specific tool to answer the user’s question, even if Claude thinks it can provide an answer without using a tool. You can do this by specifying the tool in the `tool_choice` field like so:

```
tool_choice = {"type": "tool", "name": "get_weather"}

```

When working with the tool\_choice parameter, we have four possible options:

* `auto` allows Claude to decide whether to call any provided tools or not. This is the default value when `tools` are provided.
* `any` tells Claude that it must use one of the provided tools, but doesn’t force a particular tool.
* `tool` allows us to force Claude to always use a particular tool.
* `none` prevents Claude from using any tools. This is the default value when no `tools` are provided.

This diagram illustrates how each option works:

Note that when you have `tool_choice` as `any` or `tool`, we will prefill the assistant message to force a tool to be used. This means that the models will not emit a chain-of-thought `text` content block before `tool_use` content blocks, even if explicitly asked to do so.

When using [extended thinking](/en/docs/build-with-claude/extended-thinking) with tool use, `tool_choice: {"type": "any"}` and `tool_choice: {"type": "tool", "name": "..."}` are not supported and will result in an error. Only `tool_choice: {"type": "auto"}` (the default) and `tool_choice: {"type": "none"}` are compatible with extended thinking.

Our testing has shown that this should not reduce performance. If you would like to keep chain-of-thought (particularly with Opus) while still requesting that the model use a specific tool, you can use `{"type": "auto"}` for `tool_choice` (the default) and add explicit instructions in a `user` message. For example: `What's the weather like in London? Use the get_weather tool in your response.`

# [​](#json-output) JSON output

Tools do not necessarily need to be client functions — you can use tools anytime you want the model to return JSON output that follows a provided schema. For example, you might use a `record_summary` tool with a particular schema. See [tool use examples](/en/docs/build-with-claude/tool-use#json-mode) for a full working example.

# [​](#chain-of-thought) Chain of thought

When using tools, Claude will often show its “chain of thought”, i.e. the step-by-step reasoning it uses to break down the problem and decide which tools to use. The Claude Opus 3 model will do this if `tool_choice` is set to `auto` (this is the default value, see [Forcing tool use](/_sites/docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#forcing-tool-use)), and Sonnet and Haiku can be prompted into doing it.

For example, given the prompt “What’s the weather like in San Francisco right now, and what time is it there?”, Claude might respond with:

JSON

```
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "<thinking>To answer this question, I will: 1. Use the get_weather tool to get the current weather in San Francisco. 2. Use the get_time tool to get the current time in the America/Los_Angeles timezone, which covers San Francisco, CA.</thinking>"
    },
    {
      "type": "tool_use",
      "id": "toolu_01A09q90qw90lq917835lq9",
      "name": "get_weather",
      "input": {"location": "San Francisco, CA"}
    }
  ]
}

```

This chain of thought gives insight into Claude’s reasoning process and can help you debug unexpected behavior.

With the Claude Sonnet 3 model, chain of thought is less common by default, but you can prompt Claude to show its reasoning by adding something like `"Before answering, explain your reasoning step-by-step in tags."` to the user message or system prompt.

It’s important to note that while the `<thinking>` tags are a common convention Claude uses to denote its chain of thought, the exact format (such as what this XML tag is named) may change over time. Your code should treat the chain of thought like any other assistant-generated text, and not rely on the presence or specific formatting of the `<thinking>` tags.

# [​](#parallel-tool-use) Parallel tool use

By default, Claude may use multiple tools to answer a user query. You can disable this behavior by:

* Setting `disable_parallel_tool_use=true` when tool\_choice type is `auto`, which ensures that Claude uses **at most one** tool
* Setting `disable_parallel_tool_use=true` when tool\_choice type is `any` or `tool`, which ensures that Claude uses **exactly one** tool

**Parallel tool use with Claude Sonnet 3.7**

Claude Sonnet 3.7 may be less likely to make make parallel tool calls in a response, even when you have not set `disable_parallel_tool_use`. To work around this, we recommend enabling [token-efficient tool use](/en/docs/build-with-claude/tool-use/token-efficient-tool-use), which helps encourage Claude to use parallel tools. This beta feature also reduces latency and saves an average of 14% in output tokens.

If you prefer not to opt into the token-efficient tool use beta, you can also introduce a “batch tool” that can act as a meta-tool to wrap invocations to other tools simultaneously. We find that if this tool is present, the model will use it to simultaneously call multiple tools in parallel for you.

See [this example](https://github.com/anthropics/anthropic-cookbook/blob/main/tool_use/parallel_tools_claude_3_7_sonnet.ipynb) in our cookbook for how to use this workaround.

# [​](#handling-tool-use-and-tool-result-content-blocks) Handling tool use and tool result content blocks

Claude’s response differs based on whether it uses a client or server tool.

# [​](#handling-results-from-client-tools) Handling results from client tools

The response will have a `stop_reason` of `tool_use` and one or more `tool_use` content blocks that include:

* `id`: A unique identifier for this particular tool use block. This will be used to match up the tool results later.
* `name`: The name of the tool being used.
* `input`: An object containing the input being passed to the tool, conforming to the tool’s `input_schema`.

JSON

```
{
  "id": "msg_01Aq9w938a90dw8q",
  "model": "claude-opus-4-20250514",
  "stop_reason": "tool_use",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "<thinking>I need to use the get_weather, and the user wants SF, which is likely San Francisco, CA.</thinking>"
    },
    {
      "type": "tool_use",
      "id": "toolu_01A09q90qw90lq917835lq9",
      "name": "get_weather",
      "input": {"location": "San Francisco, CA", "unit": "celsius"}
    }
  ]
}

```

When you receive a tool use response for a client tool, you should:

1. Extract the `name`, `id`, and `input` from the `tool_use` block.
2. Run the actual tool in your codebase corresponding to that tool name, passing in the tool `input`.
3. Continue the conversation by sending a new message with the `role` of `user`, and a `content` block containing the `tool_result` type and the following information:
   * `tool_use_id`: The `id` of the tool use request this is a result for.
   * `content`: The result of the tool, as a string (e.g. `"content": "15 degrees"`) or list of nested content blocks (e.g. `"content": [{"type": "text", "text": "15 degrees"}]`). These content blocks can use the `text` or `image` types.
   * `is_error` (optional): Set to `true` if the tool execution resulted in an error.

Example of successful tool result

JSON

```
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "15 degrees"
    }
  ]
}

```

Example of tool result with images

JSON

```
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": [
        {"type": "text", "text": "15 degrees"},
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "/9j/4AAQSkZJRg...",
          }
        }
      ]
    }
  ]
}

```

Example of empty tool result

JSON

```
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
    }
  ]
}

```

After receiving the tool result, Claude will use that information to continue generating a response to the original user prompt.

# [​](#handling-results-from-server-tools) Handling results from server tools

Claude executes the tool internally and incorporates the results directly into its response without requiring additional user interaction.

**Differences from other APIs**

Unlike APIs that separate tool use or use special roles like `tool` or `function`, Anthropic’s API integrates tools directly into the `user` and `assistant` message structure.

Messages contain arrays of `text`, `image`, `tool_use`, and `tool_result` blocks. `user` messages include client content and `tool_result`, while `assistant` messages contain AI-generated content and `tool_use`.

# [​](#handling-the-pause-turn-stop-reason) Handling the `pause_turn` stop reason

When using server tools like web search, the API may return a `pause_turn` stop reason, indicating that the API has paused a long-running turn.

Here’s how to handle the `pause_turn` stop reason:

Python

TypeScript

```
import anthropic

client = anthropic.Anthropic()

# Initial request with web search

response = client.messages.create(
    model="claude-3-7-sonnet-latest",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Search for comprehensive information about quantum computing breakthroughs in 2025"
        }
    ],
    tools=[{
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 10
    }]
)

# Check if the response has pause_turn stop reason

if response.stop_reason == "pause_turn":
    # Continue the conversation with the paused content
    messages = [
        {"role": "user", "content": "Search for comprehensive information about quantum computing breakthroughs in 2025"},
        {"role": "assistant", "content": response.content}
    ]

    # Send the continuation request
    continuation = client.messages.create(
        model="claude-3-7-sonnet-latest",
        max_tokens=1024,
        messages=messages,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 10
        }]
    )

    print(continuation)
else:
    print(response)

```

When handling `pause_turn`:

* **Continue the conversation**: Pass the paused response back as-is in a subsequent request to let Claude continue its turn
* **Modify if needed**: You can optionally modify the content before continuing if you want to interrupt or redirect the conversation
* **Preserve tool state**: Include the same tools in the continuation request to maintain functionality

# [​](#troubleshooting-errors) Troubleshooting errors

There are a few different types of errors that can occur when using tools with Claude:

Tool execution error

If the tool itself throws an error during execution (e.g. a network error when fetching weather data), you can return the error message in the `content` along with `"is_error": true`:

JSON

```
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "ConnectionError: the weather service API is not available (HTTP 500)",
      "is_error": true
    }
  ]
}

```

Claude will then incorporate this error into its response to the user, e.g. “I’m sorry, I was unable to retrieve the current weather because the weather service API is not available. Please try again later.”

Max tokens exceeded

If Claude’s response is cut off due to hitting the `max_tokens` limit, and the truncated response contains an incomplete tool use block, you’ll need to retry the request with a higher `max_tokens` value to get the full tool use.

Invalid tool name

If Claude’s attempted use of a tool is invalid (e.g. missing required parameters), it usually means that the there wasn’t enough information for Claude to use the tool correctly. Your best bet during development is to try the request again with more-detailed `description` values in your tool definitions.

However, you can also continue the conversation forward with a `tool_result` that indicates the error, and Claude will try to use the tool again with the missing information filled in:

JSON

```
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "Error: Missing required 'location' parameter",
      "is_error": true
    }
  ]
}

```

If a tool request is invalid or missing parameters, Claude will retry 2-3 times with corrections before apologizing to the user.

To prevent Claude from reflecting on search quality with <search\_quality\_reflection> tags, add “Do not reflect on the quality of the returned search results in your response” to your prompt.

Server tool errors

When server tools encounter errors (e.g., network issues with Web Search), Claude will transparently handle these errors and attempt to provide an alternative response or explanation to the user. Unlike client tools, you do not need to handle `is_error` results for server tools.

For web search specifically, possible error codes include:

* `too_many_requests`: Rate limit exceeded
* `invalid_input`: Invalid search query parameter
* `max_uses_exceeded`: Maximum web search tool uses exceeded
* `query_too_long`: Query exceeds maximum length
* `unavailable`: An internal error occurred

Was this page helpful?

YesNo

Overview[Token-efficient tool use (beta)](/en/docs/agents-and-tools/tool-use/token-efficient-tool-use)

On this page
