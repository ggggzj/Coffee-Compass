# 用户认证系统设置指南

## 第一步：安装依赖

首先需要安装必要的 npm 包：

```bash
npm install bcryptjs @types/bcryptjs
```

## 第二步：配置环境变量

在 `.env` 文件中添加以下环境变量：

```env
# NextAuth 配置
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-random-secret-key-here

# Google OAuth (可选，如果使用 Google 登录)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

生成 `NEXTAUTH_SECRET`：
```bash
openssl rand -base64 32
```

## 第三步：更新数据库

运行 Prisma 迁移以创建新的数据库表：

```bash
# 生成 Prisma Client
npm run db:generate

# 推送数据库 schema 更改
npm run db:push
```

这将创建以下新表：
- `User` - 用户表
- `Account` - OAuth 账户表（NextAuth 需要）
- `Session` - 会话表（NextAuth 需要）
- `VerificationToken` - 验证令牌表（NextAuth 需要）
- `Review` - 评论表
- `Favorite` - 收藏表
- `VisitHistory` - 访问历史表
- `Report` - 举报表
- `ShopSubmission` - 商店提交表

## 第四步：创建管理员用户（可选）

如果需要创建管理员用户，可以通过 Prisma Studio 或直接运行 SQL：

```bash
npm run db:studio
```

然后在 Prisma Studio 中手动创建用户，或使用以下 SQL（需要先安装 bcryptjs）：

```sql
-- 密码是 "admin123" (已哈希)
INSERT INTO "User" (id, email, password, role, "createdAt", "updatedAt")
VALUES (
  gen_random_uuid(),
  'admin@example.com',
  '$2a$10$YourHashedPasswordHere',
  'admin',
  NOW(),
  NOW()
);
```

## 第五步：测试认证系统

1. 启动开发服务器：
```bash
npm run dev
```

2. 访问注册页面：http://localhost:3000/auth/register
3. 创建新账户
4. 登录：http://localhost:3000/auth/signin

## 功能说明

### 已实现的功能

1. **用户认证**
   - 邮箱/密码注册和登录
   - Google OAuth 登录（需要配置）
   - 会话管理

2. **用户相关 API**
   - `/api/auth/register` - 用户注册
   - `/api/auth/[...nextauth]` - NextAuth 认证路由
   - `/api/favorites` - 收藏管理（GET, POST, DELETE）
   - `/api/reviews` - 评论管理（GET, POST）
   - `/api/visits` - 访问历史（GET, POST）

3. **前端更新**
   - 登录/注册页面
   - Navigation 组件显示登录状态
   - Profile 页面使用真实后端数据
   - 收藏功能从 localStorage 迁移到数据库

### 下一步

1. 更新 ShopCard 组件以支持收藏功能
2. 创建评论表单组件
3. 实现商店提交功能
4. 完善管理后台功能

## 注意事项

- 确保数据库已启动（`docker-compose up -d`）
- 所有用户相关的 API 都需要认证
- Profile 页面需要登录才能访问
- 管理员角色可以访问 `/admin` 页面

