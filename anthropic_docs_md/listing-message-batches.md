# List Message Batches - Anthropic

**Source:** https://docs.anthropic.com/en/api/listing-message-batches

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

GET

/

v1

/

messages

/

batches

cURL

Python

JavaScript

PHP

Go

Java

```
curl https://api.anthropic.com/v1/messages/batches \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01"
```

200

4XX

```
{
  "data": [
    {
      "archived_at": "2024-08-20T18:37:24.100435Z",
      "cancel_initiated_at": "2024-08-20T18:37:24.100435Z",
      "created_at": "2024-08-20T18:37:24.100435Z",
      "ended_at": "2024-08-20T18:37:24.100435Z",
      "expires_at": "2024-08-20T18:37:24.100435Z",
      "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
      "processing_status": "in_progress",
      "request_counts": {
        "canceled": 10,
        "errored": 30,
        "expired": 10,
        "processing": 100,
        "succeeded": 50
      },
      "results_url": "https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results",
      "type": "message_batch"
    }
  ],
  "first_id": "<string>",
  "has_more": true,
  "last_id": "<string>"
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

[​](#response-data-archived-at)

data.archived\_at

string | null

required

RFC 3339 datetime string representing the time at which the Message Batch was archived and its results became unavailable.

Examples:

`"2024-08-20T18:37:24.100435Z"`

[​](#response-data-cancel-initiated-at)

data.cancel\_initiated\_at

string | null

required

RFC 3339 datetime string representing the time at which cancellation was initiated for the Message Batch. Specified only if cancellation was initiated.

Examples:

`"2024-08-20T18:37:24.100435Z"`

[​](#response-data-created-at)

data.created\_at

string

required

RFC 3339 datetime string representing the time at which the Message Batch was created.

Examples:

`"2024-08-20T18:37:24.100435Z"`

[​](#response-data-ended-at)

data.ended\_at

string | null

required

RFC 3339 datetime string representing the time at which processing for the Message Batch ended. Specified only once processing ends.

Processing ends when every request in a Message Batch has either succeeded, errored, canceled, or expired.

Examples:

`"2024-08-20T18:37:24.100435Z"`

[​](#response-data-expires-at)

data.expires\_at

string

required

RFC 3339 datetime string representing the time at which the Message Batch will expire and end processing, which is 24 hours after creation.

Examples:

`"2024-08-20T18:37:24.100435Z"`

[​](#response-data-id)

data.id

string

required

Unique object identifier.

The format and length of IDs may change over time.

Examples:

`"msgbatch_013Zva2CMHLNnXjNJJKqJ2EF"`

[​](#response-data-processing-status)

data.processing\_status

enum<string>

required

Processing status of the Message Batch.

Available options:

`in_progress`,

`canceling`,

`ended`

[​](#response-data-request-counts)

data.request\_counts

object

required

Tallies requests within the Message Batch, categorized by their status.

Requests start as `processing` and move to one of the other statuses only once processing of the entire batch ends. The sum of all values always matches the total number of requests in the batch.

Show child attributes

[​](#response-data-request-counts-canceled)

data.request\_counts.canceled

integer

default:0

required

Number of requests in the Message Batch that have been canceled.

This is zero until processing of the entire Message Batch has ended.

Examples:

`10`

[​](#response-data-request-counts-errored)

data.request\_counts.errored

integer

default:0

required

Number of requests in the Message Batch that encountered an error.

This is zero until processing of the entire Message Batch has ended.

Examples:

`30`

[​](#response-data-request-counts-expired)

data.request\_counts.expired

integer

default:0

required

Number of requests in the Message Batch that have expired.

This is zero until processing of the entire Message Batch has ended.

Examples:

`10`

[​](#response-data-request-counts-processing)

data.request\_counts.processing

integer

default:0

required

Number of requests in the Message Batch that are processing.

Examples:

`100`

[​](#response-data-request-counts-succeeded)

data.request\_counts.succeeded

integer

default:0

required

Number of requests in the Message Batch that have completed successfully.

This is zero until processing of the entire Message Batch has ended.

Examples:

`50`

[​](#response-data-results-url)

data.results\_url

string | null

required

URL to a `.jsonl` file containing the results of the Message Batch requests. Specified only once processing ends.

Results in the file are not guaranteed to be in the same order as requests. Use the `custom_id` field to match results to requests.

[​](#response-data-type)

data.type

enum<string>

default:message\_batch

required

Object type.

For Message Batches, this is always `"message_batch"`.

Available options:

`message_batch`

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

Retrieve Message Batch Results[Cancel a Message Batch](/en/api/canceling-message-batches)

cURL

Python

JavaScript

PHP

Go

Java

```
curl https://api.anthropic.com/v1/messages/batches \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01"
```

200

4XX

```
{
  "data": [
    {
      "archived_at": "2024-08-20T18:37:24.100435Z",
      "cancel_initiated_at": "2024-08-20T18:37:24.100435Z",
      "created_at": "2024-08-20T18:37:24.100435Z",
      "ended_at": "2024-08-20T18:37:24.100435Z",
      "expires_at": "2024-08-20T18:37:24.100435Z",
      "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
      "processing_status": "in_progress",
      "request_counts": {
        "canceled": 10,
        "errored": 30,
        "expired": 10,
        "processing": 100,
        "succeeded": 50
      },
      "results_url": "https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results",
      "type": "message_batch"
    }
  ],
  "first_id": "<string>",
  "has_more": true,
  "last_id": "<string>"
}
```
