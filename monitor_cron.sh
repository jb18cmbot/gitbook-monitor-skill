#!/bin/bash
# GitBook 监控 - Cron 包装脚本

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SKILL_DIR/venv"
LOG_FILE="$SKILL_DIR/monitor.log"

cd "$SKILL_DIR"

# 记录运行时间
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 检查中..." >> "$LOG_FILE"

# 激活虚拟环境并运行监控
if [ -d "$VENV" ]; then
    source "$VENV/bin/activate"
    OUTPUT=$(python3 "$SKILL_DIR/monitor_gitbook.py" 2>&1)
    
    # 如果有输出（变更或错误），记录到日志
    if [ -n "$OUTPUT" ]; then
        echo "$OUTPUT" >> "$LOG_FILE"
        echo "---" >> "$LOG_FILE"
    fi
    
    # 如果检测到变更文件，删除它（避免重复）
    if [ -f "$SKILL_DIR/gitbook_changes.json" ]; then
        rm "$SKILL_DIR/gitbook_changes.json"
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 错误：虚拟环境不存在" >> "$LOG_FILE"
fi
