# Prompt validation - Anthropic

**Source:** https://docs.anthropic.com/en/api/prompt-validation

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# API reference

* Messages
* Models
* Message Batches
* Files
* Text Completions (Legacy)

  + [Migrating from Text Completions](/en/api/migrating-from-text-completions-to-messages)
  + [POST

    Create a Text Completion](/en/api/complete)
  + [Streaming Text Completions](/en/api/streaming)
  + [Prompt validation](/en/api/prompt-validation)

# SDKs

* [Client SDKs](/en/api/client-sdks)
* [OpenAI SDK compatibility (beta)](/en/api/openai-sdk)

# Examples

* [Messages examples](/en/api/messages-examples)
* [Message Batches examples](/en/api/messages-batch-examples)

**Legacy API**

The Text Completions API is a legacy API. Future models and features will require use of the [Messages API](/en/api/messages), and we recommend [migrating](/en/api/migrating-from-text-completions-to-messages) as soon as possible.

The Anthropic API performs basic prompt sanitization and validation to help ensure that your prompts are well-formatted for Claude.

When creating Text Completions, if your prompt is not in the specified format, the API will first attempt to lightly sanitize it (for example, by removing trailing spaces). This exact behavior is subject to change, and we strongly recommend that you format your prompts with the [recommended](/en/docs/prompt-engineering#the-prompt-is-formatted-correctly) alternating `\n\nHuman:` and `\n\nAssistant:` turns.

Then, the API will validate your prompt under the following conditions:

* The first conversational turn in the prompt must be a `\n\nHuman:` turn
* The last conversational turn in the prompt be an `\n\nAssistant:` turn
* The prompt must be less than `100,000 - 1` tokens in length.

# [​](#examples) Examples

The following prompts will results in [API errors](/en/api/errors):

Python

```
# Missing "\n\nHuman:" and "\n\nAssistant:" turns

prompt = "Hello, world"

# Missing "\n\nHuman:" turn

prompt = "Hello, world\n\nAssistant:"

# Missing "\n\nAssistant:" turn

prompt = "\n\nHuman: Hello, Claude"

# "\n\nHuman:" turn is not first

prompt = "\n\nAssistant: Hello, world\n\nHuman: Hello, Claude\n\nAssistant:"

# "\n\nAssistant:" turn is not last

prompt = "\n\nHuman: Hello, Claude\n\nAssistant: Hello, world\n\nHuman: How many toes do dogs have?"

# "\n\nAssistant:" only has one "\n"

prompt = "\n\nHuman: Hello, Claude \nAssistant:"

```

The following are currently accepted and automatically sanitized by the API, but you should not rely on this behavior, as it may change in the future:

Python

```
# No leading "\n\n" for "\n\nHuman:"

prompt = "Human: Hello, Claude\n\nAssistant:"

# Trailing space after "\n\nAssistant:"

prompt = "\n\nHuman: Hello, Claude:\n\nAssistant: "

```

Was this page helpful?

YesNo

Streaming Text Completions[Client SDKs](/en/api/client-sdks)

On this page
