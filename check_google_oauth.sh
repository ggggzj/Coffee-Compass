#!/bin/bash

echo "🔍 检查 Google OAuth 配置..."
echo ""

if [ ! -f .env ]; then
    echo "❌ .env 文件不存在"
    exit 1
fi

GOOGLE_CLIENT_ID=$(grep "^GOOGLE_CLIENT_ID=" .env | cut -d '=' -f2)
GOOGLE_CLIENT_SECRET=$(grep "^GOOGLE_CLIENT_SECRET=" .env | cut -d '=' -f2)

if [ -z "$GOOGLE_CLIENT_ID" ] || [ "$GOOGLE_CLIENT_ID" = "" ]; then
    echo "❌ GOOGLE_CLIENT_ID 未设置"
    echo "   请在 .env 文件中添加: GOOGLE_CLIENT_ID=你的客户端ID"
else
    echo "✅ GOOGLE_CLIENT_ID 已设置"
    echo "   值: ${GOOGLE_CLIENT_ID:0:30}..."
fi

if [ -z "$GOOGLE_CLIENT_SECRET" ] || [ "$GOOGLE_CLIENT_SECRET" = "" ]; then
    echo "❌ GOOGLE_CLIENT_SECRET 未设置"
    echo "   请在 .env 文件中添加: GOOGLE_CLIENT_SECRET=你的客户端密钥"
else
    echo "✅ GOOGLE_CLIENT_SECRET 已设置"
    echo "   值: ${GOOGLE_CLIENT_SECRET:0:20}..."
fi

echo ""
echo "📝 配置指南: 查看 GOOGLE_OAUTH_QUICK_SETUP.md"
