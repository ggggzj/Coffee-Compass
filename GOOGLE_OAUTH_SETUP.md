# Google OAuth 配置指南

## 问题说明

如果看到错误 "Missing required parameter: client_id"，说明 Google OAuth 未正确配置。

## 解决方案

### 方案 1: 配置 Google OAuth（推荐用于生产环境）

#### 步骤 1: 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 Google+ API

#### 步骤 2: 创建 OAuth 2.0 凭据

1. 在 Google Cloud Console 中，转到 **API & Services** > **Credentials**
2. 点击 **Create Credentials** > **OAuth client ID**
3. 如果提示，先配置 OAuth 同意屏幕：
   - 选择 **External**（外部用户）
   - 填写应用名称：`CoffeeCompass`
   - 添加你的邮箱作为支持邮箱
   - 保存并继续
4. 创建 OAuth 客户端 ID：
   - **Application type**: Web application
   - **Name**: CoffeeCompass Web Client
   - **Authorized JavaScript origins**: 
     - `http://localhost:3000` (开发环境)
     - `https://yourdomain.com` (生产环境)
   - **Authorized redirect URIs**:
     - `http://localhost:3000/api/auth/callback/google` (开发环境)
     - `https://yourdomain.com/api/auth/callback/google` (生产环境)
5. 点击 **Create**
6. 复制 **Client ID** 和 **Client Secret**

#### 步骤 3: 配置环境变量

在 `.env` 文件中添加：

```env
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
```

#### 步骤 4: 重启开发服务器

```bash
# 停止当前服务器（Ctrl+C）
# 然后重新启动
npm run dev
```

### 方案 2: 禁用 Google OAuth（临时方案）

如果暂时不需要 Google 登录，可以禁用 Google provider：

编辑 `lib/auth.ts`，注释掉 Google provider：

```typescript
export const { handlers, signIn, signOut, auth } = NextAuth({
  adapter: PrismaAdapter(prisma) as any,
  providers: [
    Credentials({
      // ... credentials config
    }),
    // Google({
    //   clientId: process.env.GOOGLE_CLIENT_ID || '',
    //   clientSecret: process.env.GOOGLE_CLIENT_SECRET || '',
    // }),
  ],
  // ... rest of config
})
```

然后重启开发服务器。

### 方案 3: 添加条件检查（推荐）

修改 `lib/auth.ts`，只在配置了 Google credentials 时才启用：

```typescript
providers: [
  Credentials({
    // ... credentials config
  }),
  ...(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET
    ? [
        Google({
          clientId: process.env.GOOGLE_CLIENT_ID,
          clientSecret: process.env.GOOGLE_CLIENT_SECRET,
        }),
      ]
    : []),
],
```

这样即使没有配置 Google OAuth，应用也能正常运行。

## 验证配置

配置完成后，验证：

1. 检查环境变量：
   ```bash
   grep GOOGLE .env
   ```

2. 重启开发服务器：
   ```bash
   npm run dev
   ```

3. 尝试 Google 登录：
   - 访问 `/auth/signin`
   - 点击 "Sign in with Google"
   - 应该跳转到 Google 登录页面

## 常见问题

### 问题 1: "redirect_uri_mismatch"

**原因**: 重定向 URI 不匹配

**解决**: 确保在 Google Cloud Console 中配置的重定向 URI 与 NextAuth 使用的完全一致：
- 开发环境: `http://localhost:3000/api/auth/callback/google`
- 生产环境: `https://yourdomain.com/api/auth/callback/google`

### 问题 2: "invalid_client"

**原因**: Client ID 或 Client Secret 错误

**解决**: 
- 检查 `.env` 文件中的值是否正确
- 确保没有多余的空格或引号
- 重启开发服务器

### 问题 3: OAuth 同意屏幕未配置

**原因**: 首次创建 OAuth 客户端时需要配置同意屏幕

**解决**: 
- 在 Google Cloud Console 中完成 OAuth 同意屏幕配置
- 选择 "External" 用户类型
- 填写必填字段

## 安全注意事项

1. **不要提交 `.env` 文件到 Git**
   - 确保 `.env` 在 `.gitignore` 中

2. **生产环境配置**
   - 使用环境变量管理服务（如 Vercel、Railway 等）
   - 不要硬编码 credentials

3. **限制 OAuth 客户端**
   - 只添加必要的重定向 URI
   - 定期检查 OAuth 客户端的使用情况

## 快速测试

如果只是想测试应用功能，可以：
1. 使用邮箱/密码注册和登录
2. Google OAuth 是可选的，不影响其他功能

