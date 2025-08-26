import json
import os
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import pymysql.cursors
from flask import Flask, request
import chardet

app = Flask(__name__)

# 数据库配置信息
db_config = {
    'host': 'localhost',
    'user': '',  # 替换为你的数据库用户名
    'password': '',  # 替换为你的数据库密码
    'db': '',  # 替换为你的数据库名
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 设置日志
log_dir = 'logs'
if not os.path.exists(log_dir):
    try:
        os.makedirs(log_dir)  # 确保创建了日志目录
    except OSError as e:
        app.logger.error(f"Failed to create log directory: {e}")
        raise

log_filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.log'
log_file_path = os.path.join(log_dir, log_filename)

# 日志格式设置
log_format = '%(asctime)s - %(levelname)s - %(message)s - IP Address: %(ip)s - HTTP Status Code: %(statusCode)s'
logger = logging.getLogger(__name__)

# 创建一个旋转文件处理器
handler = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=5)
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 连接数据库的函数
def get_db_connection():
    try:
        return pymysql.connect(**db_config)
    except pymysql.MySQLError as e:
        ip = request.remote_addr
        logger.error(f"Database connection failed: {e} ", extra={'ip': ip, 'statusCode': 500})
        print(f"Database connection failed: {e}")
        return None

# 插入数据到数据库的函数
def insert_data_to_db(detail, dwmc, yqbh, upload_time):
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                # 去除百分号并转换为浮点数
                normalized_value = float(detail.get('jiancezhi', '').replace('%', '').strip('%')) / 100
                sql = """
                    INSERT INTO nwla_agri_safecheck (
                        check_items, check_value, check_addr, cust_name, sample_no, telphone,
                        check_oper, check_data, sample_name, check_result, check_unit, check_dev_no, check_time
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """
                cursor.execute(sql, (
                    detail['jiancexiangmu'], normalized_value,
                    detail['jiancedidian'], detail['shanghumingcheng'],
                    detail['yangpinbianhao'], detail['lianxidianhua'],
                    detail['jianceren'], detail['jianceriqi'],
                    detail['yangpinmingcheng'], detail['jiancejieguo'],
                    dwmc, yqbh, upload_time
                ))
            connection.commit()
        except Exception as e:
            ip = request.remote_addr
            logger.error(f"Error inserting data into database: {e} ", extra={'ip':ip,'statusCode': 500})
            print(f"Error inserting data into database: {e}")
        finally:
            connection.close()

# 验证用户名和密码的函数
def validate_credentials(model_json):
    username = model_json.get('username')
    password = model_json.get('password')
    return username == 'admin' and password == 'Hengmei123'

# 处理 POST 请求的函数
def handle_post_request(datajson,ip):
    model_json = json.loads(datajson)
    if not validate_credentials(model_json):
        logger.info("账号或密码错误 - ", extra={'ip':ip,'statusCode': 401})
        return "-2"  # 账号或密码错误

    details = model_json.get('details')
    if not details:
        logger.info("检测数据为空 - ", extra={'ip':ip,'statusCode': 400})
        return "-3"  # 检测数据为空

    try:
        upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dwmc = model_json.get('dwmc')
        yqbh = model_json.get('yqbh')

        for detail in details:
            insert_data_to_db(detail, dwmc, yqbh, upload_time)
        logger.info("检测数据上传成功 - ", extra={'ip':ip,'statusCode': 200})
        return "success"  # 检测数据上传成功

    except Exception as e:
        ip = request.remote_addr
        logger.error(f"Error processing request: {e} - ",extra={'ip': ip, 'statusCode': 500})
        print(f"Error processing request: {e}")
        return "fail"  # 远程服务器故障

@app.route('/data', methods=['POST'])
def receive_json():
    content_type = request.headers.get('Content-Type')
    model_json_str = None
    logger.info(f"JSON data received from {request.remote_addr}")

    if content_type == 'application/json':
        model_json_str = request.data.decode('utf-8')
    elif content_type == 'application/x-www-form-urlencoded':
        model_json_str = request.form.get('modelJson')

    if not model_json_str:
        ip = request.remote_addr
        logger.info("No modelJson provided - ", extra={'ip': ip, 'statusCode': 200})
        return "No modelJson provided", 400
    ip = request.remote_addr
    response = handle_post_request(model_json_str,ip)
    status_code = 200 if response == "success" else 500
    return response, status_code

@app.route('/')
def hello_world():
    ip = request.remote_addr
    logger.info("Main page accessed - ", extra={'ip': ip, 'statusCode': 200})
    return 'Welcome to the main page and you have accessed!'
#用于有浏览器设备进行连接检测

@app.route('/txt', methods=['POST'])
def validate_and_save_txt_file():
    ip = request.remote_addr

    # 检查请求中是否有文件
    if 'file' not in request.files:
        logger.info("No file part", extra={'ip': ip, 'statusCode': 400})
        return "No file part", 400

    file = request.files['file']
    if file.filename == '':
        logger.info("No selected file", extra={'ip': ip, 'statusCode': 400})
        return "No selected file", 400

    # 读取文件内容为二进制，并使用 GB2312 解码
    try:
        file.seek(0)  # 重置文件指针到文件开始位置
        binary_content = file.read()  # 读取文件内容为二进制
        file_content = binary_content.decode('gb2312')  # 使用 GB2312 解码
        logger.info(f"File encoding detected: GB2312", extra={'ip': ip, 'statusCode': 200})
    except UnicodeDecodeError as e:
        logger.error(f"Error decoding file content with GB2312 encoding: {e}", extra={'ip': ip, 'statusCode': 500})
        return str(e), 500
        # 尝试解析 JSON 数据
    try:
        model_json = json.loads(file_content)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e.msg} at position {e.pos}", extra={'ip': ip, 'statusCode': 400})
        error_fragment = file_content[max(0, e.pos - 20):e.pos + 20]  # 打印错误位置附近的字符
        logger.error(f"JSON decode error near: {error_fragment}", extra={'ip': ip, 'statusCode': 400})
        return "Invalid JSON format", 400

    # 验证 username 和 password
    if not validate_credentials(model_json):
        logger.info("账号或密码错误", extra={'ip': ip, 'statusCode': 401})
        return "-2", 401  # 账号或密码错误

    # 验证 details 是否为空，并且验证 key 是否缺失
    details = model_json.get('details', [])
    if not details:
        logger.info("检测数据为空", extra={'ip': ip, 'statusCode': 400})
        return "-3", 400  # 检测数据为空

    for detail in details:
        if not isinstance(detail, dict):
            logger.error("Invalid structure in details list", extra={'ip': ip, 'statusCode': 400})
            return "Invalid structure in details list", 400
        # 确保 details 中的字典不缺少关键键
        required_keys = ['jiancedidian', 'jiancejieguo', 'jianceren', 'jianceriqi',
                         'jiancexiangmu', 'jiancezhi', 'lianxidianhua',
                         'shanghumingcheng', 'yangpinbianhao', 'yangpinmingcheng']
        for key in required_keys:
            if key not in detail or not detail[key]:  # 允许值为空字符串
                logger.error(f"Missing or empty key '{key}' in details", extra={'ip': ip, 'statusCode': 400})
                return f"Missing or empty key '{key}' in details", 400
            # if key not in detail or detail[key] is None or detail[key] == "":
            #     detail[key] = "NULL"

    # 验证 dwmc 是否为空
    dwmc = model_json.get('dwmc', "")
    if not dwmc:
        logger.info("dwmc 不能为空", extra={'ip': ip, 'statusCode': 400})
        return "dwmc 不能为空", 400

    # 验证 yqbh 是否为空
    yqbh = model_json.get('yqbh')
    if not yqbh:
        logger.info("yqbh 不能为空", extra={'ip': ip, 'statusCode': 400})
        return "yqbh 不能为空", 400

    try:
        upload_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for detail in details:
            insert_data_to_db(detail, dwmc, yqbh, upload_time)
        logger.info("检测数据上传成功 - ", extra={'ip': ip, 'statusCode': 200})
        return "success", 200
    except Exception as e:
        logger.error(f"Error inserting data into database: {e} ", extra={'ip': ip, 'statusCode': 500})
        print(f"Error inserting data into database: {e}")

    # 保存文件
    try:
        new_filename, save_path = save_file(file, model_json, ip)
        logger.info("File saved successfully", extra={'ip': ip, 'statusCode': 200})
        return "success", 200
    except Exception as e:
        logger.error(f"Error saving file: {e}", extra={'ip': ip, 'statusCode': 500})
        return str(e), 500

# 处理 details 列表并保持键顺序的函数
def process_details(details):
    keys_order = [
        "jiancedidian", "jiancejieguo", "jianceren", "jianceriqi", "jiancexiangmu",
        "jiancezhi", "lianxidianhua", "shanghumingcheng", "yangpinbianhao",
        "yangpinmingcheng"
    ]
    processed_details = []
    for detail in details:
        new_detail = {key: detail.get(key, None) for key in keys_order if key in detail}
        processed_details.append(new_detail)
    return processed_details

# 保存文件的函数
def save_file(file, model_json, ip):
    filename = file.filename
    receive_time = datetime.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{os.path.splitext(filename)[0]}_{receive_time}.txt"
    save_path = os.path.join(app.root_path, 'uploads', new_filename)  # 假设有一个uploads目录用于保存文件
    os.makedirs(os.path.dirname(save_path), exist_ok=True)  # 确保目录存在
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(model_json, ensure_ascii=False, indent=4))
        logger.info(f"File '{new_filename}' saved successfully at {save_path}", extra={'ip': ip})
        return new_filename, save_path
    except Exception as e:
        logger.error(f"Error saving file: {e}", extra={'ip': ip, 'statusCode': 500})
        raise

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=False)
#为保证安全，与7.23将debug模式关闭！
#相对最终版本，移除txt，只回复状态值，并没有具体内容，对方有相应


#2024.8.3 加回了日志，但只测试了200情况，其他不确定

#这里具体代码信息请自行调整哦~~~只是个例子




