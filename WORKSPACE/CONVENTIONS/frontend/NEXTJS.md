# Next.js 규칙

## 🔴 필수 규칙 (MUST)

### RSC (React Server Components) 패턴
✅ **`page.tsx` = Server Component** (데이터 fetching)
✅ **`*-client.tsx` = Client Component** (UI 렌더링 & 인터랙션)
❌ **page.tsx에서 useState, useEffect, onClick 사용 금지**

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

### Feature 구조 (앞장서 따르기)
✅ **`app/(dashboard)/announcements/` 구조 참고 필수**
✅ 파일 순서: `_types.ts` → `service.ts` → `use-*.ts` → `*-client.tsx` → `page.tsx`

### router.refresh()
✅ **Mutation 후 `router.refresh()` 호출** (page.tsx 재실행)
✅ Custom hook에서 호출 (client component에서 직접 호출 금지)

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
✅ **`apiClient.get/post/put/delete` 사용**
❌ **fetch() 직접 사용 금지**

```typescript
// service.ts
import { apiClient } from "@/lib/apiClient"

export async function listSamples() {
  return await apiClient.get("/api/v1/samples")
}
```

## ⚠️ 권장 사항 (SHOULD)

```bash
# 개발 서버
npm run dev

# 빌드
npm run build

# Lint
npm run lint
```

---

💬 **구체적인 Next.js RSC 패턴 질문이 있으면 물어보세요**
