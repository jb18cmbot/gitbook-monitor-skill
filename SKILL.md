# GitBook Monitor Skill

自动监控 GitBook 内容变更并推送 Telegram 通知。

## 描述

监控指定的 GitBook 文档，检测内容变更（新增/删除/修改页面），自动通过 Telegram 发送通知。支持自定义检查间隔和小时统计报告。

## 前置要求

- Linux 系统（支持 systemd 或 cron）
- Python 3.7+
- OpenClaw 已配置 Telegram

## 安装

```bash
# 1. 进入技能目录
cd ~/.openclaw/skills/gitbook-monitor

# 2. 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate
pip install langchain-community beautifulsoup4 requests

# 3. 配置
cp config.example.json config.json
# 编辑 config.json，填入你的 GitBook URL 和 Telegram Chat ID

# 4. 安装服务
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

**参数说明**：
- `gitbook_url`: 要监控的 GitBook URL
- `telegram_chat_id`: Telegram 聊天 ID（通过 `@userinfobot` 获取）
- `check_interval`: 检查间隔（秒），默认 30
- `enable_hourly_report`: 是否启用小时统计报告

## 使用

安装后会自动运行，无需手动操作。

**查看状态**：
```bash
# systemd
systemctl --user status gitbook-monitor.timer

# cron
crontab -l | grep gitbook
```

**查看日志**：
```bash
tail -f ~/.openclaw/skills/gitbook-monitor/monitor.log
```

**卸载**：
```bash
cd ~/.openclaw/skills/gitbook-monitor
./uninstall.sh
```

## 通知示例

**内容变更通知**：
```
🔔 GitBook 内容变更

• 新增页面：getting-started/installation
• 内容变更：api/reference (+245 字符)

🔗 https://your-gitbook-url.gitbook.io/your-book
```

**小时统计报告**：
```
📊 GitBook 监控小时报告

本小时访问次数：120
错误次数：0
总访问次数：4504
总错误次数：2
检测到变更：3 次
```

## 故障排查

### 查看详细日志
```bash
tail -f ~/.openclaw/skills/gitbook-monitor/monitor.log
```

### 手动测试
```bash
cd ~/.openclaw/skills/gitbook-monitor
source venv/bin/activate
python3 monitor_gitbook.py
```

### 检查服务状态
```bash
# systemd
systemctl --user status gitbook-monitor.timer
journalctl --user -u gitbook-monitor.service -f

# cron
crontab -l
```

## 技术细节

- 使用 LangChain GitbookLoader 抓取内容
- SHA256 哈希快速检测变更
- 详细对比页面差异
- 通过 OpenClaw 发送 Telegram 消息
- 支持 systemd timer（优先）或 cron（fallback）

## 许可证

MIT License
