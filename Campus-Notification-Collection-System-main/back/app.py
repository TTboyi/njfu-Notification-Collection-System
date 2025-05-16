from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
from datetime import datetime
import traceback

app = Flask(__name__)
CORS(app)

# 设置数据库文件路径
DB_DIR = os.path.dirname(os.path.abspath(__file__))
QQ_DB_PATH = os.path.join(DB_DIR, 'qq_groups.db')
WEB_DB_PATH = os.path.join(DB_DIR, 'website.db')

def get_db_connection(db_path):
    """获取数据库连接"""
    try:
        if not os.path.exists(db_path):
            raise Exception(f"数据库文件不存在: {db_path}")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"数据库连接错误: {str(e)}")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"数据库路径: {db_path}")
        print(f"堆栈跟踪: {traceback.format_exc()}")
        raise

def standardize_date(date_str):
    """统一日期格式为 YYYY-MM-DD"""
    try:
        # 尝试不同的日期格式
        formats = [
            '%Y-%m-%d',           # 2024-03-21
            '%Y/%m/%d',           # 2024/03/21
            '%Y年%m月%d日',        # 2024年03月21日
            '%Y.%m.%d',           # 2024.03.21
            '%Y-%m-%d %H:%M:%S',  # 2024-03-21 14:30:00
            '%Y/%m/%d %H:%M:%S',  # 2024/03/21 14:30:00
            '%Y年%m月%d日 %H:%M:%S' # 2024年03月21日 14:30:00
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        # 如果所有格式都不匹配，返回原始字符串
        return date_str
    except Exception:
        return date_str

def process_row(row, source_type):
    """处理数据行，统一日期格式"""
    row_dict = dict(row)
    row_dict['source'] = source_type
    
    # 处理日期字段
    if 'publish_date' in row_dict:
        row_dict['publish_date'] = standardize_date(row_dict['publish_date'])
    if 'date' in row_dict:
        row_dict['date'] = standardize_date(row_dict['date'])
    
    return row_dict

def get_data_from_both_dbs(query_func, source=None):
    """从两个数据库获取数据并合并结果"""
    results = []
    
    # 从QQ群数据库获取数据
    if source is None or source == 'QQ群':
        try:
            conn = get_db_connection(QQ_DB_PATH)
            qq_results = query_func(conn, 'QQ群')
            results.extend([process_row(row, 'QQ群') for row in qq_results])
            conn.close()
        except Exception as e:
            print(f"从QQ群数据库获取数据时出错: {e}")
    
    # 从官网数据库获取数据
    if source is None or source == '官网':
        try:
            conn = get_db_connection(WEB_DB_PATH)
            web_results = query_func(conn, '官网')
            results.extend([process_row(row, '官网') for row in web_results])
            conn.close()
        except Exception as e:
            print(f"从官网数据库获取数据时出错: {e}")
    
    return results

@app.route('/api/competitions', methods=['GET'])
def get_competitions():
    """获取竞赛信息"""
    try:
        source = request.args.get('source', None)
        
        def query_competitions(conn, source_type):
            cursor = conn.cursor()
            query = 'SELECT *, ? as source FROM competitions ORDER BY publish_date DESC'
            cursor.execute(query, (source_type,))
            return [dict(row) for row in cursor.fetchall()]
        
        competitions = get_data_from_both_dbs(query_competitions, source)
        return jsonify({"data": competitions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notices', methods=['GET'])
def get_notices():
    """获取教务通知"""
    try:
        source = request.args.get('source', None)
        
        def query_notices(conn, source_type):
            cursor = conn.cursor()
            notices_query = 'SELECT * FROM notices ORDER BY publish_date DESC'
            exams_query = 'SELECT * FROM exams ORDER BY publish_date DESC'
            
            cursor.execute(notices_query)
            notices = cursor.fetchall()
            
            cursor.execute(exams_query)
            exams = cursor.fetchall()
            
            return notices + exams
        
        notices = get_data_from_both_dbs(query_notices, source)
        return jsonify({"data": notices})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/exams', methods=['GET'])
def get_exams():
    """获取考试信息"""
    try:
        source = request.args.get('source', None)
        
        def query_exams(conn, source_type):
            cursor = conn.cursor()
            query = 'SELECT *, ? as source FROM exams WHERE category = "通知" ORDER BY publish_date DESC'
            cursor.execute(query, (source_type,))
            return [dict(row) for row in cursor.fetchall()]
        
        exams = get_data_from_both_dbs(query_exams, source)
        return jsonify({"data": exams})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/internships', methods=['GET'])
def get_internships():
    """获取实习信息"""
    try:
        source = request.args.get('source', None)
        
        def query_internships(conn, source_type):
            cursor = conn.cursor()
            query = 'SELECT *, ? as source FROM college_internships WHERE category = "实习" ORDER BY publish_date DESC'
            cursor.execute(query, (source_type,))
            return [dict(row) for row in cursor.fetchall()]
        
        internships = get_data_from_both_dbs(query_internships, source)
        return jsonify({"data": internships})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search():
    """搜索所有内容"""
    try:
        keyword = request.args.get('keyword', '')
        source = request.args.get('source', None)
        category = request.args.get('category', None)
        
        if not keyword:
            return jsonify({"error": "请提供搜索关键词"}), 400

        def search_in_db(conn, source_type):
            cursor = conn.cursor()
            results = []
            tables = ['competitions', 'notices', 'exams', 'college_internships']
            
            for table in tables:
                query = f'''
                    SELECT *, ? as source, '{table}' as table_name 
                    FROM {table} 
                    WHERE (title LIKE ? OR content LIKE ? OR keywords LIKE ?)
                '''
                params = [source_type, f'%{keyword}%', f'%{keyword}%', f'%{keyword}%']
                
                if category:
                    query += ' AND category = ?'
                    params.append(category)
                    
                cursor.execute(query, params)
                results.extend([dict(row) for row in cursor.fetchall()])
            
            return results
        
        results = get_data_from_both_dbs(search_in_db, source)
        return jsonify({"data": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/item/<table>/<int:id>', methods=['GET'])
def get_item(table, id):
    """获取单个项目详情"""
    try:
        if table not in ['competitions', 'notices', 'exams', 'college_internships']:
            return jsonify({"error": "无效的表名"}), 400

        conn = get_db_connection(QQ_DB_PATH)
        cursor = conn.cursor()
        
        # 更新浏览量
        cursor.execute(f'UPDATE {table} SET views = views + 1 WHERE id = ?', (id,))
        conn.commit()
        
        # 获取更新后的数据
        cursor.execute(f'SELECT * FROM {table} WHERE id = ?', (id,))
        item = cursor.fetchone()
        
        conn.close()
        
        if item is None:
            return jsonify({"error": "项目不存在"}), 404
            
        return jsonify({"data": dict(item)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/favorite/<table>/<int:id>', methods=['POST'])
def toggle_favorite(table, id):
    """切换收藏状态"""
    try:
        if table not in ['competitions', 'notices', 'exams', 'college_internships']:
            return jsonify({"error": "无效的表名"}), 400

        conn = get_db_connection(QQ_DB_PATH)
        cursor = conn.cursor()
        
        # 更新收藏数
        cursor.execute(f'UPDATE {table} SET favorites = favorites + 1 WHERE id = ?', (id,))
        conn.commit()
        
        # 获取更新后的数据
        cursor.execute(f'SELECT favorites FROM {table} WHERE id = ?', (id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result is None:
            return jsonify({"error": "项目不存在"}), 404
            
        return jsonify({"favorites": result['favorites']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取分类统计"""
    try:
        def query_categories(conn, source_type):
            cursor = conn.cursor()
            # 获取所有表的分类统计
            tables = ['competitions', 'notices', 'exams', 'college_internships']
            stats = {}
            
            for table in tables:
                query = f'''
                    SELECT category, COUNT(*) as count 
                    FROM {table} 
                    WHERE category IS NOT NULL
                    GROUP BY category
                '''
                cursor.execute(query)
                for row in cursor.fetchall():
                    category = row['category']
                    if category not in stats:
                        stats[category] = {'官网': 0, 'QQ群': 0}
                    stats[category][source_type] = row['count']
            
            return stats
        
        # 获取两个数据库的分类统计
        qq_stats = get_data_from_both_dbs(query_categories, 'QQ群')
        web_stats = get_data_from_both_dbs(query_categories, '官网')
        
        # 合并统计结果
        merged_stats = {}
        for category in set(list(qq_stats.keys()) + list(web_stats.keys())):
            merged_stats[category] = {
                '官网': web_stats.get(category, {}).get('官网', 0),
                'QQ群': qq_stats.get(category, {}).get('QQ群', 0)
            }
        
        # 获取所有分类
        categories = list(merged_stats.keys())
        
        return jsonify({
            "categories": categories,
            "stats": merged_stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_db():
    """测试数据库连接和内容"""
    try:
        result = {
            "success": True,
            "databases": {
                "qq_groups": {"path": QQ_DB_PATH, "tables": {}},
                "website": {"path": WEB_DB_PATH, "tables": {}}
            }
        }
        
        # 测试QQ群数据库
        try:
            conn = get_db_connection(QQ_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table['name']
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                result["databases"]["qq_groups"]["tables"][table_name] = [dict(row) for row in rows]
            conn.close()
        except Exception as e:
            result["databases"]["qq_groups"]["error"] = str(e)
        
        # 测试官网数据库
        try:
            conn = get_db_connection(WEB_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                table_name = table['name']
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                result["databases"]["website"]["tables"][table_name] = [dict(row) for row in rows]
            conn.close()
        except Exception as e:
            result["databases"]["website"]["error"] = str(e)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    try:
        # 启动前检查数据库连接
        print("正在检查数据库连接...")
        for db_path in [QQ_DB_PATH, WEB_DB_PATH]:
            if os.path.exists(db_path):
                print(f"检查数据库: {db_path}")
                conn = get_db_connection(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"数据库中的表: {[table[0] for table in tables]}")
                conn.close()
        print("数据库连接测试成功")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"启动服务器时出错: {str(e)}")
        print(f"堆栈跟踪: {traceback.format_exc()}") 