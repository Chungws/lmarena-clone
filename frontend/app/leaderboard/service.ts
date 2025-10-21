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
 * @param sortBy - Field to sort by (default: "elo_score")
 * @param order - Sort order (default: "desc")
 * @returns Leaderboard data with metadata
 */
export async function getLeaderboard(
  sortBy: SortBy = "elo_score",
  order: SortOrder = "desc"
): Promise<LeaderboardResponse> {
  const params = new URLSearchParams({
    sort_by: sortBy,
    order,
  });

  return await apiClient.get<LeaderboardResponse>(
    `/api/leaderboard?${params.toString()}`
  );
}
