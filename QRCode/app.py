"""
自定义二维码生成器 - 面向对象版本
支持：
1. 多种样式的二维码生成
2. URL编码数据注入
3. 批量生成
4. 自定义图标
"""

import streamlit as st
import qrcode
from PIL import Image
import io
import base64
import os
from urllib.parse import urlencode, quote
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import json


@dataclass
class QRCodeConfig:
    """二维码配置类 - 封装所有配置参数"""
    # 内容相关
    content: str = ""
    content_type: str = "文本"
    
    # 样式相关
    style_preset: str = "经典黑白"
    fill_color: str = "#000000"
    back_color: str = "#FFFFFF"
    
    # 尺寸相关
    box_size: int = 15
    border: int = 1
    dpi: int = 300
    
    # 容错级别
    error_correction: str = "极高 (H - 30%)"
    
    # 图标相关
    logo_option: str = "无图标"
    logo_size: int = 20
    logo_file: Optional[Any] = None
    
    # 联系方式相关
    vcard_data: Dict[str, str] = field(default_factory=dict)
    
    # 批量模式
    batch_mode: bool = False
    
    def to_url_params(self) -> str:
        """将用户关键信息转换为URL参数（不包含样式配置）"""
        params = {
            'type': self.content_type,
        }
        
        # 添加联系方式数据或普通内容
        if self.vcard_data:
            # 只编码非空的字段
            params['vcard'] = json.dumps(self.vcard_data, ensure_ascii=False)
        elif self.content:
            # 只有内容不为空时才添加
            params['content'] = self.content
        
        return urlencode(params, quote_via=quote)


class QRCodeStyle:
    """二维码样式管理类"""
    PRESETS = {
        "经典黑白": {"fill": "#000000", "back": "#FFFFFF", "desc": "传统二维码样式"},
        "商务蓝": {"fill": "#1E3A8A", "back": "#F0F9FF", "desc": "专业商务风格"},
        "活力橙": {"fill": "#EA580C", "back": "#FFF7ED", "desc": "充满活力的暖色调"},
        "自然绿": {"fill": "#15803D", "back": "#F0FDF4", "desc": "清新自然风格"},
        "浪漫粉": {"fill": "#BE185D", "back": "#FDF2F8", "desc": "温馨浪漫氛围"},
        "科技紫": {"fill": "#6B21A8", "back": "#FAF5FF", "desc": "科技感十足"},
        "自定义": {"fill": "#000000", "back": "#FFFFFF", "desc": "完全自定义颜色"}
    }
    
    ERROR_CORRECTION_MAP = {
        "低 (L - 7%)": qrcode.constants.ERROR_CORRECT_L,
        "中 (M - 15%)": qrcode.constants.ERROR_CORRECT_M,
        "高 (Q - 25%)": qrcode.constants.ERROR_CORRECT_Q,
        "极高 (H - 30%)": qrcode.constants.ERROR_CORRECT_H
    }
    
    @classmethod
    def get_colors(cls, preset: str) -> tuple:
        """获取预设样式的颜色"""
        style = cls.PRESETS.get(preset, cls.PRESETS["经典黑白"])
        return style["fill"], style["back"]
    
    @classmethod
    def get_description(cls, preset: str) -> str:
        """获取样式描述"""
        return cls.PRESETS.get(preset, {}).get("desc", "")


class QRCodeGenerator:
    """二维码生成器类"""
    
    # 固定的部署URL - 用户无法修改
    DEPLOY_URL = "https://negiao-pages.share.connect.posit.cloud/Others/decoder.html"
    
    def __init__(self, config: QRCodeConfig):
        self.config = config
    
    def generate(self, data: Optional[str] = None, use_default_logo: bool = False) -> Image.Image:
        """生成二维码图像"""
        # 如果没有指定data，则使用generate_qr_content生成URL
        if data is None:
            content = self.generate_qr_content()
        else:
            content = data
        
        # 创建二维码对象
        qr = qrcode.QRCode(
            version=1,
            error_correction=QRCodeStyle.ERROR_CORRECTION_MAP[self.config.error_correction],
            box_size=self.config.box_size,
            border=self.config.border,
        )
        qr.add_data(content)
        qr.make(fit=True)
        
        # 生成图像
        img = qr.make_image(
            fill_color=self.config.fill_color, 
            back_color=self.config.back_color
        ).convert("RGB")
        
        # 添加图标
        if self.config.logo_option != "无图标":
            img = self._add_logo(img, use_default_logo)
        
        return img
    
    def _add_logo(self, img: Image.Image, use_default: bool) -> Image.Image:
        """在二维码中心添加图标"""
        logo_path = None
        
        # 确定图标来源
        if use_default and os.path.exists("icon.jpg"):
            logo_path = "icon.jpg"
            logo_img = Image.open(logo_path)
        elif self.config.logo_file:
            logo_img = Image.open(self.config.logo_file)
        else:
            return img
        
        # 计算图标尺寸
        qr_width, qr_height = img.size
        logo_max_size = int(qr_width * self.config.logo_size / 100)
        
        # 调整图标大小
        logo_img.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
        
        # 添加白色背景
        logo_bg = Image.new('RGB', 
                           (logo_img.size[0] + 20, logo_img.size[1] + 20), 
                           self.config.back_color)
        
        # 粘贴图标到背景
        if logo_img.mode == 'RGBA':
            logo_bg.paste(logo_img, (10, 10), logo_img)
        else:
            logo_bg.paste(logo_img, (10, 10))
        
        # 计算居中位置并粘贴
        logo_pos = (
            (qr_width - logo_bg.size[0]) // 2,
            (qr_height - logo_bg.size[1]) // 2
        )
        img.paste(logo_bg, logo_pos)
        
        return img
    
    def save_to_buffer(self, img: Image.Image) -> bytes:
        """将图像保存到字节流"""
        buf = io.BytesIO()
        img.save(buf, format='PNG', dpi=(self.config.dpi, self.config.dpi))
        return buf.getvalue()
    
    def generate_qr_content(self) -> str:
        """
        生成二维码内容（URL）
        - 如果是网址类型：直接返回用户输入的网址
        - 其他类型：返回带编码参数的固定部署URL
        """
        # 如果是网址类型，直接使用用户输入的网址
        if self.config.content_type == "网址":
            return self.config.content
        
        # 其他类型（文本、联系方式等），生成带参数的URL
        params = self.config.to_url_params()
        return f"{self.DEPLOY_URL}?{params}"


class VCardBuilder:
    """电子名片构建器"""
    
    @staticmethod
    def build(data: Dict[str, str]) -> str:
        """从字典构建名片内容"""
        lines = []
        field_names = {
            'name': '姓名',
            'title': '职位',
            'company': '公司',
            'tel': '电话',
            'email': '邮箱',
            'wechat': '微信',
            'qq': 'QQ',
            'alipay': '支付宝',
            'website': '网站',
            'address': '地址',
            'note': '备注'
        }
        
        for key, label in field_names.items():
            if data.get(key):
                lines.append(f"{label}: {data[key]}")
        
        return "\n".join(lines)


# 设置页面配置
st.set_page_config(page_title="二维码生成器", page_icon="📱", layout="wide")

st.title("📱 自定义二维码生成器")
st.markdown("生成个性化二维码，支持自定义颜色、样式、中心图标和URL编码")

# 作者信息
st.info("👤 **作者主页**: [点击访问 NEGIAO 主页](https://negiao-pages.share.connect.posit.cloud/) | 💬 欢迎联系交流与反馈")


# ========== UI 配置部分 ==========
# 侧边栏配置
st.sidebar.header("⚙️ 二维码配置")

# 初始化配置对象
config = QRCodeConfig()

# 1. 内容输入
content_type = st.sidebar.radio("内容类型", ["文本", "网址", "联系方式/名片", "批量网址"])
config.content_type = content_type

if content_type == "文本":
    content = st.sidebar.text_area("输入文本内容", height=100, placeholder="请输入要生成二维码的文本...")
    config.content = content
    config.batch_mode = False
    
elif content_type == "联系方式/名片":
    st.sidebar.markdown("**📇 填写联系信息**")
    vcard_data = {
        'name': st.sidebar.text_input("姓名", placeholder="张三"),
        'title': st.sidebar.text_input("职位", placeholder="职位名称"),
        'company': st.sidebar.text_input("公司/组织", placeholder="公司名称"),
        'tel': st.sidebar.text_input("电话", placeholder="138-0000-0000"),
        'email': st.sidebar.text_input("邮箱", placeholder="example@email.com"),
        'wechat': st.sidebar.text_input("微信号", placeholder="WeChat ID"),
        'qq': st.sidebar.text_input("QQ", placeholder="12345678"),
        'alipay': st.sidebar.text_input("支付宝", placeholder="Alipay账号"),
        'website': st.sidebar.text_input("网站", placeholder="https://example.com"),
        'address': st.sidebar.text_input("地址", placeholder="公司/家庭地址"),
        'note': st.sidebar.text_area("备注", height=70, placeholder="其他信息")
    }
    
    # 过滤空值
    config.vcard_data = {k: v for k, v in vcard_data.items() if v}
    config.content = VCardBuilder.build(config.vcard_data)
    config.batch_mode = False
    
elif content_type == "批量网址":
    content = st.sidebar.text_area(
        "输入多个网址（每行一个）", 
        height=150, 
        placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com"
    )
    config.content = content
    config.batch_mode = True
else:
    content = st.sidebar.text_input("输入网址", placeholder="https://example.com")
    config.content = content
    config.batch_mode = False

# 2. 预设样式选择
st.sidebar.subheader("🎨 样式配置")
style_choice = st.sidebar.selectbox(
    "选择预设样式",
    list(QRCodeStyle.PRESETS.keys()),
    help="选择预设配色方案"
)
config.style_preset = style_choice

# 显示样式说明
st.sidebar.caption(f"💡 {QRCodeStyle.get_description(style_choice)}")

# 颜色配置
if style_choice == "自定义":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        config.fill_color = st.color_picker("前景色", QRCodeStyle.PRESETS[style_choice]["fill"])
    with col2:
        config.back_color = st.color_picker("背景色", QRCodeStyle.PRESETS[style_choice]["back"])
else:
    config.fill_color, config.back_color = QRCodeStyle.get_colors(style_choice)
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.color_picker("前景色", config.fill_color, disabled=True)
    with col2:
        st.color_picker("背景色", config.back_color, disabled=True)

# 3. 尺寸和容错级别
st.sidebar.subheader("📐 尺寸设置")
config.box_size = st.sidebar.slider("像素块大小", 10, 30, 15, help="控制二维码的精细程度")
config.border = st.sidebar.slider("边框宽度", 1, 10, 1, help="二维码周围的空白边框")

dpi_options = [72, 150, 300, 600]
config.dpi = st.sidebar.select_slider(
    "输出 DPI (分辨率)",
    options=dpi_options,
    value=300,
    help="DPI越高图片越清晰"
)

config.error_correction = st.sidebar.selectbox(
    "容错级别",
    ["低 (L - 7%)", "中 (M - 15%)", "高 (Q - 25%)", "极高 (H - 30%)"],
    index=3,
    help='容错级别越高，二维码越密集，但可承受更多损坏'
)

# 4. 中心图标配置
st.sidebar.subheader("🖼️ 中心图标 (可选)")
logo_option = st.sidebar.radio("图标来源", ["无图标", "使用默认图标", "上传自定义图标"])
config.logo_option = logo_option

use_default_logo = False
if logo_option == "使用默认图标":
    use_default_logo = True
    if os.path.exists("icon.jpg"):
        st.sidebar.image("icon.jpg", width=100, caption="默认图标预览")
    config.logo_size = st.sidebar.slider("图标大小比例 (%)", 10, 30, 20)
elif logo_option == "上传自定义图标":
    config.logo_file = st.sidebar.file_uploader("上传中心图标 (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if config.logo_file:
        config.logo_size = st.sidebar.slider("图标大小比例 (%)", 10, 30, 20)

# 智能提示
if (logo_option != "无图标") and (config.error_correction in ["低 (L - 7%)", "中 (M - 15%)"]):
    st.sidebar.warning('⚠️ 当前容错级别较低，添加中心图标可能影响识别。建议选择"高"或"极高"容错级别。')

if (logo_option != "无图标") and config.logo_size > 30:
    st.sidebar.warning('⚠️ 图标尺寸过大可能遮挡过多二维码数据，建议控制在30%以内。')


# ========== 主界面渲染 ==========
if config.content:
    # 创建生成器实例
    generator = QRCodeGenerator(config)
    
    # 批量模式
    if config.batch_mode:
        urls = [url.strip() for url in config.content.split('\n') if url.strip()]
        
        if urls:
            st.subheader(f"📦 批量生成 - 共 {len(urls)} 个二维码")
            
            # 生成设置信息
            with st.expander("🎯 生成设置", expanded=False):
                st.write(f"- **样式**: {config.style_preset}")
                st.write(f"- **前景色**: `{config.fill_color}` | **背景色**: `{config.back_color}`")
                st.write(f"- **像素块**: {config.box_size} | **边框**: {config.border} | **DPI**: {config.dpi}")
                st.write(f"- **容错级别**: {config.error_correction}")
                if config.logo_option == "使用默认图标":
                    st.write(f"- **中心图标**: ✅ 默认图标 ({config.logo_size}%)")
                elif config.logo_file:
                    st.write(f"- **中心图标**: ✅ 自定义图标 ({config.logo_size}%)")
            
            # 生成所有二维码
            qr_images = []
            for idx, url in enumerate(urls, 1):
                try:
                    # 为每个URL创建单独的配置
                    url_config = QRCodeConfig(
                        content=url,
                        content_type="网址",
                        style_preset=config.style_preset,
                        fill_color=config.fill_color,
                        back_color=config.back_color,
                        box_size=config.box_size,
                        border=config.border,
                        dpi=config.dpi,
                        error_correction=config.error_correction,
                        logo_option=config.logo_option,
                        logo_size=config.logo_size,
                        logo_file=config.logo_file
                    )
                    url_generator = QRCodeGenerator(url_config)
                    qr_img = url_generator.generate(use_default_logo=use_default_logo)
                    qr_url = url_generator.generate_qr_content()  # 获取二维码实际URL
                    qr_images.append((url, qr_img, qr_url))
                except Exception as e:
                    st.error(f"❌ 第 {idx} 个网址生成失败: {url}\n错误: {str(e)}")
            
            # 网格展示
            cols_per_row = 3
            for i in range(0, len(qr_images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, (url, qr_img, qr_url) in enumerate(qr_images[i:i+cols_per_row]):
                    with cols[j]:
                        st.image(qr_img, use_container_width=True)
                        st.caption(f"🔗 原始网址: {url[:40]}{'...' if len(url) > 40 else ''}")
                        
                        # 下载按钮
                        buf = io.BytesIO()
                        qr_img.save(buf, format='PNG', dpi=(config.dpi, config.dpi))
                        st.download_button(
                            label="📥 下载",
                            data=buf.getvalue(),
                            file_name=f"qrcode_{i+j+1}.png",
                            mime="image/png",
                            key=f"download_{i+j}"
                        )
                        
                        # 显示二维码中的URL
                        with st.expander("🔍 查看二维码URL"):
                            st.code(qr_url, language="text")
                            st.caption("扫描二维码后访问此URL")
            
            st.success(f"✅ 成功生成 {len(qr_images)} 个二维码")
        else:
            st.warning("请输入至少一个网址")
    
    # 单个模式
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 内容预览")
            st.info(f"**类型**: {config.content_type}\n\n**内容**: {config.content[:100]}{'...' if len(config.content) > 100 else ''}")
            
            st.subheader("🎯 生成设置")
            st.write(f"- **样式**: {config.style_preset}")
            st.write(f"- **前景色**: `{config.fill_color}`")
            st.write(f"- **背景色**: `{config.back_color}`")
            st.write(f"- **像素块大小**: {config.box_size}")
            st.write(f"- **边框宽度**: {config.border}")
            st.write(f"- **输出 DPI**: {config.dpi}")
            st.write(f"- **容错级别**: {config.error_correction}")
            if config.logo_option == "使用默认图标":
                st.write(f"- **中心图标**: ✅ 默认图标 ({config.logo_size}%)")
            elif config.logo_file:
                st.write(f"- **中心图标**: ✅ 自定义图标 ({config.logo_size}%)")
            else:
                st.write(f"- **中心图标**: ❌ 无")
            
            # 显示二维码URL
            st.subheader("🔍 二维码URL")
            qr_url = generator.generate_qr_content()
            st.code(qr_url, language="text")
            if config.content_type == "网址":
                st.caption("💡 网址类型：直接使用您输入的网址")
            else:
                st.caption("💡 已将数据编码到URL参数中，扫描后访问部署的网页自动解析")
        
        with col2:
            st.subheader("🖼️ 二维码预览")
            
            try:
                # 生成二维码
                qr_img = generator.generate(use_default_logo=use_default_logo)
                
                # 显示二维码
                st.image(qr_img, use_container_width=True)
                
                # 下载按钮
                byte_img = generator.save_to_buffer(qr_img)
                st.download_button(
                    label=f"📥 下载二维码 ({config.dpi} DPI)",
                    data=byte_img,
                    file_name=f"qrcode_{config.dpi}dpi.png",
                    mime="image/png",
                    type="primary"
                )
            
            except Exception as e:
                st.error(f"生成失败: {str(e)}")
else:
    st.info("👈 请在左侧输入内容以生成二维码")
    
    # 显示预设样式示例
    st.subheader("🎨 预设样式示例")
    
    cols = st.columns(4)
    style_names = ["经典黑白", "商务蓝", "活力橙", "自然绿"]
    
    for idx, style_name in enumerate(style_names):
        with cols[idx]:
            st.markdown(f"### {style_name}")
            st.caption(QRCodeStyle.get_description(style_name))
            fill, back = QRCodeStyle.get_colors(style_name)
            example_config = QRCodeConfig(
                content="示例二维码",
                fill_color=fill,
                back_color=back,
                box_size=12,
                border=4,
                error_correction="中 (M - 15%)"
            )
            example_gen = QRCodeGenerator(example_config)
            example_qr = example_gen.generate()
            st.image(example_qr, width=180)
    
    # 第二行
    cols2 = st.columns(4)
    style_names2 = ["浪漫粉", "科技紫"]
    
    for idx, style_name in enumerate(style_names2):
        with cols2[idx]:
            st.markdown(f"### {style_name}")
            st.caption(QRCodeStyle.get_description(style_name))
            fill, back = QRCodeStyle.get_colors(style_name)
            example_config = QRCodeConfig(
                content="示例二维码",
                fill_color=fill,
                back_color=back,
                box_size=12,
                border=4,
                error_correction="中 (M - 15%)"
            )
            example_gen = QRCodeGenerator(example_config)
            example_qr = example_gen.generate()
            st.image(example_qr, width=180)

# 页脚说明
st.markdown("---")
st.markdown("""
**使用说明：**
1. 在左侧选择内容类型（文本/网址/联系方式）并输入内容
2. 选择预设样式或自定义颜色
3. 调整像素块大小、DPI和容错级别
4. （可选）添加中心图标
5. 点击下载按钮保存二维码

**二维码工作原理：**
- **网址类型**：二维码直接包含您输入的网址，扫描后直接访问
- **其他类型**（文本/联系方式）：数据会编码到URL参数中，扫描后访问部署的网页自动解析显示
- 部署地址：`https://negiao-pages.share.connect.posit.cloud/`

**技术支持**: 基于面向对象设计，使用 `qrcode` 和 `Pillow` 库构建
""")
