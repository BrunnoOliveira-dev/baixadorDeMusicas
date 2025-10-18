# Permite executar este arquivo diretamente (python main.py)
# adicionando a pasta raiz do projeto ao sys.path para suportar imports absolutos.
import os as _os, sys as _sys
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _ROOT not in _sys.path:
    _sys.path.insert(0, _ROOT)

from baixador.spotify.api import main_spotify
from baixador.tasks.download import creat_link, download_link
import os
import logging
import asyncio


async def main(link):
    os.system('cls' if os.name == 'nt' else 'clear')
    logging.info(f'Iniciando download para o link: {link}')
    if not ("youtu.be" in link or "youtube.com" in link or "spotify.com" in link):
        print('Link inválido! Forneça um link do YouTube ou Spotify.')
        return
    if "youtu.be" in link or "youtube.com" in link:
        logging.info('Detectado link do YouTube.')
        await baixar_pelo_youtube(link)
    else:
        logging.info('Detectado link do Spotify.')
        await baixar_pelo_spotify(link)

async def baixar_pelo_youtube(link_youtube):
    logging.info(f'Baixando música do YouTube: {link_youtube}')
    try:
        await download_link(link_youtube)
        logging.info('Download do YouTube finalizado.')
        print('Download do YouTube finalizado!')
    except Exception as e:
        logging.error(f'Erro ao baixar do YouTube: {e}')
        print(f'Erro ao baixar do YouTube: {e}')

async def baixar_pelo_spotify(link_spotify):
    logging.info(f'Baixando músicas da playlist do Spotify: {link_spotify}')
    try:
        musicas = main_spotify(link_spotify)
        qt_musicas = len(musicas)
        logging.info(f'{qt_musicas} músicas encontradas na playlist.')
        print(f'{qt_musicas} músicas encontradas na playlist.')
        for idx, musica in enumerate(musicas, 1):
            print(f'Baixando {idx}/{qt_musicas}: {musica}...')
        await creat_link(musicas)
        logging.info('Download das músicas do Spotify finalizado.')
        print('Download das músicas do Spotify finalizado!')
    except Exception as e:
        logging.error(f'Erro ao baixar do Spotify: {e}')
        print(f'Erro ao baixar do Spotify: {e}')

async def main_loop():
    while True:
        link = input('Digite o link do YouTube ou Spotify: ').strip()
        # link = "https://open.spotify.com/playlist/2vItd0F4ImtvpJ2QHOJsEj?si=cbfdbbe9e83f4b37".strip()
        if not link:
            print('Link não informado. Encerrando.')
            break
        await main(link)  # aqui pode ser sua função que processa o link
        executar_novamente = input('Deseja adicionar mais alguma playlist? [S/n]   ').strip().capitalize()
        if executar_novamente != 'S':
            break
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    asyncio.run(main_loop())
