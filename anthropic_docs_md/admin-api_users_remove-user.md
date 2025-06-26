# Remove User - Anthropic

**Source:** https://docs.anthropic.com/en/api/admin-api/users/remove-user

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
  - [GET

      Get User](/en/api/admin-api/users/get-user)
  - [GET

      List Users](/en/api/admin-api/users/list-users)
  - [POST

      Update User](/en/api/admin-api/users/update-user)
  - [DEL

      Remove User](/en/api/admin-api/users/remove-user)
  + Organization Invites
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

users

/

{user\_id}

cURL

Python

JavaScript

PHP

Go

Java

```
curl --request DELETE "https://api.anthropic.com/v1/organizations/users/user_01WCz1FkmYMm4gnmykNKUu3Q" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

200

4XX

```
{
  "id": "user_01WCz1FkmYMm4gnmykNKUu3Q",
  "type": "user_deleted"
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

# Path Parameters

[​](#parameter-user-id)

user\_id

string

required

ID of the User.

# Response

200

2004XX

application/json

Successful Response

[​](#response-id)

id

string

required

ID of the User.

Examples:

`"user_01WCz1FkmYMm4gnmykNKUu3Q"`

[​](#response-type)

type

enum<string>

default:user\_deleted

required

Deleted object type.

For Users, this is always `"user_deleted"`.

Available options:

`user_deleted`

Was this page helpful?

YesNo

Update User[Get Invite](/en/api/admin-api/invites/get-invite)

cURL

Python

JavaScript

PHP

Go

Java

```
curl --request DELETE "https://api.anthropic.com/v1/organizations/users/user_01WCz1FkmYMm4gnmykNKUu3Q" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

200

4XX

```
{
  "id": "user_01WCz1FkmYMm4gnmykNKUu3Q",
  "type": "user_deleted"
}
```
