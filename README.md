# Flask_testing_Project-for-the-machine
A small-scale project involving a detection machine designed to establish a connection between the machine and a computer, both operating on the same network, to enable the sharing of detection data and its subsequent storage in a centralized database.

## Here are some details about the Project in Chinese.

### 1.务必保证你的检测仪和你的电脑等接收设备在一个局域网内

### 2.如何使用数据库

```python
# 数据库配置信息
db_config = {
    'host': '', #你的数据库在哪里 本地？（localhost) 服务器？（具体ip）
    'user': '',  # 替换为你的数据库用户名
    'password': '',  # 替换为你的数据库密码
    'db': '',  # 替换为你的数据库名
    'charset': 'utf8mb4',  #编码格式
    'cursorclass': pymysql.cursors.DictCursor
}
```

请务必注意，你给的用户名是否有足够的权力！！！如果在服务器，请确定网络正常！

### 3.如果有问题，或者不知道啥错误，看看目录里有没有日志文件呗……

```txt
日志文件名（按启动时间命名，格式：年-月-日_时-分-秒.log）
```

```txt
日志格式（包含：时间、日志级别、信息、请求IP、HTTP状态码）
```

### 4.小不足，你可以尝试结合数据库读入和sm4等算法完善

```python
def validate_credentials(model_json):
    username = model_json.get('username')  # 从JSON中取用户名
    password = model_json.get('password')  # 从JSON中取密码
    # 固定验证逻辑（仅允许定下的用户名和密码登录登录）
    return username == '' and password == ''  #在这里定下密码啥的呗
```

#### *这里限制了用户名和密码哦·~*

### 5.不确定是不是网络连接导致的传输失败？

#### 局域网下直接访问电脑等接收端的设备（浏览器输入你的==接收端ip:8090==，如果在一个局域网，会有个index加上一段话等你！

```txt
Welcome to the main page and you have accessed!
```

### 6.怎么发？

**接收端写你的接收端ip:8090/data哦~**

### 7.路由里/txt干啥用的？

**自己本地测试用的，你发个txt文件过来也行，但是格式必须正确才行，和json文件一样的格式**

### 8.格式示例？

```json
{'modelJson': '{"dwmc":"泰山学院","username":"admin","details":[{"jiancexiangmu":"有机磷和氨基甲酸酯类农药残留","jiancezhi":"27.232%","jiancedidian":"泰山学院","shanghumingcheng":"泰山学院","yangpinbianhao":"172120869945001","lianxidianhua":"123456","jianceren":"泰山学院","jianceriqi":"2024-07-17 17:56:24","yangpinmingcheng":"梨没洗","jiancejieguo":"合格"}],"password":"Hengmei123","yqbh":"972c2d18094700000000"}'}
```

