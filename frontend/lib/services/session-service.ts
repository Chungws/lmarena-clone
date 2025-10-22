/**
 * Session Service
 *
 * API client for session-related endpoints
 */

import { apiClient } from "@/lib/apiClient";

// ==================== Types ====================

export interface SessionItem {
  session_id: string;
  title: string;
  created_at: string;
  last_active_at: string;
}

export interface SessionListResponse {
  sessions: SessionItem[];
  total: number;
}

export interface BattleItem {
  battle_id: string;
  left_model_id: string;
  right_model_id: string;
  conversation: Array<{
    role: string;
    content: string;
  }>;
  status: string;
  vote?: string;
  created_at: string;
}

export interface BattleListResponse {
  session_id: string;
  battles: BattleItem[];
}

// ==================== API Functions ====================

/**
 * Fetch session list for a user
 *
 * @param userId - Anonymous user ID (UUID string)
 * @param limit - Maximum number of sessions to return (default: 50)
 * @param offset - Number of sessions to skip (default: 0)
 * @returns Session list with total count
 */
export async function fetchSessions(
  userId: string,
  limit: number = 50,
  offset: number = 0
): Promise<SessionListResponse> {
  const params = new URLSearchParams({
    user_id: userId,
    limit: String(limit),
    offset: String(offset),
  });

  return await apiClient.get<SessionListResponse>(
    `/api/sessions?${params.toString()}`
  );
}

/**
 * Fetch all battles for a specific session
 *
 * @param sessionId - Session ID
 * @returns Battle list with vote information
 */
export async function fetchSessionBattles(
  sessionId: string
): Promise<BattleListResponse> {
  return await apiClient.get<BattleListResponse>(
    `/api/sessions/${sessionId}/battles`
  );
}
