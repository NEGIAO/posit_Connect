#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能名片URL编码功能测试脚本
测试数据编码、解码和URL生成
"""

import json
import base64

def encode_card_data(name, title="", company="", email="", phone="", 
                     wechat="", location="", website="", github="", 
                     bio="", skills=""):
    """
    将名片数据编码为Base64
    
    Args:
        name: 姓名
        title: 职位
        company: 公司
        email: 邮箱
        phone: 电话
        wechat: 微信
        location: 所在地
        website: 网站
        github: GitHub
        bio: 个人简介
        skills: 技能（逗号分隔）
    
    Returns:
        tuple: (encoded_data, card_url, card_data_dict)
    """
    # 构建数据字典
    card_data = {}
    if name: card_data['name'] = name
    if title: card_data['title'] = title
    if company: card_data['company'] = company
    if email: card_data['email'] = email
    if phone: card_data['phone'] = phone
    if wechat: card_data['wechat'] = wechat
    if location: card_data['location'] = location
    if website: card_data['website'] = website
    if github: card_data['github'] = github
    if bio: card_data['bio'] = bio
    
    # 处理技能
    if skills:
        skills_list = [s.strip() for s in skills.replace(',', '\n').split('\n') if s.strip()]
        if skills_list:
            card_data['skills'] = skills_list
    
    # 转为JSON
    json_str = json.dumps(card_data, ensure_ascii=False, indent=2)
    
    # Base64编码
    encoded_data = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    # 生成完整URL（需要替换为实际模板URL）
    template_url = "https://你的用户名.github.io/card-template/card_template.html"
    card_url = f"{template_url}?data={encoded_data}"
    
    return encoded_data, card_url, card_data


def decode_card_data(encoded_data):
    """
    解码Base64数据
    
    Args:
        encoded_data: Base64编码的字符串
    
    Returns:
        dict: 解码后的数据字典
    """
    json_str = base64.b64decode(encoded_data).decode('utf-8')
    return json.loads(json_str)


def test_basic_info():
    """测试基本信息编码"""
    print("=" * 60)
    print("测试1：基本信息")
    print("=" * 60)
    
    encoded, url, data = encode_card_data(
        name="张三",
        title="高级软件工程师",
        company="某科技有限公司",
        email="zhangsan@example.com",
        phone="138-8888-8888"
    )
    
    print(f"\n原始数据：")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    print(f"\nBase64编码：")
    print(f"  长度: {len(encoded)} 字符")
    print(f"  内容: {encoded[:50]}...")
    
    print(f"\n完整URL：")
    print(f"  长度: {len(url)} 字符")
    print(f"  内容: {url}")
    
    # 验证解码
    decoded = decode_card_data(encoded)
    print(f"\n解码验证：")
    print(f"  成功: {decoded == data}")
    
    return url


def test_full_info():
    """测试完整信息编码"""
    print("\n" + "=" * 60)
    print("测试2：完整信息（包含简介和技能）")
    print("=" * 60)
    
    encoded, url, data = encode_card_data(
        name="李明",
        title="高级数据科学家",
        company="AI创新科技公司",
        email="liming@example.com",
        phone="139-9999-9999",
        wechat="liming_data",
        location="中国·深圳",
        website="https://liming.dev",
        github="https://github.com/liming",
        bio="5年机器学习经验，专注于计算机视觉和NLP领域，热衷于开源项目，曾参与多个大型AI项目的开发与优化。",
        skills="Python, TensorFlow, PyTorch, 数据可视化, SQL, Docker, Kubernetes, AWS"
    )
    
    print(f"\n原始数据：")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    print(f"\nBase64编码：")
    print(f"  长度: {len(encoded)} 字符")
    
    print(f"\n完整URL：")
    print(f"  长度: {len(url)} 字符")
    
    # URL长度检查
    if len(url) > 2000:
        print(f"  ⚠️ 警告: URL超过2000字符，可能在某些扫码器中出现问题")
    else:
        print(f"  ✅ URL长度正常")
    
    print(f"\nURL内容：")
    print(url)
    
    return url


def test_chinese_encoding():
    """测试中文编码"""
    print("\n" + "=" * 60)
    print("测试3：中文字符编码")
    print("=" * 60)
    
    encoded, url, data = encode_card_data(
        name="王小明",
        bio="我是一名全栈工程师，擅长前端和后端开发，熟悉Vue、React、Node.js等技术栈。",
        skills="前端开发, 后端开发, 全栈工程师"
    )
    
    print(f"\n原始数据：")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    print(f"\nBase64编码（中文）：")
    print(f"  长度: {len(encoded)} 字符")
    
    # 验证解码
    decoded = decode_card_data(encoded)
    print(f"\n解码验证：")
    print(f"  姓名匹配: {decoded['name'] == '王小明'}")
    print(f"  简介匹配: {decoded['bio'] == data['bio']}")
    print(f"  ✅ 中文编码/解码成功")


def test_url_length_estimation():
    """测试不同数据量的URL长度"""
    print("\n" + "=" * 60)
    print("测试4：URL长度估算")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "最小数据",
            "data": {"name": "张三", "email": "test@example.com"}
        },
        {
            "name": "中等数据",
            "data": {
                "name": "李四",
                "title": "工程师",
                "company": "科技公司",
                "email": "test@example.com",
                "phone": "138-0000-0000"
            }
        },
        {
            "name": "大量数据",
            "data": {
                "name": "王五",
                "title": "高级架构师",
                "company": "某大型互联网公司",
                "email": "test@example.com",
                "phone": "138-0000-0000",
                "wechat": "wangwu_tech",
                "location": "中国·北京·海淀区",
                "website": "https://wangwu.dev",
                "github": "https://github.com/wangwu",
                "bio": "10年软件开发经验，精通多种编程语言和框架，曾主导多个千万级用户产品的架构设计与开发。" * 2,  # 重复2次模拟长文本
                "skills": ["Python", "Java", "Go", "JavaScript", "React", "Vue", "Node.js", 
                          "Docker", "Kubernetes", "AWS", "微服务", "分布式系统"]
            }
        }
    ]
    
    template_url = "https://username.github.io/card/card_template.html"
    
    print(f"\n模板URL长度: {len(template_url)} 字符")
    print("-" * 60)
    
    for case in test_cases:
        json_str = json.dumps(case['data'], ensure_ascii=False)
        encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        url = f"{template_url}?data={encoded}"
        
        print(f"\n{case['name']}:")
        print(f"  JSON长度: {len(json_str)} 字符")
        print(f"  编码后: {len(encoded)} 字符")
        print(f"  完整URL: {len(url)} 字符")
        
        if len(url) > 2000:
            print(f"  ⚠️ 超出推荐长度")
        else:
            print(f"  ✅ 长度正常")


def generate_test_urls():
    """生成测试用的QR码URL"""
    print("\n" + "=" * 60)
    print("测试5：生成测试URL（可直接扫码）")
    print("=" * 60)
    
    test_users = [
        {
            "name": "张三",
            "title": "产品经理",
            "email": "zhangsan@example.com",
            "phone": "138-0001-0001",
            "skills": "产品设计, 用户研究, 数据分析"
        },
        {
            "name": "李四",
            "title": "UI设计师",
            "email": "lisi@example.com",
            "phone": "138-0002-0002",
            "bio": "5年UI/UX设计经验，擅长移动端和Web端界面设计",
            "skills": "Figma, Sketch, Adobe XD, 原型设计"
        }
    ]
    
    print("\n将以下URL粘贴到应用中生成QR码：\n")
    
    for i, user in enumerate(test_users, 1):
        _, url, _ = encode_card_data(**user)
        print(f"用户{i}: {user['name']}")
        print(f"  {url}")
        print()


if __name__ == "__main__":
    print("\n🧪 智能名片URL编码功能测试\n")
    
    # 运行所有测试
    test_basic_info()
    test_full_info()
    test_chinese_encoding()
    test_url_length_estimation()
    generate_test_urls()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)
    print("\n💡 提示：")
    print("1. URL长度建议控制在2000字符以内")
    print("2. 中文会增加编码长度（UTF-8）")
    print("3. 技能标签建议6个以内")
    print("4. 个人简介建议200字以内")
    print("5. 记得将模板URL替换为实际部署的地址")
    print("\n🚀 准备部署模板文件到GitHub Pages或其他平台！\n")
