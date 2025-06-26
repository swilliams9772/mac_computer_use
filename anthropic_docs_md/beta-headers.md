# Beta headers - Anthropic

**Source:** https://docs.anthropic.com/en/api/beta-headers

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# Using the APIs

* [Overview](/en/api/overview)
* Forming requests

  + [Versions](/en/api/versioning)
  + [Rate limits](/en/api/rate-limits)
  + [Service tiers](/en/api/service-tiers)
  + [Beta headers](/en/api/beta-headers)
* Handling responses

# SDKs

* [Client SDKs](/en/api/client-sdks)
* [OpenAI SDK compatibility (beta)](/en/api/openai-sdk)

# Examples

* [Messages examples](/en/api/messages-examples)
* [Message Batches examples](/en/api/messages-batch-examples)

Beta headers allow you to access experimental features and new model capabilities before they become part of the standard API.

These features are subject to change and may be modified or removed in future releases.

# [​](#how-to-use-beta-headers) How to use beta headers

To access beta features, include the `anthropic-beta` header in your API requests:

```
POST /v1/messages
Content-Type: application/json
X-API-Key: YOUR_API_KEY
anthropic-beta: BETA_FEATURE_NAME

```

When using the SDK, you can specify beta headers in the request options:

Python

TypeScript

cURL

```
from anthropic import Anthropic

client = Anthropic()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ],
    extra_headers={
        "anthropic-beta": "beta-feature-name"
    }
)

```

Beta features are experimental and may:

* Have breaking changes without notice
* Be deprecated or removed
* Have different rate limits or pricing
* Not be available in all regions

# [​](#multiple-beta-features) Multiple beta features

To use multiple beta features in a single request, include all feature names in the header separated by commas:

```
anthropic-beta: feature1,feature2,feature3

```

# [​](#version-naming-conventions) Version naming conventions

Beta feature names typically follow the pattern: `feature-name-YYYY-MM-DD`, where the date indicates when the beta version was released. Always use the exact beta feature name as documented.

# [​](#error-handling) Error handling

If you use an invalid or unavailable beta header, you’ll receive an error response:

```
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "Unsupported beta header: invalid-beta-name"
  }
}

```

# [​](#getting-help) Getting help

For questions about beta features:

1. Check the documentation for the specific feature
2. Review the [API changelog](/en/api/versioning) for updates
3. Contact support for assistance with production usage

Remember that beta features are provided “as-is” and may not have the same SLA guarantees as stable API features.

Was this page helpful?

YesNo

Service tiers[Errors](/en/api/errors)

On this page
