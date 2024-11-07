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
    logger.debug("Inicializando RAG Handler...")
    rag_handler = RAGHandler()
    logger.debug("RAG Handler inicializado correctamente")
except Exception as e:
    logger.error(f"Error al inicializar RAG Handler: {str(e)}")
    raise

@app.route('/')
def home():
    return render_template('index.html', movies=MOVIES)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get('message', '')
        logger.debug(f"Mensaje recibido: {user_message}")
        
        logger.debug("Procesando mensaje con RAG...")
        response = rag_handler.query(user_message)
        
        if not response or response.strip() == '':
            response = "Lo siento, no pude generar una respuesta. Por favor, intenta reformular tu pregunta."
            
        logger.debug(f"Respuesta generada: {response}")
        
        return jsonify({
            'message': response
        })
    except Exception as e:
        logger.error(f"Error en chat: {str(e)}", exc_info=True)
        error_message = "Hubo un error procesando tu pregunta. Por favor, intenta de nuevo en unos momentos."
        return jsonify({
            'message': error_message
        }), 500

if __name__ == '__main__':
    app.run(debug=True)