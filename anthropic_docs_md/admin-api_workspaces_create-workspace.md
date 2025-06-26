# Create Workspace - Anthropic

**Source:** https://docs.anthropic.com/en/api/admin-api/workspaces/create-workspace

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

POST

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
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "name": "Workspace Name"
  }'
```

200

4XX

```
{
  "id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ",
  "type": "workspace",
  "name": "Workspace Name",
  "created_at": "2024-10-30T23:58:27.427722Z",
  "archived_at": "2024-11-01T23:59:27.427722Z",
  "display_color": "#6C5BB9"
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

# Body

application/json

[​](#body-name)

name

string

required

Name of the Workspace.

Required string length: `1 - 40`

# Response

200

2004XX

application/json

Successful Response

[​](#response-id)

id

string

required

ID of the Workspace.

Examples:

`"wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ"`

[​](#response-type)

type

enum<string>

default:workspace

required

Object type.

For Workspaces, this is always `"workspace"`.

Available options:

`workspace`

[​](#response-name)

name

string

required

Name of the Workspace.

Examples:

`"Workspace Name"`

[​](#response-created-at)

created\_at

string

required

RFC 3339 datetime string indicating when the Workspace was created.

Examples:

`"2024-10-30T23:58:27.427722Z"`

[​](#response-archived-at)

archived\_at

string | null

required

RFC 3339 datetime string indicating when the Workspace was archived, or null if the Workspace is not archived.

Examples:

`"2024-11-01T23:59:27.427722Z"`

[​](#response-display-color)

display\_color

string

required

Hex color code representing the Workspace in the Anthropic Console.

Examples:

`"#6C5BB9"`

Was this page helpful?

YesNo

Update Workspace[Archive Workspace](/en/api/admin-api/workspaces/archive-workspace)

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
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "name": "Workspace Name"
  }'
```

200

4XX

```
{
  "id": "wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ",
  "type": "workspace",
  "name": "Workspace Name",
  "created_at": "2024-10-30T23:58:27.427722Z",
  "archived_at": "2024-11-01T23:59:27.427722Z",
  "display_color": "#6C5BB9"
}
```
