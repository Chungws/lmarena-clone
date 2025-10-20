# Next.js Rules

## 🔴 Required Rules (MUST)

### RSC (React Server Components) Pattern
✅ **`page.tsx` = Server Component** (data fetching)
✅ **`*-client.tsx` = Client Component** (UI rendering & interactions)
❌ **DO NOT use useState, useEffect, onClick in page.tsx**

```typescript
// page.tsx (Server) - MUST be async
export default async function Page() {
  const data = await fetchData()  // Server-side
  return <ClientComponent data={data} />
}

// feature-client.tsx (Client) - MUST have "use client"
"use client"
export default function ClientComponent({ data }: Props) {
  const { mutate } = useMutation()
  // UI rendering & interactions
}
```

### Feature Structure Pattern
✅ **Follow consistent file structure**
✅ File order: `_types.ts` → `service.ts` → `use-*.ts` → `*-client.tsx` → `page.tsx`

```bash
app/feature-name/
├── _types.ts              # TypeScript interfaces
├── service.ts             # API calls
├── use-feature.ts         # Custom hooks
├── feature-client.tsx     # Client component
└── page.tsx               # Server component
```

### router.refresh()
✅ **Call `router.refresh()` after mutations** (re-runs page.tsx)
✅ Call from custom hooks (DO NOT call directly in client components)

```typescript
// use-feature.ts
export function useFeature() {
  const router = useRouter()

  const create = async (data) => {
    await service.create(data)
    router.refresh()  // ← Re-run page.tsx!
  }

  return { create }
}
```

### API Client
✅ **Use `apiClient.get/post/put/delete`**
❌ **DO NOT use fetch() directly**

```typescript
// service.ts
import { apiClient } from "@/lib/apiClient"

export async function listBattles() {
  return await apiClient.get("/api/battles")
}
```

## ⚠️ Recommendations (SHOULD)

```bash
# Dev server
npm run dev

# Build
npm run build

# Lint
npm run lint
```

---

💬 **Ask if you have specific Next.js RSC pattern questions**
