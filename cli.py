import argparse
import asyncio
import os
from baixador.tasks.download import creat_link, download_link
from baixador.spotify.api import main_spotify

def main():
    parser = argparse.ArgumentParser(description="Baixador de músicas YouTube/Spotify")
    parser.add_argument("link", help="Link do YouTube ou Spotify")
    parser.add_argument("--output", help="Pasta de destino", default=None)
    args = parser.parse_args()

    link = args.link.strip()
    output = args.output or os.getcwd()

    async def process():
        if "youtu.be" in link or "youtube.com" in link:
            await download_link(link, path=output)
        elif "spotify.com" in link:
            musicas = main_spotify(link)
            await creat_link(musicas, path=output)
        else:
            print("Link inválido! Forneça um link do YouTube ou Spotify.")

    asyncio.run(process())

if __name__ == "__main__":
    main()
