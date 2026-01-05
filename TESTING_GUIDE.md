# 测试指南

## 准备工作

### 1. 安装依赖

```bash
npm install
npm install bcryptjs @types/bcryptjs
```

### 2. 启动数据库

```bash
docker-compose up -d
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
DATABASE_URL="postgresql://coffeecompass:coffeecompass@localhost:5432/coffeecompass?schema=public"
NEXT_PUBLIC_MAPBOX_TOKEN="your-mapbox-token"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-random-secret-key-here"
```

生成 NEXTAUTH_SECRET：
```bash
openssl rand -base64 32
```

### 4. 初始化数据库

```bash
npm run db:generate
npm run db:push
npm run db:seed
```

### 5. 启动开发服务器

```bash
npm run dev
```

## 功能测试清单

### ✅ 用户认证测试

1. **注册功能**
   - [ ] 访问 `/auth/register`
   - [ ] 填写注册表单（姓名、邮箱、密码）
   - [ ] 提交后应跳转到登录页面
   - [ ] 验证邮箱唯一性（重复邮箱应报错）

2. **登录功能**
   - [ ] 访问 `/auth/signin`
   - [ ] 使用注册的邮箱和密码登录
   - [ ] 登录后应跳转到首页
   - [ ] Navigation 应显示用户名和登出按钮

3. **会话管理**
   - [ ] 刷新页面后应保持登录状态
   - [ ] 点击登出应清除会话

### ✅ 咖啡店浏览测试

1. **主页功能**
   - [ ] 显示咖啡店列表
   - [ ] 显示地图
   - [ ] 筛选功能（城市、场景、排序）
   - [ ] 点击商店卡片应打开详情抽屉

2. **商店详情**
   - [ ] ShopDrawer 显示完整信息
   - [ ] 显示适合度评分和详情
   - [ ] 显示设施详情

### ✅ 收藏功能测试

1. **添加收藏**
   - [ ] 在 ShopCard 上点击心形图标
   - [ ] 未登录时应跳转到登录页
   - [ ] 登录后点击应添加收藏
   - [ ] 心形图标应变为红色（已收藏状态）

2. **移除收藏**
   - [ ] 在已收藏的商店上再次点击心形图标
   - [ ] 应移除收藏
   - [ ] 心形图标应变为灰色

3. **查看收藏**
   - [ ] 访问 `/profile` 页面
   - [ ] FavoritesList 应显示所有收藏的商店
   - [ ] 可以移除收藏

### ✅ 评论功能测试

1. **提交评论**
   - [ ] 在 ShopDrawer 中点击 "Write Review"
   - [ ] 填写评分（7个维度）
   - [ ] 添加文字评论（可选）
   - [ ] 提交评论
   - [ ] 评论应出现在评论列表中

2. **查看评论**
   - [ ] ShopDrawer 应显示所有评论
   - [ ] 评论应显示用户名和日期
   - [ ] 评论应显示评分详情

3. **评论影响评分**
   - [ ] 提交评论后，商店的综合评分应更新
   - [ ] 评分应为所有评论的平均值

### ✅ 访问历史测试

1. **自动记录**
   - [ ] 打开 ShopDrawer 时应自动记录访问
   - [ ] 访问 `/profile` 页面
   - [ ] VisitHistory 应显示访问记录

### ✅ 商店提交测试

1. **提交新商店**
   - [ ] 点击导航栏的 "Submit Shop"
   - [ ] 填写所有必填字段
   - [ ] 设置设施评分
   - [ ] 提交表单
   - [ ] 应显示成功消息

2. **表单验证**
   - [ ] 空字段应显示错误
   - [ ] 无效的坐标应显示错误
   - [ ] 重复的商店名称和地址应显示错误

### ✅ 管理后台测试

1. **访问权限**
   - [ ] 普通用户不应访问 `/admin`
   - [ ] 管理员可以访问 `/admin`

2. **商店审核**
   - [ ] 查看待审核的商店提交
   - [ ] 点击 "Approve" 应批准商店
   - [ ] 批准后应创建商店记录
   - [ ] 点击 "Reject" 应拒绝提交

3. **举报管理**
   - [ ] 查看举报列表
   - [ ] 可以标记为 "Resolved" 或 "Dismissed"

### ✅ 推荐系统测试

1. **个性化推荐**
   - [ ] 访问 `/profile` 页面
   - [ ] WeeklyRecommendations 应显示推荐
   - [ ] 推荐应基于用户的收藏和偏好
   - [ ] 每个场景应有 3 个推荐

2. **推荐逻辑**
   - [ ] 已收藏/访问过的商店不应出现在推荐中
   - [ ] 推荐应匹配用户偏好
   - [ ] 推荐应显示适合度评分

## 常见问题排查

### 数据库连接失败

```bash
# 检查 Docker 容器是否运行
docker-compose ps

# 重启数据库
docker-compose restart postgres
```

### Prisma 错误

```bash
# 重新生成 Prisma Client
npm run db:generate

# 重置数据库（会删除所有数据）
docker-compose down -v
docker-compose up -d
npm run db:push
npm run db:seed
```

### NextAuth 错误

- 确保 `NEXTAUTH_SECRET` 已设置
- 确保 `NEXTAUTH_URL` 正确
- 清除浏览器 cookies 和 localStorage

### API 错误

- 检查浏览器控制台的错误信息
- 检查服务器终端的错误日志
- 确保所有环境变量已设置

## 性能测试

1. **加载速度**
   - [ ] 首页应在 2 秒内加载
   - [ ] 地图应在 3 秒内加载
   - [ ] API 响应应在 500ms 内

2. **数据量测试**
   - [ ] 测试大量商店（100+）
   - [ ] 测试大量评论（50+ per shop）
   - [ ] 测试大量收藏（20+）

## 浏览器兼容性

- [ ] Chrome/Edge (最新版本)
- [ ] Firefox (最新版本)
- [ ] Safari (最新版本)
- [ ] 移动端浏览器

## 安全测试

1. **认证安全**
   - [ ] 未登录用户不能访问受保护的路由
   - [ ] API 路由需要认证
   - [ ] 密码应加密存储

2. **数据验证**
   - [ ] 所有输入应验证
   - [ ] SQL 注入防护（Prisma 自动处理）
   - [ ] XSS 防护（React 自动转义）

