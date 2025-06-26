# Streaming Text Completions - Anthropic

**Source:** https://docs.anthropic.com/en/api/streaming

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# API reference

* Messages
* Models
* Message Batches
* Files
* Text Completions (Legacy)

  + [Migrating from Text Completions](/en/api/migrating-from-text-completions-to-messages)
  + [POST

    Create a Text Completion](/en/api/complete)
  + [Streaming Text Completions](/en/api/streaming)
  + [Prompt validation](/en/api/prompt-validation)

# SDKs

* [Client SDKs](/en/api/client-sdks)
* [OpenAI SDK compatibility (beta)](/en/api/openai-sdk)

# Examples

* [Messages examples](/en/api/messages-examples)
* [Message Batches examples](/en/api/messages-batch-examples)

**Legacy API**

The Text Completions API is a legacy API. Future models and features will require use of the [Messages API](/en/api/messages), and we recommend [migrating](/en/api/migrating-from-text-completions-to-messages) as soon as possible.

When creating a Text Completion, you can set `"stream": true` to incrementally stream the response using [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent%5Fevents/Using%5Fserver-sent%5Fevents) (SSE). If you are using our [client libraries](/en/api/client-sdks), parsing these events will be handled for you automatically. However, if you are building a direct API integration, you will need to handle these events yourself.

# [​](#example) Example

Shell

```
curl https://api.anthropic.com/v1/complete \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --data '
{
  "model": "claude-2",
  "prompt": "\n\nHuman: Hello, world!\n\nAssistant:",
  "max_tokens_to_sample": 256,
  "stream": true
}
'

```

Response

```
event: completion
data: {"type": "completion", "completion": " Hello", "stop_reason": null, "model": "claude-2.0"}

event: completion
data: {"type": "completion", "completion": "!", "stop_reason": null, "model": "claude-2.0"}

event: ping
data: {"type": "ping"}

event: completion
data: {"type": "completion", "completion": " My", "stop_reason": null, "model": "claude-2.0"}

event: completion
data: {"type": "completion", "completion": " name", "stop_reason": null, "model": "claude-2.0"}

event: completion
data: {"type": "completion", "completion": " is", "stop_reason": null, "model": "claude-2.0"}

event: completion
data: {"type": "completion", "completion": " Claude", "stop_reason": null, "model": "claude-2.0"}

event: completion
data: {"type": "completion", "completion": ".", "stop_reason": null, "model": "claude-2.0"}

event: completion
data: {"type": "completion", "completion": "", "stop_reason": "stop_sequence", "model": "claude-2.0"}

```

# [​](#events) Events

Each event includes a named event type and associated JSON data.

Event types: `completion`, `ping`, `error`.

# [​](#error-event-types) Error event types

We may occasionally send [errors](/en/api/errors) in the event stream. For example, during periods of high usage, you may receive an `overloaded_error`, which would normally correspond to an HTTP 529 in a non-streaming context:

Example error

```
event: completion
data: {"completion": " Hello", "stop_reason": null, "model": "claude-2.0"}

event: error
data: {"error": {"type": "overloaded_error", "message": "Overloaded"}}

```

# [​](#older-api-versions) Older API versions

If you are using an [API version](/en/api/versioning) prior to `2023-06-01`, the response shape will be different. See [versioning](/en/api/versioning) for details.

Was this page helpful?

YesNo

Create a Text Completion[Prompt validation](/en/api/prompt-validation)

On this page
