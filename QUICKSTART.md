# 快速启动指南

## 5分钟快速启动

### 1. 安装依赖
```bash
npm install
```

### 2. 启动数据库
```bash
docker-compose up -d
```

等待几秒钟让数据库完全启动。

### 3. 设置环境变量
```bash
cp .env.example .env
```

编辑 `.env` 文件，至少设置：
- `DATABASE_URL` (已默认配置，通常不需要修改)
- `NEXT_PUBLIC_MAPBOX_TOKEN` (必须！从 https://www.mapbox.com/ 获取免费token)

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

访问 http://localhost:3000

## 常见问题

### Mapbox Token 在哪里获取？
1. 访问 https://www.mapbox.com/
2. 注册免费账号
3. 在 Dashboard 中找到 "Access token"
4. 复制 token 到 `.env` 文件的 `NEXT_PUBLIC_MAPBOX_TOKEN`

### 数据库连接失败？
确保 Docker 容器正在运行：
```bash
docker-compose ps
```

如果容器未运行，启动它：
```bash
docker-compose up -d
```

### 端口已被占用？
如果 5432 端口被占用，修改 `docker-compose.yml` 中的端口映射。

### 重置数据库？
```bash
docker-compose down -v
docker-compose up -d
npm run db:push
npm run db:seed
```

## 下一步

- 查看 `README.md` 了解完整文档
- 探索代码结构
- 自定义咖啡店数据（编辑 `prisma/seed.ts`）

