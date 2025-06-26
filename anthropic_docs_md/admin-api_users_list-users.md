# List Users - Anthropic

**Source:** https://docs.anthropic.com/en/api/admin-api/users/list-users

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

GET

/

v1

/

organizations

/

users

cURL

Python

JavaScript

PHP

Go

Java

```
curl "https://api.anthropic.com/v1/organizations/users" \
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
      "id": "user_01WCz1FkmYMm4gnmykNKUu3Q",
      "type": "user",
      "email": "user@emaildomain.com",
      "name": "Jane Doe",
      "role": "user",
      "added_at": "2024-10-30T23:58:27.427722Z"
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

[​](#parameter-email)

email

string

Filter by user email.

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

ID of the User.

Examples:

`"user_01WCz1FkmYMm4gnmykNKUu3Q"`

[​](#response-data-type)

data.type

enum<string>

default:user

required

Object type.

For Users, this is always `"user"`.

Available options:

`user`

[​](#response-data-email)

data.email

string

required

Email of the User.

Examples:

`"user@emaildomain.com"`

[​](#response-data-name)

data.name

string

required

Name of the User.

Examples:

`"Jane Doe"`

[​](#response-data-role)

data.role

enum<string>

required

Organization role of the User.

Available options:

`user`,

`developer`,

`billing`,

`admin`

Examples:

`"user"`

`"developer"`

`"billing"`

`"admin"`

[​](#response-data-added-at)

data.added\_at

string

required

RFC 3339 datetime string indicating when the User joined the Organization.

Examples:

`"2024-10-30T23:58:27.427722Z"`

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

Get User[Update User](/en/api/admin-api/users/update-user)

cURL

Python

JavaScript

PHP

Go

Java

```
curl "https://api.anthropic.com/v1/organizations/users" \
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
      "id": "user_01WCz1FkmYMm4gnmykNKUu3Q",
      "type": "user",
      "email": "user@emaildomain.com",
      "name": "Jane Doe",
      "role": "user",
      "added_at": "2024-10-30T23:58:27.427722Z"
    }
  ],
  "has_more": true,
  "first_id": "<string>",
  "last_id": "<string>"
}
```
