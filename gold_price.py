import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/gold')
def get_gold_prices():
    # 同时获取黄金T+D和伦敦金
    url = "https://hq.sinajs.cn/list=gds_AUTD,hf_XAU"
    headers = {"Referer": "https://finance.sina.com.cn/"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        # 这种接口通常是 GBK 编码
        content = response.content.decode('gbk')
        lines = content.strip().split('\n')
        
        # 解析 AUTD (国内金价)
        # 格式：...="最新价,0,买入,卖出,最高,最低,时间..."
        autd_data = lines[0].split('"')[1].split(',')
        price_cn = autd_data[0] # 第一位是最新价
        
        # 解析 hf_XAU (国际金价)
        # 格式：...="最新价,涨跌,开盘,昨收,最高,最低,时间,昨收,今开..."
        xau_data = lines[1].split('"')[1].split(',')
        price_intl = xau_data[0] # 第一位是最新价
        
        return jsonify({
            "shanghai": price_cn,    # 单位：元/克
            "london": price_intl,    # 单位：美元/盎司
            "time": autd_data[6]     # 成交时间
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    print("服务已启动：http://127.0.0.1:5000/api/gold")
    app.run(debug=True, port=5000)