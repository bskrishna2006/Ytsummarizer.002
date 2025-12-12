import { useState } from 'react';
import { useApp } from '../context/AppContext';

const TranscriptViewer = () => {
  const { transcript } = useApp();
  const [isExpanded, setIsExpanded] = useState(false);

  if (!transcript) return null;

  const wordCount = transcript.split(/\s+/).length;

  return (
    <div className="animate-fadeIn">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between py-3 text-left border-t border-gray-800"
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-300">Full Transcript</span>
          <span className="text-xs text-gray-500">{wordCount.toLocaleString()} words</span>
        </div>
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="pt-4 pb-2">
          <div className="max-h-64 overflow-y-auto text-sm text-gray-400 leading-relaxed bg-gray-800 rounded-lg p-4 border border-gray-700">
            {transcript}
          </div>
          <div className="flex gap-2 mt-3">
            <button
              onClick={() => navigator.clipboard.writeText(transcript)}
              className="text-xs text-gray-400 hover:text-white transition-colors"
            >
              Copy transcript
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TranscriptViewer;
