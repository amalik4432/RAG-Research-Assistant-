# Retrieval Research Assistant Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  RETRIEVAL RESEARCH ASSISTANT                    │
│                     (FastAPI + ChromaDB)                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Documents      │────▶│   Ingestion      │────▶│   ChromaDB       │
│  (PDF/TXT/MD)    │     │   Pipeline       │     │   (Vectors)      │
│                  │     │                  │     │                  │
│  /docs/          │     │  ingest.py       │     │  chroma_db/      │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                               │                           │
                               │                           │
                               ▼                           ▼
                         ┌──────────────────┐     ┌──────────────────┐
                         │  Gemini API      │     │   Embeddings     │
                         │  Embeddings      │     │   + Metadata     │
                         │  (text-embed-3)  │     │   + Documents    │
                         └──────────────────┘     └──────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   User           │────▶│   FastAPI        │────▶│   RAG Pipeline   │
│   Browser/API    │     │   Web Server     │     │   rag.py         │
│                  │     │                  │     │                  │
│  Chat UI         │◀────│  app.py          │◀────│  retrieve()      │
└──────────────────┘     └──────────────────┘     │  answer()        │
                                                   └──────────────────┘
                                                           │
                                                           ▼
                                                   ┌──────────────────┐
                                                   │  Gemini API      │
                                                   │  Gemini 2.0 Flash│
                                                   │  (Chat)          │
                                                   └──────────────────┘
```

## Component Details

### 1. Ingestion Pipeline (`ingest.py`)

**Purpose:** Process documents and store in vector database

```
Documents → Read → Chunk → Embed → Store
```

**Steps:**

1. **Read Documents**
   - Scan `/docs` folder
   - Support PDF, TXT, MD formats
   - Extract text content

2. **Chunk Text**
   - Split into 500-1000 character chunks
   - 100 character overlap
   - Smart boundary detection (sentences)

3. **Create Embeddings** - Call Google Gemini API - Model: `models/text-embedding-004`
   - Batch processing (100 texts/batch)

4. **Store in ChromaDB**
   - Save embeddings as vectors
   - Store original text
   - Add metadata (source, chunk_index, etc.)

**Key Functions:**

- `read_document(file_path)` - Read file content
- `chunk_text(text)` - Split into chunks
- `create_embeddings(texts)` - Generate embeddings
- `ingest_to_chromadb(chunks)` - Store in DB

### 2. RAG Pipeline (`rag.py`)

**Purpose:** Retrieve relevant context and generate answers

```
Question → Embed → Search → Retrieve → Generate Answer
```

**Steps:**

1. **Embed Question**
   - Convert question to vector
   - Same model as documents

2. **Semantic Search**
   - Query ChromaDB with question vector
   - Find top-K similar chunks
   - Return with metadata

3. **Generate Answer**
   - Build context from retrieved chunks
     - Call Gemini 2.0 Flash
   - Use strict system prompt
   - Return answer with sources

**Key Functions:**

- `create_query_embedding(query)` - Embed question
- `retrieve_context(query, top_k)` - Search ChromaDB
- `generate_answer(query, contexts)` - Call GPT
- `retrieve_and_answer(question)` - Main pipeline

### 3. FastAPI Application (`app.py`)

**Purpose:** Web server and API endpoints

**Endpoints:**

```
GET  /          → HTML Chat UI
GET  /health    → Health check
POST /ask       → Question answering
GET  /docs      → API documentation (auto-generated)
```

**Request Flow:**

```
Client Request → FastAPI → Input Validation → RAG Pipeline → Response
```

**Features:**

- Pydantic models for validation
- Error handling
- Logging
- CORS support
- Embedded chat UI

### 4. Chat UI (embedded in `app.py`)

**Purpose:** User-friendly chat interface

**Features:**

- Modern, responsive design
- Real-time chat
- Loading indicators
- Source attribution
- Error handling
- Auto-scroll

**Technologies:**

- Vanilla JavaScript
- CSS3 animations
- Fetch API for requests

## Data Flow

### Ingestion Flow

```
┌─────────────┐
│  Document   │
│  file.pdf   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Extract     │
│ Text        │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Split into  │
│ Chunks      │
│ (750 chars) │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Gemini API      │
│ Create Embedding│
│ [0.1, 0.3, ...] │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ ChromaDB        │
│ Store:          │
│ - Vector        │
│ - Text          │
│ - Metadata      │
└─────────────────┘
```

### Query Flow

```
┌─────────────┐
│  User Query │
│ "What is X?"│
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Gemini API      │
│ Create Embedding│
│ [0.2, 0.4, ...] │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ ChromaDB        │
│ Vector Search   │
│ Find Top-5      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Retrieved Chunks│
│ 1. "X is..."    │
│ 2. "X has..."   │
│ 3. "X does..."  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Build Context   │
│ Combine chunks  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Gemini 2.0 Flash│
│ Generate Answer │
│ "Based on..."   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Return to User  │
│ Answer + Sources│
└─────────────────┘
```

## Technology Stack

### Core Technologies

```
┌──────────────────────────────────┐
│ Python 3.8+                      │
├──────────────────────────────────┤
│ FastAPI 0.104+                   │
│ - Web framework                  │
│ - Auto API docs                  │
│ - Pydantic validation            │
├──────────────────────────────────┤
│ ChromaDB 0.4+                    │
│ - Vector database                │
│ - Local storage                  │
│ - Similarity search              │
├──────────────────────────────────┤
│ Google Gemini API                │
│ - text-embedding-004             │
│ - gemini-2.0-flash               │
├──────────────────────────────────┤
│ Uvicorn                          │
│ - ASGI server                    │
└──────────────────────────────────┘
```

### Supporting Libraries

- **pypdf** - PDF parsing
- **python-dotenv** - Environment variables
- **python-multipart** - File uploads
- **pydantic** - Data validation

## Storage Architecture

### ChromaDB Structure

```
chroma_db/
├── Collection: "rag_documents"
│   ├── Embeddings (vectors)
│   ├── Documents (text)
│   ├── Metadata
│   │   ├── source: filename
│   │   ├── chunk_index: position
│   │   ├── total_chunks: count
│   │   └── file_type: extension
│   └── IDs: chunk_0, chunk_1, ...
```

### Vector Dimensions

- Embedding model: models/text-embedding-004
- Vector size: 768 dimensions
- Distance metric: Cosine similarity

## API Architecture

### REST API Structure

```
app.py
│
├── GET /
│   └── Returns: HTML chat interface
│
├── GET /health
│   └── Returns: {"status": "healthy"}
│
├── POST /ask
│   ├── Input: {"question": "..."}
│   └── Output: {"answer": "...", "context": [...]}
│
└── GET /docs
    └── Returns: OpenAPI documentation
```

### Request/Response Models

**Request:**

```python
class QuestionRequest(BaseModel):
    question: str  # min_length=1
```

**Response:**

```python
class AnswerResponse(BaseModel):
    answer: str
    context: list[ContextItem]

class ContextItem(BaseModel):
    text: str
    source: str
    chunk_index: str
```

## Security Architecture

### Current Implementation

- ✅ API key in environment variable
- ✅ Input validation
- ✅ Error handling
- ✅ No secrets in code

### Production Recommendations

- 🔐 Add API authentication
- 🔐 Implement rate limiting
- 🔐 Add HTTPS/TLS
- 🔐 User access control
- 🔐 Audit logging

## Performance Characteristics

### Ingestion Performance

- **100 pages**: ~2-3 minutes
- **Bottleneck**: Gemini API calls
- **Optimization**: Batch processing implemented

### Query Performance

- **Response time**: 1-3 seconds
- **Components**:
  - Embedding: ~100ms
  - Vector search: ~50ms
    - Gemini 2.0 Flash: 1-2s
- **Optimization**: Consider caching

### Scalability

- **Current**: Single-user, local
- **Limitations**:
  - ChromaDB on disk
  - Synchronous processing
  - No load balancing

## Error Handling Strategy

### Levels of Error Handling

```
┌─────────────────────────────────────┐
│ User-Facing Errors                  │
│ - "I don't know"                    │
│ - "Service temporarily unavailable" │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ Application-Level Errors            │
│ - HTTP exceptions                   │
│ - Validation errors                 │
│ - API error responses               │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│ System-Level Errors                 │
│ - Logged to console                 │
│ - Stack traces                      │
│ - Debug information                 │
└─────────────────────────────────────┘
```

### Error Categories

1. **Input Errors**: Validation failures
2. **API Errors**: Gemini rate limits, failures
3. **Database Errors**: ChromaDB connection issues
4. **System Errors**: File I/O, memory issues

## Monitoring & Logging

### Current Logging

```
Level: INFO
Format: timestamp - module - level - message
Output: Console/stdout
```

### Logged Events

- Document processing
- Embedding creation
- Query execution
- Answer generation
- API requests
- Errors and exceptions

## Configuration Management

### Environment Variables (.env)

```
GEMINI_API_KEY=...
```

### Application Configuration

- Hardcoded in modules
- Easy to modify
- No external config files

### Recommended for Production

- External config file
- Environment-specific settings
- Secret management service

## Deployment Architecture

### Current (Development)

```
Local Machine
├── Python environment
├── ChromaDB (local disk)
└── Uvicorn server
```

### Recommended (Production)

```
Cloud Platform (AWS/GCP/Azure)
├── Container (Docker)
├── Vector DB (Managed ChromaDB/Pinecone)
├── Web Server (Gunicorn + Uvicorn)
├── Load Balancer
├── CDN (for static assets)
└── Monitoring (Datadog/New Relic)
```

## Future Enhancements

### Phase 1 (Easy)

- [ ] Add conversation history
- [ ] Implement caching
- [ ] Add more document types
- [ ] Improve UI/UX

### Phase 2 (Medium)

- [ ] User authentication
- [ ] Multi-user support
- [ ] Analytics dashboard
- [ ] Rate limiting

### Phase 3 (Advanced)

- [ ] Streaming responses
- [ ] Multi-language support
- [ ] Fine-tuned models
- [ ] Advanced RAG techniques

---

**This architecture is designed for:**

- ✅ Ease of understanding
- ✅ Quick setup and testing
- ✅ Local development
- ✅ Easy extension
- ✅ Production readiness (with security additions)
