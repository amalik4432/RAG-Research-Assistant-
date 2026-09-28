"""
RAG Pipeline for Question Answering
Retrieves relevant chunks from ChromaDB and generates answers using Gemini 2.0 Flash
"""

import os
import logging
from typing import List, Dict, Any, Tuple
import chromadb
import google.generativeai as genai
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
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "rag_documents"
EMBEDDING_MODEL = "models/text-embedding-004"
CHAT_MODEL = "gemini-2.0-flash"
TOP_K = 5  # Number of chunks to retrieve

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# System prompt for RAG
SYSTEM_PROMPT = """You are a helpful assistant that answers questions based ONLY on the provided context.

Instructions:
- Use ONLY the information from the provided context to answer questions
- If the context doesn't contain enough information to answer the question, say "I don't know based on the available documents" or "The provided documents don't contain information about that"
- Be concise and accurate
- If you quote from the context, be precise
- Do not make up information or use knowledge outside the provided context
"""


def get_chroma_collection():
    """Get or create ChromaDB collection"""
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
        return collection
    except Exception as e:
        logger.error(f"Error accessing ChromaDB collection: {e}")
        logger.error("Make sure you've run the ingestion pipeline first (python ingest.py)")
        return None


def create_query_embedding(query: str) -> List[float]:
    """Create embedding for the query using Gemini"""
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=query,
            task_type="retrieval_query"
        )
        return result['embedding']
    except Exception as e:
        logger.error(f"Error creating query embedding: {e}")
        return []


def retrieve_context(query: str, top_k: int = TOP_K) -> List[Dict[str, Any]]:
    """
    Retrieve top-k most relevant chunks from ChromaDB
    """
    collection = get_chroma_collection()
    
    if not collection:
        return []
    
    # Create query embedding
    query_embedding = create_query_embedding(query)
    
    if not query_embedding:
        logger.error("Failed to create query embedding")
        return []
    
    # Query ChromaDB
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        contexts = []
        if results and results['documents'] and len(results['documents']) > 0:
            for i in range(len(results['documents'][0])):
                context = {
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None
                }
                contexts.append(context)
        
        logger.info(f"Retrieved {len(contexts)} relevant chunks")
        return contexts
    
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return []


def generate_answer(query: str, contexts: List[Dict[str, Any]]) -> str:
    """
    Generate answer using Gemini with retrieved context
    """
    if not contexts:
        return "I couldn't find any relevant information in the documents to answer your question."
    
    # Build context string
    context_str = "\n\n---\n\n".join([
        f"Source: {ctx['metadata'].get('source', 'unknown')}\n{ctx['text']}"
        for ctx in contexts
    ])
    
    # Create prompt with system instructions, context, and question
    prompt = f"""{SYSTEM_PROMPT}

Context from documents:

{context_str}

---

Question: {query}

Please answer the question based only on the context provided above."""
    
    try:
        # Call Gemini
        model = genai.GenerativeModel(CHAT_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,  # Lower temperature for more factual responses
                max_output_tokens=500,
            )
        )
        
        # Check if response was blocked
        if not response.parts:
            logger.error(f"Response blocked. Prompt feedback: {response.prompt_feedback}")
            return "I couldn't generate a response. Please try rephrasing your question."
        
        answer = response.text
        logger.info("Generated answer successfully")
        return answer
    
    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "I encountered an error while generating the answer. Please try again."


def retrieve_and_answer(question: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Main RAG pipeline: retrieve context and generate answer
    
    Args:
        question: User's question
    
    Returns:
        Tuple of (answer, contexts_used)
    """
    logger.info(f"Processing question: {question}")
    
    # Retrieve relevant context
    contexts = retrieve_context(question)
    
    # Generate answer
    answer = generate_answer(question, contexts)
    
    # Return answer and contexts
    return answer, contexts


def format_context_for_response(contexts: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Format context data for API response
    """
    formatted = []
    for ctx in contexts:
        formatted.append({
            'text': ctx['text'][:200] + '...' if len(ctx['text']) > 200 else ctx['text'],
            'source': ctx['metadata'].get('source', 'unknown'),
            'chunk_index': str(ctx['metadata'].get('chunk_index', ''))
        })
    return formatted


if __name__ == "__main__":
    # Test the RAG pipeline
    test_question = "What is this document about?"
    
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("GEMINI_API_KEY not found in environment variables")
        exit(1)
    
    print(f"\nQuestion: {test_question}\n")
    answer, contexts = retrieve_and_answer(test_question)
    print(f"Answer: {answer}\n")
    print(f"Used {len(contexts)} context chunks")

