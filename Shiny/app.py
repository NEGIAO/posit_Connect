from shiny import App, render, ui
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 生成示例数据
np.random.seed(42)
df = pd.DataFrame({
    'x': range(1, 101),
    'y': np.cumsum(np.random.randn(100))
})

# UI 定义
app_ui = ui.page_fluid(
    ui.h2("✨ Shiny for Python 交互式应用"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_slider("n_points", "数据点数量", 10, 100, 50),
            ui.input_select(
                "plot_type",
                "图表类型",
                choices=["折线图", "散点图", "柱状图"]
            )
        ),
        ui.output_plot("main_plot"),
        ui.output_table("data_table")
    )
)

# Server 定义
def server(input, output, session):
    
    @output
    @render.plot
    def main_plot():
        n = input.n_points()
        plot_df = df.head(n)
        
        fig = go.Figure()
        
        if input.plot_type() == "折线图":
            fig.add_trace(go.Scatter(x=plot_df['x'], y=plot_df['y'], mode='lines'))
        elif input.plot_type() == "散点图":
            fig.add_trace(go.Scatter(x=plot_df['x'], y=plot_df['y'], mode='markers'))
        else:
            fig.add_trace(go.Bar(x=plot_df['x'], y=plot_df['y']))
        
        fig.update_layout(
            title="数据可视化",
            xaxis_title="X 轴",
            yaxis_title="Y 轴"
        )
        
        return fig
    
    @output
    @render.table
    def data_table():
        n = input.n_points()
        return df.head(n).describe()

# 创建应用
app = App(app_ui, server)
