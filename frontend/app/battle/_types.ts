/**
 * TypeScript types for Battle Mode
 */

export type VoteOption = "left_better" | "right_better" | "tie" | "both_bad";

export type BattleStatus = "ongoing" | "voted" | "abandoned";

export interface Response {
  position: "left" | "right";
  text: string;
  latency_ms: number;
}

export interface CreateSessionResponse {
  session_id: string;
  battle_id: string;
  message_id: string;
  responses: Response[];
}

export interface CreateBattleResponse {
  session_id: string;
  battle_id: string;
  message_id: string;
  responses: Response[];
}

export interface SendFollowUpResponse {
  battle_id: string;
  message_id: string;
  responses: Response[];
  message_count: number;
  max_messages?: number;
}

export interface VoteResponse {
  battle_id: string;
  vote: VoteOption;
  revealed_models: {
    left: string;
    right: string;
  };
}

export interface ConversationMessage {
  role: "user" | "assistant";
  position?: "left" | "right";
  text: string;
  timestamp?: string;
}

export interface BattleState {
  sessionId: string | null;
  battleId: string | null;
  status: BattleStatus;
  conversation: ConversationMessage[];
  revealedModels: { left: string; right: string } | null;
  isLoading: boolean;
  error: string | null;
}
