import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import io
import base64
import os

# 设置页面配置
st.set_page_config(page_title="二维码生成器", page_icon="📱", layout="wide")

st.title("📱 自定义二维码生成器")
st.markdown("生成个性化二维码，支持自定义颜色、样式和中心图标")

# 作者信息
st.info("👤 **作者主页**: [点击访问 NEGIAO 主页](https://negiao-pages.share.connect.posit.cloud/) | 💬 欢迎联系交流与反馈")

# 预设样式
PRESET_STYLES = {
    "经典黑白": {"fill": "#000000", "back": "#FFFFFF", "desc": "传统二维码样式"},
    "商务蓝": {"fill": "#1E3A8A", "back": "#F0F9FF", "desc": "专业商务风格"},
    "活力橙": {"fill": "#EA580C", "back": "#FFF7ED", "desc": "充满活力的暖色调"},
    "自然绿": {"fill": "#15803D", "back": "#F0FDF4", "desc": "清新自然风格"},
    "浪漫粉": {"fill": "#BE185D", "back": "#FDF2F8", "desc": "温馨浪漫氛围"},
    "科技紫": {"fill": "#6B21A8", "back": "#FAF5FF", "desc": "科技感十足"},
    "自定义": {"fill": "#000000", "back": "#FFFFFF", "desc": "完全自定义颜色"}
}

# 侧边栏配置
st.sidebar.header("⚙️ 二维码配置")

# 1. 内容输入
content_type = st.sidebar.radio("内容类型", ["文本", "网址"])

if content_type == "文本":
    content = st.sidebar.text_area("输入文本内容", height=100, placeholder="请输入要生成二维码的文本...")
else:
    content = st.sidebar.text_input("输入网址", placeholder="https://example.com")

# 2. 预设样式选择
st.sidebar.subheader("🎨 样式配置")
style_choice = st.sidebar.selectbox(
    "选择预设样式",
    list(PRESET_STYLES.keys()),
    help="选择预设配色方案"
)

# 显示样式说明
st.sidebar.caption(f"💡 {PRESET_STYLES[style_choice]['desc']}")

# 颜色配置
if style_choice == "自定义":
    col1, col2 = st.sidebar.columns(2)
    with col1:
        fill_color = st.color_picker("前景色", PRESET_STYLES[style_choice]["fill"])
    with col2:
        back_color = st.color_picker("背景色", PRESET_STYLES[style_choice]["back"])
else:
    fill_color = PRESET_STYLES[style_choice]["fill"]
    back_color = PRESET_STYLES[style_choice]["back"]
    # 显示当前配色
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.color_picker("前景色", fill_color, disabled=True)
    with col2:
        st.color_picker("背景色", back_color, disabled=True)

# 3. 尺寸和容错级别
st.sidebar.subheader("📐 尺寸设置")
box_size = st.sidebar.slider("像素块大小", 10, 30, 15, help="控制二维码的精细程度，值越大越清晰")
border = st.sidebar.slider("边框宽度", 1, 10, 1, help="二维码周围的空白边框")

dpi_options = [72, 150, 300, 600]
output_dpi = st.sidebar.select_slider(
    "输出 DPI (分辨率)",
    options=dpi_options,
    value=300,
    help="DPI越高图片越清晰，72适合屏幕显示，300适合打印，600适合高质量印刷"
)

error_correction = st.sidebar.selectbox(
    "容错级别",
    ["低 (L - 7%)", "中 (M - 15%)", "高 (Q - 25%)", "极高 (H - 30%)"],
    index=2,
    help='容错级别越高，二维码越密集，但可承受更多损坏。添加中心图标建议选择"高"或"极高"'
)

# 错误纠正级别映射
error_map = {
    "低 (L - 7%)": qrcode.constants.ERROR_CORRECT_L,
    "中 (M - 15%)": qrcode.constants.ERROR_CORRECT_M,
    "高 (Q - 25%)": qrcode.constants.ERROR_CORRECT_Q,
    "极高 (H - 30%)": qrcode.constants.ERROR_CORRECT_H
}

# 4. 中心图标配置
st.sidebar.subheader("🖼️ 中心图标 (可选)")
logo_option = st.sidebar.radio("图标来源", ["无图标", "使用默认图标", "上传自定义图标"])

logo_file = None
use_default_logo = False
logo_size = 20  # 默认值

if logo_option == "使用默认图标":
    use_default_logo = True
    default_logo_path = "icon.png"
    if os.path.exists(default_logo_path):
        st.sidebar.image(default_logo_path, width=100, caption="默认图标预览")
    logo_size = st.sidebar.slider("图标大小比例 (%)", 10, 30, 20, help="图标相对于二维码的大小，建议不超过30%以确保可识别性")
elif logo_option == "上传自定义图标":
    logo_file = st.sidebar.file_uploader("上传中心图标 (PNG/JPG)", type=["png", "jpg", "jpeg"])
    if logo_file:
        logo_size = st.sidebar.slider("图标大小比例 (%)", 10, 30, 20, help="图标相对于二维码的大小，建议不超过30%以确保可识别性")

# 智能提示：检查容错级别与图标的匹配
if (logo_option != "无图标") and (error_correction in ["低 (L - 7%)", "中 (M - 15%)"]):
    st.sidebar.warning('⚠️ 当前容错级别较低，添加中心图标可能影响识别。建议选择"高"或"极高"容错级别。')

if (logo_option != "无图标") and logo_size > 30:
    st.sidebar.warning('⚠️ 图标尺寸过大可能遮挡过多二维码数据，建议控制在30%以内。')

# 生成二维码函数
def generate_qr_code(data, fill_color, back_color, box_size, border, error_level, logo=None, logo_size=25, use_default=False):
    """生成高清二维码"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_level,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # 生成二维码图像
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    img = img.convert("RGB")
    
    # 处理中心图标
    logo_to_use = None
    if use_default and os.path.exists("icon.png"):
        logo_to_use = "icon.png"
    elif logo:
        logo_to_use = logo
    
    # 如果有 logo，添加到中心
    if logo_to_use:
        if isinstance(logo_to_use, str):
            logo_img = Image.open(logo_to_use)
        else:
            logo_img = Image.open(logo_to_use)
        
        # 计算 logo 尺寸
        qr_width, qr_height = img.size
        logo_max_size = int(qr_width * logo_size / 100)
        
        # 调整 logo 大小，保持比例
        logo_img.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
        
        # 为logo添加白色背景（防止与二维码冲突）
        logo_bg = Image.new('RGB', (logo_img.size[0] + 20, logo_img.size[1] + 20), back_color)
        logo_bg_pos = (10, 10)
        if logo_img.mode == 'RGBA':
            logo_bg.paste(logo_img, logo_bg_pos, logo_img)
        else:
            logo_bg.paste(logo_img, logo_bg_pos)
        
        # 计算居中位置
        logo_pos = (
            (qr_width - logo_bg.size[0]) // 2,
            (qr_height - logo_bg.size[1]) // 2
        )
        
        # 粘贴 logo
        img.paste(logo_bg, logo_pos)
    
    return img

# 主界面
if content:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 内容预览")
        st.info(f"**类型**: {content_type}\n\n**内容**: {content[:100]}{'...' if len(content) > 100 else ''}")
        
        st.subheader("🎯 生成设置")
        st.write(f"- **样式**: {style_choice}")
        st.write(f"- **前景色**: `{fill_color}`")
        st.write(f"- **背景色**: `{back_color}`")
        st.write(f"- **像素块大小**: {box_size} (高清晰度)")
        st.write(f"- **边框宽度**: {border}")
        st.write(f"- **输出 DPI**: {output_dpi}")
        st.write(f"- **容错级别**: {error_correction}")
        if logo_option == "使用默认图标":
            st.write(f"- **中心图标**: ✅ 默认图标 ({logo_size}%)")
        elif logo_file:
            st.write(f"- **中心图标**: ✅ 自定义图标 ({logo_size}%)")
        else:
            st.write(f"- **中心图标**: ❌ 无")
    
    with col2:
        st.subheader("🖼️ 二维码预览")
        
        try:
            # 生成二维码
            qr_img = generate_qr_code(
                content,
                fill_color,
                back_color,
                box_size,
                border,
                error_map[error_correction],
                logo_file if logo_file else None,
                logo_size,
                use_default_logo
            )
            
            # 显示二维码
            st.image(qr_img, use_container_width=True)
            
            # 转换为字节流用于下载 - 使用用户选择的DPI
            buf = io.BytesIO()
            qr_img.save(buf, format='PNG', dpi=(output_dpi, output_dpi))
            byte_img = buf.getvalue()
            
            # 下载按钮
            st.download_button(
                label=f"📥 下载二维码 ({output_dpi} DPI)",
                data=byte_img,
                file_name=f"qrcode_{output_dpi}dpi.png",
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
            st.caption(PRESET_STYLES[style_name]['desc'])
            example_qr = generate_qr_code(
                "示例二维码", 
                PRESET_STYLES[style_name]['fill'], 
                PRESET_STYLES[style_name]['back'], 
                12, 
                4, 
                qrcode.constants.ERROR_CORRECT_M
            )
            st.image(example_qr, width=180)
    
    # 第二行
    cols2 = st.columns(4)
    style_names2 = ["浪漫粉", "科技紫"]
    
    for idx, style_name in enumerate(style_names2):
        with cols2[idx]:
            st.markdown(f"### {style_name}")
            st.caption(PRESET_STYLES[style_name]['desc'])
            example_qr = generate_qr_code(
                "示例二维码", 
                PRESET_STYLES[style_name]['fill'], 
                PRESET_STYLES[style_name]['back'], 
                12, 
                4, 
                qrcode.constants.ERROR_CORRECT_M
            )
            st.image(example_qr, width=180)

# 页脚说明
st.markdown("---")
st.markdown("""
**使用说明：**
1. 在左侧选择内容类型（文本/网址）并输入内容
2. 选择预设样式或自定义颜色
3. 调整像素块大小（推荐15-20以获得高清晰度）
4. 选择输出DPI（72=屏幕显示，300=打印，600=高质量印刷）
5. 选择容错级别（**添加图标必须选择"高"或"极高"**）
6. （可选）选择默认图标或上传自定义图标（**建议图标大小≤30%**）
7. 点击下载按钮保存指定 DPI 的二维码图片

**重要提示**:  
- 添加中心图标会遮挡部分二维码数据，必须配合**高容错级别**（Q或H）才能确保可识别  
- 图标大小建议控制在**20-30%**之间，过大会导致无法扫描  
- 系统会自动为图标添加白色背景边距，提高识别率

**DPI 说明**: 72 DPI适合屏幕查看，300 DPI适合普通打印，600 DPI适合专业印刷  
**技术支持**: 基于 `qrcode` 和 `Pillow` 库构建
""")
