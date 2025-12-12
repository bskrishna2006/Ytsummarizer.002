import { useApp } from '../context/AppContext';

const Sidebar = () => {
  const { totalVideos, totalWordsProcessed } = useApp();

  const features = [
    'AI-powered summarization',
    'Multiple summary styles',
    'Detailed analytics',
    'Smart chunking for long videos',
    'Secure API handling',
  ];

  const techStack = ['Groq LLaMA 3.1-8B', 'React + Vite', 'Flask', 'yt-dlp'];

  return (
    <div className="space-y-6">
      {/* Features */}
      <div>
        <h3 className="text-sm font-medium text-gray-400 mb-3">Features</h3>
        <ul className="space-y-2">
          {features.map((feature, index) => (
            <li key={index} className="flex items-center gap-2 text-sm text-gray-300">
              <span className="w-1 h-1 bg-accent rounded-full"></span>
              {feature}
            </li>
          ))}
        </ul>
      </div>

      {/* Session Stats */}
      {totalVideos > 0 && (
        <div className="pt-6 border-t border-gray-800">
          <h3 className="text-sm font-medium text-gray-400 mb-3">This Session</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between text-gray-300">
              <span>Videos processed</span>
              <span className="font-medium text-white">{totalVideos}</span>
            </div>
            <div className="flex justify-between text-gray-300">
              <span>Words processed</span>
              <span className="font-medium text-white">{totalWordsProcessed.toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}

      {/* Tech Stack */}
      <div className="pt-6 border-t border-gray-800">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Built with</h3>
        <div className="flex flex-wrap gap-2">
          {techStack.map((tech, index) => (
            <span key={index} className="text-xs px-2 py-1 bg-gray-800 text-gray-400 rounded border border-gray-700">
              {tech}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
