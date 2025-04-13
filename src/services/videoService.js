// Arquivo para integrar o frontend com o backend híbrido
const apiBaseUrl = 'https://josdev1215.pythonanywhere.com';

// Função para fazer upload de vídeo
async function uploadVideo(file, title, description)  {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('description', description);
    
    const response = await fetch(`${apiBaseUrl}/videos`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`Erro na API: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Erro ao fazer upload de vídeo:', error);
    throw error;
  }
}

// Função para verificar status de processamento de vídeo
async function checkVideoStatus(videoId) {
  try {
    const response = await fetch(`${apiBaseUrl}/videos/${videoId}`, {
      method: 'GET',
    });
    
    if (!response.ok) {
      throw new Error(`Erro na API: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Erro ao verificar status do vídeo:', error);
    throw error;
  }
}

// Função para otimizar SEO
async function optimizeSEO(content, platform, keywords = []) {
  try {
    const response = await fetch(`${apiBaseUrl}/seo/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        content,
        platform,
        keywords,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Erro na API: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Erro ao otimizar SEO:', error);
    throw error;
  }
}

// Função para verificar periodicamente o status do processamento
function pollProcessingStatus(videoId, onUpdate, interval = 5000) {
  const checkInterval = setInterval(async () => {
    try {
      const result = await checkVideoStatus(videoId);
      onUpdate(result);
      
      if (result.video.status === 'processed') {
        clearInterval(checkInterval);
      }
    } catch (error) {
      console.error('Erro ao verificar status:', error);
    }
  }, interval);
  
  return {
    stop: () => clearInterval(checkInterval)
  };
}

// Exportar funções para uso no frontend
export default {
  uploadVideo,
  checkVideoStatus,
  optimizeSEO,
  pollProcessingStatus,
};
