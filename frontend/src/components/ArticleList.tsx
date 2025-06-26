import React, { useEffect, useMemo } from 'react';
import { useSSE } from '../hooks/useSSE';
import { useArticleStore, Article } from '../stores/articleStore';

interface ArticleCardProps {
  article: Article;
}

const ArticleCard: React.FC<ArticleCardProps> = ({ article }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getAuthorDisplayName = (author: Article['author']) => {
    const fullName = `${author.first_name} ${author.last_name}`.trim();
    return fullName || author.username;
  };

  return (
    <article className="bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-300 overflow-hidden">
      {article.featured_image && (
        <div className="aspect-video overflow-hidden">
          <img 
            src={article.featured_image} 
            alt={article.title}
            className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
          />
        </div>
      )}
      
      <div className="p-6">
        <div className="flex items-center justify-between mb-3">
          {article.category && (
            <span className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
              {article.category.name}
            </span>
          )}
          <span className="text-sm text-gray-500">
            {article.reading_time} min read
          </span>
        </div>
        
        <h2 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2 hover:text-blue-600 transition-colors">
          {article.title}
        </h2>
        
        {article.excerpt && (
          <p className="text-gray-600 mb-4 line-clamp-3">
            {article.excerpt}
          </p>
        )}
        
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>By {getAuthorDisplayName(article.author)}</span>
          <time dateTime={article.publishedAt}>
            {formatDate(article.publishedAt)}
          </time>
        </div>
      </div>
    </article>
  );
};

interface ConnectionStatusProps {
  status: 'connected' | 'disconnected' | 'connecting' | 'error';
  reconnectCount?: number;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ status, reconnectCount }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'connected': return 'text-green-600';
      case 'connecting': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      case 'disconnected': return 'text-gray-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusDot = () => {
    switch (status) {
      case 'connected': return 'bg-green-600';
      case 'connecting': return 'bg-yellow-600 animate-pulse';
      case 'error': return 'bg-red-600 animate-pulse';
      case 'disconnected': return 'bg-gray-600';
      default: return 'bg-gray-600';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'connected': return 'Live Updates';
      case 'connecting': return reconnectCount ? `Reconnecting... (${reconnectCount})` : 'Connecting...';
      case 'error': return 'Connection Error';
      case 'disconnected': return 'Offline';
      default: return 'Unknown';
    }
  };

  return (
    <div className={`flex items-center ${getStatusColor()}`}>
      <span className={`w-2 h-2 rounded-full mr-2 ${getStatusDot()}`}></span>
      <span className="text-sm font-medium">{getStatusText()}</span>
    </div>
  );
};

export const ArticleList: React.FC = () => {
  const { 
    articles,
    language, 
    connectionStatus,
    handleRealtimeUpdate,
    setConnectionStatus,
    getArticlesByLanguage
  } = useArticleStore();

  // Connect to SSE endpoint for current language
  const { connectionState, reconnectCount } = useSSE(`/api/content/events/article-updates-${language}/`, {
    withCredentials: true,
    onOpen: () => {
      console.log('SSE connection established');
      setConnectionStatus('connected');
    },
    onError: () => {
      console.error('SSE connection error');
      setConnectionStatus('error');
    },
    onMessage: (event) => {
      try {
        const data = JSON.parse(event.data);
        handleRealtimeUpdate(data);
      } catch (error) {
        console.error('Failed to parse SSE data:', error);
      }
    }
  });

  // Sync connection status
  useEffect(() => {
    setConnectionStatus(connectionState);
  }, [connectionState, setConnectionStatus]);

  // Filter articles by current language
  const filteredArticles = useMemo(() => {
    return getArticlesByLanguage(language);
  }, [articles, language, getArticlesByLanguage]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Latest Articles</h1>
          <p className="text-gray-600 mt-2">
            Real-time updates from VITAL MASTERY
          </p>
        </div>
        <ConnectionStatus status={connectionStatus} reconnectCount={reconnectCount} />
      </div>

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredArticles.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-gray-500 text-lg">
              No published articles yet.
            </p>
            <p className="text-gray-400 text-sm mt-2">
              Articles will appear here automatically when published.
            </p>
          </div>
        ) : (
          filteredArticles.map(article => (
            <ArticleCard key={`${article.id}_${article.language}`} article={article} />
          ))
        )}
      </div>

      {/* Article Count */}
      {filteredArticles.length > 0 && (
        <div className="text-center mt-8 text-gray-500">
          Showing {filteredArticles.length} article{filteredArticles.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
}; 