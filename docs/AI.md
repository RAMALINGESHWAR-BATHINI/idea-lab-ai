# AI & Web Intelligence

## Overview

The AI layer provides conversational AI with web search, document retrieval, and tool use. It's accessed through the `/api/ai/chat` endpoint and powers both the website chat and voice assistant.

## Architecture

```
User Message
    │
    ▼
Prompt Injection Fence (sanitizes input)
    │
    ▼
AI Orchestrator
    ├── Provider Selection (Gemini or Ollama)
    │   ├── Gemini: cloud, fast, needs API key
    │   └── Ollama: local, private, no key needed
    │
    ├── Tools (optional)
    │   ├── Web Search (SSRF-guarded)
    │   └── Document Retrieval (pgvector semantic search)
    │
    ▼
Response (text + sources + tool metadata)
```

## Provider Selection

### Gemini (Cloud)
- Model: `gemini-1.5-flash` (text), `gemini-2.0-flash-live` (voice)
- Embeddings: `text-embedding-004`
- Requires `GEMINI_API_KEY`
- Best for: fast, high-quality responses

### Ollama (Local)
- Chat model: `llama3.2`
- Embedding model: `nomic-embed-text` (768-dim)
- Requires `ollama serve` running
- Best for: private data, offline operation

## Web Search

When `use_search: true`, the AI can search the web for current information:
- Results are SSRF-guarded (no access to private IPs)
- Configurable timeout (15s) and max bytes (5MB)
- Sources are returned with the response

## Document Retrieval

Institutional documents are stored with pgvector embeddings:
1. Documents are chunked and embedded on upload
2. User queries are embedded and matched against document chunks
3. Relevant chunks are injected into the AI context
4. Only documents with `access_level <= user's level` are accessible

## Memory System

The AI maintains conversation history and long-term memory:
- `CONVERSATION_HISTORY_LIMIT=40` messages per conversation
- `MEMORY_MAX_ITEMS_PER_USER=500` long-term memories
- Memories are scoped to user, session, or institution

## Prompt Injection Defense

All user input is sanitized before reaching the LLM:
- System prompt is fenced with clear boundaries
- User input is labeled and escaped
- Tool outputs are treated as data, not instructions

## Rate Limiting

| Endpoint | Limit |
|---|---|
| `/api/ai/chat` | 30/minute (per user) |
| `/api/auth/*` | 20/minute (per IP) |
| Default | 120/minute (per IP) |

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | (empty) | Gemini API key |
| `GEMINI_TEXT_MODEL` | gemini-1.5-flash | Chat model |
| `OLLAMA_BASE_URL` | http://127.0.0.1:11434 | Ollama server |
| `OLLAMA_EMBED_MODEL` | nomic-embed-text | Embedding model |
| `EMBEDDING_PROVIDER` | ollama | ollama or gemini |
| `EMBEDDING_DIMENSION` | 768 | Vector dimension |
| `FETCH_TIMEOUT_SECONDS` | 15 | Web fetch timeout |
| `WEB_SEARCH_RESULTS` | 5 | Search result count |