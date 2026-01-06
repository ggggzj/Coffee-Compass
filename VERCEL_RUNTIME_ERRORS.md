# Vercel 运行时错误修复指南

## 🔴 当前错误

### 错误 1: NextAuth 配置错误
```
/api/auth/session: 500 Internal Server Error
"There was a problem with the server configuration"
```

### 错误 2: API 端点错误
```
/api/shops: 500 Internal Server Error
```

## 🔍 可能的原因

### 1. 环境变量未设置

NextAuth 需要以下环境变量：
- `NEXTAUTH_URL` - 应用 URL
- `NEXTAUTH_SECRET` - 密钥
- `DATABASE_URL` - 数据库连接字符串

### 2. 数据库连接问题

- `DATABASE_URL` 可能未正确配置
- 数据库可能未初始化
- Prisma Client 可能未生成

### 3. Prisma Client 未生成

在生产环境中，需要确保 Prisma Client 已生成。

## ✅ 解决方案

### 步骤 1: 检查 Vercel 环境变量

在 Vercel Dashboard 中：

1. 进入项目设置
2. 点击 **"Environment Variables"**
3. 确认以下变量已设置：

```
NEXTAUTH_URL=https://your-project.vercel.app
NEXTAUTH_SECRET=你的密钥
DATABASE_URL=你的数据库URL
NEXT_PUBLIC_MAPBOX_TOKEN=你的Mapbox Token
```

### 步骤 2: 检查数据库

确保：
- 数据库已创建（Vercel Postgres 或 Supabase）
- `DATABASE_URL` 正确
- 数据库已初始化（运行了 `db:push`）

### 步骤 3: 确保 Prisma Client 已生成

在 `package.json` 中，`build` 脚本应该包含：

```json
{
  "scripts": {
    "build": "prisma generate && next build"
  }
}
```

### 步骤 4: 检查构建日志

在 Vercel Dashboard 中：
1. 点击失败的部署
2. 查看 **"Build Logs"**
3. 查找错误信息

### 步骤 5: 检查函数日志

在 Vercel Dashboard 中：
1. 点击失败的部署
2. 查看 **"Function Logs"**
3. 查找运行时错误

## 🔧 常见问题修复

### 问题 1: NEXTAUTH_URL 错误

**症状**: NextAuth 配置错误

**解决**:
- 确保 `NEXTAUTH_URL` 是完整的 URL（包括 `https://`）
- 确保 URL 与你的实际域名匹配
- 不要有末尾斜杠

**正确格式**:
```
NEXTAUTH_URL=https://coffee-compass-two.vercel.app
```

### 问题 2: DATABASE_URL 错误

**症状**: API 端点返回 500 错误

**解决**:
- 检查 `DATABASE_URL` 格式是否正确
- 确认数据库服务正在运行
- 确认数据库已初始化

**PostgreSQL URL 格式**:
```
postgresql://user:password@host:port/database?sslmode=require
```

### 问题 3: Prisma Client 未生成

**症状**: 数据库查询失败

**解决**:
- 确保 `build` 脚本包含 `prisma generate`
- 检查构建日志确认 Prisma Client 已生成

### 问题 4: 环境变量未生效

**症状**: 环境变量似乎未设置

**解决**:
- 添加环境变量后，需要重新部署
- 确保环境变量添加到正确的环境（Production/Preview/Development）
- 检查变量名是否正确（区分大小写）

## 📋 检查清单

部署前确认：

- [ ] `NEXTAUTH_URL` 已设置且正确
- [ ] `NEXTAUTH_SECRET` 已设置
- [ ] `DATABASE_URL` 已设置且正确
- [ ] `NEXT_PUBLIC_MAPBOX_TOKEN` 已设置
- [ ] 数据库已创建并初始化
- [ ] `package.json` 中的 `build` 脚本包含 `prisma generate`
- [ ] 所有环境变量都已添加到 Vercel

## 🚀 快速修复步骤

1. **检查环境变量**
   - 在 Vercel Dashboard 中检查所有必需的环境变量

2. **重新部署**
   - 如果修改了环境变量，点击 **"Redeploy"**

3. **检查日志**
   - 查看部署日志和函数日志
   - 查找具体错误信息

4. **验证数据库**
   - 确认数据库连接正常
   - 确认数据库已初始化

## 🔍 调试技巧

### 查看详细错误

在 Vercel Dashboard 中：
1. 点击失败的部署
2. 查看 **"Function Logs"**
3. 查找堆栈跟踪

### 本地测试

在本地测试环境变量：

```bash
# 拉取 Vercel 环境变量
vercel env pull .env.production

# 使用生产环境变量测试
npm run build
```

### 检查 NextAuth 配置

确保 `lib/auth.ts` 中的配置正确：

```typescript
export const { handlers, signIn, signOut, auth } = NextAuth({
  // ... 配置
})
```

## 📝 下一步

1. 检查 Vercel 环境变量设置
2. 确认数据库连接正常
3. 重新部署应用
4. 查看日志确认错误已解决

