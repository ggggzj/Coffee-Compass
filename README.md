# CoffeeCompass

一个类似 Yelp 的咖啡店发现平台，帮助用户找到适合学习、远程工作、约会或会议的完美咖啡店。

## 功能特性

- 🗺️ **交互式地图**: 使用 Mapbox GL JS 显示咖啡店位置
- 📋 **结果列表**: 左侧可滚动的咖啡店列表
- 🔍 **智能筛选**: 按城市、场景和排序方式筛选
- ⭐ **适用性评分**: 基于场景的智能评分系统（0-100分）
- 📊 **评分明细**: 详细展示评分计算过程
- ❤️ **收藏功能**: 使用 localStorage 保存收藏的咖啡店
- 🔄 **实时同步**: 地图和列表实时同步更新

## 技术栈

- **前端**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **数据获取**: TanStack Query (React Query)
- **后端**: Next.js Route Handlers
- **验证**: Zod
- **数据库**: PostgreSQL + Prisma ORM
- **地图**: Mapbox GL JS (react-map-gl)

## 本地开发设置

### 前置要求

- Node.js 18+ 
- Docker 和 Docker Compose
- Mapbox 访问令牌（免费注册: https://www.mapbox.com/）

### 安装步骤

1. **克隆仓库并安装依赖**

```bash
cd coffeecompass
npm install
```

2. **启动 PostgreSQL 数据库**

```bash
docker-compose up -d
```

3. **配置环境变量**

复制 `.env.example` 到 `.env` 并填写必要的值：

```bash
cp .env.example .env
```

编辑 `.env` 文件，至少需要设置：

```env
DATABASE_URL="postgresql://coffeecompass:coffeecompass@localhost:5432/coffeecompass?schema=public"
NEXT_PUBLIC_MAPBOX_TOKEN="your-mapbox-token-here"
NEXTAUTH_SECRET="your-random-secret-key"
```

4. **初始化数据库**

```bash
# 生成 Prisma Client
npm run db:generate

# 推送数据库架构
npm run db:push

# 填充种子数据
npm run db:seed
```

5. **启动开发服务器**

```bash
npm run dev
```

应用将在 http://localhost:3000 运行

## 项目结构

```
coffeecompass/
├── app/                    # Next.js App Router
│   ├── api/               # API 路由
│   │   └── shops/         # 咖啡店 API
│   ├── globals.css        # 全局样式
│   ├── layout.tsx         # 根布局
│   ├── page.tsx           # 主页面
│   └── providers.tsx      # React Query Provider
├── components/            # React 组件
│   ├── FilterBar.tsx     # 筛选栏
│   ├── MapPane.tsx       # 地图组件
│   ├── ResultsList.tsx   # 结果列表
│   ├── ShopCard.tsx      # 咖啡店卡片
│   └── ShopDrawer.tsx    # 详情抽屉
├── hooks/                 # 自定义 Hooks
│   └── useDebounce.ts    # 防抖 Hook
├── lib/                   # 工具库
│   ├── prisma.ts         # Prisma Client
│   ├── scoring.ts        # 适用性评分系统
│   └── utils.ts          # 工具函数
└── prisma/                # Prisma 配置
    ├── schema.prisma     # 数据库架构
    └── seed.ts           # 种子数据脚本
```

## 适用性评分系统

系统根据不同的使用场景计算咖啡店的适用性评分：

- **学习 (Study)**: 重视安静环境、插座、座位和照明
- **远程工作 (Remote Work)**: 重视 WiFi、插座和座位
- **约会 (Date)**: 重视隐私、照明和安静环境
- **会议 (Meeting)**: 重视座位、安静环境和隐私

每个场景都有不同的权重配置，评分范围是 0-100，并提供详细的评分明细。

## API 端点

### GET /api/shops

查询咖啡店列表

**查询参数:**
- `city`: 城市 (Los Angeles | San Francisco | New York)
- `scene`: 场景 (Study | Remote Work | Date | Meeting)
- `sort`: 排序方式 (Distance | Rating | Suitability)
- `bounds`: 地图边界 (minLng,minLat,maxLng,maxLat)
- `page`: 页码 (默认: 1)
- `pageSize`: 每页数量 (默认: 20)

### GET /api/shops/[id]

获取单个咖啡店详情

**查询参数:**
- `scene`: 场景（可选，用于计算适用性评分）

## 部署到 Vercel

1. 将代码推送到 GitHub
2. 在 Vercel 中导入项目
3. 配置环境变量（参考 `.env.example`）
4. 设置 PostgreSQL 数据库（可以使用 Vercel Postgres 或其他服务）
5. 运行数据库迁移和种子数据

**注意**: 确保在 Vercel 环境变量中设置了所有必要的值，包括 `DATABASE_URL` 和 `NEXT_PUBLIC_MAPBOX_TOKEN`。

## 开发命令

```bash
npm run dev          # 启动开发服务器
npm run build        # 构建生产版本
npm run start        # 启动生产服务器
npm run lint         # 运行 ESLint
npm run db:generate  # 生成 Prisma Client
npm run db:push      # 推送数据库架构变更
npm run db:seed      # 填充种子数据
npm run db:studio    # 打开 Prisma Studio
```

## 许可证

MIT

