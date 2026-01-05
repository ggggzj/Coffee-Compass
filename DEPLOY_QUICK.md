# 🚀 快速部署指南（5分钟）

## 推荐方案：Vercel（最简单）

### 步骤 1: 准备代码（1分钟）

```bash
# 1. 确保代码已提交
git add .
git commit -m "Ready for deployment"

# 2. 推送到 GitHub（如果还没有）
# 访问 https://github.com/new 创建新仓库
git remote add origin https://github.com/你的用户名/CoffeeCompass.git
git push -u origin main
```

### 步骤 2: 部署到 Vercel（2分钟）

1. **访问 Vercel**
   - https://vercel.com/new
   - 使用 GitHub 账号登录

2. **导入项目**
   - 点击 **"Import"** 选择你的仓库
   - 点击 **"Import"** 确认

3. **配置项目**
   - Framework: Next.js（自动检测）
   - Root Directory: `./`
   - Build Command: `prisma generate && next build`（自动检测）
   - Output Directory: `.next`（自动检测）

4. **添加环境变量**
   点击 **"Environment Variables"**，添加：

   ```
   DATABASE_URL=稍后配置
   NEXT_PUBLIC_MAPBOX_TOKEN=你的Mapbox Token
   NEXTAUTH_URL=https://your-project.vercel.app（部署后更新）
   NEXTAUTH_SECRET=生成一个随机密钥
   GOOGLE_CLIENT_ID=你的Google客户端ID
   GOOGLE_CLIENT_SECRET=你的Google客户端密钥
   ```

5. **部署**
   - 点击 **"Deploy"**
   - 等待 2-5 分钟

### 步骤 3: 配置数据库（1分钟）

**使用 Vercel Postgres（推荐）：**

1. 部署完成后，在 Vercel 项目页面
2. 点击 **"Storage"** 标签
3. 点击 **"Create Database"** > **"Postgres"**
4. 创建后，会自动添加 `POSTGRES_URL` 环境变量
5. 更新 `DATABASE_URL` 环境变量：
   - 点击 **"Settings"** > **"Environment Variables"**
   - 编辑 `DATABASE_URL`，设置为 `${{Postgres.DATABASE_URL}}`
   - 或者直接复制 Postgres URL

**或使用 Supabase（免费替代）：**

1. 访问 https://supabase.com/
2. 创建新项目
3. 复制数据库 URL
4. 在 Vercel 中设置 `DATABASE_URL`

### 步骤 4: 初始化数据库（1分钟）

部署后，需要运行数据库迁移：

**方法 1: 使用 Vercel CLI**

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录
vercel login

# 链接项目
vercel link

# 拉取环境变量
vercel env pull .env.production

# 运行迁移
npm run db:push
npm run db:seed
```

**方法 2: 使用 Vercel Dashboard**

1. 在 Vercel 项目页面，点击 **"Deployments"**
2. 点击最新的部署
3. 点击 **"Functions"** 标签
4. 创建一个临时 API 路由来运行迁移（不推荐，但可以）

**方法 3: 使用 Supabase SQL Editor**

如果使用 Supabase：
1. 访问 Supabase Dashboard
2. 点击 **"SQL Editor"**
3. 运行 Prisma schema 生成的 SQL

### 步骤 5: 更新 Google OAuth（1分钟）

1. **访问 Google Cloud Console**
   - https://console.cloud.google.com/
   - 选择你的项目

2. **更新 OAuth 客户端**
   - **"API 和服务"** > **"凭据"**
   - 编辑你的 OAuth 客户端 ID
   - 添加生产环境 URI：
     - JavaScript 来源: `https://your-project.vercel.app`
     - 重定向 URI: `https://your-project.vercel.app/api/auth/callback/google`

3. **更新 Vercel 环境变量**
   - 在 Vercel 项目设置中
   - 更新 `NEXTAUTH_URL` 为你的实际域名
   - 重新部署（Vercel 会自动触发）

## ✅ 部署完成检查

- [ ] 网站可以访问
- [ ] 主页加载正常
- [ ] 地图显示正常
- [ ] 可以注册账户
- [ ] 可以登录
- [ ] Google 登录可以工作

## 🔗 获取你的链接

部署完成后，Vercel 会给你一个链接：
- 格式：`https://your-project-name.vercel.app`
- 这个链接可以分享给任何人访问

## 📝 自定义域名（可选）

1. 在 Vercel 项目设置中
2. 点击 **"Domains"**
3. 添加你的域名
4. 按照说明配置 DNS

## 🆘 如果遇到问题

查看 `DEPLOYMENT_GUIDE.md` 获取详细的故障排除指南。

