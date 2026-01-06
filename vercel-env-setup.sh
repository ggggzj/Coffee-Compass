#!/bin/bash

echo "🚀 Vercel 环境变量配置助手"
echo ""
echo "这个脚本会帮你准备部署到 Vercel 所需的环境变量"
echo ""

# 生成 NEXTAUTH_SECRET
echo "1️⃣ 生成 NEXTAUTH_SECRET..."
if command -v openssl &> /dev/null; then
    SECRET=$(openssl rand -base64 32)
    echo "✅ 生成的密钥："
    echo "   $SECRET"
    echo ""
    echo "📋 复制上面的密钥，稍后在 Vercel 中添加为 NEXTAUTH_SECRET"
else
    echo "⚠️  OpenSSL 未安装，使用 Node.js 生成..."
    SECRET=$(node -e "console.log(require('crypto').randomBytes(32).toString('base64'))")
    echo "✅ 生成的密钥："
    echo "   $SECRET"
    echo ""
    echo "📋 复制上面的密钥，稍后在 Vercel 中添加为 NEXTAUTH_SECRET"
fi

echo ""
echo "2️⃣ 检查本地环境变量..."
echo ""

# 检查本地 .env 文件
if [ -f .env ]; then
    echo "✅ 找到 .env 文件"
    echo ""
    
    # 检查 MAPBOX_TOKEN
    if grep -q "NEXT_PUBLIC_MAPBOX_TOKEN" .env; then
        echo "✅ NEXT_PUBLIC_MAPBOX_TOKEN 已设置"
        echo "   📋 从 .env 复制这个值到 Vercel"
    else
        echo "❌ NEXT_PUBLIC_MAPBOX_TOKEN 未设置"
    fi
    
    # 检查 GOOGLE_CLIENT_ID
    if grep -q "GOOGLE_CLIENT_ID" .env; then
        echo "✅ GOOGLE_CLIENT_ID 已设置（可选）"
        echo "   📋 从 .env 复制这个值到 Vercel（如果使用 Google 登录）"
    else
        echo "⚠️  GOOGLE_CLIENT_ID 未设置（可选，如果使用 Google 登录）"
    fi
    
    # 检查 GOOGLE_CLIENT_SECRET
    if grep -q "GOOGLE_CLIENT_SECRET" .env; then
        echo "✅ GOOGLE_CLIENT_SECRET 已设置（可选）"
        echo "   📋 从 .env 复制这个值到 Vercel（如果使用 Google 登录）"
    else
        echo "⚠️  GOOGLE_CLIENT_SECRET 未设置（可选，如果使用 Google 登录）"
    fi
else
    echo "❌ 未找到 .env 文件"
fi

echo ""
echo "3️⃣ 部署步骤："
echo ""
echo "   1. 访问 https://vercel.com/new"
echo "   2. 导入你的 GitHub 仓库"
echo "   3. 点击 'Deploy'（先不添加环境变量）"
echo "   4. 等待部署完成"
echo "   5. 复制你的 Vercel URL（例如：https://coffee-compass-xxxxx.vercel.app）"
echo "   6. 在 Vercel 项目设置中添加环境变量："
echo ""
echo "      NEXTAUTH_SECRET=$SECRET"
echo "      NEXTAUTH_URL=https://your-project-name.vercel.app（替换为你的实际URL）"
echo "      DATABASE_URL=稍后配置（先添加占位符）"
echo "      NEXT_PUBLIC_MAPBOX_TOKEN=从.env复制"
echo ""
echo "   7. 点击 'Redeploy' 重新部署"
echo ""
echo "📝 详细说明：查看 VERCEL_ENV_VARS.md"
