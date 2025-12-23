import streamlit as st
import qrcode
from PIL import Image
import io
import base64

# 设置页面配置
st.set_page_config(page_title="二维码生成器", page_icon="📱", layout="wide")

st.title("📱 自定义二维码生成器")
st.markdown("生成个性化二维码，支持自定义颜色、样式和中心图标")

# 侧边栏配置
st.sidebar.header("⚙️ 二维码配置")

# 1. 内容输入
content_type = st.sidebar.radio("内容类型", ["文本", "网址"])

if content_type == "文本":
    content = st.sidebar.text_area("输入文本内容", height=100, placeholder="请输入要生成二维码的文本...")
else:
    content = st.sidebar.text_input("输入网址", placeholder="https://example.com")

# 2. 样式配置
st.sidebar.subheader("🎨 样式配置")

col1, col2 = st.sidebar.columns(2)
with col1:
    fill_color = st.color_picker("前景色", "#000000")
with col2:
    back_color = st.color_picker("背景色", "#FFFFFF")

# 3. 尺寸和容错级别
box_size = st.sidebar.slider("像素块大小", 5, 20, 10, help="控制二维码的精细程度")
border = st.sidebar.slider("边框宽度", 1, 10, 4, help="二维码周围的空白边框")

error_correction = st.sidebar.selectbox(
    "容错级别",
    ["低 (L - 7%)", "中 (M - 15%)", "高 (Q - 25%)", "极高 (H - 30%)"],
    index=1,
    help="容错级别越高，二维码越密集，但可承受更多损坏"
)

# 错误纠正级别映射
error_map = {
    "低 (L - 7%)": qrcode.constants.ERROR_CORRECT_L,
    "中 (M - 15%)": qrcode.constants.ERROR_CORRECT_M,
    "高 (Q - 25%)": qrcode.constants.ERROR_CORRECT_Q,
    "极高 (H - 30%)": qrcode.constants.ERROR_CORRECT_H
}

# 4. 中心图标上传
st.sidebar.subheader("🖼️ 中心图标 (可选)")
logo_file = st.sidebar.file_uploader("上传中心图标 (PNG/JPG)", type=["png", "jpg", "jpeg"])

if logo_file:
    logo_size = st.sidebar.slider("图标大小比例 (%)", 10, 40, 20, help="图标相对于二维码的大小")

# 生成二维码函数
def generate_qr_code(data, fill_color, back_color, box_size, border, error_level, logo=None, logo_size=20):
    """生成二维码"""
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
    
    # 如果有 logo，添加到中心
    if logo:
        logo_img = Image.open(logo)
        
        # 计算 logo 尺寸
        qr_width, qr_height = img.size
        logo_max_size = int(qr_width * logo_size / 100)
        
        # 调整 logo 大小，保持比例
        logo_img.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
        
        # 计算居中位置
        logo_pos = (
            (qr_width - logo_img.size[0]) // 2,
            (qr_height - logo_img.size[1]) // 2
        )
        
        # 粘贴 logo
        img.paste(logo_img, logo_pos)
    
    return img

# 主界面
if content:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 内容预览")
        st.info(f"**类型**: {content_type}\n\n**内容**: {content[:100]}{'...' if len(content) > 100 else ''}")
        
        st.subheader("🎯 生成设置")
        st.write(f"- **前景色**: `{fill_color}`")
        st.write(f"- **背景色**: `{back_color}`")
        st.write(f"- **像素块大小**: {box_size}")
        st.write(f"- **边框宽度**: {border}")
        st.write(f"- **容错级别**: {error_correction}")
        if logo_file:
            st.write(f"- **中心图标**: ✅ 已上传 ({logo_size}%)")
    
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
                logo_size if logo_file else 20
            )
            
            # 显示二维码
            st.image(qr_img, use_container_width=True)
            
            # 转换为字节流用于下载
            buf = io.BytesIO()
            qr_img.save(buf, format='PNG')
            byte_img = buf.getvalue()
            
            # 下载按钮
            st.download_button(
                label="📥 下载二维码",
                data=byte_img,
                file_name="qrcode.png",
                mime="image/png",
                type="primary"
            )
            
        except Exception as e:
            st.error(f"生成失败: {str(e)}")
else:
    st.info("👈 请在左侧输入内容以生成二维码")
    
    # 显示示例
    st.subheader("💡 使用示例")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 文本二维码")
        st.write("输入任意文本，生成可扫描的二维码")
        example_qr1 = generate_qr_code("Hello, World!", "#000000", "#FFFFFF", 10, 4, qrcode.constants.ERROR_CORRECT_M)
        st.image(example_qr1, width=200)
    
    with col2:
        st.markdown("### 网址二维码")
        st.write("输入网址，扫描后直接跳转")
        example_qr2 = generate_qr_code("https://github.com", "#1F77B4", "#FFFFFF", 10, 4, qrcode.constants.ERROR_CORRECT_M)
        st.image(example_qr2, width=200)
    
    with col3:
        st.markdown("### 彩色二维码")
        st.write("自定义颜色，打造个性风格")
        example_qr3 = generate_qr_code("Colorful QR Code", "#FF6B6B", "#FFF3E0", 10, 4, qrcode.constants.ERROR_CORRECT_M)
        st.image(example_qr3, width=200)

# 页脚说明
st.markdown("---")
st.markdown("""
**使用说明：**
1. 在左侧选择内容类型（文本/网址）
2. 输入要生成二维码的内容
3. 自定义颜色、尺寸和容错级别
4. （可选）上传中心图标（建议使用正方形图片）
5. 点击"下载二维码"保存图片

**技术支持**: 基于 `qrcode` 和 `Pillow` 库构建
""")
