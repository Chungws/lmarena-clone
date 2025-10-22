/**
 * LocalStorage utilities for llmbattler
 *
 * Manages anonymous user ID and other client-side data
 */

const STORAGE_KEYS = {
  USER_ID: "llmbattler_user_id",
} as const;

/**
 * Generate UUID v4
 */
function generateUUID(): string {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Get anonymous user ID from localStorage
 * Creates new UUID if not exists
 */
export function getAnonymousUserId(): string {
  if (typeof window === "undefined") {
    return ""; // SSR fallback
  }

  let userId = localStorage.getItem(STORAGE_KEYS.USER_ID);

  if (!userId) {
    userId = generateUUID();
    localStorage.setItem(STORAGE_KEYS.USER_ID, userId);
  }

  return userId;
}

/**
 * Set anonymous user ID to localStorage
 */
export function setAnonymousUserId(userId: string): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.setItem(STORAGE_KEYS.USER_ID, userId);
}

/**
 * Clear anonymous user ID from localStorage
 */
export function clearAnonymousUserId(): void {
  if (typeof window === "undefined") {
    return;
  }

  localStorage.removeItem(STORAGE_KEYS.USER_ID);
}
