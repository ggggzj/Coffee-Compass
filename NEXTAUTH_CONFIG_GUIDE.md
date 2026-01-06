# NEXTAUTH_SECRET 和 NEXTAUTH_URL 配置指南

## 🔐 NEXTAUTH_SECRET（密钥）

### 这是什么？

`NEXTAUTH_SECRET` 是一个**随机生成的密钥**，用于：
- 加密 JWT token
- 保护会话安全
- 签名 cookies

### 如何生成？

#### 方法 1: 使用 OpenSSL（推荐）

```bash
openssl rand -base64 32
```

这会生成一个类似这样的随机字符串：
```
Xk8p2mN9qR5sT7vW3yZ6bC1dF4gH8jK0lM2nP5rS8tU1vW4xY7zA0bC3dE6fG9h
```

#### 方法 2: 使用 Node.js

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

#### 方法 3: 在线生成器

访问：https://generate-secret.vercel.app/32

### 本地开发环境配置

在你的 `.env` 文件中添加：

```env
NEXTAUTH_SECRET=你生成的随机密钥
```

**示例：**
```env
NEXTAUTH_SECRET=Xk8p2mN9qR5sT7vW3yZ6bC1dF4gH8jK0lM2nP5rS8tU1vW4xY7zA0bC3dE6fG9h
```

### 生产环境配置

**重要**：生产环境必须使用**不同的密钥**！

1. 生成一个新的密钥（不要使用开发环境的密钥）
2. 在 Vercel 项目设置中添加：
   - 变量名：`NEXTAUTH_SECRET`
   - 变量值：你新生成的密钥

---

## 🌐 NEXTAUTH_URL（应用 URL）

### 这是什么？

`NEXTAUTH_URL` 是你的应用的**完整 URL**，NextAuth 用它来：
- 生成回调 URL
- 验证重定向
- 构建 OAuth 回调链接

### 本地开发环境

```env
NEXTAUTH_URL=http://localhost:3000
```

**注意**：
- 必须包含协议（`http://` 或 `https://`）
- 必须包含端口号（本地开发是 `:3000`）
- 不要有末尾斜杠

### 生产环境（Vercel）

部署到 Vercel 后，你会得到一个 URL，格式类似：
```
https://your-project-name.vercel.app
```

#### 步骤 1: 部署到 Vercel

1. 访问 https://vercel.com/new
2. 导入你的 GitHub 仓库
3. 部署项目

#### 步骤 2: 获取你的 Vercel URL

部署完成后，Vercel 会显示你的项目 URL：
- 格式：`https://coffee-compass-xxxxx.vercel.app`
- 或者你设置的自定义域名

#### 步骤 3: 在 Vercel 中设置环境变量

1. 在 Vercel 项目页面
2. 点击 **"Settings"** > **"Environment Variables"**
3. 添加：
   - **变量名**：`NEXTAUTH_URL`
   - **变量值**：`https://your-project-name.vercel.app`（替换为你的实际 URL）
   - **环境**：选择 `Production`、`Preview`、`Development`（建议全选）

#### 步骤 4: 重新部署

添加环境变量后，Vercel 会自动触发重新部署，或者你可以手动点击 **"Redeploy"**。

---

## 📋 完整配置步骤

### 本地开发环境

1. **生成 NEXTAUTH_SECRET**
   ```bash
   openssl rand -base64 32
   ```

2. **编辑 .env 文件**
   ```env
   NEXTAUTH_SECRET=你生成的密钥
   NEXTAUTH_URL=http://localhost:3000
   ```

3. **重启开发服务器**
   ```bash
   npm run dev
   ```

### 生产环境（Vercel）

1. **生成新的 NEXTAUTH_SECRET**（不要使用开发环境的）
   ```bash
   openssl rand -base64 32
   ```

2. **部署到 Vercel**
   - 访问 https://vercel.com/new
   - 导入仓库并部署

3. **获取你的 Vercel URL**
   - 部署完成后，复制你的项目 URL
   - 格式：`https://your-project-name.vercel.app`

4. **在 Vercel 中添加环境变量**
   - 项目设置 > Environment Variables
   - 添加：
     ```
     NEXTAUTH_SECRET=你新生成的密钥
     NEXTAUTH_URL=https://your-project-name.vercel.app
     ```

5. **重新部署**
   - Vercel 会自动重新部署

---

## ✅ 验证配置

### 本地开发

```bash
# 检查环境变量是否设置
grep NEXTAUTH .env

# 应该看到：
# NEXTAUTH_SECRET=...
# NEXTAUTH_URL=http://localhost:3000
```

### 生产环境

1. 访问你的 Vercel 项目设置
2. 检查 Environment Variables
3. 确认两个变量都已设置
4. 访问你的网站，测试登录功能

---

## 🚨 常见错误

### 错误 1: "NEXTAUTH_SECRET is missing"

**原因**：未设置 `NEXTAUTH_SECRET`

**解决**：
- 本地：在 `.env` 文件中添加
- 生产：在 Vercel 环境变量中添加

### 错误 2: "Invalid callback URL"

**原因**：`NEXTAUTH_URL` 配置错误

**解决**：
- 确保 URL 包含协议（`https://`）
- 确保没有末尾斜杠
- 确保 URL 与你的实际域名匹配

### 错误 3: 登录后重定向失败

**原因**：`NEXTAUTH_URL` 与 Google OAuth 配置不匹配

**解决**：
- 确保 Google Cloud Console 中的重定向 URI 与 `NEXTAUTH_URL` 匹配
- 格式：`{NEXTAUTH_URL}/api/auth/callback/google`

---

## 💡 快速命令

### 生成 NEXTAUTH_SECRET

```bash
# 方法 1: OpenSSL
openssl rand -base64 32

# 方法 2: Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

### 检查当前配置

```bash
# 检查本地配置
grep NEXTAUTH .env

# 检查是否已设置（不显示值）
grep -q "NEXTAUTH_SECRET" .env && echo "✅ NEXTAUTH_SECRET 已设置" || echo "❌ 未设置"
grep -q "NEXTAUTH_URL" .env && echo "✅ NEXTAUTH_URL 已设置" || echo "❌ 未设置"
```

---

## 📝 总结

| 变量 | 本地开发 | 生产环境 |
|------|---------|---------|
| **NEXTAUTH_SECRET** | 自己生成（`openssl rand -base64 32`） | 生成新的密钥，在 Vercel 中设置 |
| **NEXTAUTH_URL** | `http://localhost:3000` | `https://your-project.vercel.app`（部署后获取） |

**关键点**：
1. `NEXTAUTH_SECRET` = 自己生成（随机密钥）
2. `NEXTAUTH_URL` = 本地是 `http://localhost:3000`，生产环境是部署后的 Vercel URL

