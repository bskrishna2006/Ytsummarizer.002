import { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

export const AppProvider = ({ children }) => {
  const [videoUrl, setVideoUrl] = useState('');
  const [videoId, setVideoId] = useState('');
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [summaryType, setSummaryType] = useState('general');
  
  // Session analytics
  const [totalVideos, setTotalVideos] = useState(0);
  const [totalWordsProcessed, setTotalWordsProcessed] = useState(0);

  const resetState = () => {
    setVideoUrl('');
    setVideoId('');
    setTranscript('');
    setSummary('');
    setStatistics(null);
    setError(null);
  };

  const updateStatistics = (stats) => {
    setStatistics(stats);
    setTotalVideos((prev) => prev + 1);
    setTotalWordsProcessed((prev) => prev + (stats?.original_word_count || 0));
  };

  const value = {
    videoUrl,
    setVideoUrl,
    videoId,
    setVideoId,
    transcript,
    setTranscript,
    summary,
    setSummary,
    statistics,
    setStatistics,
    loading,
    setLoading,
    error,
    setError,
    summaryType,
    setSummaryType,
    totalVideos,
    totalWordsProcessed,
    resetState,
    updateStatistics,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
