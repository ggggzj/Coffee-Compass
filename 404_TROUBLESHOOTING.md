# 404 错误排查指南

## 🔍 常见 404 错误原因

### 1. NextAuth 回调路由问题

如果点击 Google 登录后出现 404，可能是回调路由配置问题。

**检查：**
- 确保 Google Cloud Console 中的重定向 URI 正确
- 重定向 URI 必须是：`http://localhost:3000/api/auth/callback/google`

**解决：**
1. 检查 `.env` 文件中的 `NEXTAUTH_URL`
2. 确保值是：`NEXTAUTH_URL=http://localhost:3000`
3. 重启开发服务器

### 2. 访问了不存在的页面

如果直接访问不存在的 URL，会显示 404。

**常见错误：**
- `/auth/signin/` (末尾有斜杠)
- `/api/auth/callback/google` (直接访问回调 URL)
- `/random-page` (不存在的页面)

**解决：**
- 使用正确的 URL
- 主页：`http://localhost:3000`
- 登录页：`http://localhost:3000/auth/signin`
- 注册页：`http://localhost:3000/auth/register`

### 3. NextAuth 路由未正确配置

**检查 NextAuth 路由：**
```bash
curl http://localhost:3000/api/auth/providers
```

应该返回可用的认证提供者列表。

### 4. 开发服务器未完全启动

**检查：**
```bash
# 检查服务器是否运行
curl http://localhost:3000
```

**解决：**
```bash
# 重启开发服务器
npm run dev
```

## 🔧 快速修复步骤

### 步骤 1: 检查当前 URL

确认你访问的 URL 是否正确：
- ✅ `http://localhost:3000` - 主页
- ✅ `http://localhost:3000/auth/signin` - 登录页
- ✅ `http://localhost:3000/auth/register` - 注册页
- ✅ `http://localhost:3000/profile` - 个人资料（需要登录）
- ✅ `http://localhost:3000/submit` - 提交商店（需要登录）

### 步骤 2: 检查 NextAuth 配置

确保 `.env` 文件中有：
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=你的密钥
```

### 步骤 3: 重启服务器

```bash
# 停止服务器（Ctrl+C）
npm run dev
```

### 步骤 4: 清除浏览器缓存

- 清除 cookies
- 硬刷新页面（Cmd+Shift+R 或 Ctrl+Shift+R）

## 📝 Google OAuth 404 特定问题

如果 Google 登录时出现 404：

1. **检查重定向 URI**
   - Google Cloud Console > 凭据 > OAuth 客户端
   - 确认重定向 URI 是：`http://localhost:3000/api/auth/callback/google`

2. **检查环境变量**
   ```bash
   grep GOOGLE .env
   ```

3. **检查 NextAuth 路由**
   ```bash
   curl http://localhost:3000/api/auth/providers
   ```
   如果 Google provider 不存在，说明未配置或配置错误。

## ✅ 验证修复

修复后，验证：

1. **主页可以访问**
   ```bash
   curl http://localhost:3000
   ```

2. **登录页可以访问**
   - 浏览器访问：http://localhost:3000/auth/signin
   - 应该看到登录表单

3. **NextAuth API 正常**
   ```bash
   curl http://localhost:3000/api/auth/providers
   ```

## 🆘 如果问题仍然存在

1. 检查浏览器控制台的错误信息
2. 检查服务器终端的错误日志
3. 确认所有路由文件都存在
4. 尝试清除 `.next` 文件夹并重新构建：
   ```bash
   rm -rf .next
   npm run dev
   ```

