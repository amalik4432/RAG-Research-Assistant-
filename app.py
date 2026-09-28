"""
 FastAPI application for the Retrieval Research Assistant
Provides REST API endpoints for question answering
"""

import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import rag

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Retrieval Research Assistant API",
    description="Question answering system using Retrieval-Augmented Generation",
    version="1.0.0"
)

# Request/Response Models
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask")


class ContextItem(BaseModel):
    text: str
    source: str
    chunk_index: str


class AnswerResponse(BaseModel):
    answer: str
    context: list[ContextItem]


# HTML UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retrieval Research Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 800px;
            height: 90vh;
            max-height: 700px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 20px 20px 0 0;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 30px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 20px;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.user {
            text-align: right;
        }
        
        .message-content {
            display: inline-block;
            padding: 15px 20px;
            border-radius: 18px;
            max-width: 70%;
            word-wrap: break-word;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .message.bot .message-content {
            background: white;
            color: #333;
            border-bottom-left-radius: 5px;
            text-align: left;
        }
        
        .context-info {
            font-size: 11px;
            color: #666;
            margin-top: 8px;
            padding: 8px 12px;
            background: #f0f0f0;
            border-radius: 8px;
            display: inline-block;
        }
        
        .input-container {
            padding: 20px 30px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }
        
        .input-container input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 15px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .input-container input:focus {
            border-color: #667eea;
        }
        
        .input-container button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .input-container button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .input-container button:active {
            transform: translateY(0);
        }
        
        .input-container button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Retrieval Research Assistant</h1>
            <p>Ask questions about your documents</p>
        </div>
        
        <div class="chat-container" id="chatContainer">
            <div class="message bot">
                <div class="message-content">
                    👋 Hello! I'm your document assistant. Ask me anything about the documents in the knowledge base!
                </div>
            </div>
        </div>
        
        <div class="input-container">
            <input 
                type="text" 
                id="questionInput" 
                placeholder="Type your question here..." 
                onkeypress="if(event.key==='Enter') askQuestion()"
            />
            <button onclick="askQuestion()" id="askButton">Send</button>
        </div>
    </div>
    
    <script>
        const chatContainer = document.getElementById('chatContainer');
        const questionInput = document.getElementById('questionInput');
        const askButton = document.getElementById('askButton');
        
        function addMessage(content, isUser = false, contextInfo = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(contentDiv);
            
            if (contextInfo && !isUser) {
                const contextDiv = document.createElement('div');
                contextDiv.className = 'context-info';
                contextDiv.textContent = contextInfo;
                messageDiv.appendChild(contextDiv);
            }
            
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function addLoading() {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot';
            messageDiv.id = 'loadingMessage';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            const loadingSpinner = document.createElement('div');
            loadingSpinner.className = 'loading';
            
            contentDiv.appendChild(loadingSpinner);
            messageDiv.appendChild(contentDiv);
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function removeLoading() {
            const loadingMessage = document.getElementById('loadingMessage');
            if (loadingMessage) {
                loadingMessage.remove();
            }
        }
        
        function showError(message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = '⚠️ ' + message;
            chatContainer.appendChild(errorDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        async function askQuestion() {
            const question = questionInput.value.trim();
            
            if (!question) {
                return;
            }
            
            // Add user message
            addMessage(question, true);
            questionInput.value = '';
            
            // Disable input while processing
            askButton.disabled = true;
            questionInput.disabled = true;
            
            // Add loading indicator
            addLoading();
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                });
                
                removeLoading();
                
                if (!response.ok) {
                    throw new Error('Failed to get response from server');
                }
                
                const data = await response.json();
                
                // Format context info
                let contextInfo = null;
                if (data.context && data.context.length > 0) {
                    const sources = [...new Set(data.context.map(c => c.source))];
                    contextInfo = `📚 Sources: ${sources.join(', ')} (${data.context.length} chunks)`;
                }
                
                addMessage(data.answer, false, contextInfo);
                
            } catch (error) {
                removeLoading();
                showError('Failed to get answer. Please try again.');
                console.error('Error:', error);
            } finally {
                // Re-enable input
                askButton.disabled = false;
                questionInput.disabled = false;
                questionInput.focus();
            }
        }
        
        // Focus input on load
        questionInput.focus();
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve the chat UI
    """
    return HTML_TEMPLATE


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "Retrieval Research Assistant API",
        "version": "1.0.0"
    }


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Answer a question using RAG pipeline
    
    Args:
        request: Question request with the question text
    
    Returns:
        Answer and context used to generate it
    """
    try:
        # Check for Gemini API key
        if not os.getenv("GEMINI_API_KEY"):
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured. Please set GEMINI_API_KEY in .env file"
            )
        
        logger.info(f"Received question: {request.question}")
        
        # Get answer and context from RAG pipeline
        answer, contexts = rag.retrieve_and_answer(request.question)
        
        # Format context for response
        formatted_context = rag.format_context_for_response(contexts)
        
        return AnswerResponse(
            answer=answer,
            context=formatted_context
        )
    
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please check the logs for more information."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

