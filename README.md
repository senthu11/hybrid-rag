# Hybrid RAG: BM25 + semantic search

A Python command-line RAG project over public AI and retrieval documentation. It fetches the URLs in `sources.json`, extracts readable text, creates overlapping chunks, and combines keyword and embedding retrieval. Answers use the retrieved evidence and numbered source citations.

## Video walkthrough

[Watch the 48-second walkthrough](hybrid-rag-walkthrough.mp4)

The captioned video shows the working interface, generated answer, and side-by-side rankings using actual application captures.

## Quick start on a new computer

Install Python 3.10 or later, clone this repository, and run:

```powershell
Copy-Item .env.example .env
# Edit .env to add your own NEBIUS_API_KEY.
python rag.py ingest
python rag.py serve
```

Open http://127.0.0.1:8000. No pip dependencies are needed to run the application. The downloaded index is generated locally and is not included in this repository.

## Run on this Windows machine

### Web interface

```powershell
.\run.ps1 serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Enter a question and choose **Ask & compare** to see BM25, semantic, and hybrid results side by side. Each result includes its rank, score, source link, passage ID, and expandable full text. Matching passage IDs identify the same chunk across methods. Scores have different scales and should not be compared numerically across methods.

The optional answer uses the hybrid results, with numbered links below it. Turn off **Include an answer** to compare retrieval only. Comparison uses a single query embedding shared by semantic and hybrid retrieval. If the API fails, BM25 results remain visible. The API key stays on the server.

The server listens only on your computer's loopback interface and serves only the three UI assets; configuration files and the index are not exposed as files. It is a local development tool, not a public hosting server. Stop it with Ctrl+C. To use another port: `.\run.ps1 serve --port 8080`.

### Command line

The existing key in `.local-config/.env` is loaded automatically. No Python packages need to be installed. The launcher can use the Python runtime bundled with Codex.

```powershell
.\run.ps1 models
.\run.ps1 ingest
.\run.ps1 ask "How does retrieval augmented generation work?"
.\run.ps1 search "How can I find documents with similar meaning?" --mode semantic
.\run.ps1 search "BM25" --mode bm25
.\run.ps1 search "How does reranking improve retrieval?" --mode hybrid --top-k 5
```

With Python 3.10+ installed, `python rag.py` can replace `.\run.ps1` in every command. If PowerShell blocks scripts, use `powershell -ExecutionPolicy Bypass -File .\run.ps1 --help` for that process only.

## Configuration

For a new installation, copy `.env.example` to `.env` and set `NEBIUS_API_KEY`. Do not overwrite the existing `.local-config/.env`. Process environment variables take priority over `.env`, which takes priority over `.local-config/.env`.

| Setting | Default |
| --- | --- |
| `NEBIUS_BASE_URL` | `https://api.tokenfactory.nebius.com/v1` |
| `RAG_EMBEDDING_MODEL` | `Qwen/Qwen3-Embedding-8B` |
| `RAG_CHAT_MODEL` | `Qwen/Qwen3-30B-A3B-Instruct-2507` |

The key is used only for the configured Nebius API. Embedding requests send document chunks or search queries; answer requests send the question and retrieved chunks. These API calls use your account quota. Secrets are never included in the index. `.env`, `.local-config/`, and generated `data/` are ignored by Git.

## How retrieval works

1. Fetch HTML/plain-text pages from the explicit URL list (no recursive crawling).
2. Remove navigation and scripts, split into 180-word chunks with a 35-word overlap, and remove duplicate chunks.
3. Embed chunks through Nebius and store normalized vectors with text, URL, title, and fetch time in `data/index.json`.
4. Rank by BM25 (k1=1.5, b=0.75) and by cosine similarity independently.
5. Merge the top candidates using reciprocal rank fusion: each rank contributes `1 / (60 + rank)`.
6. Send the top results to the chat model with instructions to answer only from evidence and cite `[1]`, `[2]`, etc. Print the corresponding URLs below the answer.

BM25 search works offline after indexing. Semantic/hybrid search makes one embedding request per query. `ask` also makes a chat request. The index records its embedding model so searches always use the same model; changing that model requires re-ingestion.

## Change the data

Edit `sources.json` or run `python rag.py ingest --sources my_urls.json` with a JSON array of public URLs. Re-ingestion refreshes content and replaces the index only after successful embedding. Individual fetch failures are reported and recorded in the index. An entirely failed ingestion leaves the previous index intact.

This is a small-corpus starter project, with an in-memory vector scan and a local JSON index. It supports server-rendered HTML and plain text, not PDFs, authenticated sites, or JavaScript-rendered pages. Semantic retrieval always returns nearest neighbors, even for unrelated questions; the model is instructed to admit insufficient evidence, but citations and factual grounding still need review. Use a vector database and retrieval evaluation before scaling to large corpora. Only ingest URLs you trust and are permitted to fetch.

## Tests

```powershell
python -m unittest discover -s tests -v
```

Tests cover BM25 ranking, semantic ranking with deterministic test vectors, rank fusion, overlap boundaries, empty queries, embedding dimensions, HTML extraction, and no-evidence handling. Live API and internet access are separate integration checks.

## References

- [Nebius API integration examples](https://github.com/nebius/token-factory-cookbook)
- [Sentence Transformers semantic search](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)
- [Retrieve and rerank](https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)

