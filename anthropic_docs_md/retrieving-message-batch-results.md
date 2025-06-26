# Retrieve Message Batch Results - Anthropic

**Source:** https://docs.anthropic.com/en/api/retrieving-message-batch-results

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

GET

/

v1

/

messages

/

batches

/

{message\_batch\_id}

/

results

cURL

Python

JavaScript

PHP

Go

Java

```
curl https://api.anthropic.com/v1/messages/batches/msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d/results \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01"
```

200

4XX

```
{"custom_id":"my-second-request","result":{"type":"succeeded","message":{"id":"msg_014VwiXbi91y3JMjcpyGBHX5","type":"message","role":"assistant","model":"claude-3-5-sonnet-20240620","content":[{"type":"text","text":"Hello again! It's nice to see you. How can I assist you today? Is there anything specific you'd like to chat about or any questions you have?"}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":11,"output_tokens":36}}}}
{"custom_id":"my-first-request","result":{"type":"succeeded","message":{"id":"msg_01FqfsLoHwgeFbguDgpz48m7","type":"message","role":"assistant","model":"claude-3-5-sonnet-20240620","content":[{"type":"text","text":"Hello! How can I assist you today? Feel free to ask me any questions or let me know if there's anything you'd like to chat about."}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":10,"output_tokens":34}}}}

```

The path for retrieving Message Batch results should be pulled from the batch’s `results_url`. This path should not be assumed and may change.

200

4XX

```
{"custom_id":"my-second-request","result":{"type":"succeeded","message":{"id":"msg_014VwiXbi91y3JMjcpyGBHX5","type":"message","role":"assistant","model":"claude-3-5-sonnet-20240620","content":[{"type":"text","text":"Hello again! It's nice to see you. How can I assist you today? Is there anything specific you'd like to chat about or any questions you have?"}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":11,"output_tokens":36}}}}
{"custom_id":"my-first-request","result":{"type":"succeeded","message":{"id":"msg_01FqfsLoHwgeFbguDgpz48m7","type":"message","role":"assistant","model":"claude-3-5-sonnet-20240620","content":[{"type":"text","text":"Hello! How can I assist you today? Feel free to ask me any questions or let me know if there's anything you'd like to chat about."}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":10,"output_tokens":34}}}}

```

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

# Path Parameters

[​](#parameter-message-batch-id)

message\_batch\_id

string

required

ID of the Message Batch.

# Response

200

2004XX

application/x-jsonl

Successful Response

This is a single line in the response `.jsonl` file and does not represent the response as a whole.

[​](#response-custom-id)

custom\_id

string

required

Developer-provided ID created for each request in a Message Batch. Useful for matching results to requests, as results may be given out of request order.

Must be unique for each request within the Message Batch.

Examples:

`"my-custom-id-1"`

[​](#response-result)

result

object

required

Processing result for this request.

Contains a Message output if processing was successful, an error response if processing failed, or the reason why processing was not attempted, such as cancellation or expiration.

* SucceededResult
* ErroredResult
* CanceledResult
* ExpiredResult

Show child attributes

[​](#response-result-message)

result.message

object

required

Show child attributes

[​](#response-result-message-id)

result.message.id

string

required

Unique object identifier.

The format and length of IDs may change over time.

Examples:

`"msg_013Zva2CMHLNnXjNJJKqJ2EF"`

[​](#response-result-message-type)

result.message.type

enum<string>

default:message

required

Object type.

For Messages, this is always `"message"`.

Available options:

`message`

[​](#response-result-message-role)

result.message.role

enum<string>

default:assistant

required

Conversational role of the generated message.

This will always be `"assistant"`.

Available options:

`assistant`

[​](#response-result-message-content)

result.message.content

object[]

required

Content generated by the model.

This is an array of content blocks, each of which has a `type` that determines its shape.

Example:

```
[{"type": "text", "text": "Hi, I'm Claude."}]

```

If the request input `messages` ended with an `assistant` turn, then the response `content` will continue directly from that last turn. You can use this to constrain the model's output.

For example, if the input `messages` were:

```
[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("}
]

```

Then the response `content` might be:

```
[{"type": "text", "text": "B)"}]

```

* Tool use
* ResponseServerToolUseBlock
* ResponseWebSearchToolResultBlock
* ResponseCodeExecutionToolResultBlock
* ResponseMCPToolUseBlock
* ResponseMCPToolResultBlock
* ResponseContainerUploadBlock
* Thinking
* Redacted thinking

Show child attributes

[​](#response-result-message-content-id)

result.message.content.id

string

required

[​](#response-result-message-content-input)

result.message.content.input

object

required

[​](#response-result-message-content-name)

result.message.content.name

string

required

Minimum length: `1`

[​](#response-result-message-content-type)

result.message.content.type

enum<string>

default:tool\_use

required

Available options:

`tool_use`

Examples:

```
[
  {
    "text": "Hi! My name is Claude.",
    "type": "text"
  }
]

```

[​](#response-result-message-model)

result.message.model

string

required

The model that handled the request.

Required string length: `1 - 256`

Examples:

`"claude-3-7-sonnet-20250219"`

[​](#response-result-message-stop-reason)

result.message.stop\_reason

enum<string> | null

required

The reason that we stopped.

This may be one the following values:

* `"end_turn"`: the model reached a natural stopping point
* `"max_tokens"`: we exceeded the requested `max_tokens` or the model's maximum
* `"stop_sequence"`: one of your provided custom `stop_sequences` was generated
* `"tool_use"`: the model invoked one or more tools

In non-streaming mode this value is always non-null. In streaming mode, it is null in the `message_start` event and non-null otherwise.

Available options:

`end_turn`,

`max_tokens`,

`stop_sequence`,

`tool_use`,

`pause_turn`,

`refusal`

[​](#response-result-message-stop-sequence)

result.message.stop\_sequence

string | null

required

Which custom stop sequence was generated, if any.

This value will be a non-null string if one of your custom stop sequences was generated.

[​](#response-result-message-usage)

result.message.usage

object

required

Billing and rate-limit usage.

Anthropic's API bills and rate-limits by token counts, as tokens represent the underlying cost to our systems.

Under the hood, the API transforms requests into a format suitable for the model. The model's output then goes through a parsing stage before becoming an API response. As a result, the token counts in `usage` will not match one-to-one with the exact visible content of an API request or response.

For example, `output_tokens` will be non-zero, even for an empty string response from Claude.

Total input tokens in a request is the summation of `input_tokens`, `cache_creation_input_tokens`, and `cache_read_input_tokens`.

Show child attributes

[​](#response-result-message-usage-cache-creation)

result.message.usage.cache\_creation

object | null

required

Breakdown of cached tokens by TTL

Show child attributes

[​](#response-result-message-usage-cache-creation-ephemeral-1h-input-tokens)

result.message.usage.cache\_creation.ephemeral\_1h\_input\_tokens

integer

default:0

required

The number of input tokens used to create the 1 hour cache entry.

Required range: `x >= 0`

[​](#response-result-message-usage-cache-creation-ephemeral-5m-input-tokens)

result.message.usage.cache\_creation.ephemeral\_5m\_input\_tokens

integer

default:0

required

The number of input tokens used to create the 5 minute cache entry.

Required range: `x >= 0`

[​](#response-result-message-usage-cache-creation-input-tokens)

result.message.usage.cache\_creation\_input\_tokens

integer | null

required

The number of input tokens used to create the cache entry.

Required range: `x >= 0`

Examples:

`2051`

[​](#response-result-message-usage-cache-read-input-tokens)

result.message.usage.cache\_read\_input\_tokens

integer | null

required

The number of input tokens read from the cache.

Required range: `x >= 0`

Examples:

`2051`

[​](#response-result-message-usage-input-tokens)

result.message.usage.input\_tokens

integer

required

The number of input tokens which were used.

Required range: `x >= 0`

Examples:

`2095`

[​](#response-result-message-usage-output-tokens)

result.message.usage.output\_tokens

integer

required

The number of output tokens which were used.

Required range: `x >= 0`

Examples:

`503`

[​](#response-result-message-usage-server-tool-use)

result.message.usage.server\_tool\_use

object | null

required

The number of server tool requests.

Show child attributes

[​](#response-result-message-usage-service-tier)

result.message.usage.service\_tier

enum<string> | null

required

If the request used the priority, standard, or batch tier.

Available options:

`standard`,

`priority`,

`batch`

Examples:

```
{
  "input_tokens": 2095,
  "output_tokens": 503
}

```

[​](#response-result-message-container)

result.message.container

object | null

required

Information about the container used in this request.

This will be non-null if a container tool (e.g. code execution) was used.

Show child attributes

[​](#response-result-message-container-expires-at)

result.message.container.expires\_at

string

required

The time at which the container will expire.

[​](#response-result-message-container-id)

result.message.container.id

string

required

Identifier for the container used in this request

Examples:

```
{
  "content": [
    {
      "text": "Hi! My name is Claude.",
      "type": "text"
    }
  ],
  "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
  "model": "claude-3-7-sonnet-20250219",
  "role": "assistant",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "type": "message",
  "usage": {
    "input_tokens": 2095,
    "output_tokens": 503
  }
}

```

[​](#response-result-type)

result.type

enum<string>

default:succeeded

required

Available options:

`succeeded`

Was this page helpful?

YesNo

Retrieve a Message Batch[List Message Batches](/en/api/listing-message-batches)

cURL

Python

JavaScript

PHP

Go

Java

```
curl https://api.anthropic.com/v1/messages/batches/msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d/results \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01"
```

200

4XX

```
{"custom_id":"my-second-request","result":{"type":"succeeded","message":{"id":"msg_014VwiXbi91y3JMjcpyGBHX5","type":"message","role":"assistant","model":"claude-3-5-sonnet-20240620","content":[{"type":"text","text":"Hello again! It's nice to see you. How can I assist you today? Is there anything specific you'd like to chat about or any questions you have?"}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":11,"output_tokens":36}}}}
{"custom_id":"my-first-request","result":{"type":"succeeded","message":{"id":"msg_01FqfsLoHwgeFbguDgpz48m7","type":"message","role":"assistant","model":"claude-3-5-sonnet-20240620","content":[{"type":"text","text":"Hello! How can I assist you today? Feel free to ask me any questions or let me know if there's anything you'd like to chat about."}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":10,"output_tokens":34}}}}

```
