# Frontend UI 검증 (Playwright MCP) 규칙

## 🔴 필수 규칙 (MUST)

### UI 변경 시 Playwright MCP로 검증 필수
✅ **UI 변경 시 Playwright MCP Server로 브라우저 열어서 수동 검증**
✅ **레이아웃, 컴포넌트 렌더링 확인**
❌ **UI 확인 없이 커밋 절대 금지**

### 검증 방법 (Playwright MCP Server)

**1. 개발 서버 실행:**
```bash
cd frontend
npm run dev  # http://localhost:3000
```

**2. Claude Code에게 UI 검증 요청:**
```
"http://localhost:3000/your-feature 페이지를 Playwright로 열어서
UI가 제대로 렌더링되는지 확인해줘"
```

**3. Claude가 자동으로:**
- `mcp__playwright__browser_navigate` - 페이지 열기
- `mcp__playwright__browser_snapshot` - UI 상태 캡처
- `mcp__playwright__browser_take_screenshot` - 스크린샷 저장
- UI 요소 확인, 레이아웃 검증

**4. 확인 사항:**
- [ ] 페이지가 정상적으로 로드되는가?
- [ ] 레이아웃이 깨지지 않았는가?
- [ ] 새로 추가한 컴포넌트가 보이는가?
- [ ] 반응형 디자인이 제대로 작동하는가?
- [ ] Console 에러가 없는가?

## ⚠️ 권장 사항 (SHOULD)

### E2E 자동화 테스트 (선택적)

E2E 자동화 테스트가 필요한 경우 (복잡한 사용자 플로우):

```typescript
// frontend/tests/feature.spec.ts

import { test, expect } from '@playwright/test'

test('user can create announcement', async ({ page }) => {
  // Navigate
  await page.goto('http://localhost:3000/announcements')

  // Interact
  await page.click('button[aria-label="Create"]')
  await page.fill('input[name="title"]', 'Test')
  await page.click('button[type="submit"]')

  // Assert
  await expect(page.locator('text=Success')).toBeVisible()
})
```

**실행:**
```bash
npx playwright test --headed=false
npx playwright test --ui  # 디버깅
```

**주의:**
- E2E 테스트는 선택적 (있으면 좋지만 필수는 아님)
- UI 검증은 Playwright MCP로 수동 확인이 더 중요

---

💬 **구체적인 UI 검증 방법 질문이 있으면 물어보세요**
