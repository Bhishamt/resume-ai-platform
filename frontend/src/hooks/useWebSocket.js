/**
 * useWebSocket — real-time notification hook.
 *
 * Connects to the backend WebSocket notification endpoint and dispatches
 * incoming messages to registered event handlers.
 *
 * Usage:
 *   const { isConnected, lastMessage } = useWebSocket({
 *     onAnalysisComplete: (data) => toast.success(`ATS score: ${data.ats_score}%`),
 *     onJobMatchComplete: (data) => navigate(`/dashboard/matches/${data.match_id}`),
 *   });
 */

import { useCallback, useEffect, useRef, useState } from 'react';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || '/api/v1/ws';
const RECONNECT_DELAY_MS = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;
const PING_INTERVAL_MS = 30000;

/**
 * @typedef {Object} WebSocketHandlers
 * @property {Function} [onConnected]          - Called when connection is established
 * @property {Function} [onDisconnected]       - Called when connection is lost
 * @property {Function} [onTaskProgress]       - task_progress event
 * @property {Function} [onAnalysisComplete]   - analysis_complete event
 * @property {Function} [onJobMatchComplete]   - job_match_complete event
 * @property {Function} [onAiReady]            - ai_ready event
 * @property {Function} [onSystemMessage]      - system notification event
 * @property {Function} [onMessage]            - Raw handler for all messages
 */

/**
 * @param {WebSocketHandlers} handlers
 * @param {string | null} token - JWT access token; pass null to skip connecting
 */
function useWebSocket(handlers = {}, token = null) {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const wsRef = useRef(null);
  const pingRef = useRef(null);
  const reconnectRef = useRef(null);
  const handlersRef = useRef(handlers);

  // Keep handlers ref current without triggering re-renders
  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  const dispatchMessage = useCallback((msg) => {
    const h = handlersRef.current;
    setLastMessage(msg);

    if (h.onMessage) h.onMessage(msg);

    switch (msg.type) {
      case 'connected':
        if (h.onConnected) h.onConnected(msg);
        break;
      case 'task_progress':
        if (h.onTaskProgress) h.onTaskProgress(msg);
        break;
      case 'analysis_complete':
        if (h.onAnalysisComplete) h.onAnalysisComplete(msg);
        break;
      case 'job_match_complete':
        if (h.onJobMatchComplete) h.onJobMatchComplete(msg);
        break;
      case 'ai_ready':
        if (h.onAiReady) h.onAiReady(msg);
        break;
      case 'system':
        if (h.onSystemMessage) h.onSystemMessage(msg);
        break;
      default:
        break;
    }
  }, []);

  const startPing = useCallback((ws) => {
    pingRef.current = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, PING_INTERVAL_MS);
  }, []);

  const stopPing = useCallback(() => {
    if (pingRef.current) {
      clearInterval(pingRef.current);
      pingRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    if (!token) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const url = WS_BASE_URL.startsWith('/')
      ? `${protocol}//${host}${WS_BASE_URL}/notifications?token=${token}`
      : `${WS_BASE_URL}/notifications?token=${token}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setReconnectAttempts(0);
      startPing(ws);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        dispatchMessage(msg);
      } catch {
        // Ignore malformed messages
      }
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      stopPing();

      if (handlersRef.current.onDisconnected) {
        handlersRef.current.onDisconnected(event);
      }

      // Auto-reconnect unless intentionally closed (code 1000) or auth failed (4001)
      if (event.code !== 1000 && event.code !== 4001) {
        setReconnectAttempts((prev) => {
          const next = prev + 1;
          if (next <= MAX_RECONNECT_ATTEMPTS) {
            reconnectRef.current = setTimeout(connect, RECONNECT_DELAY_MS * next);
          }
          return next;
        });
      }
    };

    ws.onerror = () => {
      // onclose will handle reconnection
    };
  }, [token, dispatchMessage, startPing, stopPing]);

  const disconnect = useCallback(() => {
    if (reconnectRef.current) {
      clearTimeout(reconnectRef.current);
      reconnectRef.current = null;
    }
    stopPing();
    if (wsRef.current) {
      wsRef.current.close(1000, 'User logged out');
      wsRef.current = null;
    }
    setIsConnected(false);
  }, [stopPing]);

  // Connect when token is available
  useEffect(() => {
    if (token) {
      connect();
    } else {
      disconnect();
    }
    return () => {
      disconnect();
    };
  }, [token]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    isConnected,
    lastMessage,
    reconnectAttempts,
    disconnect,
    /** Manually send a message to the server */
    send: useCallback((payload) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(payload));
      }
    }, []),
  };
}

export default useWebSocket;
