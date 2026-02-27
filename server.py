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

# 接口3：获取当日分时走势
@app.route('/get_fund_trend')
def get_trend():
    code = request.args.get('code')
    
    # 尝试天天基金的分时走势接口
    try:
        # 使用JSONP方式调用天天基金接口
        url = f"https://fundmobapi.1234567.com.cn/FundMApi/FundVariatChart.ashx?FCODE={code}&deviceid=123&plat=Wap&product=EFund&version=2.0"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            if data and data.get('Data') and len(data['Data']) > 0:
                # 转换数据格式
                trend_data = []
                for item in data['Data']:
                    trend_data.append({
                        'time': item.get('time', ''),
                        'data': item.get('data', 0)
                    })
                if len(trend_data) > 0:
                    return jsonify({'success': True, 'data': trend_data})
    except Exception as e:
        pass
    
    # 尝试东方财富的接口作为备用
    try:
        url = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=90.{code}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&lmt=5"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        data = res.json()
        
        if data and data.get('data') and data['data'].get('klines'):
            klines = data['data']['klines']
            if len(klines) > 0:
                # 获取最近几天的数据
                trend_data = []
                for kline in klines[-5:]:  # 最多取5天
                    parts = kline.split(',')
                    if len(parts) >= 5:
                        trend_data.append({
                            'time': parts[0],
                            'data': parts[2]  # 收盘价
                        })
                if len(trend_data) > 0:
                    return jsonify({'success': True, 'data': trend_data})
    except Exception as e:
        pass
    
    return jsonify({'success': False, 'message': '获取分时数据失败'})

if __name__ == '__main__':
    app.run(port=5000)