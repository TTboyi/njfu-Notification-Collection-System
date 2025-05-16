import re
from datetime import datetime, timedelta
import jieba
import jieba.posseg as pseg
from ncatbot.core import BotClient, GroupMessage
from ncatbot.utils import get_log
import aiosqlite
import asyncio
import os
import signal
import sys
import time
import yaml
import html
import sqlite3
import time as _time
import hashlib
import requests

# 设置数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "back", "qq_groups.db")

# 设置配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

# 关键词与表名映射
KEYWORD_TABLE_MAP = {
    "竞赛": "competitions",
    "创新": "competitions",
    "设计": "competitions",
    "通知": "competitions",
    "考试": "notices",
    "选课": "notices",
    "教学": "notices",
    "毕业": "notices",
    "成绩": "notices",
    "期末": "exams",
    "期中": "exams",
    "补考": "exams",
    "重修": "exams",
    "考场": "exams",
    "时间": "exams",
    "实习": "college_internships",
    "实训": "college_internships",
    "基地": "college_internships",
    "报到": "college_internships",
    "鉴定": "college_internships",
    "总结": "college_internships",
    "指导": "college_internships"
}

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)


def load_config():
    """读取配置文件"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def extract_links(text):
    """只提取消息文本中的普通链接和超链接，不提取图片CQ码中的url"""
    text = html.unescape(text)
    # 先去除所有CQ:image部分
    cleaned = re.sub(r'\[CQ:image,[^\]]+\]', '', text)
    # 匹配URL的正则表达式
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    # 匹配超链接的正则表达式
    hyperlink_pattern = r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"'
    # 提取普通URL
    urls = re.findall(url_pattern, cleaned)
    # 提取超链接
    hyperlinks = re.findall(hyperlink_pattern, cleaned)
    # 合并所有链接
    all_links = urls + hyperlinks
    return ",".join(list(set(all_links)))  # 去重并转换为字符串


def extract_dates(text):
    """提取文本中的所有日期"""
    dates = []
    current_date = datetime.now()

    # 定义日期模式
    date_patterns = [
        r'(\d{1,2})月(\d{1,2})[号日]',  # 4月8号
        r'(\d{1,2})\.(\d{1,2})',  # 4.8
        r'(\d{1,2})[号日]',  # 8号
        r'下个月(\d{1,2})[号日]',  # 下个月8号
        r'(\d{1,2})月(\d{1,2})日',  # 4月8日
        r'(\d{1,2})月(\d{1,2})号',  # 4月8号
        r'截止到(\d{1,2})月(\d{1,2})[号日]',  # 截止到4月8号
        r'截止日期[：:]\s*(\d{1,2})月(\d{1,2})[号日]',  # 截止日期：4月8号
        r'报名截止[：:]\s*(\d{1,2})月(\d{1,2})[号日]',  # 报名截止：4月8号
    ]

    # 处理每个模式
    for pattern in date_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            if pattern == r'(\d{1,2})[号日]':
                # 处理单个日期（如"8号"）
                day = int(match.group(1))
                date = current_date.replace(day=day)
            elif pattern == r'下个月(\d{1,2})[号日]':
                # 处理"下个月8号"的情况
                day = int(match.group(1))
                # 计算下个月的日期
                if current_date.month == 12:
                    date = current_date.replace(year=current_date.year + 1, month=1, day=day)
                else:
                    date = current_date.replace(month=current_date.month + 1, day=day)
            else:
                # 处理其他情况
                month = int(match.group(1))
                day = int(match.group(2))
                date = current_date.replace(month=month, day=day)

            dates.append(date.strftime('%Y-%m-%d'))

    # 处理汉字日期
    chinese_dates = {
        '一月': 1, '二月': 2, '三月': 3, '四月': 4, '五月': 5, '六月': 6,
        '七月': 7, '八月': 8, '九月': 9, '十月': 10, '十一月': 11, '十二月': 12
    }

    for cn_month, num_month in chinese_dates.items():
        if cn_month in text:
            # 查找月份后的日期
            date_match = re.search(f'{cn_month}(\\d{{1,2}})[号日]', text)
            if date_match:
                day = int(date_match.group(1))
                date = current_date.replace(month=num_month, day=day)
                dates.append(date.strftime('%Y-%m-%d'))

    return dates


def extract_keywords(text):
    """提取文本中的关键词"""
    keywords = []
    # 使用jieba分词提取关键词
    words = pseg.cut(text)
    for word, flag in words:
        if flag.startswith('n'):  # 提取名词
            keywords.append(word)

    # 检查预定义关键词
    for word in KEYWORD_TABLE_MAP.keys():
        if word in text:
            keywords.append(word)

    return ",".join(list(set(keywords)))  # 去重并转换为字符串


def get_table_names_by_keywords(keywords):
    """根据关键词获取对应的表名"""
    tables = set()
    for kw in keywords.split(","):
        if kw in KEYWORD_TABLE_MAP:
            tables.add(KEYWORD_TABLE_MAP[kw])
    return list(tables)


def set_wal_mode():
    """设置数据库WAL模式"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('PRAGMA journal_mode=WAL;')
    conn.commit()
    conn.close()


def extract_image_urls_and_clean_content(text):
    """提取所有图片url并去除CQ:image部分，返回(图片url列表, 清理后的文本)"""
    image_urls = []

    def repl(match):
        cq = match.group(0)
        url_match = re.search(r'url=([^,\]]+)', cq)
        if url_match:
            image_urls.append(url_match.group(1))
        return ''  # 删除CQ:image部分

    cleaned = re.sub(r'\[CQ:image,[^\]]+\]', repl, text)
    return image_urls, cleaned.strip()


def init_all_tables():
    """初始化所有数据表"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    base_table_structure = '''
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        keywords TEXT,
        link TEXT,
        publish_date TEXT,
        event_date TEXT,
        views INTEGER DEFAULT 0,
        favorites INTEGER DEFAULT 0,
        image_url TEXT
    '''
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS competitions (
            {base_table_structure}
        )
    ''')
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS notices (
            {base_table_structure}
        )
    ''')
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS exams (
            {base_table_structure}
        )
    ''')
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS college_internships (
            {base_table_structure}
        )
    ''')
    conn.commit()
    conn.close()


def download_image(url):
    """下载图片到img目录，返回本地相对路径"""
    try:
        url = url.replace('&amp;', '&')  # 修正url中的转义字符
        # 生成唯一文件名（md5）
        m = hashlib.md5()
        m.update(url.encode('utf-8'))
        filename = m.hexdigest() + '.jpg'
        local_path = os.path.join(IMG_DIR, filename)
        rel_path = os.path.relpath(local_path, os.path.dirname(__file__))
        # 如果已存在则直接返回
        if os.path.exists(local_path):
            return rel_path
        # 下载图片
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(resp.content)
            return rel_path
        else:
            print(f"图片下载失败: {url} code={resp.status_code} resp={resp.text}")
            return ''
    except Exception as e:
        print(f"图片下载异常: {url} {e}")
        return ''


def save_admin_message_to_tables(content, keywords, link, publish_time, event_dates, sender, group_name):
    """保存管理员消息到对应的表，支持图片url、去重
    注意：image_url字段现在存本地相对路径。
    """
    table_names = get_table_names_by_keywords(keywords)
    if not table_names:
        return
    # 处理图片
    image_urls, cleaned_content = extract_image_urls_and_clean_content(content)
    # 自动下载图片并存本地路径
    local_img_paths = []
    for url in image_urls:
        local_path = download_image(url)
        if local_path:
            local_img_paths.append(local_path)
    # 从content生成标题（使用前20个字符）
    title = cleaned_content[:20] + ('...' if len(cleaned_content) > 20 else '')
    # event_date处理：没有提取到日期就空字符串，有则用英文逗号拼接
    if event_dates and any(event_dates):
        event_date_str = ','.join(event_dates)
    else:
        event_date_str = ''
    for attempt in range(5):
        try:
            conn = sqlite3.connect(DB_PATH, timeout=30)
            c = conn.cursor()
            for table in table_names:
                # 去重：用内容+event_date做唯一性约束
                c.execute(f'''SELECT COUNT(*) FROM {table} WHERE content=? AND event_date=?''',
                          (cleaned_content, event_date_str))
                if c.fetchone()[0] > 0:
                    continue  # 已存在则跳过
                c.execute(f'''
                    INSERT INTO {table}
                    (title, content, keywords, link, publish_date, event_date, views, favorites, image_url)
                    VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)
                ''', (title, cleaned_content, keywords, link, publish_time, event_date_str, ','.join(local_img_paths)))
                print(f"写入表 {table}: {title}, {publish_time}, 事件日期: {event_date_str}, 图片: {local_img_paths}")
            conn.commit()
            conn.close()
            break  # 成功就退出循环
        except sqlite3.OperationalError as e:
            if 'locked' in str(e):
                print("数据库被锁，重试中...")
                _time.sleep(0.5)
            else:
                print(f"数据库写入异常: {e}")
                break


async def init_db():
    """初始化数据库"""
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                link TEXT,
                date TEXT,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()


# 初始化配置
config = load_config()
GROUP_MAP = config.get("groups", {})

# 初始化机器人
bot = BotClient()
_log = get_log()

# 设置数据库模式并初始化表
set_wal_mode()
init_all_tables()


@bot.group_event()
async def handle_message(msg: GroupMessage):
    """处理接收到的消息"""
    _log.info(msg)
    group_id = str(msg.group_id)
    group_name = GROUP_MAP.get(group_id, "未知群")
    sender = msg.sender.card or msg.sender.nickname
    msg_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    content = msg.raw_message

    try:
        member_info = await bot.api.get_group_member_info(
            group_id=group_id,
            user_id=msg.user_id,
            no_cache=True
        )
        role = None
        if isinstance(member_info, dict):
            if 'role' in member_info:
                role = member_info['role']
            elif 'data' in member_info and 'role' in member_info['data']:
                role = member_info['data']['role']
        if role in ['owner', 'admin']:
            keywords = extract_keywords(content)
            if keywords:
                link = extract_links(content)
                event_dates = extract_dates(content)
                save_admin_message_to_tables(content, keywords, link, msg_time, event_dates, sender, group_name)
                _log.info(f"已保存管理员消息到多表：{sender} - {msg_time} - {group_name}")
    except Exception as e:
        _log.error(f"获取群成员信息失败: {e}")


def main():
    """主函数"""
    # 创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # 初始化数据库
        loop.run_until_complete(init_db())

        # 启动机器人
        bot.run(bt_uin=config['bot']['uin'])
    finally:
        loop.close()


def graceful_exit(signum, frame):
    """优雅退出处理"""
    print("收到退出信号，准备退出...")
    sys.exit(0)


if __name__ == "__main__":
    # 设置信号处理
    signal.signal(signal.SIGINT, graceful_exit)  # Ctrl+C
    signal.signal(signal.SIGTERM, graceful_exit)  # kill 命令

    # 运行主函数
    main()