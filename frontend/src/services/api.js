const API_BASE = '/api/v1';

export const getStoredApiKey = () => {
  return localStorage.getItem('rag_api_key') || 'jjTecnZ4YJh4OWKvPfFFpjqwhWFP7R9gGRABtS8l61U';
};

export const setStoredApiKey = (key) => {
  localStorage.setItem('rag_api_key', key);
};

export const askText = async (question, apiKey = getStoredApiKey()) => {
  const response = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Request failed (${response.status})`);
  }

  return response.json();
};

export const askVoice = async (audioBlob, apiKey = getStoredApiKey(), ext = 'webm') => {
  const formData = new FormData();
  formData.append('file', audioBlob, `speech.${ext}`);

  const response = await fetch(`${API_BASE}/voice/ask`, {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Voice request failed (${response.status})`);
  }

  return response.json();
};

export const streamSpeech = async (question, apiKey = getStoredApiKey()) => {
  const response = await fetch(`${API_BASE}/voice/speak`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate speech stream');
  }

  return response.blob();
};

export const uploadDocument = async (file, apiKey = getStoredApiKey()) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    headers: {
      'X-API-Key': apiKey,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Upload failed (${response.status})`);
  }

  return response.json();
};

export const checkJobStatus = async (jobId, apiKey = getStoredApiKey()) => {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
    headers: {
      'X-API-Key': apiKey,
    },
  });

  if (!response.ok) {
    throw new Error(`Job check failed (${response.status})`);
  }

  return response.json();
};
