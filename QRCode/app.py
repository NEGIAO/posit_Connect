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
from qrcode.image.styledpil import StyledPilImage, SolidFillColorMask
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer
)
from PIL import Image, ImageDraw, ImageFont
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
    module_drawer: str = "间隙方块 (Gapped)"
    
    # 尺寸相关
    box_size: int = 15
    border: int = 4
    dpi: int = 300
    
    # 容错级别
    error_correction: str = "极高 (H - 30%)"
    
    # 图标相关
    logo_option: str = "无图标"
    logo_size: int = 20
    logo_file: Optional[Any] = None

    # 文字相关
    top_text: str = ""
    bottom_text: str = ""
    font_size: int = 30
    text_color: str = "#000000"
    font_file: Optional[Any] = None
    is_bold: bool = False
    text_padding: int = 20
    
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

    MODULE_DRAWERS = {
        "方块 (默认)": SquareModuleDrawer(),
        "圆点 (Circle)": CircleModuleDrawer(),
        "圆角方块 (Rounded)": RoundedModuleDrawer(),
        "间隙方块 (Gapped)": GappedSquareModuleDrawer(),
        "竖条纹 (Vertical)": VerticalBarsDrawer(),
        "横条纹 (Horizontal)": HorizontalBarsDrawer()
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
        
        # 获取模块绘制器
        module_drawer = QRCodeStyle.MODULE_DRAWERS.get(
            self.config.module_drawer, 
            SquareModuleDrawer()
        )

        # 生成图像
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=module_drawer,
            color_mask=SolidFillColorMask(
                back_color=tuple(int(self.config.back_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)),
                front_color=tuple(int(self.config.fill_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            )
        ).convert("RGB")
        
        # 添加图标
        if self.config.logo_option != "无图标":
            img = self._add_logo(img, use_default_logo)
            
        # 添加文字
        if self.config.top_text or self.config.bottom_text:
            img = self._add_text(img)
        
        return img
    
    def _add_text(self, img: Image.Image) -> Image.Image:
        """添加顶部和底部文字"""
        # 检查是否包含中文字符
        def has_chinese(text):
            return any('\u4e00' <= char <= '\u9fff' for char in text)
            
        # 加载字体
        font = None
        try:
            if self.config.font_file:
                if hasattr(self.config.font_file, 'seek'):
                    self.config.font_file.seek(0)
                font = ImageFont.truetype(self.config.font_file, self.config.font_size)
            else:
                # 根据内容选择默认字体
                # 如果包含中文，优先使用宋体/黑体
                # 如果是纯英文，优先使用 Times New Roman
                text_content = (self.config.top_text or "") + (self.config.bottom_text or "")
                
                if has_chinese(text_content):
                    # 中文优先字体列表
                    font_names = [
                        # 1. 项目本地字体 (推荐用户上传到 fonts/ 目录)
                        "fonts/SimHei.ttf", "fonts/msyh.ttc", "fonts/simsun.ttc", "fonts/NotoSansSC-Regular.ttf",
                        "SimHei.ttf", "msyh.ttc",
                        # 2. Windows 系统字体
                        "simsun.ttc", "simsun.ttf", "Microsoft YaHei.ttf", "SimHei.ttf", "STSong.ttf", "arial.ttf",
                        # 3. Linux 服务器常见字体 (Debian/Ubuntu/CentOS/Alpine)
                        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                        "/usr/share/fonts/noto/NotoSansCJK-Regular.ttc",
                        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                        "wqy-zenhei.ttc", "wqy-microhei.ttc", "DroidSansFallbackFull.ttf"
                    ]
                else:
                    # 英文优先字体列表
                    font_names = [
                        "fonts/times.ttf", "fonts/arial.ttf", "fonts/TimesNewRoman.ttf",
                        "times.ttf", "Times New Roman.ttf", "arial.ttf", 
                        "DejaVuSans.ttf", "FreeSans.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                    ]
                
                for name in font_names:
                    try:
                        font = ImageFont.truetype(name, self.config.font_size)
                        break
                    except:
                        continue
                
                if font is None:
                    # 如果找不到系统字体，使用默认字体（不支持大小调整，但总比报错好）
                    font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()

        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # 计算二维码边框大小 (像素)
        border_px = self.config.box_size * self.config.border
        
        # 计算文字高度
        top_add = 0
        bottom_add = 0
        padding = self.config.text_padding
        stroke_width = 1 if self.config.is_bold else 0
        
        if self.config.top_text:
            text_h = 0
            if hasattr(draw, 'textbbox'):
                bbox = draw.textbbox((0, 0), self.config.top_text, font=font, stroke_width=stroke_width)
                text_h = bbox[3] - bbox[1]
            else:
                text_h = self.config.font_size
            
            # 目标：文字距离二维码模块 padding 像素
            # 现有边框: border_px
            # 需要的总空间: text_h + padding * 2 (假设上下都有padding)
            # 或者: 文字中心距离模块顶部 padding + text_h/2 ?
            # 用户需求: "从二维码最顶部(模块)，到图片顶部的中间"
            # 也就是说，文字应该位于 [图片顶部, 模块顶部] 这个区间的垂直居中位置
            # 模块顶部位置(相对原图) = border_px
            # 我们添加 top_add 像素
            # 新的模块顶部位置 = top_add + border_px
            # 顶部空白区域总高度 = top_add + border_px
            # 我们希望文字在这个区域居中
            # 另外，我们需要确保这个区域足够大，至少能放下文字 + padding
            
            min_top_space = text_h + padding * 2
            top_add = max(0, min_top_space - border_px)
            
        if self.config.bottom_text:
            text_h = 0
            if hasattr(draw, 'textbbox'):
                bbox = draw.textbbox((0, 0), self.config.bottom_text, font=font, stroke_width=stroke_width)
                text_h = bbox[3] - bbox[1]
            else:
                text_h = self.config.font_size
                
            min_bottom_space = text_h + padding * 2
            bottom_add = max(0, min_bottom_space - border_px)
            
        # 创建新图像
        new_height = height + top_add + bottom_add
        new_img = Image.new("RGB", (width, new_height), self.config.back_color)
        
        # 粘贴二维码
        new_img.paste(img, (0, top_add))
        
        draw = ImageDraw.Draw(new_img)
        
        # 绘制顶部文字
        if self.config.top_text:
            if hasattr(draw, 'textbbox'):
                bbox = draw.textbbox((0, 0), self.config.top_text, font=font, stroke_width=stroke_width)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:
                text_width = len(self.config.top_text) * self.config.font_size * 0.6
                text_height = self.config.font_size
                
            x = (width - text_width) // 2
            # 垂直居中于 [0, top_add + border_px]
            # 中心点 = (top_add + border_px) / 2
            # 文字顶部 = 中心点 - text_height / 2
            y = (top_add + border_px - text_height) // 2
            draw.text((x, y), self.config.top_text, font=font, fill=self.config.text_color, stroke_width=stroke_width, stroke_fill=self.config.text_color)
            
        # 绘制底部文字
        if self.config.bottom_text:
            if hasattr(draw, 'textbbox'):
                bbox = draw.textbbox((0, 0), self.config.bottom_text, font=font, stroke_width=stroke_width)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:
                text_width = len(self.config.bottom_text) * self.config.font_size * 0.6
                text_height = self.config.font_size
                
            x = (width - text_width) // 2
            # 垂直居中于 [top_add + height - border_px, new_height]
            # 区域高度 = border_px + bottom_add
            # 区域顶部 = top_add + height - border_px
            # 文字顶部 = 区域顶部 + (区域高度 - text_height) / 2
            y = (top_add + height - border_px) + (border_px + bottom_add - text_height) // 2
            draw.text((x, y), self.config.bottom_text, font=font, fill=self.config.text_color, stroke_width=stroke_width, stroke_fill=self.config.text_color)
            
        return new_img

    def _add_logo(self, img: Image.Image, use_default: bool) -> Image.Image:
        """在二维码中心添加图标"""
        logo_path = None
        
        # 确定图标来源
        if use_default and os.path.exists("icon.jpg"):
            logo_path = "icon.jpg"
            logo_img = Image.open(logo_path)
        elif self.config.logo_file:
            if hasattr(self.config.logo_file, 'seek'):
                self.config.logo_file.seek(0)
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

# 码点样式选择
config.module_drawer = st.sidebar.selectbox(
    "码点样式",
    list(QRCodeStyle.MODULE_DRAWERS.keys()),
    index=3,
    help="选择二维码数据点的形状"
)

# 3. 尺寸和容错级别
st.sidebar.subheader("📐 尺寸设置")
config.box_size = st.sidebar.slider("像素块大小", 10, 30, 15, help="控制二维码的精细程度")
config.border = st.sidebar.slider("边框宽度", 1, 10, 4, help="二维码周围的空白边框")

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

# 5. 文字说明配置
st.sidebar.subheader("📝 文字说明 (可选)")
config.top_text = st.sidebar.text_input("顶部文字", placeholder="例如：扫描二维码")
config.bottom_text = st.sidebar.text_input("底部文字", placeholder="例如：关注公众号")

if config.top_text or config.bottom_text:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        config.font_size = st.number_input("字体大小", min_value=10, max_value=100, value=30)
    with col2:
        config.text_color = st.color_picker("文字颜色", "#000000")
    
    col3, col4 = st.sidebar.columns(2)
    with col3:
        config.is_bold = st.sidebar.checkbox("文字加粗", value=True)
    with col4:
        config.text_padding = st.sidebar.number_input("垂直边距", min_value=0, max_value=200, value=20, help="调整文字与二维码/边缘的距离")
        
    config.font_file = st.sidebar.file_uploader("上传字体文件 (TTF)", type=["ttf"])
    if not config.font_file:
        st.sidebar.caption("💡 未上传字体将尝试使用系统默认字体")


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
                
                if config.top_text or config.bottom_text:
                    st.write(f"- **文字说明**: 顶部: {config.top_text or '无'} | 底部: {config.bottom_text or '无'}")
            
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
                        logo_file=config.logo_file,
                        top_text=config.top_text,
                        bottom_text=config.bottom_text,
                        font_size=config.font_size,
                        text_color=config.text_color,
                        font_file=config.font_file
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
            
            if config.top_text or config.bottom_text:
                st.write(f"- **文字说明**: 顶部: {config.top_text or '无'} | 底部: {config.bottom_text or '无'}")
            
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
- 部署地址：`https://negiao-pages.share.connect.posit.cloud/Others/decoder.html`

**技术支持**: 基于面向对象设计，使用 `qrcode` 和 `Pillow` 库构建
""")
