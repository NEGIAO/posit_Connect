import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# 初始化 Dash 应用
app = dash.Dash(__name__)
server = app.server  # Posit Connect 需要

# 生成示例数据
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=100)
df = pd.DataFrame({
    'date': dates,
    'value': np.cumsum(np.random.randn(100)) + 100,
    'category': np.random.choice(['A', 'B', 'C'], 100)
})

# 布局
app.layout = html.Div([
    html.H1("📊 Dash 企业级仪表板演示", style={'textAlign': 'center'}),
    
    html.Div([
        html.Label("选择类别："),
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': cat, 'value': cat} for cat in df['category'].unique()],
            value=df['category'].unique()[0],
            style={'width': '200px'}
        )
    ], style={'padding': '20px'}),
    
    dcc.Graph(id='time-series-chart'),
    
    html.Div([
        html.H3("数据统计"),
        html.Div(id='stats-output')
    ], style={'padding': '20px'})
])

# 回调函数
@app.callback(
    [Output('time-series-chart', 'figure'),
     Output('stats-output', 'children')],
    Input('category-dropdown', 'value')
)
def update_chart(selected_category):
    filtered_df = df[df['category'] == selected_category]
    
    # 创建图表
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=filtered_df['date'],
        y=filtered_df['value'],
        mode='lines+markers',
        name=selected_category
    ))
    fig.update_layout(
        title=f'类别 {selected_category} 时间序列',
        xaxis_title='日期',
        yaxis_title='数值'
    )
    
    # 统计信息
    stats = html.Ul([
        html.Li(f"均值：{filtered_df['value'].mean():.2f}"),
        html.Li(f"标准差：{filtered_df['value'].std():.2f}"),
        html.Li(f"最大值：{filtered_df['value'].max():.2f}"),
        html.Li(f"最小值：{filtered_df['value'].min():.2f}")
    ])
    
    return fig, stats

if __name__ == '__main__':
    app.run_server(debug=True)
