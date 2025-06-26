# Overview - Anthropic

**Source:** https://docs.anthropic.com/en/api/getting-started

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

# [​](#accessing-the-api) Accessing the API

The API is made available via our web [Console](https://console.anthropic.com/). You can use the [Workbench](https://console.anthropic.com/workbench/3b57d80a-99f2-4760-8316-d3bb14fbfb1e) to try out the API in the browser and then generate API keys in [Account Settings](https://console.anthropic.com/account/keys). Use [workspaces](https://console.anthropic.com/settings/workspaces) to segment your API keys and [control spend](/en/api/rate-limits) by use case.

# [​](#authentication) Authentication

All requests to the Anthropic API must include an `x-api-key` header with your API key. If you are using the Client SDKs, you will set the API when constructing a client, and then the SDK will send the header on your behalf with every request. If integrating directly with the API, you’ll need to send this header yourself.

# [​](#content-types) Content types

The Anthropic API always accepts JSON in request bodies and returns JSON in response bodies. You will need to send the `content-type: application/json` header in requests. If you are using the Client SDKs, this will be taken care of automatically.

# [​](#response-headers) Response Headers

The Anthropic API includes the following headers in every response:

* `request-id`: A globally unique identifier for the request.
* `anthropic-organization-id`: The organization ID associated with the API key used in the request.

# [​](#examples) Examples

* curl
* Python
* TypeScript

Shell

```
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data \
'{
    "model": "claude-opus-4-20250514",
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "Hello, world"}
    ]
}'

```

Shell

```
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data \
'{
    "model": "claude-opus-4-20250514",
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "Hello, world"}
    ]
}'

```

Install via PyPI:

```
pip install anthropic

```

Python

```
import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="my_api_key",
)
message = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)
print(message.content)

```

Install via npm:

```
npm install @anthropic-ai/sdk

```

TypeScript

```
import Anthropic from '@anthropic-ai/sdk';

const anthropic = new Anthropic({
  apiKey: 'my_api_key', // defaults to process.env["ANTHROPIC_API_KEY"]
});

const msg = await anthropic.messages.create({
  model: "claude-opus-4-20250514",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello, Claude" }],
});
console.log(msg);

```

Was this page helpful?

YesNo

[Versions](/en/api/versioning)

On this page
