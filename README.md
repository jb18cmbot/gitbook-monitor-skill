# GitBook Monitor - OpenClaw Skill

自动监控 GitBook 内容变更并推送 Telegram 通知（Linux 专用）。

## 快速安装

```bash
# 1. 克隆到 OpenClaw skills 目录
cd ~/.openclaw/skills
git clone https://github.com/jb18cmbot/gitbook-monitor.git

# 2. 安装依赖
cd gitbook-monitor
python3 -m venv venv
source venv/bin/activate
pip install langchain-community beautifulsoup4 requests

# 3. 配置
cp config.example.json config.json
nano config.json  # 编辑配置

# 4. 安装服务
./install.sh
```

## 配置说明

编辑 `config.json`：

```json
{
  "gitbook_url": "https://your-gitbook-url.gitbook.io/your-book",
  "telegram_chat_id": "your_chat_id",
  "check_interval": 30,
  "enable_hourly_report": true
}
```

获取 Telegram Chat ID：
1. 在 Telegram 中找 `@userinfobot`
2. 发送 `/start`
3. 复制你的 ID

## 功能特性

- ✅ 自动检测 GitBook 内容变更
- ✅ 实时 Telegram 推送通知
- ✅ 可自定义检查间隔（默认 30 秒）
- ✅ 详细的变更记录（新增/删除/修改页面）
- ✅ 小时统计报告
- ✅ 错误自动通知
- ✅ 支持 systemd timer 或 cron

## 管理命令

```bash
# 查看状态（systemd）
systemctl --user status gitbook-monitor.timer

# 查看状态（cron）
crontab -l | grep gitbook

# 查看日志
tail -f ~/.openclaw/skills/gitbook-monitor/monitor.log

# 手动测试
cd ~/.openclaw/skills/gitbook-monitor
source venv/bin/activate
python3 monitor_gitbook.py

# 卸载
./uninstall.sh
```

## 通知示例

**内容变更**：
```
🔔 GitBook 内容变更

• 新增页面：getting-started/installation
• 内容变更：api/reference (+245 字符)

🔗 https://your-gitbook-url.gitbook.io/your-book
```

**小时报告**：
```
📊 GitBook 监控小时报告

本小时访问次数：120
错误次数：0
总访问次数：4504
检测到变更：3 次
```

## 系统要求

- Linux（支持 systemd 或 cron）
- Python 3.7+
- OpenClaw 已配置 Telegram

## 许可证

MIT License

## 作者

jb18cm
