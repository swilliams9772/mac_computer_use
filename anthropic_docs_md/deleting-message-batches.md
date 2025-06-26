# Delete a Message Batch - Anthropic

**Source:** https://docs.anthropic.com/en/api/deleting-message-batches

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# API reference

* Messages
* Models
* Message Batches

  + [POST

    Create a Message Batch](/en/api/creating-message-batches)
  + [GET

    Retrieve a Message Batch](/en/api/retrieving-message-batches)
  + [GET

    Retrieve Message Batch Results](/en/api/retrieving-message-batch-results)
  + [GET

    List Message Batches](/en/api/listing-message-batches)
  + [POST

    Cancel a Message Batch](/en/api/canceling-message-batches)
  + [DEL

    Delete a Message Batch](/en/api/deleting-message-batches)
* Files
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

messages

/

batches

/

{message\_batch\_id}

cURL

Python

JavaScript

PHP

Go

Java

```
curl -X DELETE https://api.anthropic.com/v1/messages/batches/msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01"
```

200

4XX

```
{
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "type": "message_batch_deleted"
}
```

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

# Path Parameters

[​](#parameter-message-batch-id)

message\_batch\_id

string

required

ID of the Message Batch.

# Response

200

2004XX

application/json

Successful Response

[​](#response-id)

id

string

required

ID of the Message Batch.

Examples:

`"msgbatch_013Zva2CMHLNnXjNJJKqJ2EF"`

[​](#response-type)

type

enum<string>

default:message\_batch\_deleted

required

Deleted object type.

For Message Batches, this is always `"message_batch_deleted"`.

Available options:

`message_batch_deleted`

Was this page helpful?

YesNo

Cancel a Message Batch[Create a File](/en/api/files-create)

cURL

Python

JavaScript

PHP

Go

Java

```
curl -X DELETE https://api.anthropic.com/v1/messages/batches/msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01"
```

200

4XX

```
{
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "type": "message_batch_deleted"
}
```
