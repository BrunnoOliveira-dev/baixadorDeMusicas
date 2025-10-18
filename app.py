from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
import threading
import asyncio
import os
import shutil
import uuid
from .spotify.api import main_spotify
from .tasks.download import creat_link, download_link

app = Flask(__name__)
app.secret_key = "sua_chave_super_secreta"

# Diretório base para downloads temporários e zips
DOWNLOAD_ROOT = os.path.join(app.root_path, "downloads")
os.makedirs(DOWNLOAD_ROOT, exist_ok=True)

# Status global simples (para um download por vez). Para múltiplos simultâneos, ideal seria por ID de sessão.
download_status = {"status": "idle", "message": "", "download_url": None, "request_id": None}


async def _baixar_musica_coro(link: str, req_id: str, target_dir: str) -> None:
    download_status.update({
        "status": "in-progress",
        "message": "Download iniciado...",
        "download_url": None,
        "request_id": req_id,
    })
    try:
        if "youtu.be" in link or "youtube.com" in link:
            await download_link(link, path=target_dir)
        elif "spotify.com" in link:
            # Para playlists sem credenciais, o download pode ser feito diretamente via spotdl
            musicas = main_spotify(link, output_dir=target_dir)
            # Se playlist sem credenciais usar spotdl, main_spotify pode retornar []
            if musicas:
                await creat_link(musicas, path=target_dir)

        # Compacta a pasta alvo em um ZIP
        zip_base = os.path.join(DOWNLOAD_ROOT, req_id)
        # shutil.make_archive adiciona .zip automaticamente quando base_name é sem extensão
        archive_path = shutil.make_archive(zip_base, 'zip', target_dir)
        # Monta URL relativa para evitar necessidade de app context nesta thread
        download_url = f"/download/{req_id}"
        download_status.update({
            "status": "success",
            "message": "Download finalizado com sucesso! Clique para baixar o ZIP.",
            "download_url": download_url,
        })
        # Limpa a pasta de arquivos individuais (mantém apenas o zip)
        try:
            shutil.rmtree(target_dir, ignore_errors=True)
        except Exception:
            pass
    except Exception as e:
        download_status.update({"status": "error", "message": f"Erro: {e}", "download_url": None})


def baixar_musica(link: str) -> None:
    """Wrapper síncrono para rodar a rotina assíncrona em uma thread."""
    # Cria diretório temporário por requisição
    req_id = uuid.uuid4().hex
    target_dir = os.path.join(DOWNLOAD_ROOT, req_id, "files")
    os.makedirs(target_dir, exist_ok=True)
    asyncio.run(_baixar_musica_coro(link, req_id, target_dir))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        link = request.form.get("link", "").strip()
        if link:
            threading.Thread(target=baixar_musica, args=(link,), daemon=True).start()
        return redirect(url_for("index"))
    return render_template("index.html")

# Rota que retorna o status do download
@app.route("/progress")
def progress():
    return jsonify(download_status)

# Rota para baixar o ZIP gerado
@app.route("/download/<req_id>")
def download_zip(req_id: str):
    zip_path = os.path.join(DOWNLOAD_ROOT, f"{req_id}.zip")
    if not os.path.exists(zip_path):
        return jsonify({"error": "Arquivo não encontrado."}), 404
    # Nome amigável do arquivo baixado
    filename = f"musicas_{req_id}.zip"
    return send_file(zip_path, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8085, debug=True)