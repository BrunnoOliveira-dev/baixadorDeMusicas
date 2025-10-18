import re
def sanitize_filename(name):
    """Remove caracteres inválidos para Windows"""
    return re.sub(r'[\\/*?:"<>|]', '', name)
import os
import re
from typing import List, Tuple
from dotenv import load_dotenv, set_key
import requests
import subprocess
import shutil

def extract_spotify_id(url: str) -> str:
    """Extrai o último segmento do path, removendo querystring e fragment."""
    # Remove query e fragmento
    url = url.split('?', 1)[0].split('#', 1)[0]
    partes = [p for p in url.split('/') if p]
    return partes[-1] if partes else url

def extrair_id_playlist(url):
    # Compatibilidade retro: delega para a função genérica
    return extract_spotify_id(url)

def get_spotify_credentials():
    load_dotenv(dotenv_path=".env")
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")
    while not client_id or not client_secret:
        print("Credenciais do Spotify não encontradas ou inválidas.")
        client_id = input("Digite o Client ID do Spotify: ").strip()
        client_secret = input("Digite o Client Secret do Spotify: ").strip()
        redirect_uri = input(f"Digite o Redirect URI do Spotify [{redirect_uri}]: ").strip() or redirect_uri
        set_key(".env", "SPOTIFY_CLIENT_ID", client_id)
        set_key(".env", "SPOTIFY_CLIENT_SECRET", client_secret)
        set_key(".env", "SPOTIFY_REDIRECT_URI", redirect_uri)
    return client_id, client_secret, redirect_uri

def get_musicas_playlist(sp, playlist_id):
    offset = 0
    tracks = []
    while True:
        results = sp.playlist_items(playlist_id, limit=50, offset=offset)
        tracks.extend(results['items'])
        if results['next'] is not None:
            offset += 50
        else:
            break
    return tracks

# ----------------- Fallback sem credenciais (oEmbed) -----------------

def has_spotify_credentials() -> bool:
    load_dotenv(dotenv_path=".env")
    return bool(os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET"))

def is_spotify_track(url: str) -> bool:
    return "open.spotify.com/track" in url or "/track/" in url

def is_spotify_playlist(url: str) -> bool:
    return "open.spotify.com/playlist" in url or "/playlist/" in url

def is_spotify_album(url: str) -> bool:
    return "open.spotify.com/album" in url or "/album/" in url

def _spotify_oembed(url: str) -> dict:
    """Busca metadados básicos de uma URL pública do Spotify usando oEmbed (sem auth)."""
    resp = requests.get("https://open.spotify.com/oembed", params={"url": url}, timeout=10)
    resp.raise_for_status()
    return resp.json()

def get_track_from_oembed(url: str) -> List[Tuple[str, str]]:
    """Retorna uma lista com um item: ("Titulo - Artista", cover_url) usando oEmbed.
    Não requer client_id/secret. Funciona para links de track. Para playlists/albums, oEmbed
    não retorna a lista de faixas.
    """
    data = _spotify_oembed(url)
    title = data.get("title") or ""
    author = data.get("author_name") or ""
    thumb = data.get("thumbnail_url")
    query = f"{title} - {author}".strip(" -")
    return [(query, thumb)]

def sanitize_filename(name):
    """Remove caracteres inválidos para Windows"""
    return re.sub(r'[\\/*?:"<>|]', '', name)

def download_playlist_with_spotdl(link: str, output_dir: str | None = None) -> None:
    """Tenta baixar uma playlist do Spotify usando o spotdl (sem precisar de credenciais no seu código).
    Requer que o utilitário `spotdl` esteja instalado no mesmo Python/ambiente.
    """
    if shutil.which("spotdl") is None:
        raise RuntimeError(
            "spotdl não encontrado no PATH. Instale com `pip install spotdl` ou configure credenciais do Spotify."
        )
    out = output_dir or os.getcwd()
    cmd = ["spotdl", "download", link, "--output", out]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Falha ao executar spotdl: {e}")
