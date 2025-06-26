# Files API - Anthropic

**Source:** https://docs.anthropic.com/en/docs/build-with-claude/files

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

The Files API lets you upload and manage files to use with the Anthropic API without re-uploading content with each request. This is particularly useful when using the [code execution tool](/en/docs/agents-and-tools/tool-use/code-execution-tool) to provide inputs (e.g. datasets and documents) and then download outputs (e.g. charts). You can also use the Files API to prevent having to continually re-upload frequently used documents and images across multiple API calls.

The Files API is currently in beta. Please reach out through our [feedback form](https://forms.gle/tisHyierGwgN4DUE9) to share your experience with the Files API.

# [​](#supported-models) Supported models

Referencing a `file_id` in a Messages request is supported in all models that support the given file type. For example, [images](/en/docs/build-with-claude/vision) are supported in all Claude 3+ models, [PDFs](/en/docs/build-with-claude/pdf-support) in all Claude 3.5+ models, and [various other file types](/en/docs/agents-and-tools/tool-use/code-execution-tool#supported-file-types) for the code execution tool in Claude 3.5 Haiku plus all Claude 3.7+ models.

The Files API is currently not supported on Amazon Bedrock or Google Vertex AI.

# [​](#how-the-files-api-works) How the Files API works

The Files API provides a simple create-once, use-many-times approach for working with files:

* **Upload files** to our secure storage and receive a unique `file_id`
* **Download files** that are created from the code execution tool
* **Reference files** in [Messages](/en/api/messages) requests using the `file_id` instead of re-uploading content
* **Manage your files** with list, retrieve, and delete operations

# [​](#how-to-use-the-files-api) How to use the Files API

To use the Files API, you’ll need to include the beta feature header: `anthropic-beta: files-api-2025-04-14`.

# [​](#uploading-a-file) Uploading a file

Upload a file to be referenced in future API calls:

Shell

Python

TypeScript

```
curl -X POST https://api.anthropic.com/v1/files \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14" \
  -F "file=@/path/to/document.pdf"

```

# [​](#using-a-file-in-messages) Using a file in messages

Once uploaded, reference the file using its `file_id`:

Shell

Python

TypeScript

```
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "Please summarize this document for me."
          },
          {
            "type": "document",
            "source": {
              "type": "file",
              "file_id": "file_011CNha8iCJcU1wXNR6q4V8w"
            }
          }
        ]
      }
    ]
  }'

```

# [​](#file-types-and-content-blocks) File types and content blocks

The Files API supports different file types that correspond to different content block types:

| File Type | MIME Type | Content Block Type | Use Case |
| --- | --- | --- | --- |
| PDF | `application/pdf` | `document` | Text analysis, document processing |
| Plain text | `text/plain` | `document` | Text analysis, processing |
| Images | `image/jpeg`, `image/png`, `image/gif`, `image/webp` | `image` | Image analysis, visual tasks |
| [Datasets, others](/en/docs/agents-and-tools/tool-use/code-execution-tool#supported-file-types) | Varies | `container_upload` | Analyze data, create visualizations |

# [​](#document-blocks) Document blocks

For PDFs and text files, use the `document` content block:

```
{
  "type": "document",
  "source": {
    "type": "file",
    "file_id": "file_011CNha8iCJcU1wXNR6q4V8w"
  },
  "title": "Document Title", // Optional
  "context": "Context about the document", // Optional
  "citations": {"enabled": true} // Optional, enables citations
}

```

# [​](#image-blocks) Image blocks

For images, use the `image` content block:

```
{
  "type": "image",
  "source": {
    "type": "file",
    "file_id": "file_xyz789"
  }
}

```

# [​](#managing-files) Managing files

# [​](#list-files) List files

Retrieve a list of your uploaded files:

Shell

Python

TypeScript

```
curl https://api.anthropic.com/v1/files \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14"

```

# [​](#get-file-metadata) Get file metadata

Retrieve information about a specific file:

Shell

Python

TypeScript

```
curl https://api.anthropic.com/v1/files/file_011CNha8iCJcU1wXNR6q4V8w \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14"

```

# [​](#delete-a-file) Delete a file

Remove a file from your workspace:

Shell

Python

TypeScript

```
curl -X DELETE https://api.anthropic.com/v1/files/file_011CNha8iCJcU1wXNR6q4V8w \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14"

```

# [​](#downloading-a-file) Downloading a file

Download files that have been created by the code execution tool:

Shell

Python

TypeScript

```
curl -X GET "https://api.anthropic.com/v1/files/file_011CNha8iCJcU1wXNR6q4V8w/content" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14" \
  --output downloaded_file.txt

```

You can only download files that were created by the [code execution tool](/en/docs/agents-and-tools/tool-use/code-execution-tool). Files that you uploaded cannot be downloaded.

# [​](#file-storage-and-limits) File storage and limits

# [​](#storage-limits) Storage limits

* **Maximum file size:** 32 MB per file
* **Total storage:** 100 GB per organization

# [​](#file-lifecycle) File lifecycle

* Files are scoped to the workspace of the API key. Other API keys can use files created by any other API key associated with the same workspace
* Files persist until you delete them
* Deleted files cannot be recovered
* Files are inaccessible via the API shortly after deletion, but they may persist in active `Messages` API calls and associated tool uses

# [​](#error-handling) Error handling

Common errors when using the Files API include:

* **File not found (404):** The specified `file_id` doesn’t exist or you don’t have access to it
* **Invalid file type (400):** The file type doesn’t match the content block type (e.g., using an image file in a document block)
* **File too large (413):** File exceeds the 500 MB limit
* **Storage limit exceeded (403):** Your organization has reached the 100 GB storage limit
* **Invalid filename (400):** Filename doesn’t meet the length requirements (1-255 characters) or contains forbidden characters (`<`, `>`, `:`, `"`, `|`, `?`, `*`, `\`, `/`, or unicode characters 0-31)

```
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "File not found: file_011CNha8iCJcU1wXNR6q4V8w"
  }
}

```

# [​](#usage-and-billing) Usage and billing

File API operations are **free**:

* Uploading files
* Downloading files
* Listing files
* Getting file metadata
* Deleting files

File content used in `Messages` requests are priced as input tokens. You can only download files created by the code execution tool.

# [​](#rate-limits) Rate limits

During the beta period:

* File-related API calls are limited to approximately 100 requests per minute
* [Contact us](mailto:sales@anthropic.com) if you need higher limits for your use case

Was this page helpful?

YesNo

PDF support[Overview](/en/docs/agents-and-tools/tool-use/overview)

On this page
