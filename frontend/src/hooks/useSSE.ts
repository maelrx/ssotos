import { useEffect, useRef, useState, useCallback } from 'react';

interface SSEEvent {
  type: string;
  data: unknown;
}

export function useSSE(url: string, enabled: boolean = true) {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!enabled) return;

    try {
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setError(null);
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setEvents((prev) => [...prev.slice(-99), { type: 'message', data }]);
        } catch {
          setEvents((prev) => [...prev.slice(-99), { type: 'message', data: event.data }]);
        }
      };

      eventSource.onerror = () => {
        setError('SSE connection error');
        eventSource.close();
      };

      // Custom event types from the API
      eventSource.addEventListener('job.created', (event) => {
        const data = JSON.parse((event as MessageEvent).data);
        setEvents((prev) => [...prev.slice(-99), { type: 'job.created', data }]);
      });

      eventSource.addEventListener('job.updated', (event) => {
        const data = JSON.parse((event as MessageEvent).data);
        setEvents((prev) => [...prev.slice(-99), { type: 'job.updated', data }]);
      });

      eventSource.addEventListener('job.completed', (event) => {
        const data = JSON.parse((event as MessageEvent).data);
        setEvents((prev) => [...prev.slice(-99), { type: 'job.completed', data }]);
      });

      eventSource.addEventListener('job.failed', (event) => {
        const data = JSON.parse((event as MessageEvent).data);
        setEvents((prev) => [...prev.slice(-99), { type: 'job.failed', data }]);
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to connect');
    }
  }, [url, enabled]);

  const disconnect = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { events, error, disconnect, reconnect: connect };
}
