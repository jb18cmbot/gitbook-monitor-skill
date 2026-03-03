# GitBook Monitor - OpenClaw Skill (Linux)

自动监控 GitBook 内容变更并推送 Telegram 通知。

## 一键安装

```bash
cd ~/.openclaw/skills
git clone https://github.com/jb18cmbot/gitbook-monitor-skill.git gitbook-monitor
cd gitbook-monitor
python3 -m venv venv
source venv/bin/activate
pip install langchain-community beautifulsoup4 requests
cp config.example.json config.json
# 编辑 config.json 填入你的配置
./install.sh
```

## 配置

编辑 `config.json`：

```json
{
  "gitbook_url": "https://your-gitbook-url.gitbook.io/your-book",
  "telegram_chat_id": "your_chat_id",
  "check_interval": 30,
  "enable_hourly_report": true
}
```

获取 Telegram Chat ID：发送消息给 `@userinfobot`

## 功能

- ✅ 自动检测内容变更（新增/删除/修改页面）
- ✅ Telegram 实时通知
- ✅ 可自定义检查间隔
- ✅ 小时统计报告
- ✅ 错误自动通知
- ✅ 支持 systemd timer 或 cron

## 管理

```bash
# 查看状态
systemctl --user status gitbook-monitor.timer  # systemd
crontab -l | grep gitbook                       # cron

# 查看日志
tail -f ~/.openclaw/skills/gitbook-monitor/monitor.log

# 卸载
./uninstall.sh
```

## 系统要求

- Linux（systemd 或 cron）
- Python 3.7+
- OpenClaw + Telegram

## 许可证

MIT
