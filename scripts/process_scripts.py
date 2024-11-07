import os
import json
import chromadb
from chromadb.utils import embedding_functions
import requests
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
import time

class ScriptProcessor:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="movie_scripts",
            metadata={"hnsw:space": "cosine"}
        )

    def get_embeddings_batch(self, texts, max_retries=3):
        """Obtener embeddings en lote con reintentos"""
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    'http://tormenta.ing.puc.cl/api/embed',
                    json={
                        "model": "nomic-embed-text",
                        "input": texts
                    }
                )
                return response.json()['embeddings']
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Error final al obtener embeddings: {e}")
                    return None
                print(f"Error al obtener embeddings (intento {attempt + 1}): {e}")
                time.sleep(1)

    def process_script(self, filename):
        """Procesar un guion individual"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        
        chunks = text_splitter.create_documents([content])
        movie_name = os.path.basename(filename).replace('.txt', '').replace('_', ' ').title()
        
        print(f"\nProcesando {movie_name}...")
        
        BATCH_SIZE = 10
        for i in range(0, len(chunks), BATCH_SIZE):
            batch_chunks = chunks[i:i + BATCH_SIZE]
            texts = [chunk.page_content for chunk in batch_chunks]
            
            embeddings = self.get_embeddings_batch(texts)
            
            if embeddings:
                ids = [f"{movie_name.lower().replace(' ', '_')}_{j}" for j in range(i, i + len(batch_chunks))]
                metadatas = [{"movie": movie_name, "chunk_id": j} for j in range(i, i + len(batch_chunks))]
                
                self.collection.add(
                    documents=texts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
            
            print(f"Procesado lote {i//BATCH_SIZE + 1}/{(len(chunks)-1)//BATCH_SIZE + 1}")
            time.sleep(0.5)
            
    def process_all_scripts(self):
        """Procesar todos los guiones en el directorio movie_scripts"""
        script_dir = "movie_scripts"
        scripts = [f for f in os.listdir(script_dir) if f.endswith(".txt")]
        
        print(f"Encontrados {len(scripts)} guiones para procesar")
        
        for filename in scripts:
            self.process_script(os.path.join(script_dir, filename))
            print(f"Completado: {filename}\n")

if __name__ == "__main__":
    print("Iniciando procesamiento de guiones...")
    processor = ScriptProcessor()
    processor.process_all_scripts()
    print("\n¡Procesamiento completado!")