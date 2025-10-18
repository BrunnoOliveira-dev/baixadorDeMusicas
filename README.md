# Baixador de Música (YouTube / Spotify)

Baixe músicas do YouTube e Spotify via linha de comando ou interface web.

## Requisitos

1. **Python 3.10+**
2. **FFmpeg** (necessário para conversão de áudio)
   - Windows: Baixe em https://www.gyan.dev/ffmpeg/builds/ e adicione ao PATH
3. **Dependências Python**:
   ```powershell
   pip install flask yt-dlp mutagen spotipy python-dotenv requests
   ```

## Como executar

### Opção 1: Interface Web

1. Abra o PowerShell na pasta **pai** que contém a pasta `baixador`:

2. Execute o servidor:
   ```powershell
   python -m baixador.app
   ```

3. Acesse no navegador:
   ```
   http://localhost:8085
   ```

4. Cole o link do YouTube ou Spotify e aguarde. Quando terminar, clique no botão para baixar o ZIP com as músicas.

### Opção 2: Linha de Comando (CLI)

Na mesma pasta pai:
```powershell
python -m baixador.cli "https://youtu.be/..." --output "C:\Users\...\Music"
```

Exemplos:
```powershell
# YouTube
python -m baixador.cli "https://youtu.be/dQw4w9WgXcQ"

# Spotify (playlist)
python -m baixador.cli "https://open.spotify.com/playlist/..."
```

## Configuração Spotify (Opcional)

Para usar playlists privadas do Spotify, crie um arquivo `.env` na raiz do projeto:
```
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

Obtenha as credenciais em: https://developer.spotify.com/dashboard

> Se não configurar, o app tenta baixar via `spotdl` (instale com `pip install spotdl`).

## Pronto!

Agora você pode baixar músicas colando links do YouTube ou Spotify.
