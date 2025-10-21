/**
 * API service for Leaderboard
 */

import { apiClient } from "@/lib/apiClient";
import type {
  LeaderboardResponse,
  SortBy,
  SortOrder,
} from "./_types";

/**
 * Fetch leaderboard data
 *
 * @param sortBy - Field to sort by (default: "rank")
 * @param order - Sort order (default: "asc")
 * @returns Leaderboard data with metadata
 */
export async function getLeaderboard(
  sortBy: SortBy = "rank",
  order: SortOrder = "asc"
): Promise<LeaderboardResponse> {
  // Map 'rank' to 'elo_score' for backend (rank is derived from elo_score)
  const backendSortBy = sortBy === "rank" ? "elo_score" : sortBy;
  // Reverse order for rank (asc rank = desc elo_score)
  const backendOrder = sortBy === "rank"
    ? (order === "asc" ? "desc" : "asc")
    : order;

  const params = new URLSearchParams({
    sort_by: backendSortBy,
    order: backendOrder,
  });

  return await apiClient.get<LeaderboardResponse>(
    `/api/leaderboard?${params.toString()}`
  );
}
