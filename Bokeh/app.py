from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import Select, Slider
import numpy as np

# 初始化数据
x = np.linspace(0, 4*np.pi, 100)
y = np.sin(x)

# 创建图表
plot = figure(
    title="📈 Bokeh 交互式可视化",
    x_axis_label='X',
    y_axis_label='Y',
    width=800,
    height=400
)
line = plot.line(x, y, line_width=2, color='#00D9FF')

# 控件
function_select = Select(
    title="函数类型:",
    value="sin",
    options=["sin", "cos", "tan"]
)

frequency_slider = Slider(
    title="频率",
    start=0.1,
    end=5,
    value=1,
    step=0.1
)

amplitude_slider = Slider(
    title="振幅",
    start=0.1,
    end=5,
    value=1,
    step=0.1
)

# 回调函数
def update():
    func = function_select.value
    freq = frequency_slider.value
    amp = amplitude_slider.value
    
    x_new = np.linspace(0, 4*np.pi, 100)
    
    if func == "sin":
        y_new = amp * np.sin(freq * x_new)
    elif func == "cos":
        y_new = amp * np.cos(freq * x_new)
    else:
        y_new = amp * np.tan(freq * x_new)
        y_new = np.clip(y_new, -10, 10)  # 限制 tan 值范围
    
    line.data_source.data = {'x': x_new, 'y': y_new}

# 绑定事件
function_select.on_change('value', lambda attr, old, new: update())
frequency_slider.on_change('value', lambda attr, old, new: update())
amplitude_slider.on_change('value', lambda attr, old, new: update())

# 布局
layout = column(
    row(function_select, frequency_slider, amplitude_slider),
    plot
)

curdoc().add_root(layout)
curdoc().title = "Bokeh 应用"
