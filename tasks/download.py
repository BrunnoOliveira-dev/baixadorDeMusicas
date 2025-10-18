import asyncio
from ..youtube.api import get_link_from_youtube, download_link

async def process_song_parallel(song_name, path=None):
    link = await get_link_from_youtube(song_name)
    if link:
        await download_link(link, path)
    else:
        print(f"Não encontrou link para: {song_name}")

async def creat_link(musicas, path=None, max_concurrent=20):
    sema = asyncio.Semaphore(max_concurrent)
    tasks = []
    for song in musicas:
        song_name = song[0] if isinstance(song, tuple) else song
        async def task_wrapper(name):
            async with sema:
                await process_song_parallel(name, path)
        tasks.append(asyncio.create_task(task_wrapper(song_name)))
    await asyncio.gather(*tasks, return_exceptions=True)
