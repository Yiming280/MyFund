from flask import Flask, request, jsonify
import requests
import re

app = Flask(__name__)

# 解决跨域问题：允许网页访问这个 Python 程序
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/get_fund')
def get_fund():
    # 获取网页传来的基金代码
    code = request.args.get('code')
    if not code:
        return "Missing code", 400

    # 模拟浏览器去访问天天基金接口
    url = f"http://fundgz.1234567.com.cn/js/{code}.js"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        # 解析数据：天天基金返回的是 jsonpgz({...}) 格式，我们需要花括号里的内容
        content = response.text
        json_str = re.findall(r'\((.*)\)', content)[0]
        return json_str
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    print("Python 助手已启动！正在监听端口 5000...")
    app.run(port=5000)