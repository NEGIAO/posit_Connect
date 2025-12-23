from shiny import App, render, ui, reactive
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# -----------------------------------------------------------------------------
# 典型用途：科学计算与模拟 (Scientific Simulation)
# 核心特色：Shiny 的响应式图 (Reactivity Graph)
# 这里的计算逻辑是联动的：改变参数 -> 重新采样 -> 重新计算统计量 -> 更新图表
# 这种"牵一发而动全身"的逻辑在 Shiny 中实现最为优雅。
# -----------------------------------------------------------------------------

app_ui = ui.page_fluid(
    ui.panel_title("🎲 中心极限定理 (CLT) 交互模拟器"),
    
    ui.layout_sidebar(
        ui.sidebar(
            ui.h4("参数设置"),
            ui.input_select(
                "dist_type", "原始分布类型",
                {"uniform": "均匀分布 (Uniform)", "exp": "指数分布 (Exponential)", "beta": "Beta 分布"}
            ),
            ui.input_slider("sample_size", "每次采样的样本量 (n)", 1, 100, 30),
            ui.input_slider("n_sims", "模拟次数 (Simulations)", 100, 5000, 1000),
            ui.hr(),
            ui.markdown("""
            **原理说明**：
            无论原始分布是什么形状，只要样本量 $n$ 足够大，
            样本均值的分布都会趋近于正态分布。
            """),
            bg="#f8f9fa"
        ),
        
        ui.layout_columns(
            ui.card(
                ui.card_header("1. 原始总体分布"),
                ui.output_plot("dist_plot")
            ),
            ui.card(
                ui.card_header("2. 样本均值的分布"),
                ui.output_plot("means_plot")
            )
        ),
        
        ui.card(
            ui.card_header("统计检验 (Shapiro-Wilk Normality Test)"),
            ui.output_text_verbatim("stats_summary")
        )
    )
)

def server(input, output, session):
    
    # 响应式计算：生成原始数据
    # 只有当分布类型改变时才重新计算
    @reactive.Calc
    def population_data():
        n = 10000
        dist = input.dist_type()
        if dist == "uniform":
            return np.random.uniform(0, 1, n)
        elif dist == "exp":
            return np.random.exponential(1, n)
        else:
            return np.random.beta(0.5, 0.5, n)

    # 响应式计算：执行模拟
    # 当样本量、模拟次数或原始分布改变时触发
    @reactive.Calc
    def simulation_means():
        pop = population_data()
        n = input.sample_size()
        sims = input.n_sims()
        
        means = []
        for _ in range(sims):
            sample = np.random.choice(pop, n)
            means.append(np.mean(sample))
        return np.array(means)

    @output
    @render.plot
    def dist_plot():
        fig, ax = plt.subplots()
        ax.hist(population_data(), bins=30, density=True, color='#FF6B6B', alpha=0.7)
        ax.set_title("原始总体分布 (非正态)", fontsize=10)
        return fig

    @output
    @render.plot
    def means_plot():
        means = simulation_means()
        fig, ax = plt.subplots()
        
        # 绘制直方图
        ax.hist(means, bins=30, density=True, color='#00D9FF', alpha=0.7, label="样本均值")
        
        # 绘制拟合的正态曲线
        mu, std = stats.norm.fit(means)
        x = np.linspace(min(means), max(means), 100)
        p = stats.norm.pdf(x, mu, std)
        ax.plot(x, p, 'k', linewidth=2, label="正态拟合")
        
        ax.set_title(f"样本均值分布 (n={input.sample_size()})", fontsize=10)
        ax.legend()
        return fig

    @output
    @render.text
    def stats_summary():
        means = simulation_means()
        shapiro_stat, p_value = stats.shapiro(means[:5000]) # Shapiro limit 5000
        
        res = f"模拟统计量:\n"
        res += f"均值: {np.mean(means):.4f}\n"
        res += f"标准差: {np.std(means):.4f}\n\n"
        res += f"正态性检验 (Shapiro-Wilk):\n"
        res += f"W-statistic: {shapiro_stat:.4f}\n"
        res += f"P-value: {p_value:.4e}\n"
        
        if p_value > 0.05:
            res += ">> 结论: 样本均值服从正态分布 (P > 0.05)"
        else:
            res += ">> 结论: 尚未完全服从正态分布 (P < 0.05)"
            
        return res

app = App(app_ui, server)
