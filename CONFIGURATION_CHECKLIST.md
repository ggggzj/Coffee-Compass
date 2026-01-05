# Google OAuth 配置检查清单

## 📋 配置前准备

- [ ] 已访问 https://console.cloud.google.com/
- [ ] 已使用 Google 账号登录

## 🔧 Google Cloud Console 配置

### 项目设置
- [ ] 已创建项目 "CoffeeCompass"
- [ ] 项目已选择（页面顶部显示项目名称）

### API 启用
- [ ] 已访问 "API 和服务" > "库"
- [ ] 已搜索并找到 "Google Identity Services API" 或 "Google+ API"
- [ ] 已点击 "启用" 按钮
- [ ] API 状态显示为 "已启用"

### OAuth 同意屏幕
- [ ] 已访问 "API 和服务" > "OAuth 同意屏幕"
- [ ] 已选择 "外部" 用户类型
- [ ] 已填写应用名称：`CoffeeCompass`
- [ ] 已填写用户支持电子邮件：`zguo7940@usc.edu`
- [ ] 已填写开发者联系信息：`zguo7940@usc.edu`
- [ ] 已点击 "保存并继续" 完成所有步骤
- [ ] 已返回到信息中心

### OAuth 客户端创建
- [ ] 已访问 "API 和服务" > "凭据"
- [ ] 已点击 "+ 创建凭据" > "OAuth 客户端 ID"
- [ ] 已选择应用类型：Web 应用程序
- [ ] 已填写名称：`CoffeeCompass Web Client`

**已获授权的 JavaScript 来源：**
- [ ] 已添加：`http://localhost:3000`
- [ ] 确认没有多余的空格或斜杠

**已获授权的重定向 URI：**
- [ ] 已添加：`http://localhost:3000/api/auth/callback/google`
- [ ] ⚠️ 确认完全匹配（包括 `http://` 和完整路径）
- [ ] 确认没有多余的空格或斜杠

- [ ] 已点击 "创建" 按钮
- [ ] 已复制 **客户端 ID** (Client ID)
- [ ] 已复制 **客户端密钥** (Client Secret)

## 💻 项目配置

### 环境变量
- [ ] 已打开 `.env` 文件
- [ ] 已添加 `GOOGLE_CLIENT_ID=你的客户端ID`
- [ ] 已添加 `GOOGLE_CLIENT_SECRET=你的客户端密钥`
- [ ] 确认值没有引号（直接粘贴，不要加引号）
- [ ] 确认值没有多余的空格
- [ ] 已保存文件 (Cmd+S 或 Ctrl+S)

### 服务器重启
- [ ] 已停止开发服务器（Ctrl+C）
- [ ] 已重新启动：`npm run dev`
- [ ] 服务器启动成功，没有错误

## 🧪 测试验证

### 功能测试
- [ ] 已访问 http://localhost:3000/auth/signin
- [ ] 能看到 "Sign in with Google" 按钮
- [ ] 点击按钮后跳转到 Google 登录页面
- [ ] 可以选择 Google 账号
- [ ] 授权后成功重定向回应用
- [ ] 登录成功，显示用户名

### 错误检查
- [ ] 浏览器控制台没有错误
- [ ] 服务器终端没有错误
- [ ] 没有看到 "Missing required parameter: client_id" 错误
- [ ] 没有看到 "redirect_uri_mismatch" 错误

## 🔍 快速检查命令

运行以下命令检查配置：

```bash
# 检查环境变量
grep GOOGLE .env

# 运行配置检查脚本
./check_google_oauth.sh
```

## ✅ 配置完成标志

配置成功后，你应该能够：
1. ✅ 看到 Google 登录按钮
2. ✅ 点击后跳转到 Google 登录页面
3. ✅ 登录后成功返回应用
4. ✅ 在应用中看到你的 Google 账号信息

## 🆘 如果遇到问题

1. **检查环境变量**
   ```bash
   grep GOOGLE .env
   ```

2. **检查 Google Cloud Console**
   - 确认 OAuth 客户端已创建
   - 确认重定向 URI 完全匹配

3. **检查服务器日志**
   - 查看终端中的错误信息
   - 查看浏览器控制台的错误

4. **重启服务器**
   ```bash
   # 停止服务器（Ctrl+C）
   npm run dev
   ```

5. **清除浏览器缓存**
   - 清除 cookies
   - 硬刷新页面 (Cmd+Shift+R 或 Ctrl+Shift+R)

## 📚 相关文档

- `GOOGLE_OAUTH_QUICK_SETUP.md` - 快速配置指南
- `GOOGLE_OAUTH_STEP_BY_STEP.md` - 详细步骤指南
- `GOOGLE_OAUTH_SETUP.md` - 完整设置文档

