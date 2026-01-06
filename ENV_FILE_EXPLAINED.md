# .env 文件说明

## 📝 什么是 .env 文件？

`.env` 是一个**环境变量配置文件**，用于存储敏感信息和配置数据，比如：
- 数据库连接字符串
- API 密钥
- 密码和密钥
- 第三方服务的凭据

## 🔍 为什么需要 .env 文件？

1. **安全性**：敏感信息不会提交到 Git 仓库
2. **灵活性**：不同环境（开发、生产）可以使用不同的配置
3. **便捷性**：集中管理所有配置

## 📍 .env 文件在哪里？

`.env` 文件位于**项目根目录**，和 `package.json` 在同一级：

```
CoffeeCompass/
├── .env              ← 在这里！
├── .env.example      ← 示例文件（可选）
├── package.json
├── prisma/
├── app/
└── ...
```

## 🔐 如何查看 .env 文件？

### 方法 1: 使用命令行

```bash
# 查看 .env 文件内容（注意：不要显示完整内容，只显示变量名）
cat .env

# 或者使用编辑器打开
code .env        # VS Code
nano .env        # 终端编辑器
vim .env         # Vim 编辑器
```

### 方法 2: 在编辑器中打开

在 VS Code 或其他编辑器中：
1. 在文件浏览器中找到项目根目录
2. 找到 `.env` 文件（可能需要显示隐藏文件）
3. 双击打开

**注意**：`.env` 文件可能被隐藏，需要：
- VS Code: 设置中启用显示隐藏文件
- Finder (Mac): `Cmd + Shift + .` 显示隐藏文件

## 📋 .env 文件示例内容

你的 `.env` 文件应该包含类似这样的内容：

```env
# 数据库连接
DATABASE_URL=postgresql://user:password@localhost:5432/coffeecompass

# Mapbox Token（地图服务）
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ1IjoieW91cnVzZXJuYW1lIiwiYSI6ImNs...

# NextAuth 配置
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-random-secret-key-here

# Google OAuth（可选）
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
```

## 🔍 如何找到这些值？

### 1. DATABASE_URL（数据库连接）

**本地开发环境：**
```env
DATABASE_URL=postgresql://coffeecompass:coffeecompass@localhost:5432/coffeecompass
```

这个值在 `docker-compose.yml` 文件中定义。

**查看方法：**
```bash
# 查看 docker-compose.yml
cat docker-compose.yml
```

### 2. NEXT_PUBLIC_MAPBOX_TOKEN（Mapbox Token）

如果你已经配置了 Mapbox：
- 访问 https://account.mapbox.com/
- 登录你的账号
- 在 "Access tokens" 页面找到你的 token

### 3. NEXTAUTH_SECRET（NextAuth 密钥）

如果还没有，可以生成一个：

```bash
openssl rand -base64 32
```

### 4. GOOGLE_CLIENT_ID 和 GOOGLE_CLIENT_SECRET

如果你配置了 Google OAuth：
- 访问 https://console.cloud.google.com/
- 进入你的项目
- "API 和服务" > "凭据"
- 找到你的 OAuth 客户端 ID

## 🚨 重要提示

### 1. .env 文件不会被提交到 Git

`.env` 文件在 `.gitignore` 中，**不会**被提交到 Git 仓库。这是为了安全！

### 2. 不要分享 .env 文件

`.env` 文件包含敏感信息，**不要**：
- ❌ 提交到 Git
- ❌ 分享给他人
- ❌ 发布到公共平台

### 3. 使用 .env.example 作为模板

如果项目有 `.env.example` 文件，可以：
```bash
# 复制示例文件
cp .env.example .env

# 然后编辑 .env 文件，填入真实值
```

## 📝 部署时如何使用？

部署到 Vercel 时，你需要：

1. **在 Vercel 项目设置中添加环境变量**
   - 不要上传 `.env` 文件
   - 在 Vercel Dashboard 中手动添加每个变量

2. **从本地 .env 复制值**
   - 打开本地的 `.env` 文件
   - 复制每个变量的值
   - 粘贴到 Vercel 的环境变量设置中

## 🔍 快速检查命令

```bash
# 检查 .env 文件是否存在
test -f .env && echo "✅ .env 文件存在" || echo "❌ .env 文件不存在"

# 查看 .env 文件中的变量名（不显示值）
grep -E "^[A-Z_]+=" .env | cut -d '=' -f1

# 检查特定变量是否存在
grep -q "NEXT_PUBLIC_MAPBOX_TOKEN" .env && echo "✅ Mapbox Token 已设置" || echo "❌ Mapbox Token 未设置"
```

## 💡 示例：查看你的 .env 文件

运行以下命令查看你的环境变量配置：

```bash
# 查看所有环境变量名（不显示值，保护隐私）
grep -E "^[A-Z_]+=" .env | cut -d '=' -f1 | sort
```

## ✅ 总结

- `.env` 文件 = 配置文件，存储敏感信息
- 位置 = 项目根目录
- 用途 = 存储数据库连接、API 密钥等
- 安全 = 不会被提交到 Git
- 部署 = 需要手动在 Vercel 中添加这些变量

需要我帮你查看或创建 `.env` 文件吗？

