import { useState, useEffect, useCallback, useRef } from 'react';
import { useSSE } from './useSSE';

// Types for real-time events
interface ArticleStats {
  views_count: number;
  likes_count: number;
  comments_count: number;
}

interface Comment {
  id: number;
  article_id: number;
  author: {
    id: number;
    username: string;
    full_name: string;
  };
  content: string;
  parent_id?: number;
  created_at: string;
  updated_at: string;
  is_reply: boolean;
}

interface Like {
  id: number;
  article_id: number;
  user_id: number;
  created_at: string;
}

interface EditingSession {
  article_id: number;
  user: {
    id: number;
    username: string;
    full_name: string;
  };
  cursor_position?: number;
  session_id: string;
  is_auto_saving: boolean;
}

interface SSEEvent {
  type: string;
  action: string;
  data: any;
  metadata: {
    timestamp: string;
    channel: string;
  };
}

// Hook for real-time article statistics
export const useArticleStats = (articleId: number) => {
  const [stats, setStats] = useState<ArticleStats>({
    views_count: 0,
    likes_count: 0,
    comments_count: 0,
  });
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // SSE connection for real-time updates
  const { connectionState, lastEvent } = useSSE(
    `/api/v1/sse/article/${articleId}/`,
    {
      eventTypes: ['view', 'like', 'comment'],
      onMessage: (event) => {
        try {
          const eventData: SSEEvent = JSON.parse(event.data);
          
          switch (eventData.type) {
            case 'view':
              if (eventData.action === 'incremented') {
                setStats(prev => ({ ...prev, views_count: eventData.data.views_count }));
              }
              break;
            case 'like':
              if (eventData.action === 'created') {
                setStats(prev => ({ ...prev, likes_count: prev.likes_count + 1 }));
              } else if (eventData.action === 'deleted') {
                setStats(prev => ({ ...prev, likes_count: Math.max(0, prev.likes_count - 1) }));
              }
              break;
            case 'comment':
              if (eventData.action === 'created') {
                setStats(prev => ({ ...prev, comments_count: prev.comments_count + 1 }));
              } else if (eventData.action === 'deleted') {
                setStats(prev => ({ ...prev, comments_count: Math.max(0, prev.comments_count - 1) }));
              }
              break;
          }
        } catch (err) {
          console.error('Error parsing SSE event:', err);
        }
      },
      onError: (error) => {
        setError('Connection error occurred');
        console.error('SSE connection error:', error);
      },
    }
  );

  // Fetch initial stats
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`/api/v1/articles/${articleId}/stats/`);
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        } else {
          setError('Failed to fetch article stats');
        }
      } catch (err) {
        setError('Network error occurred');
        console.error('Error fetching stats:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, [articleId]);

  const incrementViews = useCallback(async () => {
    try {
      await fetch(`/api/v1/articles/${articleId}/increment-views/`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (err) {
      console.error('Error incrementing views:', err);
    }
  }, [articleId]);

  return {
    stats,
    isLoading,
    error,
    connectionState,
    incrementViews,
  };
};

// Hook for real-time comments
export const useRealtimeComments = (articleId: number) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { connectionState } = useSSE(
    `/api/v1/sse/article/${articleId}/`,
    {
      eventTypes: ['comment'],
      onMessage: (event) => {
        try {
          const eventData: SSEEvent = JSON.parse(event.data);
          
          if (eventData.type === 'comment') {
            const comment = eventData.data as Comment;
            
            switch (eventData.action) {
              case 'created':
                setComments(prev => [comment, ...prev]);
                break;
              case 'updated':
                setComments(prev => 
                  prev.map(c => c.id === comment.id ? comment : c)
                );
                break;
              case 'deleted':
                setComments(prev => 
                  prev.filter(c => c.id !== comment.id)
                );
                break;
            }
          }
        } catch (err) {
          console.error('Error processing comment event:', err);
        }
      },
    }
  );

  const addComment = useCallback(async (content: string, parentId?: number) => {
    try {
      const response = await fetch(`/api/v1/articles/${articleId}/comments/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          content,
          parent: parentId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to add comment');
      }

      return await response.json();
    } catch (err) {
      console.error('Error adding comment:', err);
      throw err;
    }
  }, [articleId]);

  return {
    comments,
    isLoading,
    error,
    connectionState,
    addComment,
  };
};

// Hook for like functionality
export const useArticleLike = (articleSlug: string) => {
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  const toggleLike = useCallback(async () => {
    try {
      setIsLoading(true);
      
      const method = isLiked ? 'DELETE' : 'POST';
      const response = await fetch(`/api/v1/articles/${articleSlug}/like/`, {
        method,
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setIsLiked(data.liked);
        setLikesCount(data.likes_count);
      }
    } catch (err) {
      console.error('Error toggling like:', err);
    } finally {
      setIsLoading(false);
    }
  }, [articleSlug, isLiked]);

  return {
    isLiked,
    likesCount,
    isLoading,
    toggleLike,
    setIsLiked,
    setLikesCount,
  };
};

// Hook for collaborative editing
export const useCollaborativeEditing = (articleId: number) => {
  const [activeEditors, setActiveEditors] = useState<EditingSession[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const heartbeatRef = useRef<NodeJS.Timeout | null>(null);

  const { connectionState } = useSSE(
    `/api/v1/sse/editing/${articleId}/`,
    {
      eventTypes: ['editing'],
      onMessage: (event) => {
        try {
          const eventData: SSEEvent = JSON.parse(event.data);
          
          if (eventData.type === 'editing') {
            const session = eventData.data as EditingSession;
            
            switch (eventData.action) {
              case 'session_started':
                setActiveEditors(prev => {
                  const existing = prev.find(e => e.user.id === session.user.id);
                  if (existing) {
                    return prev.map(e => e.user.id === session.user.id ? session : e);
                  }
                  return [...prev, session];
                });
                break;
              case 'session_ended':
                setActiveEditors(prev => 
                  prev.filter(e => e.user.id !== session.user.id)
                );
                break;
              case 'cursor_moved':
                setActiveEditors(prev => 
                  prev.map(e => 
                    e.user.id === session.user.id 
                      ? { ...e, cursor_position: session.cursor_position }
                      : e
                  )
                );
                break;
              case 'heartbeat':
                // Update last seen time for the user
                setActiveEditors(prev => 
                  prev.map(e => 
                    e.user.id === session.user.id 
                      ? { ...e, ...session }
                      : e
                  )
                );
                break;
            }
          }
        } catch (err) {
          console.error('Error processing editing event:', err);
        }
      },
    }
  );

  const startEditingSession = useCallback(async () => {
    try {
      const response = await fetch(`/api/v1/articles/${articleId}/editing/start/`, {
        method: 'POST',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setIsEditing(true);
        setActiveEditors(data.active_editors || []);

        // Start heartbeat
        heartbeatRef.current = setInterval(async () => {
          try {
            await fetch(`/api/v1/articles/${articleId}/editing/heartbeat/`, {
              method: 'POST',
              credentials: 'include',
            });
          } catch (err) {
            console.error('Heartbeat failed:', err);
          }
        }, 30000); // 30 seconds
      }
    } catch (err) {
      console.error('Error starting editing session:', err);
    }
  }, [articleId]);

  const endEditingSession = useCallback(async () => {
    try {
      if (heartbeatRef.current) {
        clearInterval(heartbeatRef.current);
        heartbeatRef.current = null;
      }

      await fetch(`/api/v1/articles/${articleId}/editing/end/`, {
        method: 'POST',
        credentials: 'include',
      });

      setSessionId(null);
      setIsEditing(false);
    } catch (err) {
      console.error('Error ending editing session:', err);
    }
  }, [articleId]);

  const updateCursorPosition = useCallback(async (position: number) => {
    if (!isEditing) return;

    try {
      await fetch(`/api/v1/articles/${articleId}/editing/cursor/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          cursor_position: position,
        }),
      });
    } catch (err) {
      console.error('Error updating cursor position:', err);
    }
  }, [articleId, isEditing]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (heartbeatRef.current) {
        clearInterval(heartbeatRef.current);
      }
      if (isEditing) {
        endEditingSession();
      }
    };
  }, [isEditing, endEditingSession]);

  return {
    activeEditors,
    sessionId,
    isEditing,
    connectionState,
    startEditingSession,
    endEditingSession,
    updateCursorPosition,
  };
};

// Hook for global notifications
export const useGlobalNotifications = () => {
  const [notifications, setNotifications] = useState<any[]>([]);

  const { connectionState } = useSSE('/api/v1/sse/global/', {
    eventTypes: ['notification', 'announcement'],
    onMessage: (event) => {
      try {
        const eventData: SSEEvent = JSON.parse(event.data);
        
        if (eventData.type === 'notification' || eventData.type === 'announcement') {
          setNotifications(prev => [eventData, ...prev.slice(0, 49)]); // Keep last 50
        }
      } catch (err) {
        console.error('Error processing notification:', err);
      }
    },
  });

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    notifications,
    connectionState,
    clearNotifications,
  };
}; 