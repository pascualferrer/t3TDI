import requests
from bs4 import BeautifulSoup
import os
import time

def download_script(url, movie_name):
    """
    Descarga el guion de una película desde IMSDB
    """
    try:
        if not os.path.exists('movie_scripts'):
            os.makedirs('movie_scripts')
        
        filename = f"movie_scripts/{movie_name.replace(' ', '_').lower()}.txt"
        if os.path.exists(filename):
            print(f"El guion de {movie_name} ya existe, saltando descarga...")
            return True
            
        print(f"Descargando {movie_name}...")
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        script_content = soup.find('pre')
        
        if script_content:
            script_text = script_content.get_text()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(script_text)
            
            print(f"✓ Guion de {movie_name} descargado exitosamente.")
            return True
        else:
            print(f"✗ No se pudo encontrar el contenido del guion para {movie_name}")
            return False
            
    except Exception as e:
        print(f"✗ Error descargando {movie_name}: {str(e)}")
        return False

movies = [
    {"name": "The Social Network", "url": "https://imsdb.com/scripts/Social-Network,-The.html"},
    {"name": "A quiet place", "url": "https://imsdb.com/scripts/A-Quiet-Place.html"},
    {"name": "Alien III", "url": "https://imsdb.com/scripts/Alien-3.html"},
    {"name": "Black Swan", "url": "https://imsdb.com/scripts/Black-Swan.html"},
    {"name": "Big Fish", "url": "https://imsdb.com/scripts/Big-Fish.html"},
    {"name": "28 Days Later", "url": "https://imsdb.com/scripts/28-Days-Later.html"},
    {"name": "Apocalypse Now", "url": "https://imsdb.com/scripts/Apocalypse-Now.html"},
    {"name": "Moon", "url": "https://imsdb.com/scripts/Moon.html"},
    {"name": "Her", "url": "https://imsdb.com/scripts/Her.html"},
    {"name": "Looper", "url": "https://imsdb.com/scripts/Looper.html"}
]

if __name__ == "__main__":
    successful_downloads = 0
    
    for movie in movies:
        if download_script(movie["url"], movie["name"]):
            successful_downloads += 1
        time.sleep(1)
    
    print(f"\nDescarga completada: {successful_downloads}/{len(movies)} guiones descargados exitosamente.")