import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .utils import (
    extrair_id_playlist,
    extract_spotify_id,
    get_spotify_credentials,
    get_musicas_playlist,
    has_spotify_credentials,
    is_spotify_track,
    is_spotify_playlist,
    get_track_from_oembed,
    download_playlist_with_spotdl,
)

def main_spotify(link, output_dir: str | None = None):
    # Sem credenciais: usar oEmbed para track ou spotdl para playlist
    if not has_spotify_credentials():
        if is_spotify_track(link):
            return get_track_from_oembed(link)
        # Playlist/álbum sem credenciais: tentar usar spotdl diretamente (baixa os arquivos)
        download_playlist_with_spotdl(link, output_dir=output_dir)
        # Retornar lista vazia sinaliza que o download já foi feito externamente
        return []

    # Com credenciais: usar API oficial
    # Se for track, buscar metadados da faixa
    if is_spotify_track(link):
        track_id = extract_spotify_id(link)
        while True:
            client_id, client_secret, redirect_uri = get_spotify_credentials()
            try:
                sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope='user-library-read'))
                break
            except Exception as e:
                print(f"Erro de autenticação Spotify: {e}\nVerifique e insira novamente suas credenciais.")
        try:
            tr = sp.track(track_id)
            track_name = tr['name']
            artists = ', '.join([a['name'] for a in tr['artists']])
            images = tr.get('album', {}).get('images', [])
            cover_url = images[0]['url'] if images else None
            return [(f"{track_name} - {artists}", cover_url)]
        except Exception:
            # Fallback último caso
            return get_track_from_oembed(link)

    # Caso contrário, tratar como playlist (ou álbum via spotdl fallback)
    id = extrair_id_playlist(link)
    playlist_id = f"{id}"
    while True:
        client_id, client_secret, redirect_uri = get_spotify_credentials()
        try:
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope='user-library-read'))
            break
        except Exception as e:
            print(f"Erro de autenticação Spotify: {e}\nVerifique e insira novamente suas credenciais.")
    musicas = []
    try:
        playlist = get_musicas_playlist(sp, playlist_id)
    except Exception:
        # Fallback: usar spotdl quando a playlist não puder ser lida (privada/404)
        download_playlist_with_spotdl(link, output_dir=output_dir)
        return []
    for track in playlist:
        track_name = track['track']['name']
        artists = [artist['name'] for artist in track['track']['artists']]
        artist_names = ', '.join(artists)
        images = track['track'].get('album', {}).get('images', [])
        cover_url = images[0]['url'] if images else None
        musicas.append((f"{track_name} - {artist_names}", cover_url))
    return musicas
