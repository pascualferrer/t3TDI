import chromadb
import requests
import logging
import json

logger = logging.getLogger(__name__)

class RAGHandler:
    def __init__(self):
        logger.debug("Iniciando conexión con ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db_v2")
        self.collection = self.chroma_client.get_collection("movie_scripts")
        logger.debug("Conexión con ChromaDB establecida")
        
    def get_embedding(self, text):
        """Obtener embedding para la consulta"""
        try:
            response = requests.post(
                'http://tormenta.ing.puc.cl/api/embed',
                json={
                    "model": "nomic-embed-text",
                    "input": text
                },
                timeout=120
            )
            response.raise_for_status()
            return response.json()['embeddings'][0]
        except Exception as e:
            logger.error(f"Error al obtener embedding: {str(e)}")
            raise
    
    def truncate_context(self, context):
        """Limitar el contexto a 500 caracteres"""
        return context[:500] if len(context) > 500 else context

    def get_llm_response(self, query, context):
        """Obtener respuesta del LLM con configuración mínima"""
        try:
            context = self.truncate_context(context)
            prompt = f"Q: {query}\nContext: {context}\nA:"
            
            for attempt in range(3):
                try:
                    response = requests.post(
                        'http://tormenta.ing.puc.cl/api/generate',
                        json={
                            "model": "integra-LLM",
                            "prompt": prompt,
                            "stream": False,
                            "temperature": 0.3,
                            "max_tokens": 50
                        },
                        timeout=240
                    )
                    
                    if response.status_code == 200:
                        return response.json().get('response', '')
                    
                except requests.Timeout:
                    context = context[:250]  # Reduce contexto a la mitad
                    prompt = f"Q: {query}\nContext: {context}\nA:"
                    continue
                    
            return "Lo siento, el servidor está ocupado. Por favor, intenta de nuevo."
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return "Error de conexión. Por favor, intenta de nuevo."
    
    def query(self, user_query):
        try:
            query_embedding = self.get_embedding(user_query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=1
            )
            
            context = results['documents'][0][0]
            
            response = self.get_llm_response(user_query, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error en query: {str(e)}")
            return f"Error: {str(e)}"