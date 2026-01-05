# 快速启动指南

## 🚀 5 分钟快速启动

### 步骤 1: 安装依赖

```bash
npm install
npm install bcryptjs @types/bcryptjs
```

### 步骤 2: 启动数据库

```bash
docker-compose up -d
```

等待几秒让数据库完全启动。

### 步骤 3: 配置环境变量

创建 `.env` 文件（如果还没有）：

```env
# 数据库连接（默认配置，通常不需要修改）
DATABASE_URL="postgresql://coffeecompass:coffeecompass@localhost:5432/coffeecompass?schema=public"

# Mapbox Token（必需！）
# 获取方式：https://www.mapbox.com/ → 注册 → Dashboard → Access token
NEXT_PUBLIC_MAPBOX_TOKEN="your-mapbox-token-here"

# NextAuth 配置（必需！）
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-random-secret-key"

# Google OAuth（可选）
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

**生成 NEXTAUTH_SECRET：**
```bash
openssl rand -base64 32
```

### 步骤 4: 初始化数据库

```bash
# 生成 Prisma Client
npm run db:generate

# 推送数据库 schema
npm run db:push

# 填充示例数据
npm run db:seed
```

### 步骤 5: 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

## ✅ 验证安装

1. **检查数据库连接**
   ```bash
   docker-compose ps
   ```
   应该显示 `coffeecompass-db` 容器运行中

2. **检查 Prisma**
   ```bash
   npm run db:studio
   ```
   应该打开 Prisma Studio，可以看到数据库表

3. **检查网站**
   - 打开 http://localhost:3000
   - 应该看到咖啡店列表和地图
   - 点击商店卡片应该打开详情抽屉

## 🧪 测试功能

### 1. 注册和登录
- 访问 `/auth/register` 创建账户
- 访问 `/auth/signin` 登录

### 2. 浏览和收藏
- 点击商店卡片查看详情
- 点击心形图标收藏商店
- 访问 `/profile` 查看收藏列表

### 3. 评论
- 在商店详情页点击 "Write Review"
- 填写评分和评论
- 提交后查看评论列表

### 4. 提交新商店
- 点击导航栏的 "Submit Shop"
- 填写商店信息
- 提交后等待管理员审核

### 5. 推荐系统
- 收藏几个不同特征的商店
- 访问 `/profile` 页面
- 查看 "Weekly Recommendations" 部分

## 🔧 常见问题

### 问题 1: 数据库连接失败

**症状：** `Error: P1001: Can't reach database server`

**解决：**
```bash
# 检查 Docker 容器
docker-compose ps

# 如果容器未运行，启动它
docker-compose up -d

# 等待几秒后重试
```

### 问题 2: Prisma Client 未生成

**症状：** `Module not found: Can't resolve '@prisma/client'`

**解决：**
```bash
npm run db:generate
```

### 问题 3: Mapbox 地图不显示

**症状：** 地图区域空白或显示错误

**解决：**
1. 检查 `NEXT_PUBLIC_MAPBOX_TOKEN` 是否设置
2. 确保 token 有效（访问 https://account.mapbox.com/）
3. 检查浏览器控制台是否有错误

### 问题 4: NextAuth 错误

**症状：** `NEXTAUTH_SECRET is not set` 或认证失败

**解决：**
1. 确保 `.env` 文件中有 `NEXTAUTH_SECRET`
2. 确保 `NEXTAUTH_URL` 正确
3. 清除浏览器 cookies 和 localStorage

### 问题 5: 端口被占用

**症状：** `Port 3000 is already in use`

**解决：**
```bash
# 查找占用端口的进程
lsof -i :3000

# 杀死进程（替换 PID）
kill -9 <PID>

# 或使用其他端口
PORT=3001 npm run dev
```

## 📊 数据库管理

### 查看数据库
```bash
npm run db:studio
```

### 重置数据库（会删除所有数据）
```bash
docker-compose down -v
docker-compose up -d
npm run db:push
npm run db:seed
```

### 备份数据库
```bash
docker exec coffeecompass-db pg_dump -U coffeecompass coffeecompass > backup.sql
```

### 恢复数据库
```bash
docker exec -i coffeecompass-db psql -U coffeecompass coffeecompass < backup.sql
```

## 🎯 下一步

1. **创建管理员账户**
   - 注册一个账户
   - 在数据库中手动设置 `role = 'admin'`
   - 或使用 Prisma Studio 修改

2. **配置 Google OAuth**（可选）
   - 访问 https://console.cloud.google.com/
   - 创建 OAuth 2.0 客户端 ID
   - 添加到 `.env` 文件

3. **自定义数据**
   - 编辑 `prisma/seed.ts` 添加更多商店
   - 运行 `npm run db:seed` 重新填充数据

## 📚 相关文档

- `TESTING_GUIDE.md` - 详细测试指南
- `CODE_REVIEW.md` - 代码审查报告
- `IMPLEMENTATION_COMPLETE.md` - 功能完成报告
- `SETUP_AUTH.md` - 认证系统设置指南

