#!/usr/bin/env python3
"""
GitBook 监控脚本
- 自动检测 GitBook 内容变更
- 有变更时发送 Telegram 通知
- 可配置检查间隔和通知选项
"""

import json
import hashlib
import time
import subprocess
from pathlib import Path
from datetime import datetime
from langchain_community.document_loaders import GitbookLoader

# 配置文件路径
CONFIG_FILE = Path(__file__).parent / "config.json"
CACHE_FILE = Path(__file__).parent / "gitbook_cache.json"
HASH_FILE = Path(__file__).parent / "gitbook_hash.txt"
STATS_FILE = Path(__file__).parent / "monitor_stats.json"

def load_config():
    """加载配置"""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_FILE}")
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_stats():
    """加载统计信息"""
    if STATS_FILE.exists():
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'total_checks': 0,
        'errors': 0,
        'changes': 0,
        'last_report_time': time.time(),
        'hourly_checks': 0,
        'hourly_errors': 0
    }

def save_stats(stats):
    """保存统计信息"""
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def send_telegram(message, chat_id):
    """发送 Telegram 消息"""
    try:
        subprocess.run([
            'openclaw', 'message', 'send',
            '--target', chat_id,
            '--message', message,
            '--channel', 'telegram'
        ], check=True, capture_output=True, text=True)
    except Exception as e:
        print(f"发送 Telegram 消息失败: {e}")

def check_hourly_report(stats, config):
    """检查是否需要发送小时报告"""
    if not config.get('enable_hourly_report', True):
        return
    
    current_time = time.time()
    elapsed = current_time - stats['last_report_time']
    
    # 每小时（3600 秒）报告一次
    if elapsed >= 3600:
        message = f"📊 GitBook 监控小时报告\n\n"
        message += f"本小时访问次数：{stats['hourly_checks']}\n"
        message += f"错误次数：{stats['hourly_errors']}\n"
        message += f"总访问次数：{stats['total_checks']}\n"
        message += f"总错误次数：{stats['errors']}\n"
        message += f"检测到变更：{stats['changes']} 次"
        
        send_telegram(message, config['telegram_chat_id'])
        
        # 重置小时统计
        stats['last_report_time'] = current_time
        stats['hourly_checks'] = 0
        stats['hourly_errors'] = 0
        save_stats(stats)

def get_content_hash(pages_data):
    """计算内容哈希"""
    content = json.dumps(pages_data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(content.encode()).hexdigest()

def load_cache():
    """加载缓存"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 兼容旧格式
            if isinstance(data, list):
                return data
            return data.get('pages', [])
    return None

def save_cache(pages_data):
    """保存缓存"""
    cache_data = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'pages': pages_data
    }
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, ensure_ascii=False, indent=2)

def load_hash():
    """加载上次的哈希"""
    if HASH_FILE.exists():
        return HASH_FILE.read_text().strip()
    return None

def save_hash(hash_value):
    """保存哈希"""
    HASH_FILE.write_text(hash_value)

def scrape_gitbook(url):
    """抓取 GitBook"""
    loader = GitbookLoader(url, load_all_paths=True)
    all_pages = loader.load()
    
    pages_data = []
    for i, page in enumerate(all_pages, 1):
        page_url = page.metadata.get('source', '')
        path = page_url.replace(f'{url}/', '').replace(url, 'home')
        
        pages_data.append({
            'id': i,
            'path': path,
            'url': page_url,
            'content': page.page_content,
            'length': len(page.page_content)
        })
    
    return pages_data

def compare_changes(old_data, new_data):
    """对比变更"""
    if old_data is None:
        return {
            'type': 'initial',
            'message': '首次运行，已建立基线'
        }
    
    changes = []
    
    # 检查页面数量变化
    if len(old_data) != len(new_data):
        changes.append(f"页面数量变化：{len(old_data)} → {len(new_data)}")
    
    # 对比每个页面
    old_dict = {p['path']: p for p in old_data}
    new_dict = {p['path']: p for p in new_data}
    
    # 新增页面
    new_pages = set(new_dict.keys()) - set(old_dict.keys())
    if new_pages:
        changes.append(f"新增页面：{', '.join(new_pages)}")
    
    # 删除页面
    deleted_pages = set(old_dict.keys()) - set(new_dict.keys())
    if deleted_pages:
        changes.append(f"删除页面：{', '.join(deleted_pages)}")
    
    # 内容变更
    for path in set(old_dict.keys()) & set(new_dict.keys()):
        old_page = old_dict[path]
        new_page = new_dict[path]
        
        if old_page['content'] != new_page['content']:
            old_len = old_page['length']
            new_len = new_page['length']
            diff = new_len - old_len
            changes.append(f"内容变更：{path} ({diff:+d} 字符)")
    
    if changes:
        return {
            'type': 'changed',
            'changes': changes,
            'old_data': old_data,
            'new_data': new_data
        }
    
    return None

def notify_ai(change_info):
    """通知 AI 分析变更（写入文件，由 AI 读取）"""
    notify_file = Path(__file__).parent / "gitbook_changes.json"
    
    with open(notify_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': time.time(),
            'change_info': change_info
        }, f, ensure_ascii=False, indent=2)
    
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 变更已记录到 {notify_file}")

def main():
    """主函数"""
    config = load_config()
    stats = load_stats()
    
    try:
        # 更新统计
        stats['total_checks'] += 1
        stats['hourly_checks'] += 1
        
        # 抓取最新内容
        new_data = scrape_gitbook(config['gitbook_url'])
        new_hash = get_content_hash(new_data)
        
        # 加载旧数据
        old_data = load_cache()
        old_hash = load_hash()
        
        # 快速哈希对比
        if old_hash == new_hash:
            # 无变更，但仍然更新缓存（更新时间戳）
            save_cache(new_data)
            save_stats(stats)
            check_hourly_report(stats, config)
            return
        
        # 详细对比
        change_info = compare_changes(old_data, new_data)
        
        if change_info:
            if change_info['type'] == 'initial':
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {change_info['message']}")
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 检测到变更：")
                for change in change_info['changes']:
                    print(f"  - {change}")

                # 更新变更统计
                stats['changes'] += 1

                # 发送 Telegram 通知
                message = "🔔 GitBook 内容变更\n\n"
                for change in change_info['changes']:
                    message += f"• {change}\n"
                message += f"\n🔗 {config['gitbook_url']}"
                send_telegram(message, config['telegram_chat_id'])

                # 通知 AI
                notify_ai(change_info)
        
        # 保存缓存
        save_cache(new_data)
        save_hash(new_hash)
        save_stats(stats)
        
        # 检查是否需要小时报告
        check_hourly_report(stats, config)
        
    except Exception as e:
        error_msg = f"❌ GitBook 监控错误\n\n{str(e)}\n\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 立即通过 Telegram 发送错误通知
        send_telegram(error_msg, config['telegram_chat_id'])
        
        # 更新错误统计
        stats['errors'] += 1
        stats['hourly_errors'] += 1
        save_stats(stats)
        
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 错误：{e}")

if __name__ == "__main__":
    main()
