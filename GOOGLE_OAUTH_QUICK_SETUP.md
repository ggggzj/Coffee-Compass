# Google OAuth 快速配置指南

## 🚀 5 分钟快速配置

### 步骤 1: 打开 Google Cloud Console

**直接访问：** https://console.cloud.google.com/

使用你的 Google 账号登录（zguo7940@usc.edu）

### 步骤 2: 创建项目（1分钟）

1. 点击页面顶部的项目选择器（显示当前项目名称的地方）
2. 点击 **"新建项目"** (New Project)
3. **项目名称**: `CoffeeCompass`
4. 点击 **"创建"** (Create)
5. 等待几秒钟，项目创建完成后会自动选择

### 步骤 3: 启用 API（30秒）

1. 在左侧菜单，点击 **"API 和服务"** (APIs & Services) > **"库"** (Library)
2. 在搜索框输入：`Google Identity`
3. 点击 **"Google Identity Services API"** 或 **"Google+ API"**
4. 点击 **"启用"** (Enable) 按钮
5. 等待几秒钟启用完成

### 步骤 4: 配置 OAuth 同意屏幕（2分钟）

1. 左侧菜单：**"API 和服务"** > **"OAuth 同意屏幕"** (OAuth consent screen)
2. 选择 **"外部"** (External) - 允许所有 Google 用户
3. 点击 **"创建"** (Create)

**填写应用信息：**
- **应用名称**: `CoffeeCompass`
- **用户支持电子邮件**: `zguo7940@usc.edu`
- **开发者联系信息**: `zguo7940@usc.edu`
- 其他字段可以留空或跳过

4. 点击 **"保存并继续"** (Save and Continue)
5. 在 **"作用域"** (Scopes) 页面，直接点击 **"保存并继续"**（使用默认）
6. 在 **"测试用户"** 页面，直接点击 **"保存并继续"**（外部用户不需要）
7. 点击 **"返回到信息中心"** (Back to Dashboard)

### 步骤 5: 创建 OAuth 客户端（1分钟）

1. 左侧菜单：**"API 和服务"** > **"凭据"** (Credentials)
2. 点击页面顶部的 **"+ 创建凭据"** (Create Credentials)
3. 选择 **"OAuth 客户端 ID"** (OAuth client ID)

**如果提示选择应用类型：**
- 选择 **"Web 应用程序"** (Web application)

**填写表单：**

**名称**: `CoffeeCompass Web Client`

**已获授权的 JavaScript 来源**:
- 点击 **"+ 添加 URI"**
- 输入: `http://localhost:3000`
- 点击 **"添加"**

**已获授权的重定向 URI**:
- 点击 **"+ 添加 URI"**
- 输入: `http://localhost:3000/api/auth/callback/google`
- ⚠️ **重要**: 必须完全匹配，包括 `http://` 和路径
- 点击 **"添加"**

4. 点击 **"创建"** (Create)

### 步骤 6: 复制凭据（30秒）

**重要**: 现在会弹出一个对话框显示你的凭据：

1. **客户端 ID** (Client ID)
   - 格式类似：`123456789-abcdefghijklmnop.apps.googleusercontent.com`
   - 点击复制图标或手动复制

2. **客户端密钥** (Client Secret)
   - 格式类似：`GOCSPX-abcdefghijklmnopqrstuvwxyz`
   - 点击复制图标或手动复制

⚠️ **注意**: 这个对话框只会显示一次！如果关闭了，需要删除并重新创建客户端 ID。

### 步骤 7: 添加到项目（1分钟）

1. 打开项目根目录的 `.env` 文件
2. 添加以下两行（替换为你刚才复制的值）：

```env
GOOGLE_CLIENT_ID=你的客户端ID（粘贴到这里）
GOOGLE_CLIENT_SECRET=你的客户端密钥（粘贴到这里）
```

**示例：**
```env
GOOGLE_CLIENT_ID=123456789-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
```

3. **保存文件** (Cmd+S 或 Ctrl+S)

### 步骤 8: 重启服务器（30秒）

```bash
# 在终端中停止当前服务器（按 Ctrl+C）
# 然后重新启动
npm run dev
```

### 步骤 9: 测试（30秒）

1. 打开浏览器访问：http://localhost:3000/auth/signin
2. 点击 **"Sign in with Google"** 按钮
3. 应该跳转到 Google 登录页面
4. 选择你的 Google 账号
5. 授权后应该重定向回应用并登录成功

## ✅ 验证配置

运行以下命令检查配置：

```bash
# 检查环境变量（不会显示完整值，只显示是否设置）
grep -E "GOOGLE_CLIENT" .env
```

应该看到两行：
```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

## 🔍 常见问题快速解决

### 问题：找不到 "API 和服务" 菜单

**解决**: 
- 确保已选择项目（页面顶部显示项目名称）
- 如果看不到，点击左上角的三条横线菜单图标

### 问题：找不到 "OAuth 客户端 ID" 选项

**解决**:
- 确保已启用 Google Identity API
- 确保已配置 OAuth 同意屏幕

### 问题：重定向 URI 不匹配错误

**解决**:
- 确保重定向 URI 完全匹配：`http://localhost:3000/api/auth/callback/google`
- 检查是否有空格或多余字符
- 确保使用的是 `http` 而不是 `https`（本地开发）

### 问题：客户端密钥丢失

**解决**:
- 如果关闭了凭据对话框，需要删除并重新创建 OAuth 客户端
- 在 "凭据" 页面，找到你的客户端 ID，点击右侧的垃圾桶图标删除
- 然后重新创建

## 📝 配置检查清单

完成配置后，确认以下所有项：

- [ ] Google Cloud 项目已创建
- [ ] Google Identity API 已启用
- [ ] OAuth 同意屏幕已配置
- [ ] OAuth 客户端 ID 已创建
- [ ] JavaScript 来源已添加：`http://localhost:3000`
- [ ] 重定向 URI 已添加：`http://localhost:3000/api/auth/callback/google`
- [ ] Client ID 已复制到 `.env` 文件
- [ ] Client Secret 已复制到 `.env` 文件
- [ ] `.env` 文件已保存
- [ ] 开发服务器已重启
- [ ] Google 登录按钮可以正常使用

## 🎯 完成！

配置完成后，Google 登录应该可以正常工作了！

如果遇到任何问题，请查看 `GOOGLE_OAUTH_STEP_BY_STEP.md` 获取更详细的说明。

