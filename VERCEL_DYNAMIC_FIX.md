# Vercel 动态路由错误修复

## 🔴 问题描述

在 Vercel 部署时出现错误：
```
Dynamic server usage: Page couldn't be rendered statically because it used 'headers'.
```

**错误位置**:
- `/api/admin/submissions/route.ts`
- `/api/recommendations/route.ts`

## 🔍 原因分析

Next.js 14 在构建时会尝试静态生成所有路由。但是这些 API 路由使用了 `auth()` 函数，而 `auth()` 内部使用了 `headers()` 来读取请求头，这导致这些路由必须是动态的，不能静态生成。

## ✅ 解决方案

在所有使用 `auth()` 的 API 路由中添加：

```typescript
export const dynamic = 'force-dynamic'
```

这会告诉 Next.js 这些路由是动态的，不应该尝试静态生成。

## 📝 已修复的文件

以下 API 路由已添加 `export const dynamic = 'force-dynamic'`:

1. ✅ `app/api/admin/submissions/route.ts`
2. ✅ `app/api/admin/submissions/[id]/route.ts`
3. ✅ `app/api/admin/reports/route.ts`
4. ✅ `app/api/admin/reports/[id]/route.ts`
5. ✅ `app/api/recommendations/route.ts`
6. ✅ `app/api/favorites/route.ts`
7. ✅ `app/api/reviews/route.ts`
8. ✅ `app/api/visits/route.ts`
9. ✅ `app/api/shops/submit/route.ts`

## 🔧 修复方法

在每个文件的开头（import 语句之后）添加：

```typescript
import { NextRequest, NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
// ... 其他 imports

export const dynamic = 'force-dynamic'  // ← 添加这一行

// ... 路由处理函数
```

## 📚 关于 `export const dynamic`

`export const dynamic = 'force-dynamic'` 是 Next.js 14 的路由段配置选项，用于：

- **强制动态渲染**: 告诉 Next.js 这个路由必须在运行时动态渲染
- **禁用静态生成**: 防止 Next.js 在构建时尝试静态生成这个路由
- **使用场景**: 当路由使用了 `headers()`, `cookies()`, `searchParams` 等动态 API 时

## ✅ 验证

修复后，重新构建应该不会出现这个错误：

```bash
npm run build
```

如果构建成功，说明问题已解决。

## 🚀 下一步

1. ✅ 提交修复
2. ✅ 推送到 GitHub
3. ✅ 在 Vercel 中重新部署

部署应该会成功！

