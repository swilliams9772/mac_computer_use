# Migrating to Claude 4 - Anthropic

**Source:** https://docs.anthropic.com/en/docs/about-claude/models/migrating-to-claude-4

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# First steps

* [Intro to Claude](/en/docs/welcome)
* [Get started](/en/docs/get-started)

# Models & pricing

* [Models overview](/en/docs/about-claude/models/overview)
* [Choosing a model](/en/docs/about-claude/models/choosing-a-model)
* [Migrating to Claude 4](/en/docs/about-claude/models/migrating-to-claude-4)
* [Model deprecations](/en/docs/about-claude/model-deprecations)
* [Pricing](/en/docs/about-claude/pricing)

# Learn about Claude

* [Building with Claude](/en/docs/overview)
* Use cases
* [Context windows](/en/docs/build-with-claude/context-windows)
* [Glossary](/en/docs/about-claude/glossary)
* Prompt engineering

# Explore features

* [Features overview](/en/docs/build-with-claude/overview)
* [Prompt caching](/en/docs/build-with-claude/prompt-caching)
* [Extended thinking](/en/docs/build-with-claude/extended-thinking)
* [Streaming Messages](/en/docs/build-with-claude/streaming)
* [Batch processing](/en/docs/build-with-claude/batch-processing)
* [Citations](/en/docs/build-with-claude/citations)
* [Multilingual support](/en/docs/build-with-claude/multilingual-support)
* [Token counting](/en/docs/build-with-claude/token-counting)
* [Embeddings](/en/docs/build-with-claude/embeddings)
* [Vision](/en/docs/build-with-claude/vision)
* [PDF support](/en/docs/build-with-claude/pdf-support)

# Agent components

* Tools
* Model Context Protocol (MCP)
* [Computer use (beta)](/en/docs/agents-and-tools/computer-use)
* [Google Sheets add-on](/en/docs/agents-and-tools/claude-for-sheets)

# Test & evaluate

* [Define success criteria](/en/docs/test-and-evaluate/define-success)
* [Develop test cases](/en/docs/test-and-evaluate/develop-tests)
* Strengthen guardrails
* [Using the Evaluation Tool](/en/docs/test-and-evaluate/eval-tool)

# Legal center

* [Anthropic Privacy Policy](https://www.anthropic.com/legal/privacy)
* [Security and compliance](https://trust.anthropic.com/)

This page provides guidance on migrating from Claude 3.7 models to Claude 4 models (Opus 4 and Sonnet 4).

In most cases, you can switch to Claude 4 models with minimal changes:

1. Update your model name:
  * From: `claude-3-7-sonnet-20250219`
   * To: `claude-sonnet-4-20250514` or `claude-opus-4-20250514`
2. Existing API calls should continue to work without modification, although API behavior has changed slightly in Claude 4 models (see [API release notes](/en/release-notes/api) for details).

# [​](#what%E2%80%99s-new-in-claude-4) What’s new in Claude 4

# [​](#new-refusal-stop-reason) New refusal stop reason

Claude 4 models introduce a new `refusal` stop reason for content that the model declines to generate for safety reasons, due to the increased intelligence of Claude 4 models:

```
{"id":"msg_014XEDjypDjFzgKVWdFUXxZP",
"type":"message",
"role":"assistant",
"model":"claude-sonnet-4-20250514",
"content":[{"type":"text","text":"I would be happy to assist you. You can "}],
"stop_reason":"refusal",
"stop_sequence":null,
"usage":{"input_tokens":564,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":22}
}

```

When migrating to Claude 4, you should update your application to [handle `refusal` stop reasons](/en/docs/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals).

# [​](#summarized-thinking) Summarized thinking

With extended thinking enabled, the Messages API for Claude 4 models returns a summary of Claude’s full thinking process. Summarized thinking provides the full intelligence benefits of extended thinking, while preventing misuse.

While the API is consistent across Claude 3.7 and 4 models, streaming responses for extended thinking might return in a “chunky” delivery pattern, with possible delays between streaming events.

Summarization is processed by a different model than the one you target in your requests. The thinking model does not see the summarized output.

For more information, see the [Extended thinking documentation](/en/docs/build-with-claude/extended-thinking#summarized-thinking).

# [​](#interleaved-thinking) Interleaved thinking

Claude 4 models support interleaving tool use with extended thinking, allowing for more natural conversations where tool uses and responses can be mixed with regular messages.

Interleaved thinking is in beta. To enable interleaved thinking, add [the beta header](/en/api/beta-headers) `interleaved-thinking-2025-05-14` to your API request.

For more information, see the [Extended thinking documentation](/en/docs/build-with-claude/extended-thinking#interleaved-thinking).

# [​](#updated-text-editor-tool) Updated text editor tool

The text editor tool has been updated for Claude 4 models with the following changes:

* **Tool type**: `text_editor_20250429`
* **Tool name**: `str_replace_based_edit_tool`
* The `undo_edit` command is no longer supported in Claude 4 models.

The `str_replace_editor` text editor tool remains the same for Claude Sonnet 3.7.

If you’re migrating from Claude Sonnet 3.7 and using the text editor tool:

```
# Claude Sonnet 3.7

tools=[
    {
        "type": "text_editor_20250124",
        "name": "str_replace_editor"
    }
]

# Claude 4

tools=[
    {
        "type": "text_editor_20250429",
        "name": "str_replace_based_edit_tool"
    }
]

```

For more information, see the [Text editor tool documentation](/en/docs/agents-and-tools/tool-use/text-editor-tool).

# [​](#token-efficient-tool-use-no-longer-supported) Token-efficient tool use no longer supported

[Token-efficient tool use](/en/docs/agents-and-tools/tool-use/token-efficient-tool-use) is only available in Claude Sonnet 3.7.

If you’re migrating from Claude Sonnet 3.7 and using token-efficient tool use, we recommend removing the `token-efficient-tools-2025-02-19` [beta header](/en/api/beta-headers) from your requests.

The `token-efficient-tools-2025-02-19` beta header can still be included in Claude 4 requests, but it will have no effect.

# [​](#extended-output-no-longer-supported) Extended output no longer supported

The `output-128k-2025-02-19` [beta header](/en/api/beta-headers) for extended output is only available in Claude Sonnet 3.7.

If you’re migrating from Claude Sonnet 3.7, we recommend removing `output-128k-2025-02-19` from your requests.

The `output-128k-2025-02-19` beta header can still be included in Claude 4 requests, but it will have no effect.

# [​](#performance-considerations) Performance considerations

# [​](#claude-sonnet-4) Claude Sonnet 4

* Improved reasoning and intelligence capabilities compared to Claude Sonnet 3.7
* Enhanced tool use accuracy

# [​](#claude-opus-4) Claude Opus 4

* Most capable model with superior reasoning and intelligence
* Slower than Sonnet models
* Best for complex tasks requiring deep analysis

# [​](#migration-checklist) Migration checklist

* Update model id in your API calls
* Test existing requests (should work without changes)
* Remove `token-efficient-tools-2025-02-19` beta header if applicable
* Remove `output-128k-2025-02-19` beta header if applicable
* Handle new `refusal` stop reason
* Update text editor tool type and name if using it
* Remove any code that uses the `undo_edit` command
* Explore new tool interleaving capabilities with extended thinking
* Review [Claude 4 prompt engineering best practices](/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) for optimal results
* Test in development before production deployment

# [​](#need-help%3F) Need help?

* Check our [API documentation](/en/api/overview) for detailed specifications.
* Review [model capabilities](/en/docs/about-claude/models/overview) for performance comparisons.
* Review [API release notes](/en/release-notes/api) for API updates.
* Contact support if you encounter any issues during migration.

Was this page helpful?

YesNo

Choosing a model[Model deprecations](/en/docs/about-claude/model-deprecations)

On this page
