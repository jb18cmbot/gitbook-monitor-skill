#!/bin/bash
# GitBook 监控卸载脚本（Linux 专用）

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 卸载 GitBook 监控..."

# systemd
if command -v systemctl &> /dev/null && systemctl --user status &> /dev/null; then
    if systemctl --user list-unit-files | grep -q "gitbook-monitor"; then
        systemctl --user stop gitbook-monitor.timer 2>/dev/null || true
        systemctl --user disable gitbook-monitor.timer 2>/dev/null || true
        rm -f "$HOME/.config/systemd/user/gitbook-monitor.service"
        rm -f "$HOME/.config/systemd/user/gitbook-monitor.timer"
        systemctl --user daemon-reload
        echo "✅ 已卸载 systemd timer"
    fi
fi

# cron
if crontab -l 2>/dev/null | grep -q "$SKILL_DIR/monitor_cron.sh"; then
    crontab -l 2>/dev/null | grep -v "$SKILL_DIR/monitor_cron.sh" | crontab -
    echo "✅ 已卸载 cron 任务"
fi

echo "✅ 卸载完成"
