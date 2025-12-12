import { useApp } from '../context/AppContext';

const ErrorAlert = () => {
  const { error, setError } = useApp();

  if (!error) return null;

  return (
    <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg animate-fadeIn">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <h4 className="text-sm font-medium text-red-400 mb-1">Error</h4>
          <p className="text-sm text-red-300/80">{error}</p>
        </div>
        <button
          onClick={() => setError(null)}
          className="text-red-400 hover:text-red-300 p-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default ErrorAlert;
