#!/bin/bash

echo "🚀 准备部署 CoffeeCompass..."
echo ""

# 检查 Git 状态
if [ -d .git ]; then
    echo "✅ Git 仓库已初始化"
    
    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  检测到未提交的更改"
        echo ""
        read -p "是否提交所有更改？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            git commit -m "Prepare for deployment"
            echo "✅ 更改已提交"
        fi
    else
        echo "✅ 没有未提交的更改"
    fi
    
    # 检查远程仓库
    if git remote get-url origin &>/dev/null; then
        echo "✅ 远程仓库已配置"
        echo "   远程 URL: $(git remote get-url origin)"
    else
        echo "⚠️  未配置远程仓库"
        echo ""
        echo "请运行以下命令添加远程仓库："
        echo "  git remote add origin https://github.com/你的用户名/CoffeeCompass.git"
        echo "  git push -u origin main"
    fi
else
    echo "❌ 未初始化 Git 仓库"
    echo ""
    echo "请运行以下命令："
    echo "  git init"
    echo "  git add ."
    echo "  git commit -m 'Initial commit'"
fi

echo ""
echo "📋 部署前检查清单："
echo ""
echo "环境变量："
if grep -q "NEXT_PUBLIC_MAPBOX_TOKEN" .env 2>/dev/null; then
    echo "  ✅ NEXT_PUBLIC_MAPBOX_TOKEN 已设置"
else
    echo "  ❌ NEXT_PUBLIC_MAPBOX_TOKEN 未设置"
fi

if grep -q "NEXTAUTH_SECRET" .env 2>/dev/null; then
    echo "  ✅ NEXTAUTH_SECRET 已设置"
else
    echo "  ❌ NEXTAUTH_SECRET 未设置"
    echo "     运行: openssl rand -base64 32"
fi

if grep -q "GOOGLE_CLIENT_ID" .env 2>/dev/null; then
    echo "  ✅ GOOGLE_CLIENT_ID 已设置"
else
    echo "  ⚠️  GOOGLE_CLIENT_ID 未设置（可选）"
fi

echo ""
echo "数据库："
if docker ps | grep -q coffeecompass-db; then
    echo "  ✅ 本地数据库运行中"
else
    echo "  ⚠️  本地数据库未运行"
fi

echo ""
echo "📝 下一步："
echo "1. 推送代码到 GitHub"
echo "2. 访问 https://vercel.com/new"
echo "3. 导入你的 GitHub 仓库"
echo "4. 配置环境变量"
echo "5. 部署！"
echo ""
echo "详细指南：查看 DEPLOYMENT_GUIDE.md"

