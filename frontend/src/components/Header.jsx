const Header = () => {
  return (
    <header className="pt-24 pb-16 px-4">
      <div className="max-w-3xl mx-auto text-center">
        {/* Simple badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 mb-6 text-xs font-medium text-gray-400 bg-gray-800 rounded-full border border-gray-700">
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
          Powered by Groq LLaMA 3.1
        </div>

        {/* Main heading - simple and clear */}
        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
          YouTube Video Summarizer
        </h1>

        {/* Subheading */}
        <p className="text-lg text-gray-400 max-w-xl mx-auto leading-relaxed">
          Transform long videos into concise summaries. Paste a URL, choose your style, get results.
        </p>
      </div>
    </header>
  );
};

export default Header;
