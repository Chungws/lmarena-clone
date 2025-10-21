/**
 * Custom hooks for Battle Mode state management
 */

"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import * as service from "./service";
import type {
  BattleState,
  VoteOption,
  ConversationMessage,
  Response,
} from "./_types";

const initialState: BattleState = {
  sessionId: null,
  battleId: null,
  status: "ongoing",
  conversation: [],
  revealedModels: null,
  isLoading: false,
  error: null,
};

export function useBattle() {
  const router = useRouter();
  const [state, setState] = useState<BattleState>(initialState);

  /**
   * Convert API responses to conversation messages
   */
  const convertResponsesToMessages = useCallback(
    (responses: Response[]): ConversationMessage[] => {
      return responses.map((response) => ({
        role: "assistant" as const,
        position: response.position,
        text: response.text,
      }));
    },
    []
  );

  /**
   * Create new session with initial prompt
   */
  const startSession = useCallback(
    async (prompt: string) => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await service.createSession(prompt);

        const userMessage: ConversationMessage = { role: "user", text: prompt };
        const assistantMessages = convertResponsesToMessages(
          response.responses
        );

        setState({
          sessionId: response.session_id,
          battleId: response.battle_id,
          status: "ongoing",
          conversation: [userMessage, ...assistantMessages],
          revealedModels: null,
          isLoading: false,
          error: null,
        });

        router.refresh();
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error:
            error instanceof Error ? error.message : "Failed to create session",
        }));
      }
    },
    [router, convertResponsesToMessages]
  );

  /**
   * Create new battle in existing session
   */
  const startNewBattle = useCallback(
    async (prompt: string) => {
      if (!state.sessionId) {
        setState((prev) => ({
          ...prev,
          error: "No active session",
        }));
        return;
      }

      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await service.createBattle(state.sessionId, prompt);

        const userMessage: ConversationMessage = { role: "user", text: prompt };
        const assistantMessages = convertResponsesToMessages(
          response.responses
        );

        setState((prev) => ({
          ...prev,
          battleId: response.battle_id,
          status: "ongoing",
          conversation: [userMessage, ...assistantMessages],
          revealedModels: null,
          isLoading: false,
          error: null,
        }));

        router.refresh();
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error:
            error instanceof Error ? error.message : "Failed to create battle",
        }));
      }
    },
    [state.sessionId, router, convertResponsesToMessages]
  );

  /**
   * Send follow-up message in current battle
   */
  const sendFollowUp = useCallback(
    async (prompt: string) => {
      if (!state.battleId) {
        setState((prev) => ({
          ...prev,
          error: "No active battle",
        }));
        return;
      }

      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await service.sendFollowUp(state.battleId, prompt);

        const userMessage: ConversationMessage = { role: "user", text: prompt };
        const assistantMessages = convertResponsesToMessages(
          response.responses
        );

        setState((prev) => ({
          ...prev,
          conversation: [...prev.conversation, userMessage, ...assistantMessages],
          isLoading: false,
          error: null,
        }));

        router.refresh();
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error:
            error instanceof Error
              ? error.message
              : "Failed to send follow-up",
        }));
      }
    },
    [state.battleId, router, convertResponsesToMessages]
  );

  /**
   * Submit vote and reveal models
   */
  const submitVote = useCallback(
    async (vote: VoteOption) => {
      if (!state.battleId) {
        setState((prev) => ({
          ...prev,
          error: "No active battle",
        }));
        return;
      }

      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const response = await service.submitVote(state.battleId, vote);

        setState((prev) => ({
          ...prev,
          status: "voted",
          revealedModels: response.revealed_models,
          isLoading: false,
          error: null,
        }));

        router.refresh();
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error:
            error instanceof Error ? error.message : "Failed to submit vote",
        }));
      }
    },
    [state.battleId, router]
  );

  /**
   * Reset to initial state
   */
  const reset = useCallback(() => {
    setState(initialState);
  }, []);

  return {
    state,
    startSession,
    startNewBattle,
    sendFollowUp,
    submitVote,
    reset,
  };
}
