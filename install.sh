#!/bin/bash
# GitBook 监控安装脚本（Linux 专用）

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SKILL_DIR/config.json"

echo "🚀 安装 GitBook 监控..."

# 检查是否在 Linux 上
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ 此技能仅支持 Linux 系统"
    exit 1
fi

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 配置文件不存在: $CONFIG_FILE"
    echo "请先复制 config.example.json 为 config.json 并编辑"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "$SKILL_DIR/venv" ]; then
    echo "❌ 虚拟环境不存在"
    echo "请先运行："
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install langchain-community beautifulsoup4 requests"
    exit 1
fi

# 读取检查间隔
CHECK_INTERVAL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['check_interval'])")

echo "📝 配置信息："
echo "  - 检查间隔: ${CHECK_INTERVAL}秒"
echo "  - 技能目录: $SKILL_DIR"

# 检测使用 systemd 还是 cron
if command -v systemctl &> /dev/null && systemctl --user status &> /dev/null; then
    # 使用 systemd
    echo "🔧 使用 systemd timer..."
    
    SERVICE_FILE="$HOME/.config/systemd/user/gitbook-monitor.service"
    TIMER_FILE="$HOME/.config/systemd/user/gitbook-monitor.timer"
    
    mkdir -p "$HOME/.config/systemd/user"
    
    # 生成 service 文件
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=GitBook Monitor Service
After=network.target

[Service]
Type=oneshot
ExecStart=$SKILL_DIR/monitor_cron.sh
WorkingDirectory=$SKILL_DIR
StandardOutput=append:$SKILL_DIR/monitor.log
StandardError=append:$SKILL_DIR/monitor.log

[Install]
WantedBy=default.target
EOF
    
    # 生成 timer 文件
    cat > "$TIMER_FILE" << EOF
[Unit]
Description=GitBook Monitor Timer
Requires=gitbook-monitor.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=${CHECK_INTERVAL}s
AccuracySec=1s

[Install]
WantedBy=timers.target
EOF
    
    # 重载并启动
    systemctl --user daemon-reload
    systemctl --user enable gitbook-monitor.timer
    systemctl --user start gitbook-monitor.timer
    
    echo ""
    echo "✨ 安装完成！"
    echo ""
    echo "📊 查看状态："
    echo "  systemctl --user status gitbook-monitor.timer"
    echo ""
    echo "📝 查看日志："
    echo "  tail -f $SKILL_DIR/monitor.log"
    echo "  journalctl --user -u gitbook-monitor.service -f"
    
else
    # 使用 cron
    echo "🔧 使用 cron..."
    
    # 计算 cron 间隔（分钟）
    CRON_INTERVAL=$((CHECK_INTERVAL / 60))
    if [ $CRON_INTERVAL -lt 1 ]; then
        CRON_INTERVAL=1
    fi
    
    CRON_ENTRY="*/$CRON_INTERVAL * * * * $SKILL_DIR/monitor_cron.sh >> $SKILL_DIR/monitor.log 2>&1"
    
    # 检查是否已存在
    if crontab -l 2>/dev/null | grep -q "$SKILL_DIR/monitor_cron.sh"; then
        echo "🔄 更新现有 cron 任务..."
        (crontab -l 2>/dev/null | grep -v "$SKILL_DIR/monitor_cron.sh"; echo "$CRON_ENTRY") | crontab -
    else
        echo "➕ 添加 cron 任务..."
        (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    fi
    
    echo ""
    echo "✨ 安装完成！"
    echo ""
    echo "📊 查看 cron 任务："
    echo "  crontab -l | grep gitbook"
    echo ""
    echo "📝 查看日志："
    echo "  tail -f $SKILL_DIR/monitor.log"
fi

echo ""
echo "🛑 卸载："
echo "  $SKILL_DIR/uninstall.sh"

# 测试运行一次
echo ""
echo "🧪 测试运行..."
$SKILL_DIR/monitor_cron.sh
echo "✅ 测试完成，请检查日志"
