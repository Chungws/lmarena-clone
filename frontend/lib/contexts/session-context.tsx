"use client";

import {
  createContext,
  useContext,
  useCallback,
  ReactNode,
  useState,
  useEffect,
} from "react";
import { useUser } from "@/lib/hooks/use-user";
import {
  fetchSessions,
  type SessionItem,
} from "@/lib/services/session-service";

// ==================== Types ====================

interface SessionContextValue {
  // Session list state
  sessions: SessionItem[];
  loading: boolean;
  error: string | null;

  // Current active session
  activeSessionId: string | null;

  // Actions
  refetchSessions: () => Promise<void>;
  selectSession: (sessionId: string | null) => void;
}

// ==================== Context ====================

const SessionContext = createContext<SessionContextValue | undefined>(
  undefined
);

// ==================== Provider ====================

interface SessionProviderProps {
  children: ReactNode;
}

export function SessionProvider({ children }: SessionProviderProps) {
  const { userId } = useUser();

  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  // Fetch sessions
  const refetchSessions = useCallback(async () => {
    if (!userId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await fetchSessions(userId, 100, 0);
      setSessions(response.sessions);
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
      setError("Failed to load sessions");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Initial load
  useEffect(() => {
    refetchSessions();
  }, [refetchSessions]);

  // Select session
  const selectSession = useCallback((sessionId: string | null) => {
    setActiveSessionId(sessionId);
  }, []);

  const value: SessionContextValue = {
    sessions,
    loading,
    error,
    activeSessionId,
    refetchSessions,
    selectSession,
  };

  return (
    <SessionContext.Provider value={value}>
      {children}
    </SessionContext.Provider>
  );
}

// ==================== Hook ====================

export function useSessionContext() {
  const context = useContext(SessionContext);
  if (context === undefined) {
    throw new Error("useSessionContext must be used within SessionProvider");
  }
  return context;
}
