from bokeh.plotting import figure, curdoc
from bokeh.layouts import gridplot, column
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral6
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# 典型用途：多图联动数据探索 (Linked Brushing)
# 核心特色：
# 1. 客户端高性能交互 (Canvas 渲染)
# 2. 共享数据源 (ColumnDataSource) 实现多图选择联动
# 3. 适合探索高维数据的相关性
# -----------------------------------------------------------------------------

# 1. 准备数据
# 模拟一个多维数据集 (例如：汽车性能数据)
N = 300
data = {
    'mpg': np.random.normal(20, 5, N),
    'hp': np.random.normal(150, 50, N),
    'weight': np.random.normal(3000, 500, N),
    'accel': np.random.normal(15, 3, N),
    'cylinders': np.random.choice(['4', '6', '8'], N)
}
source = ColumnDataSource(data=data)

# 2. 创建工具
TOOLS = "box_select,lasso_select,reset,help,wheel_zoom,pan"

# 3. 创建三个联动图表
# 图1: 马力 vs 油耗
p1 = figure(tools=TOOLS, width=400, height=350, title="马力 (HP) vs 油耗 (MPG)")
p1.scatter('hp', 'mpg', source=source, size=8, alpha=0.6,
           color=factor_cmap('cylinders', palette=Spectral6, factors=['4', '6', '8']),
           legend_group='cylinders')
p1.xaxis.axis_label = "Horsepower"
p1.yaxis.axis_label = "MPG"

# 图2: 重量 vs 加速
p2 = figure(tools=TOOLS, width=400, height=350, title="重量 (Weight) vs 加速 (Accel)")
p2.scatter('weight', 'accel', source=source, size=8, alpha=0.6,
           color=factor_cmap('cylinders', palette=Spectral6, factors=['4', '6', '8']))
p2.xaxis.axis_label = "Weight"
p2.yaxis.axis_label = "Acceleration"

# 图3: 马力 vs 重量
p3 = figure(tools=TOOLS, width=400, height=350, title="马力 (HP) vs 重量 (Weight)")
p3.scatter('hp', 'weight', source=source, size=8, alpha=0.6,
           color=factor_cmap('cylinders', palette=Spectral6, factors=['4', '6', '8']))
p3.xaxis.axis_label = "Horsepower"
p3.yaxis.axis_label = "Weight"

# 4. 添加 Hover 工具 (所有图表共享)
hover = HoverTool(tooltips=[
    ("Cylinders", "@cylinders"),
    ("MPG", "@mpg{0.0}"),
    ("HP", "@hp{0}"),
    ("Weight", "@weight{0}")
])
p1.add_tools(hover)
p2.add_tools(hover)
p3.add_tools(hover)

# 5. 布局与说明
desc = Div(text="""
<h1>🔍 Bokeh 多图联动探索</h1>
<p><b>操作指南：</b></p>
<ul>
    <li>使用 <b>Box Select (矩形选择)</b> 或 <b>Lasso Select (套索选择)</b> 工具在任意图表中选中点。</li>
    <li>观察其他图表中对应的点也会被<b>高亮显示</b>。</li>
    <li>这种 <i>Linked Brushing</i> 技术是发现多维数据相关性的利器。</li>
</ul>
<hr>
""", width=800)

layout = column(desc, gridplot([[p1, p2], [p3, None]]))

curdoc().add_root(layout)
curdoc().title = "Bokeh Linked Brushing"
