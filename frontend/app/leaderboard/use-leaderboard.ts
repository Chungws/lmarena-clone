/**
 * Custom hook for managing leaderboard state
 */

"use client";

import { useState, useEffect, useCallback } from "react";
import { getLeaderboard } from "./service";
import type {
  LeaderboardEntry,
  LeaderboardMetadata,
  SortBy,
  SortOrder,
} from "./_types";

interface UseLeaderboardReturn {
  entries: LeaderboardEntry[];
  metadata: LeaderboardMetadata | null;
  isLoading: boolean;
  error: string | null;
  sortBy: SortBy;
  sortOrder: SortOrder;
  searchQuery: string;
  setSortBy: (sortBy: SortBy) => void;
  setSortOrder: (order: SortOrder) => void;
  setSearchQuery: (query: string) => void;
  refetch: () => Promise<void>;
}

export function useLeaderboard(): UseLeaderboardReturn {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [metadata, setMetadata] = useState<LeaderboardMetadata | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState<SortBy>("elo_score");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [searchQuery, setSearchQuery] = useState("");

  const fetchLeaderboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getLeaderboard(sortBy, sortOrder);
      setEntries(data.leaderboard);
      setMetadata(data.metadata);
    } catch (err) {
      // If backend is not available, show empty state instead of error
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      if (errorMessage.includes("Failed to fetch") || errorMessage.includes("ERR_CONNECTION_REFUSED")) {
        // Backend not available - show empty state
        setEntries([]);
        setMetadata(null);
        setError(null);
      } else {
        // Real error - show error message
        setError(errorMessage);
        setEntries([]);
        setMetadata(null);
      }
    } finally {
      setIsLoading(false);
    }
  }, [sortBy, sortOrder]);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  // Filter entries based on search query (client-side)
  const filteredEntries = searchQuery
    ? entries.filter(
        (entry) =>
          entry.model_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          entry.model_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
          entry.organization.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : entries;

  return {
    entries: filteredEntries,
    metadata,
    isLoading,
    error,
    sortBy,
    sortOrder,
    searchQuery,
    setSortBy,
    setSortOrder,
    setSearchQuery,
    refetch: fetchLeaderboard,
  };
}
