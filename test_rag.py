"""
Test script for RAG Chatbot
Tests the RAG pipeline with sample questions
"""

import os
import sys
from dotenv import load_dotenv
import rag

# Load environment variables
load_dotenv()


def print_separator():
    """Print a visual separator"""
    print("\n" + "="*80 + "\n")


def test_question(question: str):
    """
    Test a single question through the RAG pipeline
    """
    print(f"Question: {question}")
    print("-" * 80)
    
    try:
        answer, contexts = rag.retrieve_and_answer(question)
        
        print(f"\nAnswer:\n{answer}\n")
        
        if contexts:
            print(f"Context Used ({len(contexts)} chunks):")
            for i, ctx in enumerate(contexts, 1):
                source = ctx['metadata'].get('source', 'unknown')
                chunk_idx = ctx['metadata'].get('chunk_index', '?')
                text_preview = ctx['text'][:150] + "..." if len(ctx['text']) > 150 else ctx['text']
                print(f"\n  {i}. Source: {source} (chunk {chunk_idx})")
                print(f"     Preview: {text_preview}")
        else:
            print("No context retrieved.")
        
        print_separator()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        print_separator()
        return False


def main():
    """
    Main test function
    """
    print_separator()
    print("RAG CHATBOT TEST SUITE")
    print_separator()
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        print("Please create a .env file with your Gemini API key")
        sys.exit(1)
    
    # Check if ChromaDB has been populated
    collection = rag.get_chroma_collection()
    if not collection:
        print("❌ Error: ChromaDB collection not found")
        print("Please run the ingestion pipeline first:")
        print("  python ingest.py")
        sys.exit(1)
    
    # Get collection stats
    try:
        count = collection.count()
        print(f"✓ ChromaDB collection found with {count} documents")
        print_separator()
    except:
        print("⚠️  Warning: Could not get collection count")
        print_separator()
    
    # Test questions
    # These are generic questions that should work with most document sets
    test_questions = [
        "What is this document about?",
        "Can you summarize the main points?",
        "What are the key topics covered?",
        "Tell me about the important information in these documents",
        "What should I know from reading these documents?"
    ]
    
    print("Running test questions...\n")
    
    success_count = 0
    for question in test_questions:
        if test_question(question):
            success_count += 1
    
    # Summary
    print("TEST SUMMARY")
    print("-" * 80)
    print(f"Total questions: {len(test_questions)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(test_questions) - success_count}")
    print_separator()
    
    if success_count == len(test_questions):
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()

