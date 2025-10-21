/**
 * Battle API Service
 *
 * Handles all API calls related to battle mode
 */

import { apiClient } from "@/lib/apiClient";
import type {
  CreateSessionResponse,
  CreateBattleResponse,
  SendFollowUpResponse,
  VoteResponse,
  VoteOption,
} from "./_types";

/**
 * Create a new session with initial prompt
 */
export async function createSession(
  prompt: string
): Promise<CreateSessionResponse> {
  return apiClient.post<CreateSessionResponse>("/api/sessions", { prompt });
}

/**
 * Create a new battle in existing session
 */
export async function createBattle(
  sessionId: string,
  prompt: string
): Promise<CreateBattleResponse> {
  return apiClient.post<CreateBattleResponse>(
    `/api/sessions/${sessionId}/battles`,
    { prompt }
  );
}

/**
 * Send follow-up message in current battle
 */
export async function sendFollowUp(
  battleId: string,
  prompt: string
): Promise<SendFollowUpResponse> {
  return apiClient.post<SendFollowUpResponse>(
    `/api/battles/${battleId}/messages`,
    { prompt }
  );
}

/**
 * Submit vote for current battle
 */
export async function submitVote(
  battleId: string,
  vote: VoteOption
): Promise<VoteResponse> {
  return apiClient.post<VoteResponse>(`/api/battles/${battleId}/vote`, {
    vote,
  });
}
