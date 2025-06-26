# Handling stop reasons - Anthropic

**Source:** https://docs.anthropic.com/en/api/handling-stop-reasons

- [Documentation](/en/home)
- [Developer Console](https://console.anthropic.com/)
- [Developer Discord](https://www.anthropic.com/discord)
- [Support](https://support.anthropic.com/)

# SDKs

* [Client SDKs](/en/api/client-sdks)
* [OpenAI SDK compatibility (beta)](/en/api/openai-sdk)

# Examples

* [Messages examples](/en/api/messages-examples)
* [Message Batches examples](/en/api/messages-batch-examples)

When you make a request to the Messages API, Claude’s response includes a `stop_reason` field that indicates why the model stopped generating its response. Understanding these values is crucial for building robust applications that handle different response types appropriately.

For details about `stop_reason` in the API response, see the [Messages API reference](/en/api/messages).

# [​](#what-is-stop-reason%3F) What is stop\_reason?

The `stop_reason` field is part of every successful Messages API response. Unlike errors, which indicate failures in processing your request, `stop_reason` tells you why Claude successfully completed its response generation.

Example response

```
{
  "id": "msg_01234",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Here's the answer to your question..."
    }
  ],
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50
  }
}

```

# [​](#stop-reason-values) Stop reason values

# [​](#end-turn) end\_turn

The most common stop reason. Indicates Claude finished its response naturally.

```
if response.stop_reason == "end_turn":
    # Process the complete response
    print(response.content[0].text)

```

# [​](#max-tokens) max\_tokens

Claude stopped because it reached the `max_tokens` limit specified in your request.

```
# Request with limited tokens

response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=10,
    messages=[{"role": "user", "content": "Explain quantum physics"}]
)

if response.stop_reason == "max_tokens":
    # Response was truncated
    print("Response was cut off at token limit")
    # Consider making another request to continue

```

# [​](#stop-sequence) stop\_sequence

Claude encountered one of your custom stop sequences.

```
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    stop_sequences=["END", "STOP"],
    messages=[{"role": "user", "content": "Generate text until you say END"}]
)

if response.stop_reason == "stop_sequence":
    print(f"Stopped at sequence: {response.stop_sequence}")

```

# [​](#tool-use) tool\_use

Claude is calling a tool and expects you to execute it.

```
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    tools=[weather_tool],
    messages=[{"role": "user", "content": "What's the weather?"}]
)

if response.stop_reason == "tool_use":
    # Extract and execute the tool
    for content in response.content:
        if content.type == "tool_use":
            result = execute_tool(content.name, content.input)
            # Return result to Claude for final response

```

# [​](#pause-turn) pause\_turn

Used with server tools like web search when Claude needs to pause a long-running operation.

```
response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{"role": "user", "content": "Search for latest AI news"}]
)

if response.stop_reason == "pause_turn":
    # Continue the conversation
    messages = [
        {"role": "user", "content": original_query},
        {"role": "assistant", "content": response.content}
    ]
    continuation = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        messages=messages,
        tools=[{"type": "web_search_20250305", "name": "web_search"}]
    )

```

# [​](#best-practices-for-handling-stop-reasons) Best practices for handling stop reasons

# [​](#1-always-check-stop-reason) 1. Always check stop\_reason

Make it a habit to check the `stop_reason` in your response handling logic:

```
def handle_response(response):
    if response.stop_reason == "tool_use":
        return handle_tool_use(response)
    elif response.stop_reason == "max_tokens":
        return handle_truncation(response)
    elif response.stop_reason == "pause_turn":
        return handle_pause(response)
    else:
        # Handle end_turn and other cases
        return response.content[0].text

```

# [​](#2-handle-max-tokens-gracefully) 2. Handle max\_tokens gracefully

When a response is truncated due to token limits:

```
def handle_truncated_response(response):
    if response.stop_reason == "max_tokens":
        # Option 1: Warn the user
        return f"{response.content[0].text}\n\n[Response truncated due to length]"

        # Option 2: Continue generation
        messages = [
            {"role": "user", "content": original_prompt},
            {"role": "assistant", "content": response.content[0].text}
        ]
        continuation = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            messages=messages + [{"role": "user", "content": "Please continue"}]
        )
        return response.content[0].text + continuation.content[0].text

```

# [​](#3-implement-retry-logic-for-pause-turn) 3. Implement retry logic for pause\_turn

For server tools that may pause:

```
def handle_paused_conversation(initial_response, max_retries=3):
    response = initial_response
    messages = [{"role": "user", "content": original_query}]

    for attempt in range(max_retries):
        if response.stop_reason != "pause_turn":
            break

        messages.append({"role": "assistant", "content": response.content})
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            messages=messages,
            tools=original_tools
        )

    return response

```

# [​](#stop-reasons-vs-errors) Stop reasons vs. errors

It’s important to distinguish between `stop_reason` values and actual errors:

# [​](#stop-reasons-successful-responses) Stop reasons (successful responses)

* Part of the response body
* Indicate why generation stopped normally
* Response contains valid content

# [​](#errors-failed-requests) Errors (failed requests)

* HTTP status codes 4xx or 5xx
* Indicate request processing failures
* Response contains error details

```
try:
    response = client.messages.create(...)

    # Handle successful response with stop_reason
    if response.stop_reason == "max_tokens":
        print("Response was truncated")

except anthropic.APIError as e:
    # Handle actual errors
    if e.status_code == 429:
        print("Rate limit exceeded")
    elif e.status_code == 500:
        print("Server error")

```

# [​](#streaming-considerations) Streaming considerations

When using streaming, `stop_reason` is:

* `null` in the initial `message_start` event
* Provided in the `message_delta` event
* Non-null in all other events

```
with client.messages.stream(...) as stream:
    for event in stream:
        if event.type == "message_delta":
            stop_reason = event.delta.stop_reason
            if stop_reason:
                print(f"Stream ended with: {stop_reason}")

```

# [​](#common-patterns) Common patterns

# [​](#handling-tool-use-workflows) Handling tool use workflows

```
def complete_tool_workflow(client, user_query, tools):
    messages = [{"role": "user", "content": user_query}]

    while True:
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            messages=messages,
            tools=tools
        )

        if response.stop_reason == "tool_use":
            # Execute tools and continue
            tool_results = execute_tools(response.content)
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            # Final response
            return response

```

# [​](#ensuring-complete-responses) Ensuring complete responses

```
def get_complete_response(client, prompt, max_attempts=3):
    messages = [{"role": "user", "content": prompt}]
    full_response = ""

    for _ in range(max_attempts):
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            messages=messages,
            max_tokens=4096
        )

        full_response += response.content[0].text

        if response.stop_reason != "max_tokens":
            break

        # Continue from where it left off
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": full_response},
            {"role": "user", "content": "Please continue from where you left off."}
        ]

    return full_response

```

By properly handling `stop_reason` values, you can build more robust applications that gracefully handle different response scenarios and provide better user experiences.

Was this page helpful?

YesNo

Errors[Messages](/en/api/messages)

On this page
