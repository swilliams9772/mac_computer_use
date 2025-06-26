# List Files - Anthropic

**Source:** https://docs.anthropic.com/en/api/files-list

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# API reference

* Messages
* Models
* Message Batches
* Files

  + [POST

    Create a File](/en/api/files-create)
  + [GET

    List Files](/en/api/files-list)
  + [GET

    Get File Metadata](/en/api/files-metadata)
  + [GET

    Download a File](/en/api/files-content)
  + [DEL

    Delete a File](/en/api/files-delete)
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

files

cURL

Python

JavaScript

PHP

Go

Java

```
curl "https://api.anthropic.com/v1/files" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14"
```

200

4XX

```
{
  "data": [
    {
      "created_at": "2023-11-07T05:31:56Z",
      "downloadable": false,
      "filename": "<string>",
      "id": "<string>",
      "mime_type": "<string>",
      "size_bytes": 1,
      "type": "file"
    }
  ],
  "first_id": "<string>",
  "has_more": false,
  "last_id": "<string>"
}
```

The Files API allows you to upload and manage files to use with the Anthropic API without having to re-upload content with each request. For more information about the Files API, see the the [developer guide for files](/en/build-with-claude/files).

The Files API is currently in beta. To use the Files API, you’ll need to include the beta feature header: `anthropic-beta: files-api-2025-04-14`.

Please reach out through our [feedback form](https://forms.gle/tisHyierGwgN4DUE9) to share your experience with the Files API.

# Headers

[​](#parameter-anthropic-beta)

anthropic-beta

string[]

Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like `beta1,beta2` or specify the header multiple times for each beta.

[​](#parameter-anthropic-version)

anthropic-version

string

required

The version of the Anthropic API you want to use.

Read more about versioning and our version history [here](https://docs.anthropic.com/en/api/versioning).

Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the [Console](https://console.anthropic.com/settings/keys). Each key is scoped to a Workspace.

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

List of file metadata objects.

Show child attributes

[​](#response-data-created-at)

data.created\_at

string

required

RFC 3339 datetime string representing when the file was created.

[​](#response-data-filename)

data.filename

string

required

Original filename of the uploaded file.

Required string length: `1 - 500`

[​](#response-data-id)

data.id

string

required

Unique object identifier.

The format and length of IDs may change over time.

[​](#response-data-mime-type)

data.mime\_type

string

required

MIME type of the file.

Required string length: `1 - 255`

[​](#response-data-size-bytes)

data.size\_bytes

integer

required

Size of the file in bytes.

Required range: `x >= 0`

[​](#response-data-type)

data.type

enum<string>

required

Object type.

For files, this is always `"file"`.

Available options:

`file`

[​](#response-data-downloadable)

data.downloadable

boolean

default:false

Whether the file can be downloaded.

[​](#response-first-id)

first\_id

string | null

ID of the first file in this page of results.

[​](#response-has-more)

has\_more

boolean

default:false

Whether there are more results available.

[​](#response-last-id)

last\_id

string | null

ID of the last file in this page of results.

Was this page helpful?

YesNo

Create a File[Get File Metadata](/en/api/files-metadata)

cURL

Python

JavaScript

PHP

Go

Java

```
curl "https://api.anthropic.com/v1/files" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14"
```

200

4XX

```
{
  "data": [
    {
      "created_at": "2023-11-07T05:31:56Z",
      "downloadable": false,
      "filename": "<string>",
      "id": "<string>",
      "mime_type": "<string>",
      "size_bytes": 1,
      "type": "file"
    }
  ],
  "first_id": "<string>",
  "has_more": false,
  "last_id": "<string>"
}
```
