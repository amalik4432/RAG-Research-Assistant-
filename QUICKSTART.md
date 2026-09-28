# 🚀 Quick Start Guide

Get your Retrieval Research Assistant running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

## Step-by-Step Setup

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Set Up Your API Key

Create a `.env` file in the project root and add your Gemini API key:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
```

Copy `.env.example` to `.env` and replace the placeholder with your real Gemini API key.

### 3️⃣ Ingest Sample Documents

The project comes with sample documents in the `docs/` folder. Ingest them:

```bash
python ingest.py
```

Expected output:

```
INFO - Starting document ingestion pipeline...
INFO - Processing file: sample_product_guide.md
INFO - Created 25 chunks from sample_product_guide.md
INFO - Processing file: company_policies.txt
INFO - Created 45 chunks from company_policies.txt
INFO - Processing file: technical_documentation.md
INFO - Created 52 chunks from technical_documentation.md
INFO - Total chunks created: 122
INFO - Creating embeddings...
INFO - Successfully ingested 122 chunks into ChromaDB
INFO - Ingestion pipeline completed successfully!
```

### 4️⃣ Run the API

```bash
uvicorn app:app --reload
```

### 5️⃣ Start Chatting!

Open your browser and go to:

```
http://localhost:8000
```

You'll see a beautiful chat interface! Try asking questions like:

- "What is the SmartHome Hub?"
- "What is the remote work policy?"
- "How do I upload a file using the CloudSync API?"
- "What are the parental leave benefits?"
- "How do I create automation rules?"

## 🧪 Test the System

Run the test script:

```bash
python test_rag.py
```

This will ask several questions and show you the answers with source context.

## 📝 Adding Your Own Documents

1. Add PDF, TXT, or MD files to the `docs/` folder
2. Run the ingestion again: `python ingest.py`
3. Start asking questions about your documents!

## 🔧 Troubleshooting

### "GEMINI_API_KEY not found"

- Make sure you created the `.env` file
- Check that `GEMINI_API_KEY` is set correctly
- Don't use quotes around the value in `.env`

### "ModuleNotFoundError"

- Make sure you installed dependencies: `pip install -r requirements.txt`
- Consider using a virtual environment

### "No documents processed"

- Check that files are in the `docs/` folder
- Verify file extensions are `.pdf`, `.txt`, or `.md`

## 🎯 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize chunking parameters in `ingest.py`
- Adjust retrieval settings in `rag.py`
- Explore the API at http://localhost:8000/docs

## 💡 Example Questions for Sample Documents

**For SmartHome Hub guide:**

- "How do I set up the SmartHome Hub?"
- "What are the technical specifications?"
- "How do I create a Good Morning routine?"

**For Company Policies:**

- "How many PTO days do I get?"
- "What is the professional development budget?"
- "What are the remote work requirements?"

**For CloudSync API:**

- "How do I authenticate with the API?"
- "Show me how to upload a file"
- "What are the rate limits?"

---

**Need help?** Check the full README.md or review the code comments in each file.
