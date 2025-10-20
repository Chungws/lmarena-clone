# Frontend UI Verification (Playwright MCP) Rules

## 🔴 Required Rules (MUST)

### Manual Verification with Playwright MCP Required for UI Changes
✅ **Use Playwright MCP Server to open browser and manually verify UI changes**
✅ **Check layout and component rendering**
❌ **NEVER commit without UI verification**

### Verification Method (Playwright MCP Server)

**1. Start dev server:**
```bash
cd frontend
npm run dev  # http://localhost:3000
```

**2. Request UI verification from Claude Code:**
```
"Open http://localhost:3000/battle with Playwright and
verify the UI renders correctly"
```

**3. Claude will automatically:**
- `mcp__playwright__browser_navigate` - Open page
- `mcp__playwright__browser_snapshot` - Capture UI state
- `mcp__playwright__browser_take_screenshot` - Save screenshot
- Verify UI elements, validate layout

**4. Verification Checklist:**
- [ ] Does the page load correctly?
- [ ] Is the layout not broken?
- [ ] Are newly added components visible?
- [ ] Does responsive design work properly?
- [ ] Are there no console errors?

## ⚠️ Recommendations (SHOULD)

### E2E Automated Tests (Optional)

For complex user flows requiring E2E automation:

```typescript
// frontend/tests/battle.spec.ts

import { test, expect } from '@playwright/test'

test('user can submit battle prompt', async ({ page }) => {
  // Navigate
  await page.goto('http://localhost:3000/battle')

  // Interact
  await page.fill('textarea[name="prompt"]', 'What is AI?')
  await page.click('button[type="submit"]')

  // Assert
  await expect(page.locator('text=Assistant A')).toBeVisible()
  await expect(page.locator('text=Assistant B')).toBeVisible()
})
```

**Run tests:**
```bash
npx playwright test --headed=false
npx playwright test --ui  # Debugging
```

**Note:**
- E2E tests are optional (nice to have, but not required)
- Manual UI verification with Playwright MCP is more important

---

💬 **Ask if you have specific UI verification questions**
