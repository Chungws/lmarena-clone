/**
 * TypeScript types for Leaderboard
 */

export interface LeaderboardEntry {
  rank: number;
  model_id: string;
  model_name: string;
  elo_score: number;
  elo_ci: number;
  vote_count: number;
  win_rate: number;
  organization: string;
  license: string;
}

export interface LeaderboardMetadata {
  total_models: number;
  total_votes: number;
  last_updated: string;
}

export interface LeaderboardResponse {
  leaderboard: LeaderboardEntry[];
  metadata: LeaderboardMetadata;
}

export type SortBy = "elo_score" | "vote_count" | "organization";
export type SortOrder = "asc" | "desc";
