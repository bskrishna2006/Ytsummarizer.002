import { useState } from 'react';
import { useApp } from '../context/AppContext';
import { useVideoSummary } from '../hooks/useVideoSummary';

const VideoInput = () => {
  const { summaryType, setSummaryType, loading } = useApp();
  const { processVideo, progress, statusMessage } = useVideoSummary();
  const [localUrl, setLocalUrl] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!localUrl.trim()) return;
    
    try {
      await processVideo(localUrl, summaryType);
    } catch (error) {
      console.error('Error processing video:', error);
    }
  };

  const summaryTypes = [
    { value: 'general', label: 'General', desc: 'Concise overview' },
    { value: 'detailed', label: 'Detailed', desc: 'Comprehensive' },
    { value: 'bullet_points', label: 'Bullet Points', desc: 'List format' },
    { value: 'key_takeaways', label: 'Key Takeaways', desc: 'Main insights' },
  ];

  return (
    <div className="space-y-6">
      {/* Main input card */}
      <div className="card shadow-soft">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* URL Input */}
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-300 mb-2">
              YouTube URL
            </label>
            <input
              type="text"
              id="url"
              value={localUrl}
              onChange={(e) => setLocalUrl(e.target.value)}
              placeholder="https://www.youtube.com/watch?v=..."
              className="input-field"
              disabled={loading}
            />
          </div>

          {/* Summary Type */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Summary Style
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {summaryTypes.map((type) => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setSummaryType(type.value)}
                  disabled={loading}
                  className={`p-3 rounded-lg text-left transition-colors ${
                    summaryType === type.value
                      ? 'bg-accent text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700 border border-gray-700'
                  } disabled:opacity-50`}
                >
                  <div className="text-sm font-medium">{type.label}</div>
                  <div className="text-xs opacity-70 mt-0.5">{type.desc}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || !localUrl.trim()}
            className="w-full btn-primary flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Processing...
              </>
            ) : (
              'Generate Summary'
            )}
          </button>
        </form>

        {/* Progress */}
        {loading && (
          <div className="mt-5 pt-5 border-t border-gray-700">
            <div className="flex justify-between text-sm text-gray-400 mb-2">
              <span>{statusMessage}</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-1.5">
              <div
                className="bg-accent h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Tips - simple text, no card */}
      <div className="text-sm text-gray-500 space-y-1 px-1">
        <p>💡 Works best with videos that have captions enabled</p>
        <p>📺 Educational and informational content recommended</p>
      </div>
    </div>
  );
};

export default VideoInput;
