from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from scripts.rag_handler import RAGHandler
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

MOVIES = [
    "The Social Network",
    "A Quiet Place",
    "Alien III",
    "Black Swan",
    "Big Fish",
    "28 Days Later",
    "Apocalypse Now",
    "Moon",
    "Her",
    "Looper"
]

try:
    logger.debug("Initializing RAG Handler...")
    rag_handler = RAGHandler()
    logger.debug("RAG Handler initialized successfully")
except Exception as e:
    logger.error(f"Error initializing RAG Handler: {str(e)}")
    raise

@app.route('/')
def home():
    return render_template('index.html', movies=MOVIES)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        logger.debug(f"Message received: {user_message}")
        
        logger.debug("Processing message with RAG...")
        response = rag_handler.query(user_message)
        
        if not response or response.strip() == '':
            response = "Sorry, I couldn’t generate a response. Please try rephrasing your question."
            
        logger.debug(f"Response generated: {response}")
        
        return jsonify({
            'message': response
        })
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}", exc_info=True)
        error_message = "There was an error processing your question. Please try again in a few moments."
        return jsonify({
            'message': error_message
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
