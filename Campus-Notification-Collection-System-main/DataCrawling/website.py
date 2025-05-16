# 导入所需的库
import sqlite3
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import socket
import sys
import os
import pytesseract
from PIL import Image
from io import BytesIO
import re
import pdfplumber
from datetime import datetime


# 设置Tesseract OCR路径
pytesseract.pytesseract.tesseract_cmd = r'D:/tesseract-ocr/tesseract.exe'

# 设置数据库路径
DB_PATH = "E:/代码/linux作业/back/website.db"

# 日期正则表达式
DATE_PATTERN = r'(\d{4}\s*[年/-]\s*\d{1,2}\s*[月/-]\s*\d{1,2}(?:\s*日)?(?:\s*\d{1,2}:\d{2})?)'


def print_progress(message, progress):
    """打印进度条"""
    bar_length = 50
    filled_length = int(bar_length * progress)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    sys.stdout.write(f'\r{message}: [{bar}] {progress * 100:.1f}%')
    sys.stdout.flush()


def simulate_progress(message, duration=3):
    """模拟进度显示"""
    start_time = time.time()
    last_progress = -1
    while time.time() - start_time < duration:
        progress = (time.time() - start_time) / duration
        if int(progress * 1000) > last_progress:
            print_progress(message, progress)
            last_progress = int(progress * 1000)
        time.sleep(0.05)
    print_progress(message, 1.0)
    print()


def check_internet_connection():
    """检查网络连接"""
    try:
        socket.create_connection(("www.baidu.com", 80), timeout=5)
        return True
    except OSError:
        return False


def check_login_status(driver):
    """检查登录状态"""
    try:
        time.sleep(3)
        current_title = driver.title
        if ("教务系统" in current_title or "教学管理系统" in current_title or "学科竞赛" in current_title):
            print("登录成功！")
            return True
        else:
            print("登录状态未知，当前页面标题：", current_title)
            return False
    except Exception as e:
        print("检查登录状态时出错：", str(e))
        return False


def test_database_connection():
    """测试数据库连接"""
    try:
        db_dir = os.path.dirname(DB_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        print(f"数据库连接成功！数据库位置：{DB_PATH}")
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"数据库连接失败：{str(e)}")
        return False


def extract_dates_from_image(image_url):
    """从图片中提取日期信息"""
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code != 200:
            return None, None
        image = Image.open(BytesIO(response.content))
        text = pytesseract.image_to_string(image, lang='chi_sim')
        dates = re.findall(DATE_PATTERN, text)
        if len(dates) == 1:
            return dates[0], None
        elif len(dates) >= 2:
            return dates[0], dates[1]
        return None, None
    except Exception as e:
        print(f"提取日期时出错：{str(e)}")
        return None, None


def extract_dates_from_text(text):
    """从文本中提取日期信息（改进版）"""
    # 过滤掉当前日期
    today = datetime.now().strftime("%Y年%m月%d日")
    today_alt = datetime.now().strftime("%Y-%m-%d")

    # 优先查找"截止时间"、"报名时间"等关键词附近的日期
    deadline_patterns = [
        r'(截止时间[:：]\s*)(\d{4}\s*[年/-]\s*\d{1,2}\s*[月/-]\s*\d{1,2}\s*日?)',
        r'(报名时间[:：]\s*)(\d{4}\s*[年/-]\s*\d{1,2}\s*[月/-]\s*\d{1,2}\s*日?)',
        r'(时间[:：]\s*)(\d{4}\s*[年/-]\s*\d{1,2}\s*[月/-]\s*\d{1,2}\s*日?)',
    ]

    duration_lines = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # 检查是否是当前日期
        if today in line or today_alt in line:
            continue

        # 查找关键词附近的日期
        for pattern in deadline_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                date = match[1]
                remark = line.replace(match[0] + match[1], '').strip(' ：:，,。.\n')
                if remark:
                    duration_lines.append(f"{date}：{remark}")
                else:
                    duration_lines.append(date)

        # 查找所有日期
        dates = re.findall(DATE_PATTERN, line)
        for date in dates:
            if today not in date and today_alt not in date:
                remark = line.replace(date, '').strip(' ：:，,。.\n')
                if remark and not any(d in remark for d in dates):
                    duration_lines.append(f"{date}：{remark}")
                else:
                    duration_lines.append(date)

    # 去重并保留顺序
    seen = set()
    unique_lines = []
    for line in duration_lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    return '\n'.join(unique_lines) if unique_lines else ''


def extract_dates_from_pdf(pdf_url):
    """从PDF文件中提取日期信息（改进版）"""
    try:
        response = requests.get(pdf_url, timeout=10)
        if response.status_code != 200:
            print(f"无法下载PDF文件，HTTP状态码: {response.status_code}")
            return None, None, ''

        temp_pdf = 'temp.pdf'
        with open(temp_pdf, 'wb') as f:
            f.write(response.content)

        text = ''
        duration_lines = []

        # 方法1: 使用pdfplumber提取文本
        try:
            with pdfplumber.open(temp_pdf) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ''
                    text += page_text

                    for line in page_text.split('\n'):
                        line = line.strip()
                        if not line:
                            continue

                        dates = re.findall(DATE_PATTERN, line)
                        for date in dates:
                            remark = line.replace(date, '').strip(' ：:，,。.\n')
                            if remark:
                                duration_lines.append(f"{date}：{remark}")
                            else:
                                duration_lines.append(date)
        except Exception as e:
            print(f"pdfplumber提取失败: {str(e)}")
            text = ''

        # 方法2: 如果文本提取失败，尝试OCR
        if not text.strip():
            print("尝试使用OCR提取PDF内容...")
            try:
                with pdfplumber.open(temp_pdf) as pdf:
                    for page in pdf.pages:
                        img = page.to_image(resolution=300).original
                        ocr_text = pytesseract.image_to_string(img, lang='chi_sim')
                        text += ocr_text

                        for line in ocr_text.split('\n'):
                            line = line.strip()
                            if not line:
                                continue

                            dates = re.findall(DATE_PATTERN, line)
                            for date in dates:
                                remark = line.replace(date, '').strip(' ：:，,。.\n')
                                if remark:
                                    duration_lines.append(f"{date}：{remark}")
                                else:
                                    duration_lines.append(date)
            except Exception as e:
                print(f"OCR提取失败: {str(e)}")

        os.remove(temp_pdf)

        if duration_lines:
            seen = set()
            unique_lines = []
            for line in duration_lines:
                if line not in seen:
                    seen.add(line)
                    unique_lines.append(line)

            duration_text = '\n'.join(unique_lines)

            all_dates = re.findall(DATE_PATTERN, text)
            if len(all_dates) >= 2:
                return all_dates[0], all_dates[1], duration_text
            elif all_dates:
                return all_dates[0], None, duration_text
            else:
                return None, None, duration_text
        else:
            print("未从PDF中提取到任何日期信息")
            return None, None, ''

    except Exception as e:
        print(f"提取PDF日期时出错：{str(e)}")
        if os.path.exists('temp.pdf'):
            os.remove('temp.pdf')
        return None, None, ''


class PageConfig:
    """页面配置类"""
    def __init__(self, url, name, table_class, keywords_rules):
        self.url = url
        self.name = name  # 页面名称
        self.table_class = table_class  # 表格的class名
        self.keywords_rules = keywords_rules  # 关键词提取规则

def get_page_configs():
    """获取所有页面的配置"""
    base_url = "https://webvpn.njfu.edu.cn/webvpn/LjIwMS4xNjkuMjE4LjE2OA==/LjIwMy4xNzIuMjAxLjEwMi4xNjIuMTU5LjIwMi4xNjguMTQ3LjE1MS4xNTYuMTczLjE0OC4xNTMuMTY1"
    
    # 竞赛页面配置
    competition_keywords = {
        "竞赛": ["竞赛"],
        "创新": ["创新"],
        "设计": ["设计"],
        "通知": ["通知"]
    }
    
    # 教务通知页面配置
    notice_keywords = {
        "考试": ["考试"],
        "选课": ["选课"],
        "教学": ["教学"],
        "毕业": ["毕业"],
        "成绩": ["成绩"]
    }
    
    # 考试通知页面配置
    exam_keywords = {
        "期末": ["期末考试"],
        "期中": ["期中考试"],
        "补考": ["补考"],
        "重修": ["重修"],
        "考场": ["考场安排"],
        "时间": ["考试时间"]
    }
    
    # 学院实习页面配置
    college_internship_keywords = {
        "实习": ["实习"],
        "实训": ["实训"],
        "基地": ["实习基地"],
        "报到": ["报到"],
        "鉴定": ["实习鉴定"],
        "总结": ["实习总结"],
        "指导": ["实习指导"]
    }
    
    return [
        PageConfig(
            f"{base_url}//sjjx/xkjs/index.html?vpn-0",
            "competitions",
            "datalist",
            competition_keywords
        ),
        PageConfig(
            f"{base_url}//jwgl/jwtz/index.html?vpn-0",
            "notices",
            "datalist",
            notice_keywords
        ),
        PageConfig(
            f"{base_url}//ksgl/kstz/index.html?vpn-0",
            "exams",
            "datalist",
            exam_keywords
        ),
        PageConfig(
            f"{base_url}//sjjx/jzsjhj/index.html?vpn-0",
            "college_internships",
            "datalist",
            college_internship_keywords
        )
    ]

def process_page(driver, page_config):
    """通用的页面处理函数"""
    print(f"\n开始处理{page_config.name}页面...")
    
    try:
        print(f"正在访问{page_config.name}页面...")
        driver.get(page_config.url)
        time.sleep(3)  # 等待页面加载
        
        print("正在获取页面内容...")
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        items = []
        # 首先尝试查找ajaxpage-list
        ajax_div = soup.find('div', id='ajaxpage-list')
        if ajax_div:
            table = ajax_div.find('table')
        else:
            # 如果没有ajaxpage-list，则直接查找datalist表格
            table = soup.find('table', class_=page_config.table_class)
        
        if not table:
            print(f"未找到{page_config.name}列表，页面结构可能有变")
            return []
            
        rows = []
        # 遍历表格行
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) >= 3:
                a_tag = tds[1].find('a')  # 标题和链接在第二列
                date_element = tds[2].find('div') or tds[2]  # 日期可能在div中或直接在td中
                
                if a_tag and date_element:
                    title = a_tag.get_text(strip=True)
                    link = a_tag['href']
                    if not link.startswith('http'):
                        link = 'https://webvpn.njfu.edu.cn' + link
                    date = date_element.get_text(strip=True).strip('[]')
                    
                    # 检查是否是我们想要的内容类型
                    if page_config.name == "competitions" and not title.endswith('通知'):
                        continue
                    if page_config.name == "competitions" and ('统计工作' in title or '更新调整工作' in title):
                        continue
                        
                    rows.append((title, date, link))
        
        # 处理每个条目
        for idx, (title, date, link) in enumerate(rows):
            print(f"\n正在处理第{idx + 1}/{len(rows)}个{page_config.name}条目: {title}")
            try:
                driver.execute_script(f"window.open('{link}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(2)
                
                detail_html = driver.page_source
                detail_soup = BeautifulSoup(detail_html, 'html.parser')
                
                content = ""
                # 查找内容
                content_div = detail_soup.find('div', id='zoom') or detail_soup.find('div', id='textarea')
                if content_div:
                    content = content_div.get_text(separator='\n', strip=True)
                
                # 提取关键字
                keywords = []
                for key, values in page_config.keywords_rules.items():
                    if key in title or key in content:
                        keywords.extend(values)
                
                keywords_str = ",".join(keywords)
                items.append((title, content, keywords_str, link, date, 0, 0))
                
            except Exception as e:
                print(f"处理{page_config.name}详情页面时出错：{str(e)}")
                items.append((title, "", "", link, date, 0, 0))
            finally:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)
                
        return items
        
    except Exception as e:
        print(f"处理{page_config.name}页面时出错：{str(e)}")
        return []

def save_to_database(all_data):
    """保存数据到数据库"""
    print("\n正在连接数据库...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 删除旧表（如果存在）
    for page_config in get_page_configs():
        cursor.execute(f'DROP TABLE IF EXISTS {page_config.name}')
    
    # 创建所有表
    for page_config in get_page_configs():
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {page_config.name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,           -- 标题
                content TEXT,        -- 内容
                keywords TEXT,       -- 关键字
                link TEXT,          -- 链接
                publish_date TEXT,   -- 发布日期
                views INTEGER DEFAULT 0,     -- 浏览量
                favorites INTEGER DEFAULT 0   -- 收藏量
            )
        ''')
    
    try:
        # 保存所有数据
        for page_config in get_page_configs():
            if page_config.name in all_data and all_data[page_config.name]:
                print(f"\n正在保存{page_config.name}数据...")
                cursor.executemany(f'''
                    INSERT INTO {page_config.name}
                    (title, content, keywords, link, publish_date, views, favorites)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', all_data[page_config.name])
                print(f"成功保存 {len(all_data[page_config.name])} 条{page_config.name}信息")
        
        conn.commit()
        
        # 显示数据库统计信息
        print("\n数据库统计:")
        for page_config in get_page_configs():
            cursor.execute(f'SELECT COUNT(*) FROM {page_config.name}')
            count = cursor.fetchone()[0]
            print(f"- {page_config.name}: {count} 条")
        
    except Exception as e:
        print(f"保存数据时出错：{str(e)}")
        conn.rollback()
    finally:
        conn.close()
        print("数据库连接已关闭")

def main():
    # 检查网络连接
    print("正在检查网络连接...")
    if not check_internet_connection():
        print("错误：无法连接到网络，请检查网络连接")
        exit(1)
    print("网络连接正常")
    
    # 配置Edge浏览器选项
    print("正在配置浏览器选项...")
    options = webdriver.EdgeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = 'eager'
    
    driver = None
    try:
        # 初始化Edge浏览器
        print("\n正在启动Edge浏览器...")
        try:
            print("正在下载/检查Edge驱动...")
            simulate_progress("下载驱动", 2)
            
            print("正在启动浏览器服务...")
            service = Service(EdgeChromiumDriverManager().install())
            service.start()
            simulate_progress("启动服务", 1)
            
            print("正在初始化浏览器...")
            driver = webdriver.Edge(service=service, options=options)
            simulate_progress("初始化浏览器", 2)
            
            driver.set_window_size(1024, 768)
            print("\nEdge浏览器启动完成！")
        except Exception as e:
            print(f"\nEdge浏览器启动失败：{str(e)}")
            print("请确保：")
            print("1. 已安装Microsoft Edge浏览器")
            print("2. 网络连接正常")
            print("3. 有足够的系统权限")
            exit(1)
            
        # 登录流程
        login_url = get_page_configs()[0].url  # 使用第一个页面作为登录入口
        
        print("\n正在访问登录页面...")
        try:
            simulate_progress("加载页面", 2)
            driver.get(login_url)
        except Exception as e:
            print(f"\n访问登录页面失败：{str(e)}")
            print("请检查网络连接和VPN状态")
            if driver:
                driver.quit()
            exit(1)
            
        wait = WebDriverWait(driver, 10)
        try:
            print("正在等待页面元素加载...")
            simulate_progress("加载元素", 2)
            username_field = wait.until(EC.presence_of_element_located((By.ID, "username")))
            password_field = wait.until(EC.presence_of_element_located((By.ID, "password")))
            print("\n成功找到登录表单！")
        except TimeoutException:
            print("\n错误：无法找到登录表单，请检查页面是否正确加载")
            if driver:
                driver.quit()
            exit(1)
            
        # 学号 和 密码
        username = "2250801313"
        password = "Mxy200436654321!"
        
        print("\n正在输入登录信息...")
        simulate_progress("输入信息", 1)
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            print("\n已点击登录按钮")
        except NoSuchElementException:
            print("\n错误：无法找到登录按钮")
            if driver:
                driver.quit()
            exit(1)
            
        if not check_login_status(driver):
            print("登录失败，程序退出")
            if driver:
                driver.quit()
            exit(1)
            
        if not test_database_connection():
            print("数据库连接失败，程序退出")
            if driver:
                driver.quit()
            exit(1)
        
        # 处理所有页面
        all_data = {}
        for page_config in get_page_configs():
            all_data[page_config.name] = process_page(driver, page_config)
        
        # 保存到数据库
        save_to_database(all_data)
        
    except Exception as e:
        print(f"\n程序运行出错：{str(e)}")
    finally:
        print("\n程序将在30秒后关闭...")
        if driver:
            time.sleep(30)
            driver.quit()
            print("浏览器已关闭")


if __name__ == "__main__":
    main()