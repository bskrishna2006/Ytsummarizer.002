import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const videoApi = {
  /**
   * Health check endpoint
   */
  healthCheck: async () => {
    const response = await api.get('/api/health');
    return response.data;
  },

  /**
   * Extract transcript from YouTube video
   * @param {string} url - YouTube video URL
   */
  getTranscript: async (url) => {
    const response = await api.post('/api/transcript', { url });
    return response.data;
  },

  /**
   * Generate summary from transcript
   * @param {Object} params - Summary parameters
   * @param {string} params.transcript - Video transcript
   * @param {string} params.summary_type - Type of summary
   * @param {number} params.chunk_size - Chunk size for processing
   * @param {number} params.max_tokens - Max tokens for summary
   */
  generateSummary: async ({ transcript, summary_type, chunk_size, max_tokens }) => {
    const response = await api.post('/api/summarize', {
      transcript,
      summary_type,
      chunk_size,
      max_tokens,
    });
    return response.data;
  },

  /**
   * Process video (extract transcript and generate summary in one call)
   * @param {Object} params - Processing parameters
   * @param {string} params.url - YouTube video URL
   * @param {string} params.summary_type - Type of summary
   * @param {number} params.chunk_size - Chunk size for processing
   * @param {number} params.max_tokens - Max tokens for summary
   */
  processVideo: async ({ url, summary_type, chunk_size, max_tokens }) => {
    const response = await api.post('/api/process', {
      url,
      summary_type,
      chunk_size,
      max_tokens,
    });
    return response.data;
  },
};

export default api;
