#!/usr/bin/env python3
"""
CLI Privado de Descargas - YouTube/yt-dlp
Automatiza descargas de videos/audio desde YouTube de forma segura y local.

Seguridad: Todo ejecuta en la VM local. Sin cookies, sin proxies, sin datos personales enviados.
"""

from pathlib import Path
import argparse
import random
import time
import sys

# Importar yt-dlp con manejo de error
try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("Error: la librería 'yt-dlp' no está instalada.")
    print("Instálala con: pip install -r requirements.txt")
    sys.exit(1)


def crear_directorio(path: Path):
    """Crea directorio recursivamente si no existe."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def opciones_ydl(formato: str, outtmpl: str):
    """
    Retorna configuración de yt-dlp según formato solicitado.
    
    Args:
        formato: 'mp3' o 'video'
        outtmpl: Template de salida (ruta + nombre del archivo)
    
    Returns:
        dict: Opciones de yt-dlp con postprocesadores configurados
    """
    if formato == 'mp3':
        # MP3: extrae audio del mejor stream disponible y convierte a MP3 320kbps
        return {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }

    # Video: descarga mejor video + audio (MP4 H.264 + AAC)
    return {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': outtmpl,
    }


def descargar_url(url: str, ydl_opts: dict):
    """
    Descarga una URL con reintentos y backoff exponencial.
    
    Args:
        url: URL de YouTube a descargar
        ydl_opts: Diccionario de opciones yt-dlp
    
    Returns:
        bool: True si descarga exitosa, False si falla tras reintentos
    """
    print(f"Iniciando descarga: {url}")
    
    # Leer número de reintentos (sin mutar el dict original)
    max_retries = ydl_opts.get('_retries', 1)
    backoff = 1
    
    # Ciclo de reintentos con backoff exponencial (1, 2, 4, 8... segundos)
    for attempt in range(1, max_retries + 1):
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"✓ Descarga completada: {url}")
            return True
        except Exception as e:
            print(f"⚠ Intento {attempt}/{max_retries} fallido para {url}")
            print(f"  Razón: {str(e)[:100]}")  # Mostrar primeros 100 caracteres del error
            
            if attempt == max_retries:
                print(f"✗ Error descargando {url} (máx reintentos alcanzados)")
                return False
            
            # Esperar antes de reintentar (backoff exponencial)
            time.sleep(backoff)
            backoff *= 2


def leer_urls_desde_archivo(ruta: Path):
    """
    Lee URLs desde archivo de texto (una por línea).
    Ignora líneas en blanco y espacios en blanco.
    
    Args:
        ruta: Path al archivo .txt
    
    Returns:
        list: Lista de URLs limpias, o None si error
    """
    try:
        with ruta.open('r', encoding='utf-8') as f:
            # Filtrar líneas en blanco y limpiar espacios
            lines = [line.strip() for line in f if line.strip()]
        
        if not lines:
            print(f"⚠ Advertencia: archivo '{ruta}' está vacío")
            return []
        
        print(f"✓ Leyendo {len(lines)} URL(s) desde {ruta}")
        return lines
    except FileNotFoundError:
        print(f"✗ Error: archivo '{ruta}' no encontrado")
        return None
    except Exception as e:
        print(f"✗ Error leyendo archivo '{ruta}': {e}")
        return None


def main():
    """
    Función principal: parsea argumentos CLI y ejecuta descargas.
    
    Argumentos:
        -u/--url: URL única (mutuamente exclusivo con --archivo)
        -a/--archivo: Archivo con URLs (mutuamente exclusivo con --url)
        -f/--formato: mp3 o video (default: mp3)
        --allow-playlist: Permitir playlists (default: evitarlas)
        --user-agent: Custom User-Agent (default: yt-dlp default)
        --retries: Número de reintentos (default: 3)
    """
    parser = argparse.ArgumentParser(
        description='CLI privado de descargas con yt-dlp',
        epilog='Uso: python3 main.py --url "https://..." o python3 main.py --archivo urls.txt'
    )
    
    # Grupo mutuamente exclusivo: URL o archivo
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--archivo', type=str, 
                       help='Archivo .txt con URLs (una por línea)')
    group.add_argument('-u', '--url', type=str, 
                       help='URL única de YouTube')
    
    # Opciones globales
    parser.add_argument('-f', '--formato', choices=['mp3', 'video'], 
                        default='mp3', 
                        help='Formato de salida (default: mp3)')
    parser.add_argument('--allow-playlist', action='store_true', 
                        help='Permitir descargar playlists (default: evitar)')
    parser.add_argument('--user-agent', type=str, 
                        help='User-Agent HTTP personalizado')
    parser.add_argument('--retries', type=int, default=3, 
                        help='Número de reintentos por URL (default: 3)')

    args = parser.parse_args()

    # Crear directorio de descargas
    descargas_dir = Path('descargas')
    crear_directorio(descargas_dir)
    outtmpl = str(descargas_dir / '%(title)s.%(ext)s')

    # Construir configuración de yt-dlp
    ydl_opts = opciones_ydl(args.formato, outtmpl)
    
    # Evitar playlists por defecto (protección contra descargas masivas accidentales)
    if not args.allow_playlist:
        ydl_opts['noplaylist'] = True
    
    # Añadir User-Agent personalizado si se solicita
    if args.user_agent:
        ydl_opts.setdefault('http_headers', {})
        ydl_opts['http_headers']['User-Agent'] = args.user_agent
    
    # Configurar reintentos
    ydl_opts['_retries'] = max(1, int(args.retries))
    
    # Configuración general de yt-dlp
    ydl_opts.setdefault('quiet', False)
    ydl_opts.setdefault('no_warnings', True)

    print(f"Formato: {args.formato} | Reintentos: {ydl_opts['_retries']}")
    print("-" * 60)

    # Modo 1: URL única
    if args.url:
        descargar_url(args.url, ydl_opts)
        return

    # Modo 2: Archivo con múltiples URLs
    ruta = Path(args.archivo)
    urls = leer_urls_desde_archivo(ruta)
    
    if urls is None:
        sys.exit(1)
    
    if not urls:
        print("⚠ No hay URLs para procesar")
        sys.exit(0)

    # Procesar cada URL con pausas anti-ban
    total = len(urls)
    print(f"\nProcesando {total} URL(s)...\n")
    
    for index, url in enumerate(urls, 1):
        print(f"[{index}/{total}]", end=" ")
        success = descargar_url(url, ydl_opts)
        
        # Pausa aleatoria entre descargas (anti-ban de YouTube)
        if success and index < total:
            pausa = random.randint(10, 25)
            print(f"Esperando {pausa}s antes de la siguiente descarga...\n")
            time.sleep(pausa)
    
    print("-" * 60)
    print("✓ Procesamiento completado")


if __name__ == '__main__':
    main()
