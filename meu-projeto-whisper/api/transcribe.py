import yt_dlp
from flask import Flask, request, send_file, jsonify, send_from_directory
import os

# Cria uma pasta temporária localmente (se não existir)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Diretório base do projeto
TEMP_DIR = os.path.join(BASE_DIR, "temp")  # Diretório para arquivos temporários
os.makedirs(TEMP_DIR, exist_ok=True)  # Garante que a pasta exista

app = Flask(__name__, static_folder="../public", static_url_path="", template_folder="../public")

# Função para baixar o áudio do YouTube
def baixar_audio_youtube(url):
    output_path = os.path.join(TEMP_DIR, "audio.mp3")  # Caminho final esperado

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(TEMP_DIR, "audio"),  # Sem extensão no outtmpl
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Verifica se o arquivo foi salvo como .mp3.mp3 e o renomeia se necessário
    audio_temp_path = os.path.join(TEMP_DIR, "audio.mp3.mp3")
    if os.path.exists(audio_temp_path) and not os.path.exists(output_path):
        os.rename(audio_temp_path, output_path)

    # Verifica se o arquivo final foi criado
    if not os.path.exists(output_path):
        raise FileNotFoundError(f"O áudio não baixad corretamente: {output_path}")

    return output_path

# Rota principal para servir a interface HTML
@app.route('/')
def index():
    return send_from_directory(app.template_folder, "index.html")

# Rota para processar a URL e enviar o áudio
@app.route('/api/download_audio', methods=['POST'])
def download_audio():
    try:
        data = request.get_json()
        youtube_url = data.get('url')

        if not youtube_url:
            return jsonify({"error": "URL do YouTube é obrigatória"}), 400

        # Baixar o áudio
        audio_path = baixar_audio_youtube(youtube_url)

        # Enviar o áudio como resposta para download
        return send_file(audio_path, as_attachment=True, download_name='audio.mp3')

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"error": str(e)}), 500

# Necessário para rodar localmente
if __name__ == "__main__":
    app.run(debug=True)
