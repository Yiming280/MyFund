FundTracker：指数基金实时看板 📈
这是一个基于 Python + Vue3 + ECharts 开发的轻量级基金看板工具。它支持基金代码查询、实时估值监控、30日历史净值趋势查看，并能将你的自选基金保存在本地浏览器中，实现自动刷新实时数值。

# 🚀 快速开始
本项目推荐使用 uv（高性能 Python 包管理器）运行。
## 1. 准备环境
确保你已安装 uv[https://docs.astral.sh/uv/getting-started/installation/]。

创建虚拟环境并安装依赖

在项目根目录下执行：
```
uv venv
uv pip install flask requests pandas lxml
```

## 2. 启动后端助手
激活环境并运行服务器
```
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

python server.py
```
保持此窗口开启，它负责抓取基金实时数据并解决跨域问题。

## 3. 打开网页
在浏览器中直接双击打开 index2.html 即可开始使用。

# 🛠️ 模块开发说明
## 1. 后端代理模块 (server.py)
由于浏览器出于安全考虑（CORS 跨域限制）禁止直接请求天天基金的接口，我们使用 Python Flask 搭建了一个透明代理。

实时接口：对接天天基金 JS 接口，通过正则表达式截取 JSON 字符串。

历史接口：利用 pandas.read_html 结合 lxml 解析历史净值 HTML 表格，并将其转化为前端可直接绘图的数组格式。

## 2. 前端展示模块 (index.html)
Vue 3 (Composition API)：负责页面的数据绑定和逻辑控制，通过 fetch 异步与后端通信。

Tailwind CSS：利用原子类快速构建美观的响应式界面，无需编写复杂的 CSS 文件。

ECharts：动态渲染图表。通过 chart.setOption 实现“今日估值”与“30日历史”的平滑切换。

## 3. 数据持久化
利用浏览器的 localStorage 存储自选基金列表。这意味着即使你刷新或关闭网页，你的自选基金依然会存在。

# 📖 关键变量含义
## 前端 (JavaScript)变量名

| 变量名     | 含义           | 作用                                                   |
|------------|----------------|--------------------------------------------------------|
| `searchCode` | 搜索框内容     | 绑定用户输入的基金代码                                 |
| `fund`       | 当前基金详情   | 存储当前查询到的名称、估值、涨跌幅等对象             |
| `showType`   | 显示模式       | `realtime` 表示今日估值，`history` 表示30日历史        |
| `favorites`  | 自选列表       | 存储在 LocalStorage 中的基金数组                      |
| `isFav`      | 是否已收藏     | (Computed) 自动判断当前查询基金是否在自选名单中      |


## 后端 (Python)
| 路由地址             | 作用             | 返回格式                                    |
|----------------------|------------------|---------------------------------------------|
| `/get_fund_realtime`   | 获取实时估值     | JSON (包含 gsz, gszzl, dwjz 等)            |
| `/get_fund_history`    | 获取30日历史     | JSON (包含 dates 和 values 数组)           |