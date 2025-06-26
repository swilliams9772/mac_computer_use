# Get a Model - Anthropic

**Source:** https://docs.anthropic.com/en/api/models

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# API reference

* Messages
* Models

  + [GET

    List Models](/en/api/models-list)
  + [GET

    Get a Model](/en/api/models)
* Message Batches
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

models

/

{model\_id}

cURL

Python

JavaScript

PHP

Go

Java

```
curl https://api.anthropic.com/v1/models/claude-3-7-sonnet-20250219 \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01"
```

200

4XX

```
{
  "created_at": "2025-02-19T00:00:00Z",
  "display_name": "Claude 3.7 Sonnet",
  "id": "claude-3-7-sonnet-20250219",
  "type": "model"
}
```

# Headers

[​](#parameter-anthropic-version)

anthropic-version

string

required

The version of the Anthropic API you want to use.

Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning).

Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the [Console](https://console.anthropic.com/settings/keys). Each key is scoped to a Workspace.

[​](#parameter-anthropic-beta)

anthropic-beta

string[]

Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like `beta1,beta2` or specify the header multiple times for each beta.

# Path Parameters

[​](#parameter-model-id)

model\_id

string

required

Model identifier or alias.

# Response

200

2004XX

application/json

Successful Response

[​](#response-created-at)

created\_at

string

required

RFC 3339 datetime string representing the time at which the model was released. May be set to an epoch value if the release date is unknown.

Examples:

`"2025-02-19T00:00:00Z"`

[​](#response-display-name)

display\_name

string

required

A human-readable name for the model.

Examples:

`"Claude 3.7 Sonnet"`

[​](#response-id)

id

string

required

Unique model identifier.

Examples:

`"claude-3-7-sonnet-20250219"`

[​](#response-type)

type

enum<string>

default:model

required

Object type.

For Models, this is always `"model"`.

Available options:

`model`

Was this page helpful?

YesNo

List Models[Create a Message Batch](/en/api/creating-message-batches)

cURL

Python

JavaScript

PHP

Go

Java

```
curl https://api.anthropic.com/v1/models/claude-3-7-sonnet-20250219 \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01"
```

200

4XX

```
{
  "created_at": "2025-02-19T00:00:00Z",
  "display_name": "Claude 3.7 Sonnet",
  "id": "claude-3-7-sonnet-20250219",
  "type": "model"
}
```
