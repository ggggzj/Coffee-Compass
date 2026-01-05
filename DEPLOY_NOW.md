# 🚀 立即部署 CoffeeCompass

## ✅ 当前状态

- ✅ Git 仓库已配置：https://github.com/ggggzj/Coffee-Compass.git
- ✅ 本地数据库运行中
- ✅ Mapbox Token 已配置
- ✅ NextAuth Secret 已配置
- ⚠️ Google OAuth 未配置（可选）

## 🚀 5分钟快速部署（Vercel）

### 步骤 1: 提交并推送代码（1分钟）

```bash
# 提交所有更改
git add .
git commit -m "Ready for deployment"

# 推送到 GitHub
git push origin main
```

### 步骤 2: 部署到 Vercel（2分钟）

1. **访问 Vercel**
   - 打开：https://vercel.com/new
   - 使用 GitHub 账号登录
   - 点击 **"Import"** 选择 `Coffee-Compass` 仓库

2. **配置项目**
   - Framework: Next.js（自动检测）
   - Build Command: `prisma generate && next build`（已自动配置）
   - 其他设置保持默认

3. **添加环境变量**
   点击 **"Environment Variables"**，添加以下变量：

   ```
   # 数据库（稍后配置）
   DATABASE_URL=稍后添加
   
   # Mapbox（从你的 .env 复制）
   NEXT_PUBLIC_MAPBOX_TOKEN=你的Mapbox Token
   
   # NextAuth（从你的 .env 复制）
   NEXTAUTH_SECRET=你的NEXTAUTH_SECRET
   NEXTAUTH_URL=https://your-project.vercel.app（部署后更新）
   
   # Google OAuth（可选，如果配置了）
   GOOGLE_CLIENT_ID=你的Google客户端ID（如果有）
   GOOGLE_CLIENT_SECRET=你的Google客户端密钥（如果有）
   ```

4. **部署**
   - 点击 **"Deploy"**
   - 等待 2-5 分钟完成部署

### 步骤 3: 配置生产数据库（1分钟）

**选项 A: 使用 Vercel Postgres（推荐）**

1. 部署完成后，在 Vercel 项目页面
2. 点击 **"Storage"** 标签
3. 点击 **"Create Database"** > **"Postgres"**
4. 创建后，复制数据库 URL
5. 在 **"Settings"** > **"Environment Variables"** 中：
   - 更新 `DATABASE_URL` 为 Postgres URL
   - 或者使用 `${{Postgres.DATABASE_URL}}`

**选项 B: 使用 Supabase（免费）**

1. 访问 https://supabase.com/
2. 点击 **"New Project"**
3. 填写项目信息
4. 等待数据库创建完成
5. 在 **"Settings"** > **"Database"** 中复制连接字符串
6. 在 Vercel 中设置 `DATABASE_URL`

### 步骤 4: 初始化生产数据库（1分钟）

部署后，需要运行数据库迁移：

**使用 Vercel CLI（推荐）：**

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录 Vercel
vercel login

# 链接到你的项目
vercel link

# 拉取生产环境变量
vercel env pull .env.production

# 运行数据库迁移
npm run db:push

# 填充种子数据
npm run db:seed
```

**或使用 Supabase SQL Editor：**

如果使用 Supabase：
1. 访问 Supabase Dashboard
2. 点击 **"SQL Editor"**
3. 运行以下命令（从 Prisma schema 生成）

### 步骤 5: 更新 Google OAuth（如果使用）（1分钟）

1. **访问 Google Cloud Console**
   - https://console.cloud.google.com/
   - 选择你的项目

2. **更新 OAuth 客户端**
   - 进入 **"API 和服务"** > **"凭据"**
   - 编辑你的 OAuth 客户端 ID
   - 添加生产环境 URI：
     - **JavaScript 来源**: `https://your-project.vercel.app`
     - **重定向 URI**: `https://your-project.vercel.app/api/auth/callback/google`

3. **更新 Vercel 环境变量**
   - 在 Vercel 项目设置中
   - 更新 `NEXTAUTH_URL` 为你的实际 Vercel 域名
   - 重新部署（会自动触发）

## 📋 部署后检查清单

- [ ] 网站可以访问（https://your-project.vercel.app）
- [ ] 主页加载正常
- [ ] 地图显示正常
- [ ] 可以注册账户
- [ ] 可以登录
- [ ] 数据库连接正常
- [ ] Google 登录可以工作（如果配置了）

## 🔗 获取你的公开链接

部署完成后，Vercel 会给你一个链接：
- 格式：`https://coffee-compass-xxxxx.vercel.app`
- 或者你可以设置自定义域名

## 🎯 快速命令

```bash
# 1. 提交代码
git add . && git commit -m "Ready for deployment" && git push

# 2. 访问 Vercel 部署
# https://vercel.com/new

# 3. 部署后初始化数据库
vercel env pull .env.production
npm run db:push
npm run db:seed
```

## 📝 重要提示

1. **环境变量**
   - 确保所有环境变量都在 Vercel 中设置
   - `NEXTAUTH_URL` 必须是完整的生产 URL（包括 https://）

2. **数据库**
   - 生产数据库需要单独配置
   - 推荐使用 Vercel Postgres 或 Supabase

3. **Google OAuth**
   - 需要在 Google Cloud Console 中添加生产环境的重定向 URI
   - 格式：`https://your-domain.vercel.app/api/auth/callback/google`

4. **构建**
   - Vercel 会自动运行 `prisma generate && next build`
   - 如果构建失败，检查错误日志

## 🆘 如果遇到问题

1. **构建失败**
   - 检查 Vercel 构建日志
   - 确保所有依赖都在 `package.json` 中

2. **数据库连接失败**
   - 检查 `DATABASE_URL` 环境变量
   - 确认数据库服务正在运行

3. **404 错误**
   - 检查 `NEXTAUTH_URL` 是否正确
   - 确认路由配置正确

## ✅ 完成！

部署完成后，你的应用就可以通过公网访问了！

需要我帮你检查部署配置吗？

