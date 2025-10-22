"use client";

import { useState, useEffect } from "react";
import { getAnonymousUserId, setAnonymousUserId } from "@/lib/storage";

/**
 * Hook for managing user ID (anonymous or authenticated)
 *
 * Returns:
 * - userId: Current user ID (anonymous UUID)
 * - isAnonymous: Always true for MVP (auth not implemented)
 * - setUserId: Function to update user ID
 */
export function useUser() {
  const [userId, setUserIdState] = useState<string>("");
  const [isAnonymous, setIsAnonymous] = useState<boolean>(true);

  useEffect(() => {
    // Get or generate anonymous user ID
    const id = getAnonymousUserId();
    setUserIdState(id);
    setIsAnonymous(true);
  }, []);

  const setUserId = (newUserId: string) => {
    setAnonymousUserId(newUserId);
    setUserIdState(newUserId);
  };

  return {
    userId,
    isAnonymous,
    setUserId,
  };
}
