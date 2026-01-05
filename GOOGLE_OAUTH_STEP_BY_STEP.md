# Google OAuth 配置步骤指南

## 📋 完整配置流程

### 步骤 1: 访问 Google Cloud Console

1. 打开浏览器，访问：https://console.cloud.google.com/
2. 使用你的 Google 账号登录（zguo7940@usc.edu）

### 步骤 2: 创建或选择项目

1. 点击页面顶部的项目选择器
2. 点击 **"新建项目"** (New Project)
3. 项目名称填写：`CoffeeCompass`
4. 点击 **"创建"** (Create)
5. 等待项目创建完成（几秒钟）

### 步骤 3: 启用 Google+ API

1. 在左侧菜单中，点击 **"API 和服务"** (APIs & Services) > **"库"** (Library)
2. 搜索 "Google+ API" 或 "Google Identity"
3. 点击 **"Google+ API"** 或 **"Google Identity Services API"**
4. 点击 **"启用"** (Enable)

### 步骤 4: 配置 OAuth 同意屏幕

1. 在左侧菜单中，点击 **"API 和服务"** > **"OAuth 同意屏幕"** (OAuth consent screen)
2. 选择 **"外部"** (External) - 允许所有 Google 用户使用
3. 点击 **"创建"** (Create)
4. 填写应用信息：
   - **应用名称**: `CoffeeCompass`
   - **用户支持电子邮件**: `zguo7940@usc.edu`
   - **应用徽标**: （可选，可以跳过）
   - **应用主页链接**: `http://localhost:3000`
   - **应用隐私政策链接**: （可选，可以跳过）
   - **应用服务条款链接**: （可选，可以跳过）
   - **已获授权的网域**: （可以跳过）
   - **开发者联系信息**: `zguo7940@usc.edu`
5. 点击 **"保存并继续"** (Save and Continue)
6. 在 **"作用域"** (Scopes) 页面，点击 **"保存并继续"**（使用默认作用域即可）
7. 在 **"测试用户"** (Test users) 页面，可以跳过（因为选择的是外部用户）
8. 点击 **"返回到信息中心"** (Back to Dashboard)

### 步骤 5: 创建 OAuth 2.0 客户端 ID

1. 在左侧菜单中，点击 **"API 和服务"** > **"凭据"** (Credentials)
2. 点击页面顶部的 **"+ 创建凭据"** (Create Credentials)
3. 选择 **"OAuth 客户端 ID"** (OAuth client ID)
4. 如果提示选择应用类型，选择 **"Web 应用程序"** (Web application)
5. 填写表单：
   - **名称**: `CoffeeCompass Web Client`
   - **已获授权的 JavaScript 来源**:
     - 点击 **"+ 添加 URI"**
     - 输入: `http://localhost:3000`
   - **已获授权的重定向 URI**:
     - 点击 **"+ 添加 URI"**
     - 输入: `http://localhost:3000/api/auth/callback/google`
6. 点击 **"创建"** (Create)
7. **重要**: 复制显示的 **"客户端 ID"** (Client ID) 和 **"客户端密钥"** (Client Secret)
   - 客户端 ID 格式类似：`123456789-abcdefghijklmnop.apps.googleusercontent.com`
   - 客户端密钥格式类似：`GOCSPX-abcdefghijklmnopqrstuvwxyz`

### 步骤 6: 配置环境变量

1. 打开项目根目录的 `.env` 文件
2. 添加以下两行（替换为你刚才复制的值）：

```env
GOOGLE_CLIENT_ID=你的客户端ID
GOOGLE_CLIENT_SECRET=你的客户端密钥
```

例如：
```env
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
```

3. 保存文件

### 步骤 7: 启用 Google OAuth（可选）

如果你想在登录页面显示 Google 登录按钮，可以在 `.env` 文件中添加：

```env
NEXT_PUBLIC_GOOGLE_OAUTH_ENABLED=true
```

### 步骤 8: 重启开发服务器

```bash
# 停止当前服务器（Ctrl+C）
# 然后重新启动
npm run dev
```

### 步骤 9: 测试 Google 登录

1. 访问 http://localhost:3000/auth/signin
2. 如果配置了 `NEXT_PUBLIC_GOOGLE_OAUTH_ENABLED=true`，应该能看到 "Sign in with Google" 按钮
3. 点击按钮，应该跳转到 Google 登录页面
4. 登录后应该重定向回应用

## 🔍 验证配置

运行以下命令检查环境变量是否设置：

```bash
grep GOOGLE .env
```

应该看到：
```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

## ⚠️ 常见问题

### 问题 1: "redirect_uri_mismatch"

**原因**: 重定向 URI 不匹配

**解决**: 
- 确保在 Google Cloud Console 中配置的重定向 URI 是：`http://localhost:3000/api/auth/callback/google`
- 确保没有多余的空格或斜杠
- 确保使用的是 `http` 而不是 `https`（本地开发）

### 问题 2: "invalid_client"

**原因**: Client ID 或 Client Secret 错误

**解决**:
- 检查 `.env` 文件中的值是否正确
- 确保没有多余的空格或引号
- 确保值是从 Google Cloud Console 复制的完整值

### 问题 3: OAuth 同意屏幕未完成

**原因**: OAuth 同意屏幕配置未完成

**解决**:
- 返回 Google Cloud Console
- 完成 OAuth 同意屏幕的所有步骤
- 确保状态是 "已发布" 或至少是 "测试中"

### 问题 4: API 未启用

**原因**: Google+ API 或 Google Identity API 未启用

**解决**:
- 在 Google Cloud Console 中启用相应的 API
- 等待几分钟让更改生效

## 📝 生产环境配置

当部署到生产环境时，需要：

1. 在 Google Cloud Console 中添加生产环境的 URI：
   - **已获授权的 JavaScript 来源**: `https://yourdomain.com`
   - **已获授权的重定向 URI**: `https://yourdomain.com/api/auth/callback/google`

2. 在生产环境的环境变量中设置：
   ```env
   GOOGLE_CLIENT_ID=你的客户端ID
   GOOGLE_CLIENT_SECRET=你的客户端密钥
   NEXTAUTH_URL=https://yourdomain.com
   ```

## ✅ 配置完成检查清单

- [ ] Google Cloud 项目已创建
- [ ] Google+ API 或 Google Identity API 已启用
- [ ] OAuth 同意屏幕已配置
- [ ] OAuth 2.0 客户端 ID 已创建
- [ ] 重定向 URI 已正确配置
- [ ] `.env` 文件中已添加 `GOOGLE_CLIENT_ID`
- [ ] `.env` 文件中已添加 `GOOGLE_CLIENT_SECRET`
- [ ] 开发服务器已重启
- [ ] Google 登录按钮可以正常使用

## 🆘 需要帮助？

如果遇到问题：
1. 检查浏览器控制台的错误信息
2. 检查服务器终端的错误日志
3. 确认所有步骤都已完成
4. 尝试清除浏览器缓存和 cookies

