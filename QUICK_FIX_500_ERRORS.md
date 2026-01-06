# 🚨 快速修复 500 错误

## 当前错误

1. ❌ `/api/auth/session` - 500 错误（NextAuth 配置问题）
2. ❌ `/api/shops` - 500 错误（可能是数据库连接问题）

## 🔧 立即修复步骤

### 步骤 1: 检查 Vercel 环境变量

在 Vercel Dashboard 中：

1. 进入项目设置
2. 点击 **"Environment Variables"**
3. **必须设置以下变量**：

```
NEXTAUTH_URL=https://coffee-compass-two.vercel.app
NEXTAUTH_SECRET=你的密钥（必须生成）
DATABASE_URL=你的数据库连接字符串
NEXT_PUBLIC_MAPBOX_TOKEN=你的Mapbox Token
```

### 步骤 2: 生成 NEXTAUTH_SECRET（如果还没有）

```bash
openssl rand -base64 32
```

复制生成的密钥，添加到 Vercel 环境变量中。

### 步骤 3: 检查 DATABASE_URL

确保：
- ✅ 数据库已创建（Vercel Postgres 或 Supabase）
- ✅ `DATABASE_URL` 格式正确
- ✅ 数据库已初始化（运行了迁移）

### 步骤 4: 重新部署

添加或修改环境变量后：
1. 点击 **"Deployments"**
2. 找到最新的部署
3. 点击 **"Redeploy"**

## 📋 必需的环境变量清单

在 Vercel 中必须设置：

- [ ] `NEXTAUTH_URL` = `https://coffee-compass-two.vercel.app`（你的实际域名）
- [ ] `NEXTAUTH_SECRET` = 生成的密钥
- [ ] `DATABASE_URL` = 数据库连接字符串
- [ ] `NEXT_PUBLIC_MAPBOX_TOKEN` = Mapbox Token

## 🔍 如何检查环境变量

### 在 Vercel Dashboard：

1. 项目页面 → **"Settings"**
2. 点击 **"Environment Variables"**
3. 查看所有变量

### 确认每个变量：

- **NEXTAUTH_URL**: 必须是完整的 URL（包括 `https://`）
- **NEXTAUTH_SECRET**: 必须是有效的密钥（32+ 字符）
- **DATABASE_URL**: 必须是有效的 PostgreSQL 连接字符串

## 🆘 如果仍然出错

### 检查部署日志：

1. 在 Vercel Dashboard
2. 点击失败的部署
3. 查看 **"Function Logs"**
4. 查找具体错误信息

### 常见错误和解决方案：

#### 错误 1: "NEXTAUTH_SECRET is missing"

**解决**: 在 Vercel 中添加 `NEXTAUTH_SECRET` 环境变量

#### 错误 2: "Invalid NEXTAUTH_URL"

**解决**: 
- 确保 `NEXTAUTH_URL` 是完整的 URL
- 格式：`https://your-domain.vercel.app`
- 不要有末尾斜杠

#### 错误 3: "Database connection failed"

**解决**:
- 检查 `DATABASE_URL` 是否正确
- 确认数据库服务正在运行
- 确认数据库已初始化

#### 错误 4: "Prisma Client not generated"

**解决**: 
- 确认 `package.json` 中的 `build` 脚本包含 `prisma generate`
- 检查构建日志确认 Prisma Client 已生成

## ✅ 验证修复

修复后：

1. **重新部署应用**
2. **访问你的网站**
3. **检查浏览器控制台**（应该没有 500 错误）
4. **测试功能**：
   - 访问主页
   - 尝试登录
   - 查看商店列表

## 🚀 快速操作

### 如果环境变量未设置：

1. **生成密钥**:
   ```bash
   openssl rand -base64 32
   ```

2. **在 Vercel 中添加**:
   - `NEXTAUTH_URL` = `https://coffee-compass-two.vercel.app`
   - `NEXTAUTH_SECRET` = 生成的密钥
   - `DATABASE_URL` = 你的数据库 URL
   - `NEXT_PUBLIC_MAPBOX_TOKEN` = 你的 Token

3. **重新部署**

### 如果环境变量已设置但仍出错：

1. **检查变量值是否正确**
2. **确认数据库连接正常**
3. **查看函数日志查找具体错误**
4. **重新部署**

## 📝 下一步

1. ✅ 检查并设置所有必需的环境变量
2. ✅ 重新部署应用
3. ✅ 验证错误已解决
4. ✅ 测试应用功能

