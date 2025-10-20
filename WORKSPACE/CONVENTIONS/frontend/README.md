# Frontend Conventions

This folder defines Frontend development conventions (Next.js 15 + React 19 + shadcn/ui).

## 📚 Document List

| Document | Rule Summary |
|----------|--------------|
| **[NEXTJS.md](./NEXTJS.md)** | RSC pattern, router.refresh(), apiClient usage |
| **[SHADCN.md](./SHADCN.md)** | Use shadcn/ui components, NO raw HTML |
| **[TESTING.md](./TESTING.md)** | Playwright MCP UI verification, required for UI changes |

## 🔴 CRITICAL Checklist

Must check before Frontend work:

```
[ ] RSC pattern: page.tsx (server) vs *-client.tsx (client) separation (NEXTJS.md)
[ ] Feature structure: Follow recommended pattern (NEXTJS.md)
[ ] shadcn/ui: Use shadcn components instead of raw HTML (SHADCN.md)
[ ] Playwright MCP: Manual verification required for UI changes! (TESTING.md)
```

## ⚡ Quick Start

```bash
cd frontend

# Setup
npm install
npm run dev  # http://localhost:3000

# Add new feature
mkdir -p app/battle
touch app/battle/{_types.ts,service.ts,use-battle.ts,battle-client.tsx,page.tsx}
npx shadcn@latest add button card dialog

# Pre-commit check
npm run lint
# For UI changes: Manual Playwright MCP verification required! (see TESTING.md)
```

## 📋 When to Read?

| Situation | Document |
|-----------|----------|
| Add new page/feature | NEXTJS.md |
| Choose UI components | SHADCN.md |
| UI verification method | TESTING.md |
| Before commit (UI changes required!) | TESTING.md |

## 🎯 Recommended Feature Structure

```bash
app/feature-name/
├── page.tsx              # Server Component (data fetching)
├── feature-client.tsx    # Client Component (UI rendering)
├── service.ts            # API communication
├── use-feature.ts        # Custom hook (mutations)
├── _types.ts             # TypeScript types
└── components/           # Feature-specific components (optional)
```

---

**Parent Document:** CONVENTIONS/README.md

💬 **Ask if you have specific questions (context7 available)**
