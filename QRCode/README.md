# 📱 二维码生成器

基于面向对象设计的二维码生成器，支持自定义样式、图标和数据URL编码。

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

## ✨ 核心功能

### 1. 多种内容类型
- **网址**：二维码直接包含URL，扫描后访问
- **文本**：数据编码到URL参数，扫描后访问 `https://negiao-pages.share.connect.posit.cloud/Others/decoder.html/?参数`
- **联系方式/名片**：VCard数据编码到URL，扫描后网页显示
- **批量网址**：批量生成多个二维码

### 2. 样式自定义
- **多种码点样式**：方块、圆点、圆角方块、间隙方块（默认）、竖条纹、横条纹

# 📱 二维码生成器

这是一个基于 Streamlit 的二维码生成器，已将核心生成逻辑抽离为模块 `qrcode_core.py`，便于维护与测试。

主要功能：
- 支持 `网址` / `文本` / `联系方式(名片)` / `批量网址` 四种内容类型
- 多种码点样式与预设配色，支持自定义前景/背景颜色
- 可选中心图标、顶部/底部文字（支持中文字体优先查找本地 `fonts/`）
- 可导出 PNG（可选 DPI）与批量生成下载

## 本次更新

- 将核心类 `QRCodeConfig`, `QRCodeStyle`, `QRCodeGenerator`, `VCardBuilder` 提取到 `qrcode_core.py`，`app.py` 仅负责 UI（Streamlit）逻辑。
- 修复了因文件合并导致的缩进/导入错误（见仓库提交记录）。

## 快速开始

1. 安装依赖（建议使用虚拟环境）

```bash
pip install -r requirements.txt
```

2. 运行 Streamlit 应用：

```bash
streamlit run app.py
```

## 模块使用（开发者）

如果你想在代码中复用核心功能，可直接导入 `qrcode_core`：

```python
from qrcode_core import QRCodeConfig, QRCodeGenerator

cfg = QRCodeConfig(content='https://example.com', content_type='网址')
gen = QRCodeGenerator(cfg)
img = gen.generate()
img.save('qrcode.png')
```

## 文件说明

- `app.py`：Streamlit UI 与交互逻辑
- `qrcode_core.py`：核心类和生成逻辑（可单元测试）
- `requirements.txt`：运行所需依赖（`streamlit`, `qrcode`, `Pillow` 等）
- `fonts/`：可选，本地中文字体用于服务器环境
- `icon.jpg`：默认中心图标（可选）

## 部署

- 将 `app.py` 与 `requirements.txt` 上传到 Posit Connect 或在服务器上运行 `streamlit run app.py`。
- 解码页面 `decoder.html` 可部署为静态页面（仓库内 `Others/decoder.html`）。

## 运行测试（建议）

- 为 `qrcode_core.py` 添加单元测试，覆盖 `generate_qr_content` 与 `generate` 的核心路径。

## 许可证

MIT License

## 联系

NEGIAO — https://negiao-pages.share.connect.posit.cloud/
VCardBuilder     # 名片构建

