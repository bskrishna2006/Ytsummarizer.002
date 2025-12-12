import { AppProvider } from './context/AppContext';
import Navbar from './components/Navbar';
import Header from './components/Header';
import VideoInput from './components/VideoInput';
import SummaryCard from './components/SummaryCard';
import StatisticsPanel from './components/StatisticsPanel';
import TranscriptViewer from './components/TranscriptViewer';
import Sidebar from './components/Sidebar';
import ErrorAlert from './components/ErrorAlert';

function App() {
  return (
    <AppProvider>
      <div className="min-h-screen bg-gray-950">
        <Navbar />

        <main>
          <Header />

          <div className="max-w-5xl mx-auto px-4 pb-16">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
              {/* Main Content */}
              <div className="lg:col-span-2 space-y-6">
                <ErrorAlert />
                <VideoInput />
                <SummaryCard />
                <StatisticsPanel />
                <TranscriptViewer />
              </div>

              {/* Sidebar */}
              <div className="lg:col-span-1">
                <div className="lg:sticky lg:top-20">
                  <Sidebar />
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Simple Footer */}
        <footer className="border-t border-gray-800 py-8 mt-16">
          <div className="max-w-5xl mx-auto px-4 text-center text-sm text-gray-500">
            <p>Built with React, Flask, and Groq AI</p>
            <p className="mt-2">© 2025 VideoSummarize</p>
          </div>
        </footer>
      </div>
    </AppProvider>
  );
}

export default App;
