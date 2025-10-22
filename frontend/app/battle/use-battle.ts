/**
 * Custom hooks for Battle Mode state management
 */

"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useUser } from "@/lib/hooks/use-user";
import { useSessionContext } from "@/lib/contexts/session-context";
import * as service from "./service";
import type {
  BattleState,
  Battle,
  VoteOption,
  ConversationMessage,
  Response,
} from "./_types";

const initialState: BattleState = {
  sessionId: null,
  battles: [],
  currentBattleId: null,
  isLoading: false,
  error: null,
};

export function useBattle() {
  const router = useRouter();
  const { userId } = useUser();
  const { refetchSessions } = useSessionContext();
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
        const response = await service.createSession(prompt, userId);

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

        // Update URL with session_id and refresh session list
        router.push(`/battle?session_id=${response.session_id}`);
        await refetchSessions();
      } catch (error) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error:
            error instanceof Error ? error.message : "Failed to create session",
        }));
      }
    },
    [userId, router, convertResponsesToMessages, refetchSessions]
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

  /**
   * Load session from battles data
   */
  const loadSession = useCallback((sessionId: string, battles: any[]) => {
    // If no sessionId, reset to initial state
    if (!sessionId) {
      setState(initialState);
      return;
    }

    if (battles.length === 0) {
      setState({
        sessionId,
        battleId: null,
        status: "ongoing",
        conversation: [],
        revealedModels: null,
        isLoading: false,
        error: null,
      });
      return;
    }

    // Accumulate ALL conversations from ALL battles in this session
    const allConversations: ConversationMessage[] = [];

    for (const battle of battles) {
      const battleMessages: ConversationMessage[] = battle.conversation.map((msg: any) => {
        if (msg.role === "user") {
          return { role: "user" as const, text: msg.content };
        } else {
          return {
            role: "assistant" as const,
            position: msg.position as "left" | "right",
            text: msg.content,
          };
        }
      });
      allConversations.push(...battleMessages);
    }

    // Get the most recent battle for status and metadata
    const latestBattle = battles[battles.length - 1];

    // Set revealed models if latest battle is voted
    const revealedModels =
      latestBattle.status === "voted"
        ? {
            left: latestBattle.left_model_id,
            right: latestBattle.right_model_id,
          }
        : null;

    setState({
      sessionId,
      battleId: latestBattle.battle_id,
      status: latestBattle.status,
      conversation: allConversations,
      revealedModels,
      isLoading: false,
      error: null,
    });
  }, []);

  return {
    state,
    startSession,
    startNewBattle,
    sendFollowUp,
    submitVote,
    reset,
    loadSession,
  };
}
