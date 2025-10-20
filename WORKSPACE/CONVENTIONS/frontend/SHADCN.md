# shadcn/ui Rules

## 🔴 Required Rules (MUST)

### Prefer shadcn/ui Components
✅ **Use shadcn/ui components instead of raw HTML**
❌ **DO NOT use `<button>`, `<div className="border">` directly**

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

### Adding Components
✅ Use `npx shadcn@latest add <component>`
❌ DO NOT manually edit components/ui/ folder

```bash
# Common components
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add table
npx shadcn@latest add form
```

## ⚠️ Recommended Components

- **Button**: All buttons
- **Card**: Containers
- **Dialog**: Modals
- **Table**: Tables
- **Form**: Forms (react-hook-form integration)
- **Input, Select, Checkbox**: Form inputs

---

💬 **Ask if you have specific shadcn/ui component questions**
