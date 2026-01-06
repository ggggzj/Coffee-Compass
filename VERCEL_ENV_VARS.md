# Vercel 环境变量配置说明

## ❌ 重要：这两个变量**不会**自动生成！

Vercel **不会**自动为你生成或设置这两个环境变量，你需要**手动配置**。

---

## 🔐 NEXTAUTH_SECRET

### ❌ 不会自动生成

**你需要自己：**
1. 生成密钥
2. 在 Vercel 中手动添加

### ✅ 配置步骤

#### 步骤 1: 生成密钥

在本地终端运行：

```bash
openssl rand -base64 32
```

这会生成一个随机字符串，例如：
```
XDIhWeNfIeTUvhu/cyU1+YyVjUZH0a4/OZqE8b6tT0U=
```

#### 步骤 2: 在 Vercel 中添加

1. 访问你的 Vercel 项目页面
2. 点击 **"Settings"**（设置）
3. 点击 **"Environment Variables"**（环境变量）
4. 点击 **"Add New"**（添加新变量）
5. 填写：
   - **Key（键）**: `NEXTAUTH_SECRET`
   - **Value（值）**: 粘贴你刚才生成的密钥
   - **Environment（环境）**: 选择 `Production`、`Preview`、`Development`（建议全选）
6. 点击 **"Save"**（保存）

---

## 🌐 NEXTAUTH_URL

### ⚠️ 部分自动：URL 会自动生成，但需要手动添加到环境变量

**情况说明：**
- ✅ Vercel 会**自动给你一个 URL**（部署后）
- ❌ 但**不会自动添加到环境变量**，需要你手动添加

### ✅ 配置步骤

#### 步骤 1: 部署项目

1. 访问 https://vercel.com/new
2. 导入你的 GitHub 仓库
3. 点击 **"Deploy"**（部署）
4. 等待部署完成（2-5分钟）

#### 步骤 2: 获取你的 URL

部署完成后，Vercel 会显示你的项目 URL：

- 在项目页面顶部，你会看到类似这样的 URL：
  ```
  https://coffee-compass-xxxxx.vercel.app
  ```
  或者如果你设置了自定义域名：
  ```
  https://yourdomain.com
  ```

**复制这个 URL！**

#### 步骤 3: 在 Vercel 中添加环境变量

1. 在 Vercel 项目页面
2. 点击 **"Settings"**（设置）
3. 点击 **"Environment Variables"**（环境变量）
4. 点击 **"Add New"**（添加新变量）
5. 填写：
   - **Key（键）**: `NEXTAUTH_URL`
   - **Value（值）**: `https://your-project-name.vercel.app`（粘贴你刚才复制的 URL）
   - **Environment（环境）**: 选择 `Production`、`Preview`、`Development`（建议全选）
6. 点击 **"Save"**（保存）

#### 步骤 4: 重新部署

添加环境变量后：
- Vercel 可能会自动触发重新部署
- 如果没有，点击 **"Deployments"** > 最新的部署 > **"Redeploy"**

---

## 📋 完整配置流程

### 部署前准备

1. **生成 NEXTAUTH_SECRET**
   ```bash
   openssl rand -base64 32
   ```
   复制生成的密钥

2. **准备其他环境变量**
   - `DATABASE_URL`（稍后配置数据库时添加）
   - `NEXT_PUBLIC_MAPBOX_TOKEN`（从本地 .env 复制）
   - `GOOGLE_CLIENT_ID`（如果使用，从本地 .env 复制）
   - `GOOGLE_CLIENT_SECRET`（如果使用，从本地 .env 复制）

### 部署步骤

#### 1. 首次部署

1. 访问 https://vercel.com/new
2. 导入 GitHub 仓库
3. 点击 **"Deploy"**
4. **先不要添加环境变量**，让项目先部署一次

#### 2. 获取 Vercel URL

部署完成后，复制你的项目 URL（例如：`https://coffee-compass-xxxxx.vercel.app`）

#### 3. 添加环境变量

在 Vercel 项目设置中添加：

```
NEXTAUTH_SECRET=你生成的密钥
NEXTAUTH_URL=https://your-project-name.vercel.app（你刚才复制的URL）
DATABASE_URL=稍后配置（先添加占位符）
NEXT_PUBLIC_MAPBOX_TOKEN=你的Mapbox Token
GOOGLE_CLIENT_ID=你的Google客户端ID（可选）
GOOGLE_CLIENT_SECRET=你的Google客户端密钥（可选）
```

#### 4. 重新部署

添加环境变量后，Vercel 会自动重新部署，或者手动点击 **"Redeploy"**

---

## 🎯 快速检查清单

部署后，确认以下内容：

- [ ] 项目已部署到 Vercel
- [ ] 已获取 Vercel URL（例如：`https://coffee-compass-xxxxx.vercel.app`）
- [ ] 已生成 `NEXTAUTH_SECRET` 并添加到 Vercel
- [ ] 已将 `NEXTAUTH_URL` 设置为你的 Vercel URL
- [ ] 已添加其他必需的环境变量
- [ ] 已重新部署项目

---

## 💡 提示

### 为什么需要手动添加？

1. **安全性**：密钥不应该自动生成，应该由你控制
2. **灵活性**：你可以使用自定义域名
3. **控制权**：你可以为不同环境设置不同的值

### 最佳实践

1. **开发环境**：使用 `http://localhost:3000`
2. **生产环境**：使用 Vercel 给你的 URL
3. **预览环境**：Vercel 会自动为每个 PR 创建预览 URL

### 环境变量优先级

Vercel 支持为不同环境设置不同的值：
- **Production**：生产环境
- **Preview**：预览环境（PR 部署）
- **Development**：本地开发（Vercel CLI）

建议：为所有环境设置相同的值，除非有特殊需求。

---

## 🆘 常见问题

### Q: 部署后找不到 URL？

A: 在 Vercel 项目页面顶部，会显示你的项目 URL。如果没有，检查部署是否成功。

### Q: 添加环境变量后需要做什么？

A: Vercel 会自动重新部署，或者你可以手动点击 "Redeploy"。

### Q: 可以部署后再添加环境变量吗？

A: 可以！但添加后需要重新部署才能生效。

### Q: 如何知道环境变量是否生效？

A: 重新部署后，访问你的网站，测试登录功能。如果登录正常，说明配置正确。

---

## ✅ 总结

| 变量 | 自动生成？ | 如何获得 |
|------|-----------|---------|
| **NEXTAUTH_SECRET** | ❌ 否 | 自己生成：`openssl rand -base64 32` |
| **NEXTAUTH_URL** | ⚠️ 部分 | URL 会自动生成，但需要手动添加到环境变量 |

**关键点**：
- ❌ **都不会自动添加到环境变量**
- ✅ **都需要你手动配置**
- ✅ **NEXTAUTH_URL 的值会在部署后给你**

