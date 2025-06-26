# Improve a prompt - Anthropic

**Source:** https://docs.anthropic.com/en/api/prompt-tools-improve

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# API reference

* Messages
* Models
* Message Batches
* Files
* + Prompt tools
  - [POST

      Generate a prompt](/en/api/prompt-tools-generate)
  - [POST

      Improve a prompt](/en/api/prompt-tools-improve)
  - [POST

      Templatize a prompt](/en/api/prompt-tools-templatize)
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

experimental

/

improve\_prompt

cURL

Python

JavaScript

PHP

Go

Java

```
curl -X POST https://api.anthropic.com/v1/experimental/improve_prompt \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "anthropic-beta: prompt-tools-2025-04-02" \
  --header "content-type: application/json" \
  --data \
'{
    "messages": [{"role": "user", "content": [{"type": "text", "text": "Create a recipe for {{food}}"}]}],
    "system": "You are a professional chef",
    "feedback": "Make it more detailed and include cooking times",
    "target_model": "claude-3-7-sonnet-20250219"
}'
```

200

4XX

```
{
  "messages": [
    {
      "content": [
        {
          "text": "<improved prompt>",
          "type": "text"
        }
      ],
      "role": "user"
    },
    {
      "content": [
        {
          "text": "<assistant prefill>",
          "type": "text"
        }
      ],
      "role": "assistant"
    }
  ],
  "system": "",
  "usage": [
    {
      "input_tokens": 490,
      "output_tokens": 661
    }
  ]
}
```

# [​](#before-you-begin) Before you begin

The prompt tools are a set of APIs to generate and improve prompts. Unlike our other APIs, this is an experimental API: you’ll need to request access, and it doesn’t have the same level of commitment to long-term support as other APIs.

These APIs are similar to what’s available in the [Anthropic Workbench](https://console.anthropic.com/workbench), and are intented for use by other prompt engineering platforms and playgrounds.

# [​](#getting-started-with-the-prompt-improver) Getting started with the prompt improver

To use the prompt generation API, you’ll need to:

1. Have joined the closed research preview for the prompt tools APIs
2. Use the API directly, rather than the SDK
3. Add the beta header `prompt-tools-2025-04-02`

# [​](#improve-a-prompt) Improve a prompt

# Headers

[​](#parameter-anthropic-beta)

anthropic-beta

string[]

Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like `beta1,beta2` or specify the header multiple times for each beta.

Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the [Console](https://console.anthropic.com/settings/keys). Each key is scoped to a Workspace.

# Body

application/json

[​](#body-messages)

messages

object[]

required

The prompt to improve, structured as a list of `message` objects.

Each message in the `messages` array must:

* Contain only text-only content blocks
* Not include tool calls, images, or prompt caching blocks

As a simple text prompt:

```
[
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "Concise recipe for {{food}}"
      }
    ]
  }
]

```

With example interactions to guide improvement:

```
[
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "Concise for {{food}}.\n\nexample\mandu: Put the mandu in the air fryer at 380F for 7 minutes."
      }
    ]
  }
]

```

Note that only contiguous user messages with text content are allowed. Assistant prefill is permitted, but other content types will cause validation errors.

Show child attributes

[​](#body-messages-content)

messages.content

stringobject[]

required

[​](#body-messages-role)

messages.role

enum<string>

required

Available options:

`user`,

`assistant`

Examples:

```
[
  {
    "content": [
      {
        "text": "<generated prompt>",
        "type": "text"
      }
    ],
    "role": "user"
  }
]

```

[​](#body-feedback)

feedback

string | null

Feedback for improving the prompt.

Use this parameter to share specific guidance on what aspects of the prompt should be enhanced or modified.

Example:

```
{
  "messages": [...],
  "feedback": "Make the recipes shorter"
}

```

When not set, the API will improve the prompt using general prompt engineering best practices.

Examples:

`"Make it more detailed and include cooking times"`

[​](#body-system)

system

string | null

The existing system prompt to incorporate, if any.

```
{
  "system": "You are a professional meal prep chef",
  [...]
}

```

Note that while system prompts typically appear as separate parameters in standard API calls, in the `improve_prompt` response, the system content will be incorporated directly into the returned user message.

Examples:

`"You are a professional chef"`

[​](#body-target-model)

target\_model

string | null

default:

The model this prompt will be used for. This optional parameter helps us understand which models our prompt tools are being used with, but it doesn't currently affect functionality.

Example:

```
"claude-3-7-sonnet-20250219"

```

Required string length: `1 - 256`

Examples:

`"claude-3-7-sonnet-20250219"`

# Response

200

2004XX

application/json

Successful Response

[​](#response-messages)

messages

object[]

required

Contains the result of the prompt improvement process in a list of `message` objects.

Includes a `user`-role message with the improved prompt text and may optionally include an `assistant`-role message with a prefill. These messages follow the standard Messages API format and can be used directly in subsequent API calls.

Show child attributes

[​](#response-messages-content)

messages.content

stringobject[]

required

[​](#response-messages-role)

messages.role

enum<string>

required

Available options:

`user`,

`assistant`

Examples:

```
[
  {
    "content": [
      {
        "text": "<improved prompt>",
        "type": "text"
      }
    ],
    "role": "user"
  },
  {
    "content": [
      {
        "text": "<assistant prefill>",
        "type": "text"
      }
    ],
    "role": "assistant"
  }
]

```

[​](#response-system)

system

string

required

Currently, the `system` field is always returned as an empty string (""). In future iterations, this field may contain generated system prompts.

Directions similar to what would normally be included in a system prompt are included in `messages` when improving a prompt.

Examples:

`""`

[​](#response-usage)

usage

object

required

Usage information

Show child attributes

[​](#response-usage-cache-creation)

usage.cache\_creation

object | null

required

Breakdown of cached tokens by TTL

Show child attributes

[​](#response-usage-cache-creation-ephemeral-1h-input-tokens)

usage.cache\_creation.ephemeral\_1h\_input\_tokens

integer

default:0

required

The number of input tokens used to create the 1 hour cache entry.

Required range: `x >= 0`

[​](#response-usage-cache-creation-ephemeral-5m-input-tokens)

usage.cache\_creation.ephemeral\_5m\_input\_tokens

integer

default:0

required

The number of input tokens used to create the 5 minute cache entry.

Required range: `x >= 0`

[​](#response-usage-cache-creation-input-tokens)

usage.cache\_creation\_input\_tokens

integer | null

required

The number of input tokens used to create the cache entry.

Required range: `x >= 0`

Examples:

`2051`

[​](#response-usage-cache-read-input-tokens)

usage.cache\_read\_input\_tokens

integer | null

required

The number of input tokens read from the cache.

Required range: `x >= 0`

Examples:

`2051`

[​](#response-usage-input-tokens)

usage.input\_tokens

integer

required

The number of input tokens which were used.

Required range: `x >= 0`

Examples:

`2095`

[​](#response-usage-output-tokens)

usage.output\_tokens

integer

required

The number of output tokens which were used.

Required range: `x >= 0`

Examples:

`503`

[​](#response-usage-server-tool-use)

usage.server\_tool\_use

object | null

required

The number of server tool requests.

Show child attributes

[​](#response-usage-service-tier)

usage.service\_tier

enum<string> | null

required

If the request used the priority, standard, or batch tier.

Available options:

`standard`,

`priority`,

`batch`

Examples:

```
[
  { "input_tokens": 490, "output_tokens": 661 }
]

```

Was this page helpful?

YesNo

Generate a prompt[Templatize a prompt](/en/api/prompt-tools-templatize)

cURL

Python

JavaScript

PHP

Go

Java

```
curl -X POST https://api.anthropic.com/v1/experimental/improve_prompt \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "anthropic-beta: prompt-tools-2025-04-02" \
  --header "content-type: application/json" \
  --data \
'{
    "messages": [{"role": "user", "content": [{"type": "text", "text": "Create a recipe for {{food}}"}]}],
    "system": "You are a professional chef",
    "feedback": "Make it more detailed and include cooking times",
    "target_model": "claude-3-7-sonnet-20250219"
}'
```

200

4XX

```
{
  "messages": [
    {
      "content": [
        {
          "text": "<improved prompt>",
          "type": "text"
        }
      ],
      "role": "user"
    },
    {
      "content": [
        {
          "text": "<assistant prefill>",
          "type": "text"
        }
      ],
      "role": "assistant"
    }
  ],
  "system": "",
  "usage": [
    {
      "input_tokens": 490,
      "output_tokens": 661
    }
  ]
}
```
