# Versions - Anthropic

**Source:** https://docs.anthropic.com/en/api/versioning

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# Using the APIs

* [Overview](/en/api/overview)
* Forming requests

  + [Versions](/en/api/versioning)
  + [Rate limits](/en/api/rate-limits)
  + [Service tiers](/en/api/service-tiers)
  + [Beta headers](/en/api/beta-headers)
* Handling responses

# SDKs

* [Client SDKs](/en/api/client-sdks)
* [OpenAI SDK compatibility (beta)](/en/api/openai-sdk)

# Examples

* [Messages examples](/en/api/messages-examples)
* [Message Batches examples](/en/api/messages-batch-examples)

For any given API version, we will preserve:

* Existing input parameters
* Existing output parameters

However, we may do the following:

* Add additional optional inputs
* Add additional values to the output
* Change conditions for specific error types
* Add new variants to enum-like output values (for example, streaming event types)

Generally, if you are using the API as documented in this reference, we will not break your usage.

# [​](#version-history) Version history

We always recommend using the latest API version whenever possible. Previous versions are considered deprecated and may be unavailable for new users.

* `2023-06-01`
  + New format for [streaming](/en/api/streaming) server-sent events (SSE):
  - Completions are incremental. For example, `" Hello"`, `" my"`, `" name"`, `" is"`, `" Claude."`  instead of `" Hello"`, `" Hello my"`, `" Hello my name"`, `" Hello my name is"`, `" Hello my name is Claude."`.
  - All events are [named events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent%5Fevents/Using%5Fserver-sent%5Fevents#named%5Fevents), rather than [data-only events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent%5Fevents/Using%5Fserver-sent%5Fevents#data-only%5Fmessages).
  - Removed unnecessary `data: [DONE]` event.
  + Removed legacy `exception` and `truncated` values in responses.
* `2023-01-01`: Initial release.

Was this page helpful?

YesNo

Overview[Rate limits](/en/api/rate-limits)

On this page
