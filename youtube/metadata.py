from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
def add_metadata_mp3(file_path, title=None, artist=None, album=None, cover_url=None):
    try:
        audio = MP3(file_path, ID3=EasyID3)
        if title: audio["title"] = title
        if artist: audio["artist"] = artist
        if album: audio["album"] = album
        audio.save()
        if cover_url:
            from mutagen.id3 import ID3, APIC
            audio = ID3(file_path)
            img_data = requests.get(cover_url).content
            audio.add(APIC(mime='image/jpeg', type=3, desc=u'Cover', data=img_data))
            audio.save()
    except Exception as e:
        print(f"Erro ao adicionar metadados MP3: {e}")
import requests
from mutagen.mp4 import MP4, MP4Cover

def add_metadata_m4a(file_path, title=None, artist=None, album=None, cover_url=None):
    try:
        audio = MP4(file_path)
        if title: audio["\xa9nam"] = title
        if artist: audio["\xa9ART"] = artist
        if album: audio["\xa9alb"] = album
        if cover_url:
            img_data = requests.get(cover_url).content
            audio["covr"] = [MP4Cover(img_data, imageformat=MP4Cover.FORMAT_JPEG)]
        audio.save()
    except Exception as e:
        print(f"Erro ao adicionar metadados: {e}")
