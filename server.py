from flask import Flask, request, jsonify
import requests
import re
import pandas as pd

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# 接口1：获取当日实时估值
@app.route('/get_fund_realtime')
def get_realtime():
    code = request.args.get('code')
    url = f"http://fundgz.1234567.com.cn/js/{code}.js"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    # 这一步是为了把 jsonpgz({...}) 变成 {...}
    # 如果接口返回内容为空（比如代码填错了），这里可能会报错
    try:
        json_str = re.findall(r'\((.*)\)', res.text)[0]
        return json_str
    except:
        return jsonify({"name": "未知基金", "fundcode": code, "gsz": "0", "gszzl": "0", "dwjz": "0", "gztime": "无数据"})

# 接口2：获取30天历史净值
@app.route('/get_fund_history')
def get_history():
    code = request.args.get('code')
    # 天天基金历史净值接口
    url = f"http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={code}&per=30&page=1"
    res = requests.get(url)
    # 使用 pandas 抓取网页中的表格
    tables = pd.read_html(res.text)
    df = tables[0] # 获取第一个表格
    # 提取日期和单位净值，并转为倒序（从旧到新）
    data = {
        "dates": df['净值日期'].tolist()[::-1],
        "values": df['单位净值'].tolist()[::-1]
    }
    return jsonify(data)

if __name__ == '__main__':
    app.run(port=5000)