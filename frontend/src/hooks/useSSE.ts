import { useEffect, useState, useRef } from 'react';

interface SSEOptions {
  withCredentials?: boolean;
  onMessage?: (event: MessageEvent) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  reconnectDelay?: number;
  maxReconnectAttempts?: number;
}

interface UseSSEReturn {
  connectionState: 'connecting' | 'connected' | 'disconnected' | 'error';
  lastEvent: MessageEvent | null;
  eventSource: EventSource | null;
  reconnectCount: number;
}

export const useSSE = (url: string, options: SSEOptions = {}): UseSSEReturn => {
  const [connectionState, setConnectionState] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('connecting');
  const [lastEvent, setLastEvent] = useState<MessageEvent | null>(null);
  const [reconnectCount, setReconnectCount] = useState(0);
  
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const {
    withCredentials = true,
    onMessage,
    onError,
    onOpen,
    reconnectDelay = 3000,
    maxReconnectAttempts = 5
  } = options;

  const connect = () => {
    try {
      const eventSource = new EventSource(url, { withCredentials });
      eventSourceRef.current = eventSource;
      
      setConnectionState('connecting');

      eventSource.onopen = () => {
        console.log(`SSE connected to ${url}`);
        setConnectionState('connected');
        setReconnectCount(0);
        onOpen?.();
      };

      eventSource.onmessage = (event) => {
        setLastEvent(event);
        onMessage?.(event);
      };

      // Listen for specific article-published events
      eventSource.addEventListener('article-published', (event: MessageEvent) => {
        console.log('Article published event received:', event.data);
        setLastEvent(event);
        onMessage?.(event);
      });

      eventSource.onerror = (error) => {
        console.error('SSE error:', error);
        setConnectionState('error');
        onError?.(error);
        
        // Attempt to reconnect if within limits
        if (reconnectCount < maxReconnectAttempts) {
          console.log(`Reconnecting in ${reconnectDelay}ms... (attempt ${reconnectCount + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectCount(prev => prev + 1);
            eventSource.close();
            connect();
          }, reconnectDelay);
        } else {
          console.error('Max reconnection attempts reached');
          setConnectionState('disconnected');
        }
      };

    } catch (error) {
      console.error('Failed to create EventSource:', error);
      setConnectionState('error');
    }
  };

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [url]);

  return {
    connectionState,
    lastEvent,
    eventSource: eventSourceRef.current,
    reconnectCount
  };
}; 