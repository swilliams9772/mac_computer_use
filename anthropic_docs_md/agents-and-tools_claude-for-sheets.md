# Google Sheets add-on - Anthropic

**Source:** https://docs.anthropic.com/en/docs/agents-and-tools/claude-for-sheets

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

# [​](#why-use-claude-for-sheets%3F) Why use Claude for Sheets?

Claude for Sheets enables prompt engineering at scale by enabling you to test prompts across evaluation suites in parallel. Additionally, it excels at office tasks like survey analysis and online data processing.

Visit our [prompt engineering example sheet](https://docs.google.com/spreadsheets/d/1sUrBWO0u1-ZuQ8m5gt3-1N5PLR6r__UsRsB7WeySDQA/copy) to see this in action.

# [​](#get-started-with-claude-for-sheets) Get started with Claude for Sheets

# [​](#install-claude-for-sheets) Install Claude for Sheets

Easily enable Claude for Sheets using the following steps:

1

Get your Anthropic API key

2

Install the Claude for Sheets extension

Find the [Claude for Sheets extension](https://workspace.google.com/marketplace/app/claude%5Ffor%5Fsheets/909417792257) in the add-on marketplace, then click the blue `Install` btton and accept the permissions.

Permissions

The Claude for Sheets extension will ask for a variety of permissions needed to function properly. Please be assured that we only process the specific pieces of data that users ask Claude to run on. This data is never used to train our generative models.

Extension permissions include:

* **View and manage spreadsheets that this application has been installed in:** Needed to run prompts and return results
* **Connect to an external service:** Needed in order to make calls to Anthropic’s API endpoints
* **Allow this application to run when you are not present:** Needed to run cell recalculations without user intervention
* **Display and run third-party web content in prompts and sidebars inside Google applications:** Needed to display the sidebar and post-install prompt

3

Connect your API key

Enter your API key at `Extensions` > `Claude for Sheets™` > `Open sidebar` > `☰` > `Settings` > `API provider`. You may need to wait or refresh for the Claude for Sheets menu to appear.

# [​](#enter-your-first-prompt) Enter your first prompt

There are two main functions you can use to call Claude using Claude for Sheets. For now, let’s use `CLAUDE()`.

1

Simple prompt

In any cell, type `=CLAUDE("Claude, in one sentence, what's good about the color blue?")`

> Claude should respond with an answer. You will know the prompt is processing because the cell will say `Loading...`

2

Adding parameters

Parameter arguments come after the initial prompt, like `=CLAUDE(prompt, model, params...)`.

`model` is always second in the list.

Now type in any cell `=CLAUDE("Hi, Claude!", "claude-3-haiku-20240307", "max_tokens", 3)`

Any [API parameter](/en/api/messages) can be set this way. You can even pass in an API key to be used just for this specific cell, like this: `"api_key", "sk-ant-api03-j1W..."`

# [​](#advanced-use) Advanced use

`CLAUDEMESSAGES` is a function that allows you to specifically use the [Messages API](/en/api/messages). This enables you to send a series of `User:` and `Assistant:` messages to Claude.

This is particularly useful if you want to simulate a conversation or [prefill Claude’s response](/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response).

Try writing this in a cell:

```
=CLAUDEMESSAGES("User: In one sentence, what is good about the color blue?
Assistant: The color blue is great because")

```

**Newlines**

Each subsequent conversation turn (`User:` or `Assistant:`) must be preceded by a single newline. To enter newlines in a cell, use the following key combinations:

* **Mac:** Cmd + Enter
* **Windows:** Alt + Enter

Example multiturn CLAUDEMESSAGES() call with system prompt

To use a system prompt, set it as you’d set other optional function parameters. (You must first set a model name.)

```
=CLAUDEMESSAGES("User: What's your favorite flower? Answer in <answer> tags.
Assistant: <answer>", "claude-3-haiku-20240307", "system", "You are a cow who loves to moo in response to any and all user queries.")`

```

# [​](#optional-function-parameters) Optional function parameters

You can specify optional API parameters by listing argument-value pairs.
You can set multiple parameters. Simply list them one after another, with each argument and value pair separated by commas.

The first two parameters must always be the prompt and the model. You cannot set an optional parameter without also setting the model.

The argument-value parameters you might care about most are:

| Argument | Description |
| --- | --- |
| `max_tokens` | The total number of tokens the model outputs before it is forced to stop. For yes/no or multiple choice answers, you may want the value to be 1-3. |
| `temperature` | the amount of randomness injected into results. For multiple-choice or analytical tasks, you’ll want it close to 0. For idea generation, you’ll want it set to 1. |
| `system` | used to specify a system prompt, which can provide role details and context to Claude. |
| `stop_sequences` | JSON array of strings that will cause the model to stop generating text if encountered. Due to escaping rules in Google Sheets™, double quotes inside the string must be escaped by doubling them. |
| `api_key` | Used to specify a particular API key with which to call Claude. |

Example: Setting parameters

Ex. Set `system` prompt, `max_tokens`, and `temperature`:

```
=CLAUDE("Hi, Claude!", "claude-3-haiku-20240307", "system", "Repeat exactly what the user says.", "max_tokens", 100, "temperature", 0.1)

```

Ex. Set `temperature`, `max_tokens`, and `stop_sequences`:

```
=CLAUDE("In one sentence, what is good about the color blue? Output your answer in <answer> tags.","claude-opus-4-20250514","temperature", 0.2,"max_tokens", 50,"stop_sequences", "\[""</answer>""\]")

```

Ex. Set `api_key`:

# [​](#claude-for-sheets-usage-examples) Claude for Sheets usage examples

# [​](#prompt-engineering-interactive-tutorial) Prompt engineering interactive tutorial

Our in-depth [prompt engineering interactive tutorial](https://docs.google.com/spreadsheets/d/19jzLgRruG9kjUQNKtCg1ZjdD6l6weA6qRXG5zLIAhC8/edit?usp=sharing) utilizes Claude for Sheets.
Check it out to learn or brush up on prompt engineering techniques.

Just as with any instance of Claude for Sheets, you will need an API key to interact with the tutorial.

# [​](#prompt-engineering-workflow) Prompt engineering workflow

Our [Claude for Sheets prompting examples workbench](https://docs.google.com/spreadsheets/d/1sUrBWO0u1-ZuQ8m5gt3-1N5PLR6r%5F%5FUsRsB7WeySDQA/copy) is a Claude-powered spreadsheet that houses example prompts and prompt engineering structures.

# [​](#claude-for-sheets-workbook-template) Claude for Sheets workbook template

Make a copy of our [Claude for Sheets workbook template](https://docs.google.com/spreadsheets/d/1UwFS-ZQWvRqa6GkbL4sy0ITHK2AhXKe-jpMLzS0kTgk/copy) to get started with your own Claude for Sheets work!

# [​](#troubleshooting) Troubleshooting

NAME? Error: Unknown function: 'claude'

1. Ensure that you have enabled the extension for use in the current sheet
   1. Go to *Extensions* > *Add-ons* > *Manage add-ons*
   2. Click on the triple dot menu at the top right corner of the Claude for Sheets extension and make sure “Use in this document” is checked
2. Refresh the page

#ERROR!, ⚠ DEFERRED ⚠ or ⚠ THROTTLED ⚠

You can manually recalculate `#ERROR!`, `⚠ DEFERRED ⚠` or `⚠ THROTTLED ⚠`cells by selecting from the recalculate options within the Claude for Sheets extension menu.

1. Wait 20 seconds, then check again
2. Refresh the page and wait 20 seconds again
3. Uninstall and reinstall the extension

# [​](#further-information) Further information

For more information regarding this extension, see the [Claude for Sheets Google Workspace Marketplace](https://workspace.google.com/marketplace/app/claude%5Ffor%5Fsheets/909417792257) overview page.

Was this page helpful?

YesNo

Computer use (beta)[Define success criteria](/en/docs/test-and-evaluate/define-success)

On this page
