import { useApp } from '../context/AppContext';

const StatisticsPanel = () => {
  const { statistics } = useApp();

  if (!statistics) return null;

  const stats = [
    { label: 'Original', value: statistics.original_word_count.toLocaleString(), unit: 'words' },
    { label: 'Summary', value: statistics.summary_word_count.toLocaleString(), unit: 'words' },
    { label: 'Compression', value: statistics.compression_ratio, unit: '%' },
    { label: 'Read time', value: statistics.reading_time_minutes, unit: 'min' },
  ];

  return (
    <div className="animate-fadeIn">
      <h3 className="text-sm font-medium text-gray-400 mb-3">Statistics</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {stats.map((stat, index) => (
          <div key={index} className="bg-gray-800 rounded-lg p-3 text-center border border-gray-700">
            <div className="text-xl font-semibold text-white">{stat.value}</div>
            <div className="text-xs text-gray-400 mt-1">{stat.label} ({stat.unit})</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StatisticsPanel;
