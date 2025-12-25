"""
核心二维码类库
包含：QRCodeConfig, QRCodeStyle, QRCodeGenerator, VCardBuilder
"""
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
import os
from urllib.parse import urlencode, quote
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
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
        try:
            qr.make(fit=True)
        except Exception as e:
            if "Invalid version" in str(e):
                raise ValueError("内容过多，无法生成二维码。\n建议：\n1. 减少文字内容\n2. 降低容错级别（如改为'低'）")
            raise e
        
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
                        "fonts/SimHei.ttf", "fonts/msyh.ttc", "fonts/simsun.ttc", "fonts/NotoSansSC-Regular.ttf",
                        "SimHei.ttf", "msyh.ttc",
                        "simsun.ttc", "simsun.ttf", "Microsoft YaHei.ttf", "SimHei.ttf", "STSong.ttf", "arial.ttf",
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
