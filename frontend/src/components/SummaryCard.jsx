import { useState } from 'react';
import { FiCopy, FiDownload, FiCheck } from 'react-icons/fi';
import { useApp } from '../context/AppContext';

const SummaryCard = () => {
  const { summary, videoId } = useApp();
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([summary], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `summary_${videoId || 'video'}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Parse markdown-style text and convert to formatted elements
  const renderFormattedText = (text) => {
    // Process bold text (**text**)
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  const renderSummary = () => {
    if (!summary) return null;

    const lines = summary.split('\n');
    const elements = [];
    let currentList = [];
    let currentSubList = [];
    let inSubList = false;

    const flushSubList = () => {
      if (currentSubList.length > 0) {
        currentList.push(
          <ul key={`sublist-${currentList.length}`} className="ml-5 mt-1 space-y-1">
            {currentSubList.map((item, i) => (
              <li key={i} className="text-gray-400 text-sm flex items-start gap-2">
                <span className="text-gray-500 mt-1.5">–</span>
                <span>{renderFormattedText(item)}</span>
              </li>
            ))}
          </ul>
        );
        currentSubList = [];
      }
    };

    const flushList = () => {
      flushSubList();
      if (currentList.length > 0) {
        elements.push(
          <ul key={`list-${elements.length}`} className="space-y-2 mb-4">
            {currentList}
          </ul>
        );
        currentList = [];
      }
    };

    lines.forEach((line, index) => {
      const trimmed = line.trim();
      
      if (!trimmed) {
        flushList();
        return;
      }

      // Main bullet point (* or •)
      if (trimmed.match(/^[\*•]\s+\*\*/)) {
        flushSubList();
        inSubList = false;
        const content = trimmed.replace(/^[\*•]\s+/, '');
        currentList.push(
          <li key={`item-${index}`} className="text-gray-200">
            <div className="flex items-start gap-2">
              <span className="text-accent mt-1">•</span>
              <div className="flex-1">
                {renderFormattedText(content)}
              </div>
            </div>
          </li>
        );
        inSubList = true;
      }
      // Sub-bullet point (- or indented)
      else if (trimmed.match(/^[-–]\s+/) || line.startsWith('    ')) {
        const content = trimmed.replace(/^[-–]\s+/, '');
        currentSubList.push(content);
      }
      // Regular bullet
      else if (trimmed.match(/^[\*•]\s+/)) {
        flushSubList();
        const content = trimmed.replace(/^[\*•]\s+/, '');
        currentList.push(
          <li key={`item-${index}`} className="text-gray-300 flex items-start gap-2">
            <span className="text-accent mt-1">•</span>
            <span>{renderFormattedText(content)}</span>
          </li>
        );
      }
      // Heading or intro text
      else {
        flushList();
        elements.push(
          <p key={`p-${index}`} className="text-gray-300 mb-3 leading-relaxed">
            {renderFormattedText(trimmed)}
          </p>
        );
      }
    });

    flushList();
    return elements;
  };

  if (!summary) return null;

  return (
    <div className="card shadow-soft animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-700">
        <h3 className="text-lg font-semibold text-white">Summary</h3>
        <span className="text-xs text-gray-500">AI Generated</span>
      </div>
      
      {/* Content */}
      <div className="mb-6">
        {renderSummary()}
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-4 border-t border-gray-700">
        <button onClick={handleCopy} className="btn-secondary flex-1 flex items-center justify-center gap-2 text-sm">
          {copied ? <FiCheck className="text-green-500" /> : <FiCopy />}
          {copied ? 'Copied!' : 'Copy'}
        </button>
        <button onClick={handleDownload} className="btn-primary flex-1 flex items-center justify-center gap-2 text-sm">
          <FiDownload />
          Download
        </button>
      </div>
    </div>
  );
};

export default SummaryCard;
