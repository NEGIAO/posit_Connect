# 测试HTML生成功能
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

# 测试
if __name__ == "__main__":
    html = generate_html_card(
        name="张三",
        title="高级软件工程师",
        company="科技有限公司",
        email="zhangsan@example.com",
        phone="138-0000-0000",
        wechat="zhangsan_wx",
        location="中国·北京",
        website="https://example.com",
        github="https://github.com/zhangsan",
        bio="5年软件开发经验，专注于Python和Web开发，热爱开源技术。",
        skills="Python, JavaScript, React\nDocker, AWS, 数据分析"
    )
    
    # 保存测试HTML
    with open("test_card.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("✅ HTML生成成功！已保存到 test_card.html")
    print("可以在浏览器中打开查看效果")
