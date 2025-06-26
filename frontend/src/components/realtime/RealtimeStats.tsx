import React, { useEffect, useState } from 'react';
import { useArticleStats } from '../../hooks/useRealtimeData';

interface RealtimeStatsProps {
  articleId: number;
  initialStats?: {
    views_count: number;
    likes_count: number;
    comments_count: number;
  };
  className?: string;
}

export const RealtimeStats: React.FC<RealtimeStatsProps> = ({
  articleId,
  initialStats = { views_count: 0, likes_count: 0, comments_count: 0 },
  className = '',
}) => {
  const { stats, isLoading, error, connectionState, incrementViews } = useArticleStats(articleId);
  const [hasIncremented, setHasIncremented] = useState(false);

  // Increment views on component mount (simulating page view)
  useEffect(() => {
    if (!hasIncremented) {
      incrementViews();
      setHasIncremented(true);
    }
  }, [incrementViews, hasIncremented]);

  // Use initial stats if still loading
  const displayStats = isLoading ? initialStats : stats;

  const formatCount = (count: number): string => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M`;
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K`;
    }
    return count.toString();
  };

  const getConnectionStatusColor = (): string => {
    switch (connectionState) {
      case 'connected': return 'text-green-500';
      case 'connecting': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      case 'disconnected': return 'text-gray-500';
      default: return 'text-gray-500';
    }
  };

  if (error) {
    return (
      <div className={`text-red-500 text-sm ${className}`}>
        <span>Error loading stats: {error}</span>
      </div>
    );
  }

  return (
    <div className={`flex items-center space-x-6 text-sm text-gray-600 ${className}`}>
      {/* Views */}
      <div className="flex items-center space-x-1">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        <span className={isLoading ? 'animate-pulse' : ''}>
          {formatCount(displayStats.views_count)} views
        </span>
      </div>

      {/* Likes */}
      <div className="flex items-center space-x-1">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
        <span className={isLoading ? 'animate-pulse' : ''}>
          {formatCount(displayStats.likes_count)} likes
        </span>
      </div>

      {/* Comments */}
      <div className="flex items-center space-x-1">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
        <span className={isLoading ? 'animate-pulse' : ''}>
          {formatCount(displayStats.comments_count)} comments
        </span>
      </div>

      {/* Connection Status Indicator */}
      <div className="flex items-center space-x-1">
        <div 
          className={`w-2 h-2 rounded-full ${getConnectionStatusColor()}`}
          title={`SSE connection: ${connectionState}`}
        >
          {connectionState === 'connecting' && (
            <div className="w-2 h-2 bg-yellow-500 rounded-full animate-ping"></div>
          )}
        </div>
        {connectionState !== 'connected' && (
          <span className={`text-xs ${getConnectionStatusColor()}`}>
            {connectionState}
          </span>
        )}
      </div>
    </div>
  );
};

export default RealtimeStats; 