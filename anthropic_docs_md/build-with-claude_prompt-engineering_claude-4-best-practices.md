# Claude 4 prompt engineering best practices - Anthropic

**Source:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices

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

  + [Overview](/en/docs/build-with-claude/prompt-engineering/overview)
  + [Claude 4 best practices](/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices)
  + [Prompt generator](/en/docs/build-with-claude/prompt-engineering/prompt-generator)
  + [Use prompt templates](/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables)
  + [Prompt improver](/en/docs/build-with-claude/prompt-engineering/prompt-improver)
  + [Be clear and direct](/en/docs/build-with-claude/prompt-engineering/be-clear-and-direct)
  + [Use examples (multishot prompting)](/en/docs/build-with-claude/prompt-engineering/multishot-prompting)
  + [Let Claude think (CoT)](/en/docs/build-with-claude/prompt-engineering/chain-of-thought)
  + [Use XML tags](/en/docs/build-with-claude/prompt-engineering/use-xml-tags)
  + [Give Claude a role (system prompts)](/en/docs/build-with-claude/prompt-engineering/system-prompts)
  + [Prefill Claude's response](/en/docs/build-with-claude/prompt-engineering/prefill-claudes-response)
  + [Chain complex prompts](/en/docs/build-with-claude/prompt-engineering/chain-prompts)
  + [Long context tips](/en/docs/build-with-claude/prompt-engineering/long-context-tips)
  + [Extended thinking tips](/en/docs/build-with-claude/prompt-engineering/extended-thinking-tips)

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

This guide provides specific prompt engineering techniques for Claude 4 models (Opus 4 and Sonnet 4) to help you achieve optimal results in your applications. These models have been trained for more precise instruction following than previous generations of Claude models.

# [​](#general-principles) General principles

# [​](#be-explicit-with-your-instructions) Be explicit with your instructions

Claude 4 models respond well to clear, explicit instructions. Being specific about your desired output can help enhance results. Customers who desire the “above and beyond” behavior from previous Claude models might need to more explicitly request these behaviors with Claude 4.

Example: Creating an analytics dashboard

**Less effective:**

```
Create an analytics dashboard

```

**More effective:**

```
Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation.

```

# [​](#add-context-to-improve-performance) Add context to improve performance

Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude 4 better understand your goals and deliver more targeted responses.

Example: Formatting preferences

**Less effective:**

```
NEVER use ellipses

```

**More effective:**

```
Your response will be read aloud by a text-to-speech engine, so never use ellipses since the text-to-speech engine will not know how to pronounce them.

```

Claude is smart enough to generalize from the explanation.

# [​](#be-vigilant-with-examples-%26-details) Be vigilant with examples & details

Claude 4 models pay attention to details and examples as part of instruction following. Ensure that your examples align with the behaviors you want to encourage and minimize behaviors you want to avoid.

# [​](#guidance-for-specific-situations) Guidance for specific situations

# [​](#control-the-format-of-responses) Control the format of responses

There are a few ways that we have found to be particularly effective in seering output formatting in Claude 4 models:

1. **Tell Claude what to do instead of what not to do**
  * Instead of: “Do not use markdown in your response”
   * Try: “Your response should be composed of smoothly flowing prose paragraphs.”
2. **Use XML format indicators**
  * Try: “Write the prose sections of your response in <smoothly\_flowing\_prose\_paragraphs> tags.”
3. **Match your prompt style to the desired output**

   The formatting style used in your prompt may influence Claude’s response style. If you are still experiencing steerability issues with output formatting, we recommend as best as you can matching your prompt style to your desired output style. For exmaple, removing markdown from your prompt can reduce the volume of markdown in the output.

# [​](#leverage-thinking-%26-interleaved-thinking-capabilities) Leverage thinking & interleaved thinking capabilities

Claude 4 offers thinking capabilities that can be especially helpful for tasks involving reflection after tool use or complex multi-step reasoning. You can guide its initial or interleaved thinking for better results.

Example prompt

```
After receiving tool results, carefully reflect on their quality and determine optimal next steps before proceeding. Use your thinking to plan and iterate based on this new information, and then take the best next action.

```

For more information on thinking capabilities, see [Extended thinking](/en/docs/build-with-claude/extended-thinking).

# [​](#optimize-parallel-tool-calling) Optimize parallel tool calling

Claude 4 models excel at parallel tool execution. They have a high success rate in using parallel tool calling without any prompting to do so, but some minor prompting can boost this behavior to ~100% parallel tool use success rate. We have found this prompt to be most effective:

Sample prompt for agents

```
For maximum efficiency, whenever you need to perform multiple independent operations, invoke all relevant tools simultaneously rather than sequentially.

```

# [​](#reduce-file-creation-in-agentic-coding) Reduce file creation in agentic coding

Claude 4 models may sometimes create new files for testing and iteration purposes, particularly when working with code. This approach allows Claude to use files, especially python scripts, as a ‘temporary scratchpad’ before saving its final output. Using temporary files can improve outcomes particularly for agentic coding use cases.

If you’d prefer to minimize net new file creation, you can instruct Claude to clean up after itself:

Sample prompt

```
If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task.

```

# [​](#enhance-visual-and-frontend-code-generation) Enhance visual and frontend code generation

For frontend code generation, you can steer Claude 4 models to create complex, detailed, and interactive designs by providing explicit encouragement:

Sample prompt

```
Don't hold back. Give it your all.

```

You can also improve Claude’s frontend performance in specific areas by providing additional modifiers and details on what to focus on:

* “Include as many relevant features and interactions as possible”
* “Add thoughtful details like hover states, transitions, and micro-interactions”
* “Create an impressive demonstration showcasing web development capabilities”
* “Apply design principles: hierarchy, contrast, balance, and movement”

# [​](#migration-considerations) Migration considerations

When migrating from Sonnet 3.7 to Claude 4:

1. **Be specific about desired behavior**: Consider describing exactly what you’d like to see in the output.
2. **Frame your instructions with modifiers**: Adding modifiers that encourage Claude to increase the quality and detail of its output can help better shape Claude’s performance. For example, instead of “Create an analytics dashboard”, use “Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation.”
3. **Request specific features explicitly**: Animations and interactive elements should be requested explicitly when desired.

Was this page helpful?

YesNo

Overview[Prompt generator](/en/docs/build-with-claude/prompt-engineering/prompt-generator)

On this page
