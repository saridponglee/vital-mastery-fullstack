import React from 'react';
import { useArticleStore } from '../stores/articleStore';

export const LanguageSwitcher: React.FC = () => {
  const { language, setLanguage } = useArticleStore();

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm text-gray-600">Language:</span>
      <div className="flex bg-gray-100 rounded-lg p-1">
        <button
          onClick={() => setLanguage('en')}
          className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
            language === 'en' 
              ? 'bg-white text-blue-600 shadow-sm' 
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          English
        </button>
        <button
          onClick={() => setLanguage('th')}
          className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
            language === 'th' 
              ? 'bg-white text-blue-600 shadow-sm' 
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          ไทย
        </button>
      </div>
    </div>
  );
}; 