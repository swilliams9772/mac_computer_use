# List Models - Anthropic

**Source:** https://docs.anthropic.com/en/api/models-list

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

cURL

Python

JavaScript

PHP

Go

Java

```
curl https://api.anthropic.com/v1/models \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01"
```

200

4XX

```
{
  "data": [
    {
      "created_at": "2025-02-19T00:00:00Z",
      "display_name": "Claude 3.7 Sonnet",
      "id": "claude-3-7-sonnet-20250219",
      "type": "model"
    }
  ],
  "first_id": "<string>",
  "has_more": true,
  "last_id": "<string>"
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

# Query Parameters

[​](#parameter-before-id)

before\_id

string

ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately before this object.

[​](#parameter-after-id)

after\_id

string

ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately after this object.

[​](#parameter-limit)

limit

integer

default:20

Number of items to return per page.

Defaults to `20`. Ranges from `1` to `1000`.

Required range: `1 <= x <= 1000`

# Response

200

2004XX

application/json

Successful Response

[​](#response-data)

data

object[]

required

Show child attributes

[​](#response-data-created-at)

data.created\_at

string

required

RFC 3339 datetime string representing the time at which the model was released. May be set to an epoch value if the release date is unknown.

Examples:

`"2025-02-19T00:00:00Z"`

[​](#response-data-display-name)

data.display\_name

string

required

A human-readable name for the model.

Examples:

`"Claude 3.7 Sonnet"`

[​](#response-data-id)

data.id

string

required

Unique model identifier.

Examples:

`"claude-3-7-sonnet-20250219"`

[​](#response-data-type)

data.type

enum<string>

default:model

required

Object type.

For Models, this is always `"model"`.

Available options:

`model`

[​](#response-first-id)

first\_id

string | null

required

First ID in the `data` list. Can be used as the `before_id` for the previous page.

[​](#response-has-more)

has\_more

boolean

required

Indicates if there are more results in the requested page direction.

[​](#response-last-id)

last\_id

string | null

required

Last ID in the `data` list. Can be used as the `after_id` for the next page.

Was this page helpful?

YesNo

Count Message tokens[Get a Model](/en/api/models)

cURL

Python

JavaScript

PHP

Go

Java

```
curl https://api.anthropic.com/v1/models \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01"
```

200

4XX

```
{
  "data": [
    {
      "created_at": "2025-02-19T00:00:00Z",
      "display_name": "Claude 3.7 Sonnet",
      "id": "claude-3-7-sonnet-20250219",
      "type": "model"
    }
  ],
  "first_id": "<string>",
  "has_more": true,
  "last_id": "<string>"
}
```
