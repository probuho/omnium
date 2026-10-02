import sys
import os
import yt_dlp

def download_video(url):
    """
    Downloads a video from the given URL using yt-dlp,
    authenticating with a cookies.txt file.
    """
    # Create downloads directory in D:\Vídeo
    download_folder = r'D:\Vídeo'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Define the path to the cookies file
    cookies_file = 'cookies.txt'

    # Check if the cookies file exists
    if not os.path.exists(cookies_file):
        print(f"[-] Error: El archivo '{cookies_file}' no se encuentra.")
        print(f"[-] Por favor, asegúrate de exportar las cookies y guardarlas en ese archivo.")
        sys.exit(1)

    # yt-dlp options
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',  # Download best video and best audio, or best single file
        'outtmpl': os.path.join(download_folder, '%(playlist_index)s - %(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': False,
        'no_warnings': True,
        'cookiefile': cookies_file,
        'overwrites': True,
        'ffmpeg_location': os.path.dirname(os.path.abspath(__file__)), # Use ffmpeg from script directory
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    try:
        print(f"[*] Usando el archivo de cookies: {cookies_file}")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"[*] Usando ffmpeg en: {script_dir}")
        print(f"[*] Iniciando descarga desde: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\n[+] Descarga completada con éxito.")
        print(f"[*] El video se ha guardado en la carpeta '{download_folder}'.")

    except Exception as e:
        print(f"\n[-] Ocurrió un error durante la descarga.")
        print(f"[-] Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Prompt the user for the video URL
    video_url = input("Por favor, introduce la URL del video y presiona Enter: ")

    # Check if the URL is empty
    if not video_url.strip():
        print("[-] No se ha introducido ninguna URL. Saliendo.")
        sys.exit(1)

    # Start the download
    download_video(video_url.strip())
