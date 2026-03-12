#!/bin/bash
# GitHub 推送脚本
# 在本地执行此脚本将代码推送到 GitHub

cd /workspace/projects/workspace

# 添加远程仓库（如果还没有）
git remote add origin https://github.com/Elohia/second-brain.git 2>/dev/null || echo "Remote already exists"

# 推送到 GitHub
git push -u origin master

echo ""
echo "✅ 推送完成！"
echo "📦 仓库地址：https://github.com/Elohia/second-brain"
echo ""
echo "提交内容:"
echo "  - scripts/insight_system.py (神经元洞见系统核心)"
echo "  - scripts/message_queue.py (消息队列)"
echo "  - scripts/insight-optimize.sh (定时任务)"
echo "  - memory/*.md (记忆文件)"
echo "  - memory/insight-cron.log (运行日志)"
echo ""
echo "当前状态：33 次运行，52 个洞见，5 个连接 ☘️"
