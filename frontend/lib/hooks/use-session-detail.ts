"use client";

import { useState, useEffect } from "react";
import {
  fetchSessionBattles,
  type BattleItem,
} from "@/lib/services/session-service";

/**
 * Hook for loading and managing a specific session's battles
 *
 * @param sessionId - Session ID to load battles for (null = no session selected)
 * @returns Battle list, loading state, and error state
 */
export function useSessionDetail(sessionId: string | null) {
  const [battles, setBattles] = useState<BattleItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Reset state when no session selected
    if (!sessionId) {
      setBattles([]);
      setLoading(false);
      setError(null);
      return;
    }

    // Fetch battles for selected session
    async function loadBattles() {
      try {
        setLoading(true);
        setError(null);
        const response = await fetchSessionBattles(sessionId);
        setBattles(response.battles);
      } catch (err) {
        console.error("Failed to fetch session battles:", err);
        setError("Failed to load session");
      } finally {
        setLoading(false);
      }
    }

    loadBattles();
  }, [sessionId]);

  return {
    battles,
    loading,
    error,
  };
}
