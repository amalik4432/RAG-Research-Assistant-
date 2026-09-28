# Retrieval Research Assistant

**Author:** Ahmad Raza

A document-grounded Retrieval-Augmented Generation (RAG) assistant built with Python, FastAPI, ChromaDB, and Google Gemini. Ask questions about your documents and get answers grounded in their content.

## Features

- 🚀 **Fast & Modern API**: Built with FastAPI for high performance
- 📚 **Multi-format Support**: Handles PDF, TXT, and Markdown files
- 🧠 **Smart Chunking**: Intelligent text chunking with overlap for better context
- 🔍 **Vector Search**: Uses ChromaDB for efficient similarity search
- 💬 **Gemini 2.0 Flash**: Generates answers using retrieved document context
- 🎨 **Beautiful UI**: Includes a modern chat interface
- 📝 **Production Ready**: Comprehensive logging, error handling, and validation

## Tech Stack

- **Python 3.8+**
- **FastAPI** - Web framework
- **ChromaDB** - Vector database for embeddings
- **Google Gemini API** - Embeddings (`text-embedding-004`) and generation (`gemini-2.0-flash`)
- **PyPDF** - PDF processing
- **Uvicorn** - ASGI server

## Project Structure

```
Retrieval Research Assistant/
├── app.py              # FastAPI application with endpoints
├── ingest.py           # Document ingestion pipeline
├── rag.py              # RAG retrieval and answer generation
├── test_rag.py         # Test script
├── requirements.txt    # Python dependencies
├── notebooks/          # Optional local-embedding retrieval notebook
│   ├── 10_RAG_pipeline.ipynb
│   └── requirements.txt
├── README.md           # This file
├── .env                # Environment variables (create this)
├── docs/               # Place your documents here
└── chroma_db/          # ChromaDB storage (auto-created)
```

## Installation

### 1. Clone or Download the Project

```bash
cd "RAG Chatbot"
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root by copying the example:

```bash
# Windows PowerShell:
Copy-Item .env.example .env

# macOS/Linux:
cp .env.example .env
```

Set your Google Gemini API key in `.env`:

```
GEMINI_API_KEY=your-gemini-api-key-here
```

> **Get your API key**: Visit [Google AI Studio](https://aistudio.google.com/apikey)

## Usage

### Step 1: Add Documents

Place your documents in the `docs/` folder:

```bash
# Create docs folder if it doesn't exist
mkdir -p docs

# Add your documents (PDF, TXT, or MD files)
cp /path/to/your/document.pdf docs/
```

### Step 2: Ingest Documents

Run the ingestion pipeline to process documents and store them in ChromaDB:

```bash
python ingest.py
```

This will:

- Read all documents from the `docs/` folder
- Split them into chunks (500-1000 characters)
- Create embeddings using Gemini
- Store everything in ChromaDB

**Expected output:**

```
2024-01-01 12:00:00 - __main__ - INFO - Starting document ingestion pipeline...
2024-01-01 12:00:00 - __main__ - INFO - Processing file: document.pdf
2024-01-01 12:00:00 - __main__ - INFO - Created 15 chunks from document.pdf
2024-01-01 12:00:00 - __main__ - INFO - Total chunks created: 15
2024-01-01 12:00:00 - __main__ - INFO - Creating embeddings...
2024-01-01 12:00:01 - __main__ - INFO - Successfully ingested 15 chunks into ChromaDB
2024-01-01 12:00:01 - __main__ - INFO - Ingestion pipeline completed successfully!
```

### Step 3: Run the API

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

The server will start at `http://localhost:8000`

### Step 4: Use the Chatbot

#### Option A: Web Interface (Recommended)

Open your browser and go to:

```
http://localhost:8000
```

You'll see a beautiful chat interface where you can ask questions!

#### Option B: API Endpoint

Send POST requests to the `/ask` endpoint:

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

**Response format:**

```json
{
  "answer": "Based on the provided documents...",
  "context": [
    {
      "text": "Relevant chunk of text...",
      "source": "document.pdf",
      "chunk_index": "0"
    }
  ]
}
```

#### Option C: Test Script

Run the test script to see the RAG system in action:

```bash
python test_rag.py
```

## API Documentation

Once the server is running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

### Endpoints

#### `GET /`

Returns the chat UI (HTML page)

#### `GET /health`

Health check endpoint

**Response:**

```json
{
  "status": "healthy",
  "service": "Retrieval Research Assistant API",
  "version": "1.0.0"
}
```

#### `POST /ask`

Ask a question to the chatbot

**Request body:**

```json
{
  "question": "Your question here"
}
```

**Response:**

```json
{
  "answer": "The answer based on your documents",
  "context": [
    {
      "text": "Relevant text chunk",
      "source": "filename.pdf",
      "chunk_index": "0"
    }
  ]
}
```

## Configuration

You can modify these settings in the respective files:

### Ingestion Configuration (`ingest.py`)

```python
DOCS_FOLDER = "./docs"           # Where to read documents from
CHROMA_DB_PATH = "./chroma_db"   # Where to store the database
CHUNK_SIZE = 750                 # Characters per chunk (500-1000)
CHUNK_OVERLAP = 100              # Overlap between chunks
EMBEDDING_MODEL = "models/text-embedding-004"  # Gemini embedding model
```

### RAG Configuration (`rag.py`)

```python
TOP_K = 5                        # Number of chunks to retrieve
CHAT_MODEL = "gemini-2.0-flash"  # Gemini generation model
```

## How It Works

### 1. Document Ingestion

```
Documents → Read & Parse → Chunk Text → Create Embeddings → Store in ChromaDB
```

- Reads PDF, TXT, and MD files
- Splits documents into overlapping chunks for better context
- Uses Gemini's `text-embedding-004` to create vector embeddings
- Stores chunks with metadata in ChromaDB

### 2. Question Answering

```
Question → Create Embedding → Search ChromaDB → Retrieve Top-K → Generate Answer
```

- Converts question to embedding
- Finds most similar chunks using vector search
- Passes relevant chunks to Gemini 2.0 Flash
- Generates answer using only the provided context

### 3. System Prompt

The chatbot is instructed to:

- Use ONLY the provided context to answer questions
- Say "I don't know" if information isn't in the documents
- Be concise and accurate
- Not make up information

## Troubleshooting

### "GEMINI_API_KEY not found"

- Make sure you created a `.env` file in the project root
- Add your API key: `GEMINI_API_KEY=...`
- Restart the server after adding the key

### "ChromaDB collection not found"

- Run the ingestion pipeline first: `python ingest.py`
- Make sure documents are in the `docs/` folder

### "No documents processed"

- Check that your documents are in the `docs/` folder
- Supported formats: `.pdf`, `.txt`, `.md`
- Check file permissions

### Port 8000 already in use

```bash
# Use a different port
uvicorn app:app --reload --port 8001
```

## Re-ingesting Documents

To update the knowledge base with new documents:

1. Add new files to the `docs/` folder
2. Run the ingestion pipeline again:
   ```bash
   python ingest.py
   ```

This will delete the old ChromaDB collection and create a new one with all documents.

## Development

### Running Tests

```bash
python test_rag.py
```

### Checking Logs

The application uses Python logging. Check the console output for detailed logs.

### Adding New Document Types

To support additional file types, modify the `read_document()` function in `ingest.py`:

```python
def read_document(file_path: str) -> str:
    extension = Path(file_path).suffix.lower()

    if extension == '.pdf':
        return read_pdf(file_path)
    elif extension in ['.txt', '.md']:
        return read_text_file(file_path)
    elif extension == '.docx':  # Add your custom handler
        return read_docx(file_path)
    # ...
```

## Performance Tips

1. **Chunk Size**: Adjust `CHUNK_SIZE` based on your documents
   - Smaller chunks (500): More precise, but may miss context
   - Larger chunks (1000): More context, but less precise

2. **Top-K**: Adjust `TOP_K` for retrieval
   - More chunks: Better context, but more tokens/cost
   - Fewer chunks: Faster, cheaper, but may miss information

3. **Embeddings and generation**: Gemini usage and pricing depend on the selected models and current Google AI terms.

## Optional Retrieval Notebook

`notebooks/10_RAG_pipeline.ipynb` demonstrates local semantic retrieval over files in `docs/` using Sentence Transformers and a separate ChromaDB collection. It is an independent retrieval experiment; it does not use the app's Gemini embeddings or generate answers.

Install its optional dependencies from the project root:

```bash
python -m pip install -r notebooks/requirements.txt
```

Open the notebook and run its cells in order. The embedding model is downloaded on first use, and the notebook's vector store is kept under `notebooks/vector_store/`.

## License

This project is available for personal and commercial use under the
[MIT License](LICENSE).

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all dependencies are installed
4. Verify your Gemini API key is valid

## Next Steps

- Add authentication for production use
- Implement caching for faster responses
- Add support for more document types
- Deploy to cloud (AWS, GCP, Azure)
- Add conversation history
- Implement streaming responses

---

**Built with Python, FastAPI, ChromaDB, and Google Gemini**
