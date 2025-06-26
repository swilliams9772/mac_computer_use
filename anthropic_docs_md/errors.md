# Errors - Anthropic

**Source:** https://docs.anthropic.com/en/api/errors#http-errors

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# SDKs

* [Client SDKs](/en/api/client-sdks)
* [OpenAI SDK compatibility (beta)](/en/api/openai-sdk)

# Examples

* [Messages examples](/en/api/messages-examples)
* [Message Batches examples](/en/api/messages-batch-examples)

# [​](#http-errors) HTTP errors

Our API follows a predictable HTTP error code format:

* 400 - `invalid_request_error`: There was an issue with the format or content of your request. We may also use this error type for other 4XX status codes not listed below.
* 401 - `authentication_error`: There’s an issue with your API key.
* 403 - `permission_error`: Your API key does not have permission to use the specified resource.
* 404 - `not_found_error`: The requested resource was not found.
* 413 - `request_too_large`: Request exceeds the maximum allowed number of bytes.
* 429 - `rate_limit_error`: Your account has hit a rate limit.
* 500 - `api_error`: An unexpected error has occurred internal to Anthropic’s systems.
* 529 - `overloaded_error`: Anthropic’s API is temporarily overloaded.

  529 errors can occur when Anthropic APIs experience high traffic across all users. In rare cases, if your organization has a sharp increase in usage, you might see this type of error.
  To avoid 529 errors, ramp up your traffic gradually and maintain consistent usage patterns.

When receiving a [streaming](/en/api/streaming) response via SSE, it’s possible that an error can occur after returning a 200 response, in which case error handling wouldn’t follow these standard mechanisms.

# [​](#error-shapes) Error shapes

Errors are always returned as JSON, with a top-level `error` object that always includes a `type` and `message` value. For example:

JSON

```
{
  "type": "error",
  "error": {
    "type": "not_found_error",
    "message": "The requested resource could not be found."
  }
}

```

In accordance with our [versioning](/en/api/versioning) policy, we may expand the values within these objects, and it is possible that the `type` values will grow over time.

# [​](#request-id) Request id

Every API response includes a unique `request-id` header. This header contains a value such as `req_018EeWyXxfu5pfWkrYcMdjWG`. When contacting support about a specific request, please include this ID to help us quickly resolve your issue.

Our official SDKs provide this value as a property on top-level response objects, containing the value of the `x-request-id` header:

Python

TypeScript

```
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)
print(f"Request ID: {message._request_id}")

```

# [​](#long-requests) Long requests

We highly encourage using the [streaming Messages API](/en/api/messages-streaming) or [Message Batches API](/en/api/creating-message-batches) for long running requests, especially those over 10 minutes.

We do not recommend setting a large `max_tokens` values without using our [streaming Messages API](/en/api/messages-streaming)
or [Message Batches API](/en/api/creating-message-batches):

* Some networks may drop idle connections after a variable period of time, which
  can cause the request to fail or timeout without receiving a response from Anthropic.
* Networks differ in reliablity; our [Message Batches API](/en/api/creating-message-batches) can help you
  manage the risk of network issues by allowing you to poll for results rather than requiring an uninterrupted network connection.

If you are building a direct API integration, you should be aware that setting a [TCP socket keep-alive](https://tldp.org/HOWTO/TCP-Keepalive-HOWTO/programming.html) can reduce the impact of idle connection timeouts on some networks.

Our [SDKs](/en/api/client-sdks) will validate that your non-streaming Messages API requests are not expected to exceed a 10 minute timeout and
also will set a socket option for TCP keep-alive.

Was this page helpful?

YesNo

Beta headers[Handling stop reasons](/en/api/handling-stop-reasons)

On this page
