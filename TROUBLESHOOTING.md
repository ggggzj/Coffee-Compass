# 故障排除指南

## 🔧 当前遇到的问题

### 问题 1: npm 权限错误 (EACCES)

**错误信息：**
```
npm error EACCES: permission denied, rename
```

**解决方案：**

**方法 1: 清理 npm 缓存（推荐）**
```bash
npm cache clean --force
```

**方法 2: 修复 npm 缓存权限**
```bash
sudo chown -R $(whoami) ~/.npm
```

**方法 3: 使用 --force 标志**
```bash
npm install --force
```

**方法 4: 使用 sudo（不推荐，但可以临时解决）**
```bash
sudo npm install
```

### 问题 2: Docker Daemon 未运行

**错误信息：**
```
Cannot connect to the Docker daemon at unix:///Users/guozhengjia/.docker/run/docker.sock
Is the docker daemon running?
```

**解决方案：**

**macOS:**
1. 打开 Docker Desktop 应用程序
2. 等待 Docker 完全启动（图标不再闪烁）
3. 验证 Docker 是否运行：
   ```bash
   docker ps
   ```

**如果 Docker Desktop 未安装：**
1. 下载并安装 Docker Desktop for Mac
2. 启动 Docker Desktop
3. 等待启动完成

**验证 Docker 运行：**
```bash
docker --version
docker ps
```

### 问题 3: Next.js 安全漏洞警告

**警告信息：**
```
npm warn deprecated next@14.0.4: This version has a security vulnerability
```

**解决方案：**

更新 Next.js 到最新版本：
```bash
npm install next@latest
```

或者更新到特定版本：
```bash
npm install next@14.2.0
```

## 🚀 完整修复步骤

### 步骤 1: 修复 npm 权限

```bash
# 清理 npm 缓存
npm cache clean --force

# 修复权限（如果需要）
sudo chown -R $(whoami) ~/.npm
```

### 步骤 2: 启动 Docker

1. 打开 Docker Desktop
2. 等待完全启动
3. 验证：
   ```bash
   docker ps
   ```

### 步骤 3: 更新 Next.js（可选但推荐）

```bash
npm install next@latest
```

### 步骤 4: 重新安装依赖

```bash
# 删除 node_modules 和 package-lock.json（如果存在）
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 安装额外依赖
npm install bcryptjs @types/bcryptjs
```

### 步骤 5: 启动数据库

```bash
docker-compose up -d
```

### 步骤 6: 验证数据库

```bash
docker-compose ps
```

应该看到 `coffeecompass-db` 容器运行中。

## 🔍 验证安装

运行以下命令验证一切正常：

```bash
# 1. 检查 Node.js 和 npm
node --version
npm --version

# 2. 检查 Docker
docker --version
docker ps

# 3. 检查数据库容器
docker-compose ps

# 4. 检查 Prisma
npx prisma --version

# 5. 生成 Prisma Client
npm run db:generate
```

## 📝 如果问题仍然存在

### npm 权限问题持续

如果 npm 权限问题持续存在，可以：

1. **使用 nvm（Node Version Manager）**
   ```bash
   # 安装 nvm
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   
   # 重新加载 shell
   source ~/.zshrc  # 或 ~/.bashrc
   
   # 安装 Node.js
   nvm install node
   nvm use node
   ```

2. **使用 yarn 代替 npm**
   ```bash
   npm install -g yarn
   yarn install
   ```

### Docker 问题持续

1. **重启 Docker Desktop**
   - 完全退出 Docker Desktop
   - 重新启动
   - 等待完全启动

2. **检查 Docker 服务**
   ```bash
   # macOS
   open -a Docker
   ```

3. **重置 Docker（最后手段）**
   - Docker Desktop → Settings → Reset to factory defaults
   - ⚠️ 这会删除所有容器和镜像

## ✅ 成功标志

安装成功后，你应该能够：

1. ✅ 运行 `npm install` 无错误
2. ✅ 运行 `docker ps` 看到 Docker 运行
3. ✅ 运行 `docker-compose up -d` 成功启动数据库
4. ✅ 运行 `npm run db:generate` 成功生成 Prisma Client
5. ✅ 运行 `npm run dev` 成功启动开发服务器

## 🆘 需要帮助？

如果问题仍然存在，请提供：
1. 完整的错误信息
2. `npm --version` 输出
3. `node --version` 输出
4. `docker --version` 输出
5. `docker ps` 输出

