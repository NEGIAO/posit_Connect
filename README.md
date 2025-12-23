# Posit Connect Cloud 多框架演示项目

> 🚀 在 Posit Connect Cloud 上部署和托管各类数据科学应用的综合示例集合  
> 🌐 **在线访问**：[Posit Connect Cloud](https://connect.posit.cloud/)

## 项目概述

本项目是一个**服务器端数据处理与可视化**的演示平台，展示了如何利用 Posit Connect Cloud 托管多种主流框架的应用。相比 GitHub Pages 等静态托管服务，Posit Connect 提供了：

- ✅ **服务器端计算**：支持 Python/R 后端逻辑执行
- ✅ **动态交互**：实时数据处理与用户交互
- ✅ **专业工具集成**：地理空间分析、机器学习、统计建模等
- ✅ **多框架支持**：涵盖 8 大主流数据科学应用框架
- ✅ **自动部署**：Git 推送即可触发云端更新

## 目录结构

```
posit_Connect/
├── Streamlit/                # Streamlit 交互式应用
│   ├── app.py                # GIS 矢量数据处理器
│   └── requirements.txt      # Python 依赖
├── Dash/                     # Plotly Dash 仪表板
│   ├── app.py
│   └── requirements.txt
├── Shiny/                    # Shiny for Python/R 应用
│   ├── app.py                # Python 版本
│   ├── app.R                 # R 版本
│   └── requirements.txt
├── Jupyter/                  # Jupyter Notebook 文档
│   ├── analysis.ipynb
│   └── requirements.txt
├── Quarto/                   # Quarto 报告与网站
│   ├── _quarto.yml
│   ├── index.qmd
│   └── requirements.txt
├── RMarkdown/                # R Markdown 报告
│   ├── report.Rmd
│   └── requirements.R
├── Bokeh/                    # Bokeh 可视化服务器
│   ├── app.py
│   └── requirements.txt
├── StaticDocument/           # 静态 HTML/PDF 文档
│   ├── document.qmd
│   └── styles.css
├── .gitignore
└── README.md                 # 项目说明文档（本文件）
```

## 支持的框架

### 🎯 已实现

| 框架 | 状态 | 描述 | 部署路径 |
|------|------|------|----------|
| **Streamlit** | ✅ 已完成 | GIS 矢量数据空间分析平台（GeoJSON/KML 处理） | `/Streamlit/` |

### 🚧 计划实现

| 框架 | 优先级 | 典型用途 | 技术栈 |
|------|--------|----------|--------|
| **Dash** | P1 | 企业级仪表板、实时监控 | Python + Plotly |
| **Shiny** | P1 | 统计分析应用、R 语言集成 | Python/R + htmlwidgets |
| **Jupyter** | P2 | 数据探索笔记本、教学文档 | IPython Kernel |
| **Quarto** | P2 | 科研报告、技术博客、多格式输出 | Markdown + Pandoc |
| **R Markdown** | P3 | R 语言统计报告 | R + knitr |
| **Bokeh** | P3 | 大规模数据可视化服务器 | Python + BokehJS |
| **Static Document** | P3 | 静态网页、PDF 文档 | HTML/CSS |

## 框架特性对比

| 特性 | Streamlit | Dash | Shiny | Jupyter | Quarto |
|------|-----------|------|-------|---------|--------|
| 开发语言 | Python | Python | Python/R | Python/R/Julia | Markdown |
| 学习曲线 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| 交互性 | 强 | 强 | 强 | 中 | 弱 |
| 企业级应用 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| 可视化库 | Matplotlib/Plotly | Plotly 原生 | ggplot2/plotly | 任意 | 任意 |
| 适用场景 | 快速原型/数据探索 | 生产级仪表板 | 统计分析工具 | 研究/教学 | 文档/博客 |

## 当前项目：Streamlit GIS 应用

### 功能亮点
- 📂 **多格式支持**：上传 GeoJSON 或 KML 矢量数据
- 🗺️ **空间分析**：基于 GeoPandas 的缓冲区分析（米级精度）
- 🌍 **交互地图**：Leafmap + Folium 双图层可视化
- 📥 **结果导出**：下载 GeoJSON/KML 格式分析结果
- 🔧 **坐标转换**：自动处理 WGS84 ↔ Web Mercator 投影

### 技术栈
- **核心库**：`streamlit`, `geopandas`, `leafmap`, `fiona`
- **依赖管理**：完整的 `requirements.txt`（106 个包）
- **GIS 引擎**：GDAL/Fiona 驱动支持

### 本地运行
```bash
cd Streamlit
pip install -r requirements.txt
streamlit run app.py
```

### 部署到 Posit Connect
1. **登录 Posit Connect Cloud**
2. **创建新应用** → 选择 **Streamlit**
3. **连接 Git 仓库**：
   ```
   Repository: https://github.com/YOUR_USERNAME/posit_Connect
   Branch: main
   App Directory: /Streamlit/
   ```
4. **自动部署**：推送代码即触发云端构建

## 开发计划

### Phase 1 - 基础框架覆盖（2025 Q1）
- [x] Streamlit 示例应用
- [ ] Dash 企业级仪表板
- [ ] Shiny for Python 交互式应用

### Phase 2 - 文档与报告（2025 Q2）
- [ ] Jupyter Notebook 数据分析教程
- [ ] Quarto 多格式报告系统
- [ ] R Markdown 统计报告模板

### Phase 3 - 高级可视化（2025 Q3）
- [ ] Bokeh 大规模数据可视化
- [ ] Static Document 静态页面生成

## 贡献指南

### 添加新框架示例
1. 在根目录创建框架文件夹（如 `Dash/`）
2. 准备核心文件：
   - `app.py` / `app.R` / `*.ipynb` 等入口文件
   - `requirements.txt` / `requirements.R` 依赖清单
3. 更新本 README 的框架状态表
4. 提交 Pull Request

### 代码规范
- Python：遵循 PEP 8
- R：遵循 tidyverse 风格指南
- 注释：中英文混合，关键逻辑必须注释
- 文档：每个应用需包含使用说明

## 技术要求

### Python 环境
- Python 3.9+
- 虚拟环境管理：`venv` 或 `conda`

### R 环境
- R 4.0+
- RStudio（推荐）

### 云端部署
- Posit Connect Cloud 账号
- Git 版本控制基础
- 可选：Docker 容器化知识

## 资源链接

- 📘 [Posit Connect 官方文档](https://docs.posit.co/connect/)
- 🎓 [Streamlit 文档](https://docs.streamlit.io/)
- 📊 [Dash 文档](https://dash.plotly.com/)
- ✨ [Shiny 文档](https://shiny.posit.co/)
- 📝 [Quarto 文档](https://quarto.org/)

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 更新日志

### 2025-12-23 · v0.1.0
- ✅ 初始化项目结构
- ✅ 完成 Streamlit GIS 矢量数据处理器
- ✅ 编写完整的 README 文档
- 🔄 规划 8 大框架实现路线图

---

**让数据科学应用触手可及 - Powered by Posit Connect Cloud**
