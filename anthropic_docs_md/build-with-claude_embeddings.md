# Embeddings - Anthropic

**Source:** https://docs.anthropic.com/en/docs/build-with-claude/embeddings#voyage-python-package

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

# [​](#before-implementing-embeddings) Before implementing embeddings

When selecting an embeddings provider, there are several factors you can consider depending on your needs and preferences:

* Dataset size & domain specificity: size of the model training dataset and its relevance to the domain you want to embed. Larger or more domain-specific data generally produces better in-domain embeddings
* Inference performance: embedding lookup speed and end-to-end latency. This is a particularly important consideration for large scale production deployments
* Customization: options for continued training on private data, or specialization of models for very specific domains. This can improve performance on unique vocabularies

# [​](#how-to-get-embeddings-with-anthropic) How to get embeddings with Anthropic

Anthropic does not offer its own embedding model. One embeddings provider that has a wide variety of options and capabilities encompassing all of the above considerations is Voyage AI.

Voyage AI makes state-of-the-art embedding models and offers customized models for specific industry domains such as finance and healthcare, or bespoke fine-tuned models for individual customers.

The rest of this guide is for Voyage AI, but we encourage you to assess a variety of embeddings vendors to find the best fit for your specific use case.

# [​](#available-models) Available Models

Voyage recommends using the following text embedding models:

| Model | Context Length | Embedding Dimension | Description |
| --- | --- | --- | --- |
| `voyage-3-large` | 32,000 | 1024 (default), 256, 512, 2048 | The best general-purpose and multilingual retrieval quality. |
| `voyage-3` | 32,000 | 1024 | Optimized for general-purpose and multilingual retrieval quality. See [blog post](https://blog.voyageai.com/2024/09/18/voyage-3/) for details. |
| `voyage-3-lite` | 32,000 | 512 | Optimized for latency and cost. See [blog post](https://blog.voyageai.com/2024/09/18/voyage-3/) for details. |
| `voyage-code-3` | 32,000 | 1024 (default), 256, 512, 2048 | Optimized for **code** retrieval. See [blog post](https://blog.voyageai.com/2024/12/04/voyage-code-3/) for details. |
| `voyage-finance-2` | 32,000 | 1024 | Optimized for **finance** retrieval and RAG. See [blog post](https://blog.voyageai.com/2024/06/03/domain-specific-embeddings-finance-edition-voyage-finance-2/) for details. |
| `voyage-law-2` | 16,000 | 1024 | Optimized for **legal** and **long-context** retrieval and RAG. Also improved performance across all domains. See [blog post](https://blog.voyageai.com/2024/04/15/domain-specific-embeddings-and-retrieval-legal-edition-voyage-law-2/) for details. |

Additionally, the following multimodal embedding models are recommended:

| Model | Context Length | Embedding Dimension | Description |
| --- | --- | --- | --- |
| `voyage-multimodal-3` | 32000 | 1024 | Rich multimodal embedding model that can vectorize interleaved text and content-rich images, such as screenshots of PDFs, slides, tables, figures, and more. See [blog post](https://blog.voyageai.com/2024/11/12/voyage-multimodal-3/) for details. |

Need help deciding which text embedding model to use? Check out the [FAQ](https://docs.voyageai.com/docs/faq#what-embedding-models-are-available-and-which-one-should-i-use&ref=anthropic).

# [​](#getting-started-with-voyage-ai) Getting started with Voyage AI

To access Voyage embeddings:

1. Sign up on Voyage AI’s website
2. Obtain an API key
3. Set the API key as an environment variable for convenience:

You can obtain the embeddings by either using the official [`voyageai` Python package](https://github.com/voyage-ai/voyageai-python) or HTTP requests, as described below.

# [​](#voyage-python-package) Voyage Python Package

The `voyageai` package can be installed using the following command:

```
pip install -U voyageai

```

Then, you can create a client object and start using it to embed your texts:

```
import voyageai

vo = voyageai.Client()
# This will automatically use the environment variable VOYAGE_API_KEY.

# Alternatively, you can use vo = voyageai.Client(api_key="<your secret key>")

texts = ["Sample text 1", "Sample text 2"]

result = vo.embed(texts, model="voyage-3", input_type="document")
print(result.embeddings[0])
print(result.embeddings[1])

```

`result.embeddings` will be a list of two embedding vectors, each containing 1024 floating-point numbers. After running the above code, the two embeddings will be printed on the screen:

```
[0.02012746, 0.01957859, ...]  # embedding for "Sample text 1"
[0.01429677, 0.03077182, ...]  # embedding for "Sample text 2"

```

When creating the embeddings, you may also specify a few other arguments to the `embed()` function. [You can read more about the specification here](https://docs.voyageai.com/docs/embeddings#python-api)

# [​](#voyage-http-api) Voyage HTTP API

You can also get embeddings by requesting Voyage HTTP API. For example, you can send an HTTP request through the `curl` command in a terminal:

```
curl https://api.voyageai.com/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $VOYAGE_API_KEY" \
  -d '{
    "input": ["Sample text 1", "Sample text 2"],
    "model": "voyage-3"
  }'

```

The response you would get is a JSON object containing the embeddings and the token usage:

```
{
  "object": "list",
  "data": [
    {
      "embedding": [0.02012746, 0.01957859, ...],
      "index": 0
    },
    {
      "embedding": [0.01429677, 0.03077182, ...],
      "index": 1
    }
  ],
  "model": "voyage-3",
  "usage": {
    "total_tokens": 10
  }
}

```

You can read more about the embedding endpoint in the [Voyage documentation](https://docs.voyageai.com/reference/embeddings-api)

# [​](#aws-marketplace) AWS Marketplace

Voyage embeddings are also available on [AWS Marketplace](https://aws.amazon.com/marketplace/seller-profile?id=seller-snt4gb6fd7ljg). Instructions for accessing Voyage on AWS are available [here](https://docs.voyageai.com/docs/aws-marketplace-model-package?ref=anthropic).

# [​](#quickstart-example) Quickstart Example

Now that we know how to get embeddings, let’s see a brief example.

Suppose we have a small corpus of six documents to retrieve from

```
documents = [
    "The Mediterranean diet emphasizes fish, olive oil, and vegetables, believed to reduce chronic diseases.",
    "Photosynthesis in plants converts light energy into glucose and produces essential oxygen.",
    "20th-century innovations, from radios to smartphones, centered on electronic advancements.",
    "Rivers provide water, irrigation, and habitat for aquatic species, vital for ecosystems.",
    "Apple’s conference call to discuss fourth fiscal quarter results and business updates is scheduled for Thursday, November 2, 2023 at 2:00 p.m. PT / 5:00 p.m. ET.",
    "Shakespeare's works, like 'Hamlet' and 'A Midsummer Night's Dream,' endure in literature."
]

```

We will first use Voyage to convert each of them into an embedding vector

```
import voyageai

vo = voyageai.Client()

# Embed the documents

doc_embds = vo.embed(
    documents, model="voyage-3", input_type="document"
).embeddings

```

The embeddings will allow us to do semantic search / retrieval in the vector space. Given an example query,

```
query = "When is Apple's conference call scheduled?"

```

we convert it into an embedding, and conduct a nearest neighbor search to find the most relevant document based on the distance in the embedding space.

```
import numpy as np

# Embed the query

query_embd = vo.embed(
    [query], model="voyage-3", input_type="query"
).embeddings[0]

# Compute the similarity

# Voyage embeddings are normalized to length 1, therefore dot-product
# and cosine similarity are the same.

similarities = np.dot(doc_embds, query_embd)

retrieved_id = np.argmax(similarities)
print(documents[retrieved_id])

```

Note that we use `input_type="document"` and `input_type="query"` for embedding the document and query, respectively. More specification can be found [here](https://docs.anthropic.com/en/docs/build-with-claude/embeddings#voyage-python-package).

The output would be the 5th document, which is indeed the most relevant to the query:

```
Apple's conference call to discuss fourth fiscal quarter results and business updates is scheduled for Thursday, November 2, 2023 at 2:00 p.m. PT / 5:00 p.m. ET.

```

If you are looking for a detailed set of cookbooks on how to do RAG with embeddings, including vector databases, check out our [RAG cookbook](https://github.com/anthropics/anthropic-cookbook/blob/main/third_party/Pinecone/rag_using_pinecone.ipynb).

# [​](#faq) FAQ

Why do Voyage embeddings have superior quality?

Embedding models rely on powerful neural networks to capture and compress semantic context, similar to generative models. Voyage’s team of experienced AI researchers optimizes every component of the embedding process, including:

* Model architecture
* Data collection
* Loss functions
* Optimizer selection

Learn more about Voyage’s technical approach on their [blog](https://blog.voyageai.com/).

What embedding models are available and which should I use?

For general-purpose embedding, we recommend:

* `voyage-3-large`: Best quality
* `voyage-3-lite`: Lowest latency and cost
* `voyage-3`: Balanced performance with superior retrieval quality at a competitive price point

For retrieval tasks, use the `input_type` parameter to specify query or document type.

**Domain-specific models:**

* Legal tasks: `voyage-law-2`
* Code and programming documentation: `voyage-code-3`
* Finance-related tasks: `voyage-finance-2`

Which similarity function should I use?

Voyage embeddings support:

* Dot-product similarity
* Cosine similarity
* Euclidean distance

Since Voyage AI embeddings are normalized to length 1:

* Cosine similarity equals dot-product similarity (dot-product computation is faster)
* Cosine similarity and Euclidean distance produce identical rankings

Learn more about embedding similarity in [Pinecone’s guide](https://www.pinecone.io/learn/vector-similarity/).

How should I use the input\_type parameter?

For retrieval tasks including RAG, always specify `input_type` as either “query” or “document”. This optimization improves retrieval quality through specialized prompt prefixing:

For queries:

```
Represent the query for retrieving supporting documents: [your query]

```

For documents:

```
Represent the document for retrieval: [your document]

```

Never omit `input_type` or set it to `None` for retrieval tasks.

For classification, clustering, or other MTEB tasks using `voyage-large-2-instruct`, follow the instructions in our [GitHub repository](https://github.com/voyage-ai/voyage-large-2-instruct).

What quantization options are available?

Quantization reduces storage, memory, and costs by converting high-precision values to lower-precision formats. Available output data types (`output_dtype`):

| Type | Description | Size Reduction |
| --- | --- | --- |
| `float` | 32-bit single-precision floating-point (default) | None |
| `int8`/`uint8` | 8-bit integers (-128 to 127 / 0 to 255) | 4x |
| `binary`/`ubinary` | Bit-packed single-bit values | 32x |

Binary types use 8-bit integers to represent packed bits, with `binary` using offset binary method.

**Example:** Binary quantization converts eight embedding values into a single 8-bit integer:

```
Original: [-0.03955078, 0.006214142, -0.07446289, -0.039001465,
          0.0046463013, 0.00030612946, -0.08496094, 0.03994751]
Binary:   [0, 1, 0, 0, 1, 1, 0, 1] → 01001101
uint8:    77
int8:     -51 (using offset binary)

```

How can I truncate Matryoshka embeddings?

Matryoshka embeddings contain coarse-to-fine representations that can be truncated by keeping leading dimensions. Here’s how to truncate 1024D vectors to 256D:

```
import voyageai
import numpy as np

def embd_normalize(v: np.ndarray) -> np.ndarray:
    """
    Normalize embedding vectors to unit length.
    Raises ValueError if any row has zero norm.
    """
    row_norms = np.linalg.norm(v, axis=1, keepdims=True)
    if np.any(row_norms == 0):
        raise ValueError("Cannot normalize rows with a norm of zero.")
    return v / row_norms

# Initialize client

vo = voyageai.Client()

# Generate 1024D vectors

embd = vo.embed(['Sample text 1', 'Sample text 2'],
               model='voyage-code-3').embeddings

# Truncate to 256D

short_dim = 256
resized_embd = embd_normalize(
    np.array(embd)[:, :short_dim]
).tolist()

```

# [​](#pricing) Pricing

Visit Voyage’s [pricing page](https://docs.voyageai.com/docs/pricing?ref=anthropic) for the most up to date pricing details.

Was this page helpful?

YesNo

Token counting[Vision](/en/docs/build-with-claude/vision)

On this page
