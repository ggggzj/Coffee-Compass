# 数据库迁移问题解决方案

## 问题说明

Prisma 检测到需要添加 `updatedAt` 字段到 `Shop` 表，但表中已有 30 行数据。无法直接添加没有默认值的必需字段。

## 解决方案

### 方案 1: 重置数据库（推荐 - 开发环境）

如果这是开发环境且数据不重要，可以重置数据库：

```bash
# 1. 停止并删除数据库容器和卷
docker-compose down -v

# 2. 重新启动数据库
docker-compose up -d

# 3. 推送 schema（这次会创建新表）
npm run db:push

# 4. 填充种子数据
npm run db:seed
```

**优点：**
- 简单快速
- 确保数据库结构完全匹配 schema

**缺点：**
- 会丢失所有现有数据

### 方案 2: 手动迁移（保留数据）

如果想保留现有数据，需要手动添加字段：

```bash
# 1. 连接到数据库
docker exec -it coffeecompass-db psql -U coffeecompass -d coffeecompass

# 2. 在 PostgreSQL 中运行：
ALTER TABLE "Shop" ADD COLUMN "updatedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP;

# 3. 退出 PostgreSQL
\q

# 4. 然后运行
npm run db:push
```

**优点：**
- 保留现有数据

**缺点：**
- 需要手动操作
- 如果其他表也有类似问题，需要逐个处理

## 推荐操作

对于开发环境，建议使用**方案 1**（重置数据库），因为：
1. 数据可以通过 `npm run db:seed` 重新填充
2. 确保数据库结构完全正确
3. 避免后续迁移问题

## 执行步骤

```bash
# 完整重置流程
docker-compose down -v
docker-compose up -d
sleep 5  # 等待数据库启动
npm run db:generate
npm run db:push
npm run db:seed
```

## 验证

重置后验证数据库：

```bash
# 检查表是否存在
docker exec -it coffeecompass-db psql -U coffeecompass -d coffeecompass -c "\dt"

# 检查 Shop 表结构
docker exec -it coffeecompass-db psql -U coffeecompass -d coffeecompass -c "\d \"Shop\""
```

应该看到 `updatedAt` 字段存在。

