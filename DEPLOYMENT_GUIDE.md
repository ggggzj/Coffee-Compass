# CoffeeCompass 部署指南

## 🚀 部署选项

### 选项 1: Vercel（推荐 - 最简单）

Vercel 是 Next.js 的官方部署平台，最适合 Next.js 应用。

#### 步骤 1: 准备代码

1. **确保代码已提交到 Git**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push
   ```

2. **创建 GitHub 仓库**（如果还没有）
   - 访问 https://github.com/new
   - 创建新仓库
   - 推送代码到 GitHub

#### 步骤 2: 部署到 Vercel

1. **访问 Vercel**
   - 访问：https://vercel.com/
   - 使用 GitHub 账号登录
   - 点击 **"Add New Project"**

2. **导入项目**
   - 选择你的 GitHub 仓库
   - 点击 **"Import"**

3. **配置项目**
   - **Framework Preset**: Next.js（自动检测）
   - **Root Directory**: `./`（默认）
   - **Build Command**: `npm run build`（默认）
   - **Output Directory**: `.next`（默认）

4. **配置环境变量**
   点击 **"Environment Variables"**，添加以下变量：

   ```
   DATABASE_URL=你的生产数据库URL
   NEXT_PUBLIC_MAPBOX_TOKEN=你的Mapbox Token
   NEXTAUTH_URL=https://your-project.vercel.app
   NEXTAUTH_SECRET=你的随机密钥
   GOOGLE_CLIENT_ID=你的Google客户端ID
   GOOGLE_CLIENT_SECRET=你的Google客户端密钥
   ```

5. **部署**
   - 点击 **"Deploy"**
   - 等待部署完成（2-5分钟）

#### 步骤 3: 配置生产数据库

**选项 A: 使用 Vercel Postgres（推荐）**

1. 在 Vercel 项目页面，点击 **"Storage"** 标签
2. 点击 **"Create Database"** > **"Postgres"**
3. 创建数据库后，会自动添加 `POSTGRES_URL` 环境变量
4. 更新 `DATABASE_URL` 环境变量为 Postgres URL

**选项 B: 使用外部数据库服务**

推荐服务：
- **Supabase**（免费）：https://supabase.com/
- **Neon**（免费）：https://neon.tech/
- **Railway**（免费额度）：https://railway.app/

#### 步骤 4: 初始化生产数据库

部署后，需要初始化数据库：

1. **使用 Vercel CLI**
   ```bash
   npm i -g vercel
   vercel login
   vercel link
   vercel env pull .env.production
   ```

2. **运行数据库迁移**
   ```bash
   # 使用生产环境的 DATABASE_URL
   DATABASE_URL="你的生产数据库URL" npm run db:push
   DATABASE_URL="你的生产数据库URL" npm run db:seed
   ```

   或者使用 Vercel 的远程执行：
   ```bash
   vercel env pull .env.production
   npm run db:push
   npm run db:seed
   ```

#### 步骤 5: 更新 Google OAuth 配置

1. **访问 Google Cloud Console**
   - https://console.cloud.google.com/
   - 选择你的项目

2. **更新 OAuth 客户端**
   - 进入 **"API 和服务"** > **"凭据"**
   - 编辑你的 OAuth 客户端 ID
   - 添加生产环境的 URI：
     - **已获授权的 JavaScript 来源**: `https://your-project.vercel.app`
     - **已获授权的重定向 URI**: `https://your-project.vercel.app/api/auth/callback/google`
   - 保存更改

### 选项 2: Railway（简单，包含数据库）

Railway 提供数据库和部署一体化服务。

#### 步骤 1: 准备代码

同 Vercel 步骤 1

#### 步骤 2: 部署到 Railway

1. **访问 Railway**
   - https://railway.app/
   - 使用 GitHub 登录

2. **创建项目**
   - 点击 **"New Project"**
   - 选择 **"Deploy from GitHub repo"**
   - 选择你的仓库

3. **添加数据库**
   - 点击 **"+ New"** > **"Database"** > **"Add PostgreSQL"**
   - Railway 会自动创建数据库

4. **配置环境变量**
   - 点击项目设置
   - 添加环境变量：
     ```
     DATABASE_URL=${{Postgres.DATABASE_URL}}
     NEXT_PUBLIC_MAPBOX_TOKEN=你的Mapbox Token
     NEXTAUTH_URL=https://your-project.up.railway.app
     NEXTAUTH_SECRET=你的随机密钥
     GOOGLE_CLIENT_ID=你的Google客户端ID
     GOOGLE_CLIENT_SECRET=你的Google客户端密钥
     ```

5. **配置构建命令**
   - 在项目设置中，设置：
     - **Build Command**: `npm run build`
     - **Start Command**: `npm start`

6. **部署**
   - Railway 会自动部署
   - 等待部署完成

#### 步骤 3: 初始化数据库

Railway 提供数据库终端访问：

1. 点击数据库服务
2. 点击 **"Query"** 标签
3. 或者使用 Railway CLI：
   ```bash
   npm i -g @railway/cli
   railway login
   railway link
   railway run npm run db:push
   railway run npm run db:seed
   ```

### 选项 3: Render

#### 步骤 1: 准备代码

同 Vercel 步骤 1

#### 步骤 2: 部署到 Render

1. **访问 Render**
   - https://render.com/
   - 使用 GitHub 登录

2. **创建 Web Service**
   - 点击 **"New +"** > **"Web Service"**
   - 连接你的 GitHub 仓库

3. **配置服务**
   - **Name**: `coffeecompass`
   - **Environment**: `Node`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`

4. **添加 PostgreSQL 数据库**
   - 点击 **"New +"** > **"PostgreSQL"**
   - 创建数据库
   - 复制数据库 URL

5. **配置环境变量**
   ```
   DATABASE_URL=你的Render数据库URL
   NEXT_PUBLIC_MAPBOX_TOKEN=你的Mapbox Token
   NEXTAUTH_URL=https://coffeecompass.onrender.com
   NEXTAUTH_SECRET=你的随机密钥
   GOOGLE_CLIENT_ID=你的Google客户端ID
   GOOGLE_CLIENT_SECRET=你的Google客户端密钥
   ```

6. **部署**
   - 点击 **"Create Web Service"**
   - 等待部署完成

## 📋 部署前检查清单

### 代码准备
- [ ] 代码已提交到 Git
- [ ] 已推送到 GitHub/GitLab
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 没有硬编码的密钥或敏感信息

### 环境变量准备
- [ ] `DATABASE_URL` - 生产数据库 URL
- [ ] `NEXT_PUBLIC_MAPBOX_TOKEN` - Mapbox Token
- [ ] `NEXTAUTH_URL` - 生产环境 URL
- [ ] `NEXTAUTH_SECRET` - 随机密钥（使用 `openssl rand -base64 32` 生成）
- [ ] `GOOGLE_CLIENT_ID` - Google OAuth 客户端 ID
- [ ] `GOOGLE_CLIENT_SECRET` - Google OAuth 客户端密钥

### 数据库准备
- [ ] 生产数据库已创建
- [ ] 数据库连接字符串已准备好
- [ ] 数据库迁移脚本已准备好

### Google OAuth 配置
- [ ] Google Cloud Console 项目已创建
- [ ] OAuth 客户端已创建
- [ ] 生产环境的重定向 URI 已添加

## 🔧 部署后步骤

### 1. 初始化数据库

```bash
# 使用生产环境的 DATABASE_URL
export DATABASE_URL="你的生产数据库URL"
npm run db:generate
npm run db:push
npm run db:seed
```

### 2. 验证部署

- [ ] 网站可以访问
- [ ] 主页加载正常
- [ ] 地图显示正常
- [ ] 可以注册和登录
- [ ] Google 登录可以工作（如果配置了）

### 3. 设置自定义域名（可选）

**Vercel:**
1. 项目设置 > Domains
2. 添加你的域名
3. 按照说明配置 DNS

**Railway:**
1. 项目设置 > Settings
2. 添加自定义域名
3. 配置 DNS 记录

## 🆘 常见部署问题

### 问题 1: 构建失败

**原因**: 依赖问题或构建错误

**解决**:
```bash
# 本地测试构建
npm run build
```

### 问题 2: 数据库连接失败

**原因**: DATABASE_URL 配置错误

**解决**:
- 检查环境变量是否正确设置
- 确认数据库服务正在运行
- 检查数据库 URL 格式

### 问题 3: Mapbox 地图不显示

**原因**: NEXT_PUBLIC_MAPBOX_TOKEN 未设置

**解决**:
- 确认环境变量已设置
- 确认变量名正确（`NEXT_PUBLIC_` 前缀）

### 问题 4: NextAuth 错误

**原因**: NEXTAUTH_URL 或 NEXTAUTH_SECRET 未设置

**解决**:
- 确认 NEXTAUTH_URL 是完整的生产 URL（包括 https://）
- 确认 NEXTAUTH_SECRET 已设置

## 📊 推荐部署方案对比

| 平台 | 难度 | 数据库 | 免费额度 | 推荐度 |
|------|------|--------|----------|--------|
| Vercel | ⭐ 简单 | 需单独配置 | 100GB 带宽/月 | ⭐⭐⭐⭐⭐ |
| Railway | ⭐⭐ 中等 | 内置 PostgreSQL | $5 免费额度 | ⭐⭐⭐⭐ |
| Render | ⭐⭐ 中等 | 需单独配置 | 750 小时/月 | ⭐⭐⭐ |
| 自建服务器 | ⭐⭐⭐⭐ 困难 | 需自己配置 | 无 | ⭐⭐ |

## 🎯 快速部署（Vercel - 推荐）

### 最快方式（5分钟）

1. **推送代码到 GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **访问 Vercel**
   - https://vercel.com/new
   - 导入 GitHub 仓库

3. **配置环境变量**
   - 添加所有必需的环境变量
   - 使用 Vercel Postgres（自动配置）

4. **部署**
   - 点击 Deploy
   - 等待完成

5. **初始化数据库**
   ```bash
   vercel env pull .env.production
   npm run db:push
   npm run db:seed
   ```

6. **更新 Google OAuth**
   - 添加生产环境的重定向 URI
   - 更新环境变量

## ✅ 部署完成检查

部署成功后，确认：

- [ ] 网站可以访问（https://your-domain.com）
- [ ] 主页加载正常
- [ ] 地图显示正常
- [ ] 可以注册账户
- [ ] 可以登录
- [ ] Google 登录可以工作
- [ ] 数据库连接正常
- [ ] 所有功能正常工作

## 📝 生产环境注意事项

1. **安全性**
   - 确保所有环境变量已设置
   - 不要提交 `.env` 文件
   - 使用强密码和密钥

2. **性能**
   - 启用 Vercel 的 Edge Functions（如果使用）
   - 配置 CDN（Vercel 自动配置）
   - 优化图片和资源

3. **监控**
   - 设置错误监控（如 Sentry）
   - 监控数据库性能
   - 设置日志记录

4. **备份**
   - 定期备份数据库
   - 使用版本控制管理代码

## 🎉 完成！

部署完成后，你的应用就可以通过公网访问了！

需要我帮你选择最适合的部署平台吗？

