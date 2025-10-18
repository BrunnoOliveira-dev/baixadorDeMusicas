import asyncio
import yt_dlp
from .metadata import add_metadata_m4a
from ..spotify.utils import sanitize_filename
import os

def get_musicas_path():
    pasta = "C:/Users/bo272/Music/musicas"
    os.makedirs(pasta, exist_ok=True)
    return pasta

async def get_link_from_youtube(song_name):
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}
    loop = asyncio.get_running_loop()
    info = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).extract_info(f"ytsearch1:{song_name}", download=False))
    if 'entries' in info and info['entries']:
        return info['entries'][0]['webpage_url']
    return None

async def download_link(link, path=None):
    if path is None:
        path = get_musicas_path()
    os.makedirs(path, exist_ok=True)
    loop = asyncio.get_running_loop()
    def ydl_download():
        ydl_opts_info = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            return ydl.extract_info(link, download=False)
    info = await loop.run_in_executor(None, ydl_download)
    title_raw = info.get('title', 'audio')
    title = sanitize_filename(title_raw)
    ydl_opts_download = {
        'format': 'bestaudio/best',
        'outtmpl': f'{path}/{title}.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'youtube_include_dash_manifest': False,
        'source_address': '0.0.0.0',
        'force_generic_extractor': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
            'preferredquality': '128',
        }],
        'http_headers': {'User-Agent': 'Mozilla/5.0'},
    }
    def ydl_download_file():
        with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
            return ydl.extract_info(link, download=True)
    info = await loop.run_in_executor(None, ydl_download_file)
    if info:
        artist = info.get('uploader', None)
        album = info.get('album', None)
        ext = 'm4a'
        file_path = os.path.join(path, f"{title}.{ext}")
        cover_url = f"https://img.youtube.com/vi/{info.get('id')}/maxresdefault.jpg" if info.get('id') else None
        await loop.run_in_executor(None, lambda: add_metadata_m4a(file_path, title, artist, album, cover_url))
        print(f"Baixado: {title}")
