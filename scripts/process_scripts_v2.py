import os
import json
import chromadb
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re
import time
import shutil

class ScriptProcessorV2:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db_v2")
        self.collection = self.chroma_client.get_or_create_collection(
            name="movie_scripts",
            metadata={"hnsw:space": "cosine"}
        )
        
        if not os.path.exists('movie_scripts_v2'):
            os.makedirs('movie_scripts_v2')

    #Antes no limpiamos los scripts ahora si lo hacemos
    def clean_text(self, text):
        """Limpia y preprocesa el texto del guión"""
        soup = BeautifulSoup(text, 'html.parser')
        text = soup.get_text()

        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\)', '', text)
        text = re.sub(r'<.*?>', '', text)
        
        text = re.sub(r'\s+', ' ', text)
        
        text = re.sub(r'^\d+\.?\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'(CONTINUED:|CONTINUED:)', '', text)
        
        text = re.sub(r'(CUT TO:|DISSOLVE TO:|FADE OUT:|FADE IN:|INT\.|EXT\.)', '', text)
        
        text = text.strip()
        
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text

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
        original_path = os.path.join('movie_scripts', filename)
        with open(original_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Limpiando texto de {filename}...")
        cleaned_content = self.clean_text(content)
        
        clean_filename = os.path.join('movie_scripts_v2', filename)
        with open(clean_filename, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        
        chunks = text_splitter.create_documents([cleaned_content])
        movie_name = filename.replace('.txt', '').replace('_', ' ').title()
        
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
        scripts = [f for f in os.listdir('movie_scripts') if f.endswith(".txt")]
        
        print(f"Encontrados {len(scripts)} guiones para procesar")
        print("Los scripts limpios se guardarán en 'movie_scripts_v2'")
        print("Los vectores se guardarán en 'chroma_db_v2'")
        print("\nIniciando procesamiento...\n")
        
        for filename in scripts:
            self.process_script(filename)
            print(f"Completado: {filename}\n")

if __name__ == "__main__":
    if os.path.exists('chroma_db_v2'):
        response = input("La carpeta chroma_db_v2 ya existe. ¿Desea eliminarla y empezar de nuevo? (s/n): ")
        if response.lower() == 's':
            shutil.rmtree('chroma_db_v2')
        else:
            print("Proceso cancelado")
            exit()
    
    print("Iniciando procesamiento de guiones versión 2...")
    processor = ScriptProcessorV2()
    processor.process_all_scripts()
    print("\n¡Procesamiento completado!")
    print("Puede encontrar:")
    print("- Scripts limpios en: movie_scripts_v2/")
    print("- Base de datos vectorial en: chroma_db_v2/")