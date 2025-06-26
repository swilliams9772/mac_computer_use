# List Workspaces - Anthropic

**Source:** https://docs.anthropic.com/en/api/admin-api/workspaces/list-workspaces

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# API reference

* Messages
* Models
* Message Batches
* Files
* + Organization Member Management
  + Organization Invites
  + Workspace Management
  - [GET

      Get Workspace](/en/api/admin-api/workspaces/get-workspace)
  - [GET

      List Workspaces](/en/api/admin-api/workspaces/list-workspaces)
  - [POST

      Update Workspace](/en/api/admin-api/workspaces/update-workspace)
  - [POST

      Create Workspace](/en/api/admin-api/workspaces/create-workspace)
  - [POST

      Archive Workspace](/en/api/admin-api/workspaces/archive-workspace)
  + Workspace Member Management
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

organizations

/

workspaces

cURL

Python

JavaScript

PHP

Go

Java

```
curl "https://api.anthropic.com/v1/organizations/workspaces" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

200

4XX

```
{
  "data": [
    {
      "id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ",
      "type": "workspace",
      "name": "Workspace Name",
      "created_at": "2024-10-30T23:58:27.427722Z",
      "archived_at": "2024-11-01T23:59:27.427722Z",
      "display_color": "#6C5BB9"
    }
  ],
  "has_more": true,
  "first_id": "<string>",
  "last_id": "<string>"
}
```

# Headers

Your unique Admin API key for authentication.

This key is required in the header of all Admin API requests, to authenticate your account and access Anthropic's services. Get your Admin API key through the [Console](https://console.anthropic.com/settings/admin-keys).

[​](#parameter-anthropic-version)

anthropic-version

string

required

The version of the Anthropic API you want to use.

Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning).

# Query Parameters

[​](#parameter-include-archived)

include\_archived

boolean

default:false

Whether to include Workspaces that have been archived in the response

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

[​](#response-data-id)

data.id

string

required

ID of the Workspace.

Examples:

`"wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ"`

[​](#response-data-type)

data.type

enum<string>

default:workspace

required

Object type.

For Workspaces, this is always `"workspace"`.

Available options:

`workspace`

[​](#response-data-name)

data.name

string

required

Name of the Workspace.

Examples:

`"Workspace Name"`

[​](#response-data-created-at)

data.created\_at

string

required

RFC 3339 datetime string indicating when the Workspace was created.

Examples:

`"2024-10-30T23:58:27.427722Z"`

[​](#response-data-archived-at)

data.archived\_at

string | null

required

RFC 3339 datetime string indicating when the Workspace was archived, or null if the Workspace is not archived.

Examples:

`"2024-11-01T23:59:27.427722Z"`

[​](#response-data-display-color)

data.display\_color

string

required

Hex color code representing the Workspace in the Anthropic Console.

Examples:

`"#6C5BB9"`

[​](#response-has-more)

has\_more

boolean

required

Indicates if there are more results in the requested page direction.

[​](#response-first-id)

first\_id

string | null

required

First ID in the `data` list. Can be used as the `before_id` for the previous page.

[​](#response-last-id)

last\_id

string | null

required

Last ID in the `data` list. Can be used as the `after_id` for the next page.

Was this page helpful?

YesNo

Get Workspace[Update Workspace](/en/api/admin-api/workspaces/update-workspace)

cURL

Python

JavaScript

PHP

Go

Java

```
curl "https://api.anthropic.com/v1/organizations/workspaces" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

200

4XX

```
{
  "data": [
    {
      "id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ",
      "type": "workspace",
      "name": "Workspace Name",
      "created_at": "2024-10-30T23:58:27.427722Z",
      "archived_at": "2024-11-01T23:59:27.427722Z",
      "display_color": "#6C5BB9"
    }
  ],
  "has_more": true,
  "first_id": "<string>",
  "last_id": "<string>"
}
```
