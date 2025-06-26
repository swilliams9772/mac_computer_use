# API - Anthropic

**Source:** https://docs.anthropic.com/en/release-notes/api

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# [​](#may-22%2C-2025) May 22, 2025

* We’ve launched [Claude Opus 4 and Claude Sonnet 4](http://www.anthropic.com/news/claude-4), our latest models with extended thinking capabilities. Learn more in our [Models & Pricing documentation](/en/docs/about-claude/models).
* The default behavior of [extended thinking](/en/docs/build-with-claude/extended-thinking) in Claude 4 models returns a summary of Claude’s full thinking process, with the full thinking encrypted and returned in the `signature` field of `thinking` block output.
* We’ve launched [interleaved thinking](/en/docs/build-with-claude/extended-thinking#interleaved-thinking) in public beta, a feature that enables Claude to think in between tool calls. To enable interleaved thinking, use the [beta header](/en/api/beta-headers) `interleaved-thinking-2025-05-14`.
* We’ve launched the [Files API](/en/docs/build-with-claude/files) in public beta, enabling you to upload files and reference them in the Messages API and code execution tool.
* We’ve launched the [Code execution tool](/en/docs/agents-and-tools/tool-use/code-execution-tool) in public beta, a tool that enables Claude to execute Python code in a secure, sandboxed environment.
* We’ve launched the [MCP connector](/en/docs/agents-and-tools/mcp-connector) in public beta, a feature that allows you to connect to remote MCP servers directly from the Messages API.
* To increase answer quality and decrease tool errors, we’ve changed the default value for the `top_p` [nucleus sampling](https://en.wikipedia.org/wiki/Top-p_sampling) parameter in the Messages API from 0.999 to 0.99 for all models. To revert this change, set `top_p` to 0.999.
  Additionally, when extended thinking is enabled, you can now set `top_p` to values between 0.95 and 1.
* We’ve moved our [Go SDK](https://github.com/anthropics/anthropic-sdk-go) from beta to GA.

# [​](#may-21%2C-2025) May 21, 2025

* We’ve moved our [Ruby SDK](https://github.com/anthropics/anthropic-sdk-ruby) from beta to GA.

# [​](#may-7%2C-2025) May 7, 2025

* We’ve launched a web search tool in the API, allowing Claude to access up-to-date information from the web. Learn more in our [web search tool documentation](/en/docs/build-with-claude/tool-use/web-search-tool).

# [​](#may-1%2C-2025) May 1, 2025

* Cache control must now be specified directly in the parent `content` block of `tool_result` and `document.source`. For backwards compatibility, if cache control is detected on the last block in `tool_result.content` or `document.source.content`, it will be automatically applied to the parent block instead. Cache control on any other blocks within `tool_result.content` and `document.source.content` will result in a validation error.

# [​](#april-9th%2C-2025) April 9th, 2025

* We launched a beta version of the [Ruby SDK](https://github.com/anthropics/anthropic-sdk-ruby)

# [​](#march-31st%2C-2025) March 31st, 2025

* We’ve moved our [Java SDK](https://github.com/anthropics/anthropic-sdk-java) from beta to GA.
* We’ve moved our [Go SDK](https://github.com/anthropics/anthropic-sdk-go) from alpha to beta.

# [​](#february-27th%2C-2025) February 27th, 2025

* We’ve added URL source blocks for images and PDFs in the Messages API. You can now reference images and PDFs directly via URL instead of having to base64-encode them. Learn more in our [vision documentation](/en/docs/vision) and [PDF support documentation](/en/docs/build-with-claude/pdf-support).
* We’ve added support for a `none` option to the `tool_choice` parameter in the Messages API that prevents Claude from calling any tools. Additionally, you’re no longer required to provide any `tools` when including `tool_use` and `tool_result` blocks.
* We’ve launched an OpenAI-compatible API endpoint, allowing you to test Claude models by changing just your API key, base URL, and model name in existing OpenAI integrations. This compatibility layer supports core chat completions functionality. Learn more in our [OpenAI SDK compatibility documentation](/en/api/openai-sdk).

# [​](#february-24th%2C-2025) February 24th, 2025

* We’ve launched [Claude Sonnet 3.7](http://www.anthropic.com/news/claude-3-7-sonnet), our most intelligent model yet. Claude Sonnet 3.7 can produce near-instant responses or show its extended thinking step-by-step. One model, two ways to think. Learn more about all Claude models in our [Models & Pricing documentation](/en/docs/about-claude/models).
* We’ve added vision support to Claude Haiku 3.5, enabling the model to analyze and understand images.
* We’ve released a token-efficient tool use implementation, improving overall performance when using tools with Claude. Learn more in our [tool use documentation](/en/docs/build-with-claude/tool-use).
* We’ve changed the default temperature in the [Console](https://console.anthropic.com/workbench) for new prompts from 0 to 1 for consistency with the default temperature in the API. Existing saved prompts are unchanged.
* We’ve released updated versions of our tools that decouple the text edit and bash tools from the computer use system prompt:
  + `bash_20250124`: Same functionality as previous version but is independent from computer use. Does not require a beta header.
  + `text_editor_20250124`: Same functionality as previous version but is independent from computer use. Does not require a beta header.
  + `computer_20250124`: Updated computer use tool with new command options including “hold\_key”, “left\_mouse\_down”, “left\_mouse\_up”, “scroll”, “triple\_click”, and “wait”. This tool requires the “computer-use-2025-01-24” anthropic-beta header.
    Learn more in our [tool use documentation](/en/docs/build-with-claude/tool-use).

# [​](#february-10th%2C-2025) February 10th, 2025

* We’ve added the `anthropic-organization-id` response header to all API responses. This header provides the organization ID associated with the API key used in the request.

# [​](#january-31st%2C-2025) January 31st, 2025

* We’ve moved our [Java SDK](https://github.com/anthropics/anthropic-sdk-java) from alpha to beta.

# [​](#january-23rd%2C-2025) January 23rd, 2025

* We’ve launched citations capability in the API, allowing Claude to provide source attribution for information. Learn more in our [citations documentation](/en/docs/build-with-claude/citations).
* We’ve added support for plain text documents and custom content documents in the Messages API.

# [​](#january-21st%2C-2025) January 21st, 2025

* We announced the deprecation of the Claude 2, Claude 2.1, and Claude Sonnet 3 models. Read more in [our documentation](/en/docs/resources/model-deprecations).

# [​](#january-15th%2C-2025) January 15th, 2025

* We’ve updated [prompt caching](/en/docs/build-with-claude/prompt-caching) to be easier to use. Now, when you set a cache breakpoint, we’ll automatically read from your longest previously cached prefix.
* You can now puts words in Claude’s mouth when using tools.

# [​](#january-10th%2C-2025) January 10th, 2025

# [​](#december-19th%2C-2024) December 19th, 2024

# [​](#december-17th%2C-2024) December 17th, 2024

The following features are now generally available in the Anthropic API:

* [Models API](/en/api/models-list): Query available models, validate model IDs, and resolve [model aliases](/en/docs/about-claude/models#model-names) to their canonical model IDs.
* [Message Batches API](/en/docs/build-with-claude/batch-processing): Process large batches of messages asynchronously at 50% of the standard API cost.
* [Token counting API](/en/docs/build-with-claude/token-counting): Calculate token counts for Messages before sending them to Claude.
* [Prompt Caching](/en/docs/build-with-claude/prompt-caching): Reduce costs by up to 90% and latency by up to 80% by caching and reusing prompt content.
* [PDF support](/en/docs/build-with-claude/pdf-support): Process PDFs to analyze both text and visual content within documents.

We also released new official SDKs:

* [Java SDK](https://github.com/anthropics/anthropic-sdk-java) (alpha)
* [Go SDK](https://github.com/anthropics/anthropic-sdk-go) (alpha)

# [​](#december-4th%2C-2024) December 4th, 2024

* We’ve added the ability to group by API key to the [Usage](https://console.anthropic.com/settings/usage) and [Cost](https://console.anthropic.com/settings/cost) pages of the [Developer Console](https://console.anthropic.com)
* We’ve added two new **Last used at** and **Cost** columns and the ability to sort by any column in the [API keys](https://console.anthropic.com/settings/keys) page of the [Developer Console](https://console.anthropic.com)

# [​](#november-21st%2C-2024) November 21st, 2024

* We’ve released the [Admin API](/en/docs/administration/administration-api), allowing users to programmatically manage their organization’s resources.

# [​](#november-20th%2C-2024) November 20th, 2024

* We’ve updated our rate limits for the Messages API. We’ve replaced the tokens per minute rate limit with new input and output tokens per minute rate limits. Read more in our [documentation](/en/api/rate-limits).
* We’ve added support for [tool use](/en/docs/build-with-claude/tool-use) in the [Workbench](https://console.anthropic.com/workbench).

# [​](#november-13th%2C-2024) November 13th, 2024

* We’ve added PDF support for all Claude Sonnet 3.5 models. Read more in our [documentation](/en/docs/build-with-claude/pdf-support).

# [​](#november-6th%2C-2024) November 6th, 2024

* We’ve retired the Claude 1 and Instant models. Read more in [our documentation](/en/docs/resources/model-deprecations).

# [​](#november-4th%2C-2024) November 4th, 2024

# [​](#november-1st%2C-2024) November 1st, 2024

* We’ve added PDF support for use with the new Claude Sonnet 3.5. Read more in our [documentation](/en/docs/build-with-claude/pdf-support).
* We’ve also added token counting, which allows you to determine the total number of tokens in a Message, prior to sending it to Claude. Read more in our [documentation](/en/docs/build-with-claude/token-counting).

# [​](#october-22nd%2C-2024) October 22nd, 2024

* We’ve added Anthropic-defined computer use tools to our API for use with the new Claude Sonnet 3.5. Read more in our [documentation](/en/docs/build-with-claude/computer-use).
* Claude Sonnet 3.5, our most intelligent model yet, just got an upgrade and is now available on the Anthropic API. Read more [here](https://www.anthropic.com/claude/sonnet).

# [​](#october-8th%2C-2024) October 8th, 2024

* The Message Batches API is now available in beta. Process large batches of queries asynchronously in the Anthropic API for 50% less cost. Read more in our [documentation](/en/docs/build-with-claude/batch-processing).
* We’ve loosened restrictions on the ordering of `user`/`assistant` turns in our Messages API. Consecutive `user`/`assistant` messages will be combined into a single message instead of erroring, and we no longer require the first input message to be a `user` message.
* We’ve deprecated the Build and Scale plans in favor of a standard feature suite (formerly referred to as Build), along with additional features that are available through sales. Read more [here](https://www.anthropic.com/api).

# [​](#october-3rd%2C-2024) October 3rd, 2024

* We’ve added the ability to disable parallel tool use in the API. Set `disable_parallel_tool_use: true` in the `tool_choice` field to ensure that Claude uses at most one tool. Read more in our [documentation](/en/docs/build-with-claude/tool-use#disabling-parallel-tool-use).

# [​](#september-10th%2C-2024) September 10th, 2024

* We’ve added Workspaces to the [Developer Console](https://console.anthropic.com). Workspaces allow you to set custom spend or rate limits, group API keys, track usage by project, and control access with user roles. Read more in our [blog post](https://www.anthropic.com/news/workspaces).

# [​](#september-4th%2C-2024) September 4th, 2024

* We announced the deprecation of the Claude 1 models. Read more in [our documentation](/en/docs/resources/model-deprecations).

# [​](#august-22nd%2C-2024) August 22nd, 2024

* We’ve added support for usage of the SDK in browsers by returning CORS headers in the API responses. Set `dangerouslyAllowBrowser: true` in the SDK instantiation to enable this feature.

# [​](#august-19th%2C-2024) August 19th, 2024

* We’ve moved 8,192 token outputs from beta to general availability for Claude Sonnet 3.5.

# [​](#august-14th%2C-2024) August 14th, 2024

* [Prompt caching](/en/docs/build-with-claude/prompt-caching) is now available as a beta feature in the Anthropic API. Cache and re-use prompts to reduce latency by up to 80% and costs by up to 90%.

# [​](#july-15th%2C-2024) July 15th, 2024

* Generate outputs up to 8,192 tokens in length from Claude Sonnet 3.5 with the new `anthropic-beta: max-tokens-3-5-sonnet-2024-07-15` header. More details [here](https://x.com/alexalbert__/status/1812921642143900036).

# [​](#july-9th%2C-2024) July 9th, 2024

* Automatically generate test cases for your prompts using Claude in the [Developer Console](https://console.anthropic.com). Read more in our [blog post](https://www.anthropic.com/news/test-case-generation).
* Compare the outputs from different prompts side by side in the new output comparison mode in the [Developer Console](https://console.anthropic.com).

# [​](#june-27th%2C-2024) June 27th, 2024

* View API usage and billing broken down by dollar amount, token count, and API keys in the new [Usage](https://console.anthropic.com/settings/usage) and [Cost](https://console.anthropic.com/settings/cost) tabs in the [Developer Console](https://console.anthropic.com).
* View your current API rate limits in the new [Rate Limits](https://console.anthropic.com/settings/limits) tab in the [Developer Console](https://console.anthropic.com).

# [​](#june-20th%2C-2024) June 20th, 2024

* [Claude Sonnet 3.5](http://anthropic.com/news/claude-3-5-sonnet), our most intelligent model yet, is now generally available across the Anthropic API, Amazon Bedrock, and Google Vertex AI.

# [​](#may-30th%2C-2024) May 30th, 2024

# [​](#may-10th%2C-2024) May 10th, 2024

* Our prompt generator tool is now available in the [Developer Console](https://console.anthropic.com). Prompt Generator makes it easy to guide Claude to generate a high-quality prompts tailored to your specific tasks. Read more in our [blog post](https://www.anthropic.com/news/prompt-generator).

Was this page helpful?

YesNo

Overview[Claude Apps](/en/release-notes/claude-apps)

On this page
