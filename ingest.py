"""
Ingestion Pipeline for RAG Chatbot
Reads documents from /docs folder, chunks them, creates embeddings, and stores in ChromaDB
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from pypdf import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DOCS_FOLDER = "./docs"
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "rag_documents"
CHUNK_SIZE = 750  # Target chunk size (between 500-1000 chars)
CHUNK_OVERLAP = 100  # Overlap between chunks for better context
EMBEDDING_MODEL = "models/text-embedding-004"

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def read_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
        return ""


def read_text_file(file_path: str) -> str:
    """Read text from TXT or MD file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading text file {file_path}: {e}")
        return ""


def read_document(file_path: str) -> str:
    """Read document based on file extension"""
    extension = Path(file_path).suffix.lower()
    
    if extension == '.pdf':
        return read_pdf(file_path)
    elif extension in ['.txt', '.md']:
        return read_text_file(file_path)
    else:
        logger.warning(f"Unsupported file type: {extension}")
        return ""


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into chunks with overlap for better context preservation
    """
    if not text or len(text.strip()) == 0:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Calculate end position
        end = start + chunk_size
        
        # If this is not the last chunk, try to break at sentence or word boundary
        if end < text_length:
            # Look for sentence ending (. ! ?) within the last 100 chars
            chunk_end = text.rfind('.', start, end)
            if chunk_end == -1:
                chunk_end = text.rfind('!', start, end)
            if chunk_end == -1:
                chunk_end = text.rfind('?', start, end)
            
            # If no sentence ending found, try to break at space
            if chunk_end == -1 or chunk_end < start + chunk_size // 2:
                chunk_end = text.rfind(' ', start, end)
            
            # If still no good breaking point, just use the chunk_size
            if chunk_end == -1 or chunk_end < start + chunk_size // 2:
                chunk_end = end
            else:
                chunk_end += 1  # Include the punctuation
        else:
            chunk_end = text_length
        
        chunk = text[start:chunk_end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = chunk_end - overlap if chunk_end - overlap > start else chunk_end
    
    return chunks


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Create embeddings using Google's Gemini embedding model
    Handles batching for large number of texts
    """
    embeddings = []
    batch_size = 100  # Process in batches to avoid rate limits
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            # Gemini processes one text at a time for embeddings
            batch_embeddings = []
            for text in batch:
                result = genai.embed_content(
                    model=EMBEDDING_MODEL,
                    content=text,
                    task_type="retrieval_document"
                )
                batch_embeddings.append(result['embedding'])
            
            embeddings.extend(batch_embeddings)
            logger.info(f"Created embeddings for batch {i//batch_size + 1} ({len(batch)} texts)")
        except Exception as e:
            logger.error(f"Error creating embeddings for batch {i//batch_size + 1}: {e}")
            # Add empty embeddings for failed batch (Gemini embeddings are 768 dimensions)
            embeddings.extend([[0.0] * 768] * len(batch))
    
    return embeddings


def process_documents() -> List[Dict[str, Any]]:
    """
    Process all documents in the docs folder
    Returns list of chunks with metadata
    """
    docs_path = Path(DOCS_FOLDER)
    
    if not docs_path.exists():
        logger.error(f"Docs folder not found: {DOCS_FOLDER}")
        return []
    
    all_chunks = []
    
    # Supported file extensions
    supported_extensions = ['.pdf', '.txt', '.md']
    
    # Process each file in the docs folder
    for file_path in docs_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            logger.info(f"Processing file: {file_path.name}")
            
            # Read document content
            content = read_document(str(file_path))
            
            if not content:
                logger.warning(f"No content extracted from {file_path.name}")
                continue
            
            # Chunk the document
            chunks = chunk_text(content)
            logger.info(f"Created {len(chunks)} chunks from {file_path.name}")
            
            # Create chunk objects with metadata
            for idx, chunk in enumerate(chunks):
                all_chunks.append({
                    'text': chunk,
                    'metadata': {
                        'source': file_path.name,
                        'chunk_index': idx,
                        'total_chunks': len(chunks),
                        'file_type': file_path.suffix.lower()
                    }
                })
    
    logger.info(f"Total chunks created: {len(all_chunks)}")
    return all_chunks


def ingest_to_chromadb(chunks: List[Dict[str, Any]]):
    """
    Ingest chunks into ChromaDB with embeddings
    """
    if not chunks:
        logger.warning("No chunks to ingest")
        return
    
    # Initialize ChromaDB
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    
    # Delete existing collection if it exists (for clean re-ingestion)
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        logger.info(f"Deleted existing collection: {COLLECTION_NAME}")
    except:
        pass
    
    # Create new collection
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "RAG chatbot document collection"}
    )
    
    # Extract texts for embedding
    texts = [chunk['text'] for chunk in chunks]
    
    # Create embeddings
    logger.info("Creating embeddings...")
    embeddings = create_embeddings(texts)
    
    # Prepare data for ChromaDB
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [chunk['metadata'] for chunk in chunks]
    
    # Add to collection
    logger.info("Adding to ChromaDB...")
    collection.add(
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    
    logger.info(f"Successfully ingested {len(chunks)} chunks into ChromaDB")


def main():
    """
    Main ingestion pipeline
    """
    logger.info("Starting document ingestion pipeline...")
    
    # Check for Gemini API key
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY not found in environment variables")
        logger.error("Please create a .env file with your Gemini API key")
        return
    
    # Process documents
    chunks = process_documents()
    
    if not chunks:
        logger.error("No documents processed. Please add documents to the /docs folder")
        return
    
    # Ingest to ChromaDB
    ingest_to_chromadb(chunks)
    
    logger.info("Ingestion pipeline completed successfully!")


if __name__ == "__main__":
    main()

