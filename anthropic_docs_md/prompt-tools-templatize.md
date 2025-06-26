# Templatize a prompt - Anthropic

**Source:** https://docs.anthropic.com/en/api/prompt-tools-templatize

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

templatize\_prompt

cURL

Python

JavaScript

PHP

Go

Java

```
curl -X POST https://api.anthropic.com/v1/experimental/templatize_prompt \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "anthropic-beta: prompt-tools-2025-04-02" \
  --header "content-type: application/json" \
  --data \
'{
    "messages": [{"role": "user", "content": "Translate hello to German"}],
    "system": "You are an English to German translator"
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
          "text": "Translate {{WORD_TO_TRANSLATE}} to {{TARGET_LANGUAGE}}",
          "type": "text"
        }
      ],
      "role": "user"
    }
  ],
  "system": "You are a professional English to {{TARGET_LANGUAGE}} translator",
  "usage": [
    {
      "input_tokens": 490,
      "output_tokens": 661
    }
  ],
  "variable_values": {
    "TARGET_LANGUAGE": "German",
    "WORD_TO_TRANSLATE": "hello"
  }
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

# [​](#templatize-a-prompt) Templatize a prompt

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

The prompt to templatize, structured as a list of `message` objects.

Each message in the `messages` array must:

* Contain only text-only content blocks
* Not include tool calls, images, or prompt caching blocks

Example of a simple text prompt:

```
[
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "Translate hello to German"
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
        "text": "Translate hello to German",
        "type": "text"
      }
    ],
    "role": "user"
  }
]

```

[​](#body-system)

system

string | null

The existing system prompt to templatize.

```
{
  "system": "You are a professional English to German translator",
  [...]
}

```

Note that this differs from the Messages API; it is strictly a string.

Examples:

`"You are a professional English to German translator"`

# Response

200

2004XX

application/json

Successful Response

[​](#response-messages)

messages

object[]

required

The templatized prompt with variable placeholders.

The response includes the input messages with specific values replaced by variable placeholders. These messages maintain the original message structure but contain uppercase variable names in place of concrete values.

For example, an input message content like `"Translate hello to German"` would be transformed to `"Translate {{WORD_TO_TRANSLATE}} to {{TARGET_LANGUAGE}}"`.

```
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Translate {{WORD_TO_TRANSLATE}} to {{TARGET_LANGUAGE}}"
        }
      ]
    }
  ]
}

```

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
        "text": "Translate {{WORD_TO_TRANSLATE}} to {{TARGET_LANGUAGE}}",
        "type": "text"
      }
    ],
    "role": "user"
  }
]

```

[​](#response-system)

system

string

required

The input system prompt with variables identified and replaced.

If no system prompt was provided in the original request, this field will be an empty string.

Examples:

`"You are a professional English to {{TARGET_LANGUAGE}} translator"`

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

[​](#response-variable-values)

variable\_values

object

required

A mapping of template variable names to their original values, as extracted from the input prompt during templatization. Each key represents a variable name identified in the templatized prompt, and each value contains the corresponding content from the original prompt that was replaced by that variable.

Example:

```
"variable_values": {
  "WORD_TO_TRANSLATE": "hello",
  "TARGET_LANGUAGE": "German"
}

```

In this example response, the original prompt – `Translate hello to German` – was templatized to `Translate WORD_TO_TRANSLATE to TARGET_LANGUAGE`, with the variable values extracted as shown.

Show child attributes

[​](#response-variable-values-key)

variable\_values.{key}

string

Examples:

```
{
  "TARGET_LANGUAGE": "German",
  "WORD_TO_TRANSLATE": "hello"
}

```

Was this page helpful?

YesNo

Improve a prompt[Migrating from Text Completions](/en/api/migrating-from-text-completions-to-messages)

cURL

Python

JavaScript

PHP

Go

Java

```
curl -X POST https://api.anthropic.com/v1/experimental/templatize_prompt \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "anthropic-beta: prompt-tools-2025-04-02" \
  --header "content-type: application/json" \
  --data \
'{
    "messages": [{"role": "user", "content": "Translate hello to German"}],
    "system": "You are an English to German translator"
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
          "text": "Translate {{WORD_TO_TRANSLATE}} to {{TARGET_LANGUAGE}}",
          "type": "text"
        }
      ],
      "role": "user"
    }
  ],
  "system": "You are a professional English to {{TARGET_LANGUAGE}} translator",
  "usage": [
    {
      "input_tokens": 490,
      "output_tokens": 661
    }
  ],
  "variable_values": {
    "TARGET_LANGUAGE": "German",
    "WORD_TO_TRANSLATE": "hello"
  }
}
```
