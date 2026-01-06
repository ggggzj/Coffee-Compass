#!/bin/bash

echo "🚀 Git 提交和推送助手"
echo ""

# 检查 Git 状态
echo "📋 当前 Git 状态："
git status --short
echo ""

# 显示已暂存的文件
echo "✅ 已暂存的文件："
git diff --cached --name-only
echo ""

# 显示未暂存的文件
echo "📝 未暂存的文件："
git diff --name-only
echo ""

# 询问是否添加所有文件
read -p "是否添加所有更改的文件？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 添加所有文件..."
    git add .
    echo "✅ 文件已添加"
    echo ""
fi

# 显示提交信息建议
echo "💡 提交信息建议："
echo "   1. Fix build errors and add deployment configuration"
echo "   2. Complete full stack implementation with fixes"
echo "   3. Fix ESLint and TypeScript errors for deployment"
echo ""

# 询问提交信息
read -p "请输入提交信息（或按回车使用默认信息）: " commit_message

if [ -z "$commit_message" ]; then
    commit_message="Fix build errors and add deployment configuration"
fi

echo ""
echo "📝 提交信息: $commit_message"
echo ""

# 确认提交
read -p "确认提交？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "💾 正在提交..."
    git commit -m "$commit_message"
    echo "✅ 提交完成"
    echo ""
    
    # 询问是否推送
    read -p "是否推送到 GitHub？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 正在推送到 GitHub..."
        git push origin main
        echo ""
        echo "✅ 推送完成！"
        echo ""
        echo "📝 下一步："
        echo "   1. 访问 https://github.com/ggggzj/Coffee-Compass"
        echo "   2. 确认更改已显示"
        echo "   3. 在 Vercel 中部署（如果已连接）"
    else
        echo "⏸️  已跳过推送，稍后可以运行: git push origin main"
    fi
else
    echo "❌ 已取消提交"
fi

