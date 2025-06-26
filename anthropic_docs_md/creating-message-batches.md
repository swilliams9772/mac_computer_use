# Create a Message Batch - Anthropic

**Source:** https://docs.anthropic.com/en/api/creating-message-batches

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# API reference

* Messages
* Models
* Message Batches

  + [POST

    Create a Message Batch](/en/api/creating-message-batches)
  + [GET

    Retrieve a Message Batch](/en/api/retrieving-message-batches)
  + [GET

    Retrieve Message Batch Results](/en/api/retrieving-message-batch-results)
  + [GET

    List Message Batches](/en/api/listing-message-batches)
  + [POST

    Cancel a Message Batch](/en/api/canceling-message-batches)
  + [DEL

    Delete a Message Batch](/en/api/deleting-message-batches)
* Files
* Text Completions (Legacy)

# SDKs

* [Client SDKs](/en/api/client-sdks)
* [OpenAI SDK compatibility (beta)](/en/api/openai-sdk)

# Examples

* [Messages examples](/en/api/messages-examples)
* [Message Batches examples](/en/api/messages-batch-examples)

POST

/

v1

/

messages

/

batches

cURL

Python

JavaScript

PHP

Go

Java

```
curl https://api.anthropic.com/v1/messages/batches \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data \
'{
    "requests": [
        {
            "custom_id": "my-first-request",
            "params": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": "Hello, world"}
                ]
            }
        },
        {
            "custom_id": "my-second-request",
            "params": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": "Hi again, friend"}
                ]
            }
        }
    ]
}'
```

200

4XX

```
{
  "archived_at": "2024-08-20T18:37:24.100435Z",
  "cancel_initiated_at": "2024-08-20T18:37:24.100435Z",
  "created_at": "2024-08-20T18:37:24.100435Z",
  "ended_at": "2024-08-20T18:37:24.100435Z",
  "expires_at": "2024-08-20T18:37:24.100435Z",
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "processing_status": "in_progress",
  "request_counts": {
    "canceled": 10,
    "errored": 30,
    "expired": 10,
    "processing": 100,
    "succeeded": 50
  },
  "results_url": "https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results",
  "type": "message_batch"
}
```

# [​](#feature-support) Feature Support

The Message Batches API supports the following models: Claude Haiku 3, Claude Opus 3, Claude Sonnet 3.5, Claude Sonnet 3.5 v2, Claude Sonnet 3.7, Claude Sonnet 4, and Claude Opus 4. All features available in the Messages API, including beta features, are available through the Message Batches API.

Batches may contain up to 100,000 requests and be up to 256 MB in total size.

# Headers

[​](#parameter-anthropic-beta)

anthropic-beta

string[]

Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like `beta1,beta2` or specify the header multiple times for each beta.

[​](#parameter-anthropic-version)

anthropic-version

string

required

The version of the Anthropic API you want to use.

Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning).

Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the [Console](https://console.anthropic.com/settings/keys). Each key is scoped to a Workspace.

# Body

application/json

[​](#body-requests)

requests

object[]

required

List of requests for prompt completion. Each is an individual request to create a Message.

Show child attributes

[​](#body-requests-custom-id)

requests.custom\_id

string

required

Developer-provided ID created for each request in a Message Batch. Useful for matching results to requests, as results may be given out of request order.

Must be unique for each request within the Message Batch.

Required string length: `1 - 64`

Examples:

`"my-custom-id-1"`

[​](#body-requests-params)

requests.params

object

required

Messages API creation parameters for the individual request.

See the [Messages API reference](/en/api/messages) for full documentation on available parameters.

Show child attributes

[​](#body-requests-params-model)

requests.params.model

string

required

The model that will complete your prompt.

See [models](https://docs.anthropic.com/en/docs/models-overview) for additional details and options.

Required string length: `1 - 256`

Examples:

`"claude-3-7-sonnet-20250219"`

[​](#body-requests-params-messages)

requests.params.messages

object[]

required

Input messages.

Our models are trained to operate on alternating `user` and `assistant` conversational turns. When creating a new `Message`, you specify the prior conversational turns with the `messages` parameter, and the model then generates the next `Message` in the conversation. Consecutive `user` or `assistant` turns in your request will be combined into a single turn.

Each input message must be an object with a `role` and `content`. You can specify a single `user`-role message, or you can include multiple `user` and `assistant` messages.

If the final message uses the `assistant` role, the response content will continue immediately from the content in that message. This can be used to constrain part of the model's response.

Example with a single `user` message:

```
[{"role": "user", "content": "Hello, Claude"}]

```

Example with multiple conversational turns:

```
[
  {"role": "user", "content": "Hello there."},
  {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
  {"role": "user", "content": "Can you explain LLMs in plain English?"},
]

```

Example with a partially-filled response from Claude:

```
[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("},
]

```

Each input message `content` may be either a single `string` or an array of content blocks, where each block has a specific `type`. Using a `string` for `content` is shorthand for an array of one content block of type `"text"`. The following input messages are equivalent:

```
{"role": "user", "content": "Hello, Claude"}

```

```
{"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}

```

Starting with Claude 3 models, you can also send image content blocks:

```
{"role": "user", "content": [
  {
    "type": "image",
    "source": {
      "type": "base64",
      "media_type": "image/jpeg",
      "data": "/9j/4AAQSkZJRg...",
    }
  },
  {"type": "text", "text": "What is in this image?"}
]}

```

We currently support the `base64` source type for images, and the `image/jpeg`, `image/png`, `image/gif`, and `image/webp` media types.

See [examples](https://docs.anthropic.com/en/api/messages-examples#vision) for more input examples.

Note that if you want to include a [system prompt](https://docs.anthropic.com/en/docs/system-prompts), you can use the top-level `system` parameter — there is no `"system"` role for input messages in the Messages API.

There is a limit of 100000 messages in a single request.

Show child attributes

[​](#body-requests-params-messages-content)

requests.params.messages.content

stringobject[]

required

[​](#body-requests-params-messages-role)

requests.params.messages.role

enum<string>

required

Available options:

`user`,

`assistant`

[​](#body-requests-params-max-tokens)

requests.params.max\_tokens

integer

required

The maximum number of tokens to generate before stopping.

Note that our models may stop *before* reaching this maximum. This parameter only specifies the absolute maximum number of tokens to generate.

Different models have different maximum values for this parameter. See [models](https://docs.anthropic.com/en/docs/models-overview) for details.

Required range: `x >= 1`

Examples:

`1024`

[​](#body-requests-params-container)

requests.params.container

string | null

Container identifier for reuse across requests.

[​](#body-requests-params-mcp-servers)

requests.params.mcp\_servers

object[]

MCP servers to be utilized in this request

Show child attributes

[​](#body-requests-params-mcp-servers-name)

requests.params.mcp\_servers.name

string

required

[​](#body-requests-params-mcp-servers-type)

requests.params.mcp\_servers.type

enum<string>

required

Available options:

`url`

[​](#body-requests-params-mcp-servers-url)

requests.params.mcp\_servers.url

string

required

[​](#body-requests-params-mcp-servers-authorization-token)

requests.params.mcp\_servers.authorization\_token

string | null

[​](#body-requests-params-mcp-servers-tool-configuration)

requests.params.mcp\_servers.tool\_configuration

object | null

Show child attributes

[​](#body-requests-params-mcp-servers-tool-configuration-allowed-tools)

requests.params.mcp\_servers.tool\_configuration.allowed\_tools

string[] | null

[​](#body-requests-params-mcp-servers-tool-configuration-enabled)

requests.params.mcp\_servers.tool\_configuration.enabled

boolean | null

[​](#body-requests-params-metadata)

requests.params.metadata

object

An object describing metadata about the request.

Show child attributes

[​](#body-requests-params-metadata-user-id)

requests.params.metadata.user\_id

string | null

An external identifier for the user who is associated with the request.

This should be a uuid, hash value, or other opaque identifier. Anthropic may use this id to help detect abuse. Do not include any identifying information such as name, email address, or phone number.

Maximum length: `256`

Examples:

`"13803d75-b4b5-4c3e-b2a2-6f21399b021b"`

[​](#body-requests-params-service-tier)

requests.params.service\_tier

enum<string>

Determines whether to use priority capacity (if available) or standard capacity for this request.

Anthropic offers different levels of service for your API requests. See [service-tiers](https://docs.anthropic.com/en/api/service-tiers) for details.

Available options:

`auto`,

`standard_only`

[​](#body-requests-params-stop-sequences)

requests.params.stop\_sequences

string[]

Custom text sequences that will cause the model to stop generating.

Our models will normally stop when they have naturally completed their turn, which will result in a response `stop_reason` of `"end_turn"`.

If you want the model to stop generating when it encounters custom strings of text, you can use the `stop_sequences` parameter. If the model encounters one of the custom sequences, the response `stop_reason` value will be `"stop_sequence"` and the response `stop_sequence` value will contain the matched stop sequence.

[​](#body-requests-params-stream)

requests.params.stream

boolean

Whether to incrementally stream the response using server-sent events.

See [streaming](https://docs.anthropic.com/en/api/messages-streaming) for details.

[​](#body-requests-params-system)

requests.params.system

stringobject[]

System prompt.

A system prompt is a way of providing context and instructions to Claude, such as specifying a particular goal or role. See our [guide to system prompts](https://docs.anthropic.com/en/docs/system-prompts).

Examples:

```
[
  {
    "text": "Today's date is 2024-06-01.",
    "type": "text"
  }
]

```

`"Today's date is 2023-01-01."`

[​](#body-requests-params-temperature)

requests.params.temperature

number

Amount of randomness injected into the response.

Defaults to `1.0`. Ranges from `0.0` to `1.0`. Use `temperature` closer to `0.0` for analytical / multiple choice, and closer to `1.0` for creative and generative tasks.

Note that even with `temperature` of `0.0`, the results will not be fully deterministic.

Required range: `0 <= x <= 1`

Examples:

`1`

[​](#body-requests-params-thinking)

requests.params.thinking

object

Configuration for enabling Claude's extended thinking.

When enabled, responses include `thinking` content blocks showing Claude's thinking process before the final answer. Requires a minimum budget of 1,024 tokens and counts towards your `max_tokens` limit.

See [extended thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking) for details.

* Enabled
* Disabled

Show child attributes

[​](#body-requests-params-thinking-budget-tokens)

requests.params.thinking.budget\_tokens

integer

required

Determines how many tokens Claude can use for its internal reasoning process. Larger budgets can enable more thorough analysis for complex problems, improving response quality.

Must be ≥1024 and less than `max_tokens`.

See [extended thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking) for details.

Required range: `x >= 1024`

[​](#body-requests-params-thinking-type)

requests.params.thinking.type

enum<string>

required

Available options:

`enabled`

[​](#body-requests-params-tool-choice)

requests.params.tool\_choice

object

How the model should use the provided tools. The model can use a specific tool, any available tool, decide by itself, or not use tools at all.

* Auto
* Any
* Tool
* None

Show child attributes

[​](#body-requests-params-tool-choice-type)

requests.params.tool\_choice.type

enum<string>

required

Available options:

`auto`

[​](#body-requests-params-tool-choice-disable-parallel-tool-use)

requests.params.tool\_choice.disable\_parallel\_tool\_use

boolean

Whether to disable parallel tool use.

Defaults to `false`. If set to `true`, the model will output at most one tool use.

[​](#body-requests-params-tools)

requests.params.tools

object[]

Definitions of tools that the model may use.

If you include `tools` in your API request, the model may return `tool_use` content blocks that represent the model's use of those tools. You can then run those tools using the tool input generated by the model and then optionally return results back to the model using `tool_result` content blocks.

Each tool definition includes:

* `name`: Name of the tool.
* `description`: Optional, but strongly-recommended description of the tool.
* `input_schema`: [JSON schema](https://json-schema.org/draft/2020-12) for the tool `input` shape that the model will produce in `tool_use` output content blocks.

For example, if you defined `tools` as:

```
[
  {
    "name": "get_stock_price",
    "description": "Get the current stock price for a given ticker symbol.",
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
]

```

And then asked the model "What's the S&P 500 at today?", the model might produce `tool_use` content blocks in the response like this:

```
[
  {
    "type": "tool_use",
    "id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "name": "get_stock_price",
    "input": { "ticker": "^GSPC" }
  }
]

```

You might then run your `get_stock_price` tool with `{"ticker": "^GSPC"}` as an input, and return the following back to the model in a subsequent `user` message:

```
[
  {
    "type": "tool_result",
    "tool_use_id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "content": "259.75 USD"
  }
]

```

Tools can be used for workflows that include running client-side tools and functions, or more generally whenever you want the model to produce a particular JSON structure of output.

See our [guide](https://docs.anthropic.com/en/docs/tool-use) for more details.

* Custom tool
* Computer use tool (2024-01-22)
* Bash tool (2024-10-22)
* Text editor tool (2024-10-22)
* Computer use tool (2025-01-24)
* Bash tool (2025-01-24)
* Text editor tool (2025-01-24)
* TextEditor\_20250429
* Web search tool (2025-03-05)
* Code execution tool (2025-05-22)

Show child attributes

[​](#body-requests-params-tools-name)

requests.params.tools.name

string

required

Name of the tool.

This is how the tool will be called by the model and in `tool_use` blocks.

Required string length: `1 - 64`

[​](#body-requests-params-tools-input-schema)

requests.params.tools.input\_schema

object

required

[JSON schema](https://json-schema.org/draft/2020-12) for this tool's input.

This defines the shape of the `input` that your tool accepts and that the model will produce.

Show child attributes

[​](#body-requests-params-tools-input-schema-type)

requests.params.tools.input\_schema.type

enum<string>

required

Available options:

`object`

[​](#body-requests-params-tools-input-schema-properties)

requests.params.tools.input\_schema.properties

object | null

Examples:

```
{
  "properties": {
    "location": {
      "description": "The city and state, e.g. San Francisco, CA",
      "type": "string"
    },
    "unit": {
      "description": "Unit for the output - one of (celsius, fahrenheit)",
      "type": "string"
    }
  },
  "required": ["location"],
  "type": "object"
}

```

[​](#body-requests-params-tools-type)

requests.params.tools.type

enum<string> | null

Available options:

`custom`

[​](#body-requests-params-tools-description)

requests.params.tools.description

string

Description of what this tool does.

Tool descriptions should be as detailed as possible. The more information that the model has about what the tool is and how to use it, the better it will perform. You can use natural language descriptions to reinforce important aspects of the tool input JSON schema.

Examples:

`"Get the current weather in a given location"`

[​](#body-requests-params-tools-cache-control)

requests.params.tools.cache\_control

object | null

Create a cache control breakpoint at this content block.

Show child attributes

[​](#body-requests-params-tools-cache-control-type)

requests.params.tools.cache\_control.type

enum<string>

required

Available options:

`ephemeral`

[​](#body-requests-params-tools-cache-control-ttl)

requests.params.tools.cache\_control.ttl

enum<string>

The time-to-live for the cache control breakpoint.

This may be one the following values:

* `5m`: 5 minutes
* `1h`: 1 hour

Defaults to `5m`.

Available options:

`5m`,

`1h`

Examples:

```
{
  "description": "Get the current weather in a given location",
  "input_schema": {
    "properties": {
      "location": {
        "description": "The city and state, e.g. San Francisco, CA",
        "type": "string"
      },
      "unit": {
        "description": "Unit for the output - one of (celsius, fahrenheit)",
        "type": "string"
      }
    },
    "required": ["location"],
    "type": "object"
  },
  "name": "get_weather"
}

```

[​](#body-requests-params-top-k)

requests.params.top\_k

integer

Only sample from the top K options for each subsequent token.

Used to remove "long tail" low probability responses. [Learn more technical details here](https://towardsdatascience.com/how-to-sample-from-language-models-682bceb97277).

Recommended for advanced use cases only. You usually only need to use `temperature`.

Required range: `x >= 0`

Examples:

`5`

[​](#body-requests-params-top-p)

requests.params.top\_p

number

Use nucleus sampling.

In nucleus sampling, we compute the cumulative distribution over all the options for each subsequent token in decreasing probability order and cut it off once it reaches a particular probability specified by `top_p`. You should either alter `temperature` or `top_p`, but not both.

Recommended for advanced use cases only. You usually only need to use `temperature`.

Required range: `0 <= x <= 1`

Examples:

`0.7`

Example:

```
{
  "max_tokens": 1024,
  "messages": [
    { "content": "Hello, world", "role": "user" }
  ],
  "model": "claude-3-7-sonnet-20250219"
}

```

# Response

200

2004XX

application/json

Successful Response

[​](#response-archived-at)

archived\_at

string | null

required

RFC 3339 datetime string representing the time at which the Message Batch was archived and its results became unavailable.

Examples:

`"2024-08-20T18:37:24.100435Z"`

[​](#response-cancel-initiated-at)

cancel\_initiated\_at

string | null

required

RFC 3339 datetime string representing the time at which cancellation was initiated for the Message Batch. Specified only if cancellation was initiated.

Examples:

`"2024-08-20T18:37:24.100435Z"`

[​](#response-created-at)

created\_at

string

required

RFC 3339 datetime string representing the time at which the Message Batch was created.

Examples:

`"2024-08-20T18:37:24.100435Z"`

[​](#response-ended-at)

ended\_at

string | null

required

RFC 3339 datetime string representing the time at which processing for the Message Batch ended. Specified only once processing ends.

Processing ends when every request in a Message Batch has either succeeded, errored, canceled, or expired.

Examples:

`"2024-08-20T18:37:24.100435Z"`

[​](#response-expires-at)

expires\_at

string

required

RFC 3339 datetime string representing the time at which the Message Batch will expire and end processing, which is 24 hours after creation.

Examples:

`"2024-08-20T18:37:24.100435Z"`

[​](#response-id)

id

string

required

Unique object identifier.

The format and length of IDs may change over time.

Examples:

`"msgbatch_013Zva2CMHLNnXjNJJKqJ2EF"`

[​](#response-processing-status)

processing\_status

enum<string>

required

Processing status of the Message Batch.

Available options:

`in_progress`,

`canceling`,

`ended`

[​](#response-request-counts)

request\_counts

object

required

Tallies requests within the Message Batch, categorized by their status.

Requests start as `processing` and move to one of the other statuses only once processing of the entire batch ends. The sum of all values always matches the total number of requests in the batch.

Show child attributes

[​](#response-request-counts-canceled)

request\_counts.canceled

integer

default:0

required

Number of requests in the Message Batch that have been canceled.

This is zero until processing of the entire Message Batch has ended.

Examples:

`10`

[​](#response-request-counts-errored)

request\_counts.errored

integer

default:0

required

Number of requests in the Message Batch that encountered an error.

This is zero until processing of the entire Message Batch has ended.

Examples:

`30`

[​](#response-request-counts-expired)

request\_counts.expired

integer

default:0

required

Number of requests in the Message Batch that have expired.

This is zero until processing of the entire Message Batch has ended.

Examples:

`10`

[​](#response-request-counts-processing)

request\_counts.processing

integer

default:0

required

Number of requests in the Message Batch that are processing.

Examples:

`100`

[​](#response-request-counts-succeeded)

request\_counts.succeeded

integer

default:0

required

Number of requests in the Message Batch that have completed successfully.

This is zero until processing of the entire Message Batch has ended.

Examples:

`50`

[​](#response-results-url)

results\_url

string | null

required

URL to a `.jsonl` file containing the results of the Message Batch requests. Specified only once processing ends.

Results in the file are not guaranteed to be in the same order as requests. Use the `custom_id` field to match results to requests.

[​](#response-type)

type

enum<string>

default:message\_batch

required

Object type.

For Message Batches, this is always `"message_batch"`.

Available options:

`message_batch`

Was this page helpful?

YesNo

Get a Model[Retrieve a Message Batch](/en/api/retrieving-message-batches)

cURL

Python

JavaScript

PHP

Go

Java

```
curl https://api.anthropic.com/v1/messages/batches \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data \
'{
    "requests": [
        {
            "custom_id": "my-first-request",
            "params": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": "Hello, world"}
                ]
            }
        },
        {
            "custom_id": "my-second-request",
            "params": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": "Hi again, friend"}
                ]
            }
        }
    ]
}'
```

200

4XX

```
{
  "archived_at": "2024-08-20T18:37:24.100435Z",
  "cancel_initiated_at": "2024-08-20T18:37:24.100435Z",
  "created_at": "2024-08-20T18:37:24.100435Z",
  "ended_at": "2024-08-20T18:37:24.100435Z",
  "expires_at": "2024-08-20T18:37:24.100435Z",
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "processing_status": "in_progress",
  "request_counts": {
    "canceled": 10,
    "errored": 30,
    "expired": 10,
    "processing": 100,
    "succeeded": 50
  },
  "results_url": "https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results",
  "type": "message_batch"
}
```
