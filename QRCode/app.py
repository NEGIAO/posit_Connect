import streamlit as st
import qrcode
from PIL import Image, ImageDraw
import io
import base64
import os
import json

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
content_type = st.sidebar.radio("内容类型", ["文本", "网址", "联系方式/名片", "批量网址", "HTML名片/简历", "智能名片(URL编码)"])

if content_type == "文本":
    content = st.sidebar.text_area("输入文本内容", height=100, placeholder="请输入要生成二维码的文本...")
    batch_mode = False
elif content_type == "联系方式/名片":
    st.sidebar.markdown("**📇 填写联系信息**")
    vcard_name = st.sidebar.text_input("姓名", placeholder="张三")
    vcard_tel = st.sidebar.text_input("电话", placeholder="138-0000-0000")
    vcard_email = st.sidebar.text_input("邮箱", placeholder="example@email.com")
    vcard_wechat = st.sidebar.text_input("微信号", placeholder="WeChat ID")
    vcard_qq = st.sidebar.text_input("QQ", placeholder="12345678")
    vcard_alipay = st.sidebar.text_input("支付宝", placeholder="Alipay账号")
    vcard_address = st.sidebar.text_input("地址", placeholder="公司/家庭地址")
    vcard_company = st.sidebar.text_input("公司/组织", placeholder="公司名称")
    vcard_title = st.sidebar.text_input("职位", placeholder="职位名称")
    vcard_website = st.sidebar.text_input("网站", placeholder="https://example.com")
    vcard_note = st.sidebar.text_area("备注", height=70, placeholder="其他信息")
    
    # 组合信息
    contact_info = []
    if vcard_name: contact_info.append(f"姓名: {vcard_name}")
    if vcard_title: contact_info.append(f"职位: {vcard_title}")
    if vcard_company: contact_info.append(f"公司: {vcard_company}")
    if vcard_tel: contact_info.append(f"电话: {vcard_tel}")
    if vcard_email: contact_info.append(f"邮箱: {vcard_email}")
    if vcard_wechat: contact_info.append(f"微信: {vcard_wechat}")
    if vcard_qq: contact_info.append(f"QQ: {vcard_qq}")
    if vcard_alipay: contact_info.append(f"支付宝: {vcard_alipay}")
    if vcard_website: contact_info.append(f"网站: {vcard_website}")
    if vcard_address: contact_info.append(f"地址: {vcard_address}")
    if vcard_note: contact_info.append(f"备注: {vcard_note}")
    
    content = "\n".join(contact_info) if contact_info else ""
    batch_mode = False
elif content_type == "批量网址":
    content = st.sidebar.text_area(
        "输入多个网址（每行一个）", 
        height=150, 
        placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com"
    )
    batch_mode = True
elif content_type == "智能名片(URL编码)":
    st.sidebar.markdown("**⚡ 智能名片（无需上传）**")
    st.sidebar.info("💡 数据编码到URL中，无需任何第三方服务！")
    smart_name = st.sidebar.text_input("👤 姓名", placeholder="张三")
    smart_title = st.sidebar.text_input("💼 职位", placeholder="高级工程师")
    smart_company = st.sidebar.text_input("🏢 公司", placeholder="科技有限公司")
    smart_email = st.sidebar.text_input("📧 邮箱", placeholder="example@email.com")
    smart_phone = st.sidebar.text_input("📱 电话", placeholder="138-0000-0000")
    smart_wechat = st.sidebar.text_input("💬 微信", placeholder="WeChat ID")
    smart_location = st.sidebar.text_input("📍 所在地", placeholder="中国·北京")
    smart_website = st.sidebar.text_input("🌐 网站", placeholder="https://example.com")
    smart_github = st.sidebar.text_input("💻 GitHub", placeholder="https://github.com/username")
    smart_bio = st.sidebar.text_area("📝 简介", height=80, placeholder="简要介绍...")
    smart_skills = st.sidebar.text_input("🎯 技能", placeholder="Python, JavaScript, React")
    content = ""  # 智能名片模式
    batch_mode = False
elif content_type == "HTML名片/简历":
    st.sidebar.markdown("**📄 填写个人信息（生成HTML页面）**")
    html_name = st.sidebar.text_input("👤 姓名", placeholder="张三")
    html_title = st.sidebar.text_input("💼 职位/头衔", placeholder="高级软件工程师")
    html_company = st.sidebar.text_input("🏢 公司/组织", placeholder="科技有限公司")
    html_email = st.sidebar.text_input("📧 邮箱", placeholder="example@email.com")
    html_phone = st.sidebar.text_input("📱 电话", placeholder="138-0000-0000")
    html_wechat = st.sidebar.text_input("💬 微信", placeholder="WeChat ID")
    html_location = st.sidebar.text_input("📍 所在地", placeholder="中国·北京")
    html_website = st.sidebar.text_input("🌐 个人网站", placeholder="https://example.com")
    html_github = st.sidebar.text_input("💻 GitHub", placeholder="https://github.com/username")
    html_bio = st.sidebar.text_area("📝 个人简介", height=100, placeholder="简要介绍自己的专业背景和技能...")
    html_skills = st.sidebar.text_area("🎯 技能标签", height=70, placeholder="Python, JavaScript, 数据分析\n（每行一个或用逗号分隔）")
    content = ""  # HTML模式不需要直接内容
    batch_mode = False
else:
    content = st.sidebar.text_input("输入网址", placeholder="https://example.com")
    batch_mode = False

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
    index=3,
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
    default_logo_path = "icon.jpg"
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

# HTML名片生成函数
def generate_html_card(name, title, company, email, phone, wechat, location, website, github, bio, skills):
    """生成专业HTML名片/简历页面"""
    # 处理技能标签
    skills_list = []
    if skills:
        # 支持逗号或换行分隔
        for line in skills.replace(',', '\n').split('\n'):
            skill = line.strip()
            if skill:
                skills_list.append(skill)
    
    skills_html = ''.join([f'<span class="skill-tag">{skill}</span>' for skill in skills_list])
    
    # 生成HTML
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name or "个人名片"} - 数字名片</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", 
                         "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .card {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 100%;
            overflow: hidden;
            animation: fadeIn 0.6s ease-out;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .name {{
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .title {{
            font-size: 16px;
            opacity: 0.95;
            margin-bottom: 4px;
        }}
        .company {{
            font-size: 14px;
            opacity: 0.85;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 14px;
            color: #667eea;
            font-weight: bold;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .info-item {{
            display: flex;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
            gap: 12px;
        }}
        .info-item:last-child {{
            border-bottom: none;
        }}
        .icon {{
            font-size: 18px;
            width: 24px;
            text-align: center;
        }}
        .info-text {{
            flex: 1;
            color: #333;
            font-size: 14px;
            word-break: break-all;
        }}
        .info-link {{
            color: #667eea;
            text-decoration: none;
        }}
        .info-link:hover {{
            text-decoration: underline;
        }}
        .bio {{
            color: #555;
            line-height: 1.6;
            font-size: 14px;
        }}
        .skills {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}
        .skill-tag {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="name">{name or "未命名"}</div>
            {f'<div class="title">{title}</div>' if title else ''}
            {f'<div class="company">{company}</div>' if company else ''}
        </div>
        
        <div class="content">
            {f'''<div class="section">
                <div class="section-title">📝 关于我</div>
                <div class="bio">{bio}</div>
            </div>''' if bio else ''}
            
            <div class="section">
                <div class="section-title">📞 联系方式</div>
                {f'<div class="info-item"><span class="icon">📧</span><a href="mailto:{email}" class="info-text info-link">{email}</a></div>' if email else ''}
                {f'<div class="info-item"><span class="icon">📱</span><span class="info-text">{phone}</span></div>' if phone else ''}
                {f'<div class="info-item"><span class="icon">💬</span><span class="info-text">微信: {wechat}</span></div>' if wechat else ''}
                {f'<div class="info-item"><span class="icon">📍</span><span class="info-text">{location}</span></div>' if location else ''}
            </div>
            
            {f'''<div class="section">
                <div class="section-title">🌐 在线主页</div>
                {f'<div class="info-item"><span class="icon">🌐</span><a href="{website}" target="_blank" class="info-text info-link">{website}</a></div>' if website else ''}
                {f'<div class="info-item"><span class="icon">💻</span><a href="{github}" target="_blank" class="info-text info-link">{github}</a></div>' if github else ''}
            </div>''' if (website or github) else ''}
            
            {f'''<div class="section">
                <div class="section-title">🎯 技能专长</div>
                <div class="skills">
                    {skills_html}
                </div>
            </div>''' if skills_html else ''}
        </div>
        
        <div class="footer">
            通过二维码访问 • 由 NEGIAO 二维码生成器创建
        </div>
    </div>
</body>
</html>'''
    
    return html_template

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
    if use_default and os.path.exists("icon.jpg"):
        logo_to_use = "icon.jpg"
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
if content_type == "智能名片(URL编码)":
    # 智能名片模式（URL参数编码）
    st.subheader("⚡ 智能名片生成器（URL编码方案）")
    
    st.info("""
    **🎯 工作原理：**
    - 您的信息将被编码到URL参数中
    - 无需上传文件，无需第三方服务
    - 扫码即可访问，数据永不过期
    - 完全免费，零门槛使用
    """)
    
    if smart_name or smart_email or smart_phone:
        # 准备数据
        card_data = {}
        if smart_name: card_data['name'] = smart_name
        if smart_title: card_data['title'] = smart_title
        if smart_company: card_data['company'] = smart_company
        if smart_email: card_data['email'] = smart_email
        if smart_phone: card_data['phone'] = smart_phone
        if smart_wechat: card_data['wechat'] = smart_wechat
        if smart_location: card_data['location'] = smart_location
        if smart_website: card_data['website'] = smart_website
        if smart_github: card_data['github'] = smart_github
        if smart_bio: card_data['bio'] = smart_bio
        
        # 处理技能
        if smart_skills:
            skills_list = [s.strip() for s in smart_skills.replace(',', '\n').split('\n') if s.strip()]
            if skills_list:
                card_data['skills'] = skills_list
        
        # 编码数据
        json_str = json.dumps(card_data, ensure_ascii=False)
        encoded_data = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        
        # 生成URL（这里需要你上传card_template.html到某个地方）
        # 方案1：上传到GitHub Gist作为模板
        # 方案2：部署到GitHub Pages
        # 方案3：使用任何静态托管服务
        
        # 临时使用本地模板URL（需要替换为实际URL）
        template_url = "https://你的GitHub用户名.github.io/card_template.html"
        card_url = f"{template_url}?data={encoded_data}"
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 生成的URL")
            
            # 显示URL长度信息
            url_length = len(card_url)
            if url_length > 2000:
                st.warning(f"⚠️ URL长度: {url_length} 字符（可能超出某些扫码器限制）")
            else:
                st.success(f"✅ URL长度: {url_length} 字符（正常范围）")
            
            # 显示URL
            st.code(card_url, language="text")
            
            # 提供复制按钮
            st.markdown(f"**🔗 完整链接：**")
            st.text_input("复制此链接", card_url, label_visibility="collapsed")
            
            st.markdown("---")
            st.markdown("**📤 部署模板说明：**")
            st.warning("""
⚠️ **首次使用需要部署模板**

1. 上传 `card_template.html` 到：
   - GitHub Pages（推荐）
   - GitHub Gist
   - Netlify Drop
   - 任何静态托管

2. 获取模板URL（如：https://你的用户名.github.io/card_template.html）

3. 修改上方的 `template_url` 变量

**提示**：模板文件在应用目录下已生成，您可以下载并上传
            """)
            
        with col2:
            st.subheader("🖼️ 二维码预览")
            
            # 配置信息
            st.markdown("**生成设置：**")
            st.write(f"- **样式**: {style_choice}")
            st.write(f"- **DPI**: {output_dpi}")
            st.write(f"- **容错级别**: {error_correction}")
            
            st.markdown("---")
            
            try:
                # 生成QR码
                qr_img = generate_qr_code(
                    card_url,
                    fill_color,
                    back_color,
                    box_size,
                    border,
                    error_map[error_correction],
                    logo_file if logo_file else None,
                    logo_size,
                    use_default_logo
                )
                
                st.image(qr_img, use_container_width=True)
                
                # 下载按钮
                buffer = io.BytesIO()
                qr_img.save(buffer, format='PNG', dpi=(output_dpi, output_dpi))
                buffer.seek(0)
                
                st.download_button(
                    label=f"⬇️ 下载二维码 ({output_dpi} DPI)",
                    data=buffer,
                    file_name=f"smartcard_{smart_name or 'card'}_{output_dpi}dpi.png",
                    mime="image/png",
                    help=f"下载 {output_dpi} DPI 高清二维码"
                )
                
                st.success("✅ 二维码生成成功！")
                
            except Exception as e:
                st.error(f"❌ 生成失败：{str(e)}")
        
        # 数据预览
        st.markdown("---")
        with st.expander("👁️ 查看编码数据（JSON格式）", expanded=False):
            st.json(card_data)
            st.caption(f"Base64编码后长度: {len(encoded_data)} 字符")
    else:
        st.info("👈 请在左侧填写至少姓名、邮箱或电话信息")

elif content_type == "HTML名片/简历":
    # HTML名片模式
    st.subheader("📄 HTML名片/简历生成器")
    
    if html_name or html_email or html_phone:
        # 生成HTML
        html_content = generate_html_card(
            html_name, html_title, html_company, html_email, html_phone,
            html_wechat, html_location, html_website, html_github, html_bio, html_skills
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📥 下载HTML文件")
            
            # 提供HTML下载
            html_bytes = html_content.encode('utf-8')
            filename = f"{html_name or 'card'}_card.html"
            
            st.download_button(
                label="⬇️ 下载 HTML 名片",
                data=html_bytes,
                file_name=filename,
                mime="text/html",
                help="下载生成的HTML名片文件"
            )
            
            st.markdown("---")
            st.markdown("**📤 发布步骤：**")
            st.info("""
1. **下载HTML文件** ⬇️
2. **选择托管平台**（任选其一）：
   - 🌐 [GitHub Gist](https://gist.github.com) - 免费，创建Gist后点击Raw获取链接
   - 📄 [GitHub Pages](https://pages.github.com) - 免费，支持自定义域名
   - ☁️ [Netlify Drop](https://app.netlify.com/drop) - 拖拽即可部署
   - 🚀 [Vercel](https://vercel.com) - 专业托管平台
3. **上传HTML文件**，获取访问链接
4. **在右侧输入该链接**，生成QR码
            """)
            
            with st.expander("💡 推荐方案：GitHub Gist（最简单）"):
                st.markdown("""
**步骤详解：**
1. 访问 [gist.github.com](https://gist.github.com)
2. 粘贴下载的HTML内容（或上传文件）
3. 文件名改为 `index.html`
4. 点击 "Create public gist"
5. 点击右上角 "Raw" 按钮
6. 复制浏览器地址栏的链接
7. 将链接粘贴到右侧"网址输入"框
8. 生成二维码即可！

**优点**：无需注册，永久免费，秒级发布
                """)
        
        with col2:
            st.subheader("🔗 生成二维码")
            
            html_url = st.text_input(
                "输入HTML页面链接",
                placeholder="https://gist.githubusercontent.com/...",
                help="上传HTML到托管平台后，将获取的链接粘贴到这里"
            )
            
            if html_url:
                st.markdown("**生成设置：**")
                st.write(f"- **样式**: {style_choice}")
                st.write(f"- **DPI**: {output_dpi}")
                st.write(f"- **容错级别**: {error_correction}")
                
                st.markdown("---")
                st.subheader("🖼️ 二维码预览")
                
                try:
                    qr_img = generate_qr_code(
                        html_url,
                        fill_color,
                        back_color,
                        box_size,
                        border,
                        error_map[error_correction],
                        logo_file if logo_file else None,
                        logo_size,
                        use_default_logo
                    )
                    
                    st.image(qr_img, use_container_width=True)
                    
                    # 转换为高DPI图片并提供下载
                    buffer = io.BytesIO()
                    qr_img.save(buffer, format='PNG', dpi=(output_dpi, output_dpi))
                    buffer.seek(0)
                    
                    st.download_button(
                        label=f"⬇️ 下载二维码 ({output_dpi} DPI)",
                        data=buffer,
                        file_name=f"qrcode_{html_name or 'card'}_{output_dpi}dpi.png",
                        mime="image/png",
                        help=f"下载 {output_dpi} DPI 高清二维码图片"
                    )
                    
                    st.success(f"✅ 二维码生成成功！扫码即可访问您的HTML名片")
                    
                except Exception as e:
                    st.error(f"❌ 生成失败：{str(e)}")
            else:
                st.info("👆 请先上传HTML到托管平台，然后在上方输入链接")
        
        # 实时预览HTML效果
        st.markdown("---")
        with st.expander("👁️ 预览HTML效果", expanded=True):
            st.components.v1.html(html_content, height=600, scrolling=True)
    else:
        st.info("👈 请在左侧填写至少姓名、邮箱或电话信息")

elif content:
    # 批量模式处理
    if batch_mode:
        urls = [url.strip() for url in content.split('\n') if url.strip()]
        
        if urls:
            st.subheader(f"📦 批量生成 - 共 {len(urls)} 个二维码")
            
            # 生成设置信息
            with st.expander("🎯 生成设置", expanded=False):
                st.write(f"- **样式**: {style_choice}")
                st.write(f"- **前景色**: `{fill_color}` | **背景色**: `{back_color}`")
                st.write(f"- **像素块**: {box_size} | **边框**: {border} | **DPI**: {output_dpi}")
                st.write(f"- **容错级别**: {error_correction}")
                if logo_option == "使用默认图标":
                    st.write(f"- **中心图标**: ✅ 默认图标 ({logo_size}%)")
                elif logo_file:
                    st.write(f"- **中心图标**: ✅ 自定义图标 ({logo_size}%)")
            
            # 生成所有二维码
            qr_images = []
            for idx, url in enumerate(urls, 1):
                try:
                    qr_img = generate_qr_code(
                        url,
                        fill_color,
                        back_color,
                        box_size,
                        border,
                        error_map[error_correction],
                        logo_file if logo_file else None,
                        logo_size,
                        use_default_logo
                    )
                    qr_images.append((url, qr_img))
                except Exception as e:
                    st.error(f"❌ 第 {idx} 个网址生成失败: {url}\n错误: {str(e)}")
            
            # 网格展示
            cols_per_row = 3
            for i in range(0, len(qr_images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, (url, qr_img) in enumerate(qr_images[i:i+cols_per_row]):
                    with cols[j]:
                        st.image(qr_img, use_container_width=True)
                        st.caption(f"🔗 {url[:40]}{'...' if len(url) > 40 else ''}")
                        
                        # 单个下载按钮
                        buf = io.BytesIO()
                        qr_img.save(buf, format='PNG', dpi=(output_dpi, output_dpi))
                        st.download_button(
                            label="📥 下载",
                            data=buf.getvalue(),
                            file_name=f"qrcode_{i+j+1}.png",
                            mime="image/png",
                            key=f"download_{i+j}"
                        )
            
            st.success(f"✅ 成功生成 {len(qr_images)} 个二维码")
        else:
            st.warning("请输入至少一个网址")
    
    # 单个模式处理
    else:
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
