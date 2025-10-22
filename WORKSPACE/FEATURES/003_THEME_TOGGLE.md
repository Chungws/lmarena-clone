# Feature: Theme Toggle (Dark/Light Mode Switch)

**Status:** Completed
**Priority:** Low (Quality of Life)
**Estimated Time:** 1 day

---

## Overview

Enable users to switch between dark and light themes according to their preference. Currently, the application only supports dark mode (forced in `layout.tsx`).

**Goals:**
- Provide user choice for theme preference
- Persist theme selection across sessions (localStorage)
- Support system theme detection (optional)
- Seamless theme switching without page reload

**Background:**
- Current implementation: `defaultTheme="dark"` and `enableSystem={false}` in layout.tsx
- next-themes already installed and configured
- Color variables already defined for both light and dark modes in globals.css

---

## Design Decisions

### Theme Provider Configuration
**Decision:** Enable system theme detection + user override
```tsx
// layout.tsx
<ThemeProvider
  attribute="class"
  defaultTheme="system"    // Changed from "dark"
  enableSystem={true}      // Changed from false
>
```
- Respects user's system preference by default
- User can manually override via toggle button
- Preference stored in localStorage by next-themes

### Theme Toggle UI Location
**Decision:** Add to Header component (desktop) and Sidebar (mobile)
- **Desktop:** Theme toggle button in header (top-right area)
- **Mobile:** Theme toggle in sidebar navigation
- Consistent placement with other UI controls (Login button)

### Theme Toggle Button Design
**Decision:** Icon-based toggle button
- **Icons:** Sun icon (light mode), Moon icon (dark mode)
- **Component:** Custom ThemeToggle component using shadcn/ui Button
- **States:**
  - Light mode → Show Sun icon
  - Dark mode → Show Moon icon
  - System mode → Show Monitor icon (optional)

### Animation
**Decision:** Smooth transition with CSS
```css
* {
  transition: background-color 200ms ease, color 200ms ease;
}
```
- Prevents jarring color changes
- 200ms duration for smooth feel

---

## Implementation Phases

### Phase 1: Frontend - Theme Toggle Component

**Tasks:**
- [x] Create `components/theme-toggle.tsx` component
  - [x] Use `useTheme()` hook from next-themes
  - [x] Implement toggle button with Sun/Moon icons
  - [x] Add click handler to cycle through themes (light → dark)
  - [x] Add aria-label for accessibility
- [x] Update `layout.tsx`
  - [x] Change `defaultTheme="dark"` to `defaultTheme="system"`
  - [x] Change `enableSystem={false}` to `enableSystem={true}`
- [x] Update `app/globals.css`
  - [x] Light mode colors already defined
  - [x] Add smooth transition for theme changes (200ms ease)
- [x] Add ThemeToggle to Sidebar component
  - [x] Add to sidebar footer (above collapse toggle)
  - [x] Visible on both desktop and mobile
  - [x] Shows "Toggle Theme" label when expanded
- [x] Test theme switching
  - [x] Verified theme persists across page reloads (localStorage)
  - [x] Verified UI components work in both themes
  - [x] Checked battle page and leaderboard in both themes
- [x] **Playwright MCP Verification**
  - [x] Clicked theme toggle button
  - [x] Verified theme changes visually (light/dark)
  - [x] Navigated between pages and verified theme persists
  - [x] Tested major UI components in both themes

---

## Component Structure

### ThemeToggle Component

```tsx
"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      aria-label="Toggle theme"
    >
      {theme === "dark" ? (
        <Sun className="h-5 w-5" />
      ) : (
        <Moon className="h-5 w-5" />
      )}
    </Button>
  );
}
```

---

## Testing Strategy

**Frontend:**
- **Playwright MCP Manual Verification:**
  1. Open application in browser
  2. Click theme toggle button
  3. Verify theme switches between light/dark
  4. Verify all UI elements display correctly in both themes:
     - Battle cards
     - Leaderboard table
     - Sidebar
     - Header
     - Input fields
     - Buttons
  5. Reload page and verify theme persists
  6. Test system theme detection (if implemented)

**Visual Regression:**
- Take screenshots of key pages in both themes
- Verify no visual bugs or contrast issues

---

## Success Criteria

- [x] Theme toggle button visible in sidebar (both desktop and mobile)
- [x] Clicking toggle switches between light and dark themes
- [x] Theme preference persists across page reloads (localStorage)
- [x] All UI components work correctly in both themes
- [x] No hydration errors or console warnings
- [x] Smooth transition animation when switching themes (200ms)
- [x] System theme detection works (enabled)

---

## Future Enhancements (Post-MVP)

- Add "System" theme option (3-state toggle: light → dark → system)
- Add keyboard shortcut (e.g., Ctrl+Shift+T)
- Add theme selection in user settings page (requires authentication)
- Custom theme colors (theme builder)

---

**Related Documents:**
- [CONVENTIONS/frontend/](../CONVENTIONS/frontend/) - Frontend conventions
- [001_BATTLE_MVP.md](./001_BATTLE_MVP.md) - Battle mode feature (UI components to test)
- [002_LEADERBOARD_MVP.md](./002_LEADERBOARD_MVP.md) - Leaderboard feature (UI components to test)

---

## Phase 2: Battle UI Improvements (Added 2025-01-22)

**Goals:**
- Make vote controls sticky at bottom (floating UI)
- Keep conversation visible after voting
- Optimize space usage (compact sticky controls)

**Implementation:**
- [x] Change battle-client layout to `h-full` flexbox
- [x] Move "Continue Conversation or Vote" to sticky bottom
- [x] Compact UI: 60px textarea, sm buttons, reduced padding
- [x] Fixed height calculation (use h-full instead of calc(100vh - X))
- [x] Add backdrop blur effect for modern look
- [x] Test sticky behavior and conversation persistence

**Files Changed:**
- `app/battle/battle-client.tsx` - Sticky UI implementation

**Total Changes (including Theme):** 247 lines (222+, 175-)

---

**Last Updated:** 2025-01-22 (Theme + Battle UI Completed)
