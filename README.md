# Movies Chatbot

Chatbot que responde preguntas sobre películas usando sus guiones. Utiliza RAG (Retrieval-Augmented Generation) para proporcionar respuestas contextualizadas.

## Películas Disponibles
- The Social Network
- A Quiet Place
- Alien III
- Black Swan
- Big Fish
- 28 Days Later
- Apocalypse Now
- Moon
- Her
- Looper

## Archivos

Los archivos process_scripts.py y download_scripts.py ya se corrieron obteniendo sus resultados correspondientes.

## Instalación

1. Crear entorno virtual e instalar dependencias:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Ejecutar la aplicación:
```bash
python app.py
```

3. Abrir en el navegador:
```
http://localhost:5000
```

## Tecnologías
- Flask
- ChromaDB
- LangChain