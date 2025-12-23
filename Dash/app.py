import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 典型用途：企业级实时监控看板 (Enterprise Dashboard)
# 核心特色：
# 1. 高度定制化布局 (基于 React/Bootstrap)
# 2. 适合复杂交互 (Cross-filtering)
# 3. 生产级外观 (深色模式)
# -----------------------------------------------------------------------------

# 使用 Bootstrap 的 CYBORG 主题 (深色科技感)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

# 模拟实时数据生成
def generate_data():
    now = datetime.now()
    times = [now - timedelta(minutes=i) for i in range(60)][::-1]
    prices = 100 + np.cumsum(np.random.randn(60))
    volumes = np.random.randint(100, 1000, 60)
    return pd.DataFrame({'time': times, 'price': prices, 'volume': volumes})

df_initial = generate_data()

# 布局定义
app.layout = dbc.Container([
    # 顶部导航栏
    dbc.NavbarSimple(
        brand="📈 FinTech 实时交易监控中心",
        brand_href="#",
        color="primary",
        dark=True,
        className="mb-4"
    ),

    # 关键指标卡片 (KPI Cards)
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("当前价格"),
            dbc.CardBody(html.H2(id="kpi-price", className="text-info"))
        ], color="dark", inverse=True), width=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("24h 涨跌幅"),
            dbc.CardBody(html.H2(id="kpi-change", className="text-success"))
        ], color="dark", inverse=True), width=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("实时成交量"),
            dbc.CardBody(html.H2(id="kpi-volume", className="text-warning"))
        ], color="dark", inverse=True), width=3),
        
        dbc.Col(dbc.Card([
            dbc.CardHeader("系统状态"),
            dbc.CardBody(html.H4("🟢 在线监控中", className="text-light"))
        ], color="success", inverse=True), width=3),
    ], className="mb-4"),

    # 主图表区域
    dbc.Row([
        # 左侧：K线图/趋势图
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("价格趋势 (实时刷新)"),
                dbc.CardBody(dcc.Graph(id="price-chart", style={"height": "400px"}))
            ], color="secondary", inverse=True)
        ], width=8),

        # 右侧：控制面板与分布图
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("交易分布"),
                dbc.CardBody(dcc.Graph(id="volume-chart", style={"height": "200px"}))
            ], color="secondary", inverse=True, className="mb-3"),
            
            dbc.Card([
                dbc.CardHeader("控制台"),
                dbc.CardBody([
                    html.Label("刷新频率 (ms):"),
                    dcc.Slider(500, 5000, step=500, value=1000, id='interval-slider'),
                    html.Hr(),
                    dbc.Button("导出报告", color="info", className="w-100")
                ])
            ], color="secondary", inverse=True)
        ], width=4)
    ]),

    # 定时器组件，用于模拟实时数据推送
    dcc.Interval(id='interval-component', interval=1000, n_intervals=0)

], fluid=True)

# 回调逻辑
@callback(
    [Output('price-chart', 'figure'),
     Output('volume-chart', 'figure'),
     Output('kpi-price', 'children'),
     Output('kpi-change', 'children'),
     Output('kpi-volume', 'children'),
     Output('interval-component', 'interval')],
    [Input('interval-component', 'n_intervals'),
     Input('interval-slider', 'value')]
)
def update_metrics(n, interval_val):
    # 模拟新数据
    df = generate_data()
    current_price = df['price'].iloc[-1]
    start_price = df['price'].iloc[0]
    change = (current_price - start_price) / start_price
    current_vol = df['volume'].iloc[-1]

    # 价格图表 (Plotly Dark Template)
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(
        x=df['time'], y=df['price'],
        mode='lines', fill='tozeroy',
        line=dict(color='#00D9FF', width=2),
        name='Price'
    ))
    fig_price.update_layout(
        template='plotly_dark',
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#444')
    )

    # 成交量图表
    fig_vol = go.Figure(go.Bar(
        x=df['time'], y=df['volume'],
        marker_color='#FF6B6B'
    ))
    fig_vol.update_layout(
        template='plotly_dark',
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showticklabels=False),
        yaxis=dict(showgrid=False)
    )

    # 格式化 KPI
    kpi_p = f"${current_price:.2f}"
    kpi_c = f"{change:+.2%}"
    kpi_v = f"{current_vol:,}"

    return fig_price, fig_vol, kpi_p, kpi_c, kpi_v, interval_val

if __name__ == '__main__':
    app.run_server(debug=True)
