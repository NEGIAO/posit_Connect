# Posit Connect Cloud 多框架演示项目

> 🚀 在 Posit Connect Cloud 上部署和托管各类数据科学应用的综合示例集合  
> 🌐 **在线访问**：[Posit Connect Cloud](https://connect.posit.cloud/)

## 项目概述

本项目是一个**全栈数据科学应用**的演示平台，精心挑选了 8 大主流框架的**典型应用场景**。每个示例都旨在展示该框架最核心的优势和特色，帮助开发者快速理解"什么场景用什么工具"。

相比 GitHub Pages 等静态托管服务，Posit Connect 提供了：
- ✅ **服务器端计算**：支持 Python/R 后端逻辑执行
- ✅ **动态交互**：实时数据处理与用户交互
- ✅ **多框架支持**：涵盖 8 大主流数据科学应用框架
- ✅ **自动部署**：Git 推送即可触发云端更新

## 目录结构与典型案例

```
posit_Connect/
├── Streamlit/                # 🤖 机器学习快速原型
│   ├── app.py                # Iris 鸢尾花分类器 (ML Prototyping)
│   └── requirements.txt
├── Dash/                     # 📊 企业级实时仪表板
│   ├── app.py                # 实时金融交易监控 (Real-time Dashboard)
│   └── requirements.txt
├── Shiny/                    # 🧮 科学计算与模拟
│   ├── app.py                # Python版: 中心极限定理模拟 (Scientific Simulation)
│   ├── app.R                 # R版: 传染病动力学模型 (SEIR Model)
│   └── requirements.txt
├── Bokeh/                    # 🔍 多图联动探索
│   ├── app.py                # 交互式多维数据刷选 (Linked Brushing)
│   └── requirements.txt
├── Jupyter/                  # 📓 端到端分析工作流
│   ├── analysis.ipynb        # 房价预测 ML Pipeline (Narrative Notebook)
│   └── requirements.txt
├── Quarto/                   # 📝 学术出版级文档
│   ├── index.qmd             # 气候变化影响评估 (Academic Paper)
│   └── requirements.txt
├── RMarkdown/                # 📉 参数化自动报告
│   ├── report.Rmd            # 区域销售月报 (Parameterized Reporting)
│   └── requirements.R
├── StaticDocument/           # 📘 知识库与规范
│   ├── document.qmd          # API 开发文档 (Knowledge Base)
│   └── styles.css
└── README.md
```

## 框架选型指南

| 框架 | 典型用途 | 核心特色 | 示例项目 |
|------|----------|----------|----------|
| **Streamlit** | **ML 原型/工具** | 脚本即应用 (Script-to-App)，开发极快 | 🤖 鸢尾花分类器 |
| **Dash** | **企业级看板** | 高度定制布局，适合复杂生产环境 | 📊 实时交易监控 |
| **Shiny** | **科学模拟** | 强大的响应式图 (Reactivity)，逻辑严密 | 🧮 CLT/SEIR 模拟 |
| **Bokeh** | **数据探索** | 高性能交互，自定义工具，多图联动 | 🔍 联动刷选器 |
| **Jupyter** | **分析叙事** | 代码+文本+结果，展示分析过程 | 📓 房价预测流 |
| **Quarto** | **学术出版** | 多格式输出 (PDF/Word)，引用/公式支持 | 📝 气候评估报告 |
| **R Markdown** | **自动化报告** | 参数化生成，定时发送不同版本 | 📉 区域销售月报 |
| **Static** | **文档/规范** | 轻量级，访问控制，无需后端 | 📘 API 文档 |

## 快速开始

### 1. 本地运行 Streamlit (ML 原型)
```bash
cd Streamlit
pip install -r requirements.txt
streamlit run app.py
```

### 2. 本地运行 Dash (企业看板)
```bash
cd Dash
pip install -r requirements.txt
python app.py
```

### 3. 部署到 Posit Connect
1. **登录 Posit Connect Cloud**
2. **创建新应用** → 选择对应框架
3. **连接 Git 仓库**：
   ```
   Repository: https://github.com/YOUR_USERNAME/posit_Connect
   Branch: main
   App Directory: /Streamlit/ (或 /Dash/, /Shiny/ 等)
   ```
4. **自动部署**：推送代码即触发云端构建

## 贡献指南

欢迎提交 Pull Request 添加更多"典型案例"！请确保：
1. 代码简洁明了，注释清晰
2. 包含 `requirements.txt` 或依赖说明
3. 体现该框架的独特优势

## 许可证

MIT License
