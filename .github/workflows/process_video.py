import os
import sys
import json
import requests
import tempfile
import subprocess
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# Obter dados do evento
event_data = json.loads(os.environ.get('GITHUB_EVENT_PATH', '{}'))
client_payload = event_data.get('client_payload', {})

video_id = client_payload.get('video_id')
video_url = client_payload.get('video_url')
video_title = client_payload.get('title', 'video')

if not video_id or not video_url:
    print("Dados de vídeo incompletos")
    sys.exit(1)

# Baixar o vídeo
temp_dir = tempfile.mkdtemp()
input_path = os.path.join(temp_dir, f"{video_id}_original.mp4")

response = requests.get(video_url)
with open(input_path, 'wb') as f:
    f.write(response.content)

# Processar para diferentes formatos
formats = {
    'vertical': {'ratio': '9:16', 'resolution': '1080x1920'},
    'horizontal': {'ratio': '16:9', 'resolution': '1920x1080'},
    'square': {'ratio': '1:1', 'resolution': '1080x1080'}
}

processed_versions = {}

for format_name, format_data in formats.items():
    output_path = os.path.join(temp_dir, f"{video_id}_{format_name}.mp4")
    thumbnail_path = os.path.join(temp_dir, f"{video_id}_{format_name}_thumb.jpg")
    
    # Processar vídeo com FFmpeg
    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-vf', f"scale={format_data['resolution'].split('x')[0]}:{format_data['resolution'].split('x')[1]}:force_original_aspect_ratio=decrease,pad={format_data['resolution'].replace('x', ':')}:(ow-iw)/2:(oh-ih)/2",
        '-c:v', 'libx264', '-crf', '23', '-preset', 'medium',
        '-c:a', 'aac', '-b:a', '128k',
        output_path
    ])
    
    # Gerar thumbnail
    subprocess.run([
        'ffmpeg', '-i', output_path,
        '-ss', '00:00:01', '-vframes', '1',
        thumbnail_path
    ])
    
    # Fazer upload para o Cloudinary
    video_result = cloudinary.uploader.upload(
        output_path,
        resource_type="video",
        public_id=f"startpost/{video_id}/{format_name}",
        overwrite=True
    )
    
    thumbnail_result = cloudinary.uploader.upload(
        thumbnail_path,
        public_id=f"startpost/{video_id}/{format_name}_thumb",
        overwrite=True
    )
    
    processed_versions[format_name] = {
        'format': format_name,
        'url': video_result['secure_url'],
        'thumbnail_url': thumbnail_result['secure_url']
    }

# Notificar o backend sobre a conclusão do processamento
pythonanywhere_url = os.environ.get('PYTHONANYWHERE_API_URL')
webhook_url = f"{pythonanywhere_url}/api/webhook/process-complete"

response = requests.post(
    webhook_url,
    json={
        'video_id': video_id,
        'versions': list(processed_versions.values())
    }
)

if response.status_code == 200:
    print("Processamento concluído e backend notificado com sucesso!")
else:
    print(f"Erro ao notificar backend: {response.status_code}")
    print(response.text)
