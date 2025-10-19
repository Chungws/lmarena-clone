# Frontend Conventions

이 폴더는 Frontend (Next.js 15 + React 19 + shadcn/ui) 개발 컨벤션을 정의합니다.

## 📚 문서 목록

| 문서 | 규칙 요약 |
|------|---------|
| **[NEXTJS.md](./NEXTJS.md)** | RSC 패턴, router.refresh(), apiClient 사용 |
| **[SHADCN.md](./SHADCN.md)** | shadcn/ui 우선 사용, Raw HTML 금지 |
| **[TESTING.md](./TESTING.md)** | Playwright MCP UI 검증, UI 변경 시 필수 |

## 🔴 CRITICAL 체크리스트

Frontend 작업 전 반드시 확인:

```
[ ] RSC 패턴: page.tsx (server) vs *-client.tsx (client) 분리 (NEXTJS.md)
[ ] announcements/ 구조: 참고 패턴 따르기 (NEXTJS.md)
[ ] shadcn/ui: Raw HTML 대신 shadcn 컴포넌트 사용 (SHADCN.md)
[ ] Playwright MCP: UI 변경 시 수동 검증 필수! (TESTING.md)
```

## ⚡ Quick Start

```bash
cd frontend

# 환경 설정
npm install
npm run dev  # http://localhost:3000

# 새 기능 추가 (announcements/ 구조 참고)
mkdir -p app/\(dashboard\)/feature
touch app/\(dashboard\)/feature/{_types.ts,service.ts,use-feature.ts,feature-client.tsx,page.tsx}
npx shadcn@latest add button card dialog

# 커밋 전 체크
npm run lint
# UI 변경 시: Playwright MCP로 수동 검증 필수! (TESTING.md 참고)
```

## 📋 언제 읽어야 하나?

| 상황 | 문서 |
|------|------|
| 새 페이지/기능 추가 | NEXTJS.md |
| UI 컴포넌트 선택 | SHADCN.md |
| UI 검증 방법 | TESTING.md |
| 커밋 전 (UI 변경 시 필수!) | TESTING.md |

## 🎯 참고 구조

**항상 `announcements/` 폴더 구조를 참고하세요:**

```bash
app/(dashboard)/announcements/
├── page.tsx                      # Server Component (데이터 fetching)
├── announcements-client.tsx      # Client Component (UI 렌더링)
├── service.ts                    # API 통신
├── use-announcements.ts          # Custom hook (mutations)
├── _types.ts                     # TypeScript types
└── announcement-create-modal.tsx # Modal component
```

---

**상위 문서:** CONVENTIONS/README.md

💬 **구체적인 질문이 있으면 물어보세요 (context7 활용 가능)**
