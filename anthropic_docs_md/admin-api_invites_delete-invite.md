# Delete Invite - Anthropic

**Source:** https://docs.anthropic.com/en/api/admin-api/invites/delete-invite

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
  - [GET

      Get Invite](/en/api/admin-api/invites/get-invite)
  - [GET

      List Invites](/en/api/admin-api/invites/list-invites)
  - [POST

      Create Invite](/en/api/admin-api/invites/create-invite)
  - [DEL

      Delete Invite](/en/api/admin-api/invites/delete-invite)
  + Workspace Management
  + Workspace Member Management
* Text Completions (Legacy)

# SDKs

* [Client SDKs](/en/api/client-sdks)
* [OpenAI SDK compatibility (beta)](/en/api/openai-sdk)

# Examples

* [Messages examples](/en/api/messages-examples)
* [Message Batches examples](/en/api/messages-batch-examples)

DELETE

/

v1

/

organizations

/

invites

/

{invite\_id}

cURL

Python

JavaScript

PHP

Go

Java

```
curl --request DELETE "https://api.anthropic.com/v1/organizations/invites/invite_015gWxCN9Hfg2QhZwTK7Mdeu" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

200

4XX

```
{
  "id": "invite_015gWxCN9Hfg2QhZwTK7Mdeu",
  "type": "invite_deleted"
}
```

**The Admin API is unavailable for individual accounts.** To collaborate with teammates and add members, set up your organization in **Console → Settings → Organization**.

# Headers

Your unique Admin API key for authentication.

This key is required in the header of all Admin API requests, to authenticate your account and access Anthropic's services. Get your Admin API key through the [Console](https://console.anthropic.com/settings/admin-keys).

[​](#parameter-anthropic-version)

anthropic-version

string

required

The version of the Anthropic API you want to use.

Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning).

# Path Parameters

[​](#parameter-invite-id)

invite\_id

string

required

ID of the Invite.

# Response

200

2004XX

application/json

Successful Response

[​](#response-id)

id

string

required

ID of the Invite.

Examples:

`"invite_015gWxCN9Hfg2QhZwTK7Mdeu"`

[​](#response-type)

type

enum<string>

default:invite\_deleted

required

Deleted object type.

For Invites, this is always `"invite_deleted"`.

Available options:

`invite_deleted`

Was this page helpful?

YesNo

Create Invite[Get Workspace](/en/api/admin-api/workspaces/get-workspace)

cURL

Python

JavaScript

PHP

Go

Java

```
curl --request DELETE "https://api.anthropic.com/v1/organizations/invites/invite_015gWxCN9Hfg2QhZwTK7Mdeu" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

200

4XX

```
{
  "id": "invite_015gWxCN9Hfg2QhZwTK7Mdeu",
  "type": "invite_deleted"
}
```
