import { useState } from 'react';
import { videoApi } from '../services/api';
import { useApp } from '../context/AppContext';

export const useVideoSummary = () => {
  const {
    setVideoId,
    setTranscript,
    setSummary,
    setStatistics,
    setLoading,
    setError,
    updateStatistics,
  } = useApp();

  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState('');

  const processVideo = async (url, summaryType = 'general') => {
    try {
      setLoading(true);
      setError(null);
      setProgress(0);
      setStatusMessage('Starting process...');

      // Extract transcript
      setProgress(20);
      setStatusMessage('🔍 Extracting video information...');
      
      setProgress(40);
      setStatusMessage('Fetching video transcript...');

      setProgress(70);
      setStatusMessage('Generating AI summary...');

      // Process video (full pipeline)
      const result = await videoApi.processVideo({
        url,
        summary_type: summaryType,
        chunk_size: 2500,
        max_tokens: 500,
      });

      if (result.success) {
        setVideoId(result.video_id);
        setTranscript(result.transcript);
        setSummary(result.summary);
        setStatistics(result.statistics);
        updateStatistics(result.statistics);

        setProgress(100);
        setStatusMessage('Summary generated successfully!');

        return result;
      }
    } catch (err) {
      const errorMessage = err.response?.data?.message || err.message || 'An error occurred';
      setError(errorMessage);
      setStatusMessage('');
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
      setTimeout(() => {
        setProgress(0);
        setStatusMessage('');
      }, 2000);
    }
  };

  return {
    processVideo,
    progress,
    statusMessage,
  };
};
