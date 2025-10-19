# shadcn/ui 규칙

## 🔴 필수 규칙 (MUST)

### shadcn/ui 우선 사용
✅ **Raw HTML 대신 shadcn/ui 컴포넌트 사용**
❌ **`<button>`, `<div className="border">` 등 직접 사용 금지**

```tsx
// ❌ WRONG
<div className="border p-4">
  <button className="bg-blue-500 px-4 py-2">Click</button>
</div>

// ✅ CORRECT
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

<Card>
  <CardContent>
    <Button>Click</Button>
  </CardContent>
</Card>
```

### 컴포넌트 추가
✅ `npx shadcn@latest add <component>` 사용
❌ components/ui/ 폴더 직접 수정 금지

```bash
# 자주 사용하는 컴포넌트
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add table
npx shadcn@latest add form
```

## ⚠️ 권장 컴포넌트

- **Button**: 모든 버튼
- **Card**: 컨테이너
- **Dialog**: 모달
- **Table**: 테이블
- **Form**: 폼 (react-hook-form 통합)
- **Input, Select, Checkbox**: 폼 입력

---

💬 **구체적인 shadcn/ui 컴포넌트 질문이 있으면 물어보세요**
