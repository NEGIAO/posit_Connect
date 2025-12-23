"""
二维码生成器单元测试
用于验证核心功能是否正常工作
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """测试导入"""
    print("🔍 测试导入...")
    try:
        from app import (
            QRCodeConfig, 
            QRCodeStyle, 
            QRCodeGenerator, 
            VCardBuilder
        )
        print("✅ 所有类导入成功")
        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_config_creation():
    """测试配置创建"""
    print("\n🔍 测试配置创建...")
    try:
        from app import QRCodeConfig
        
        config = QRCodeConfig(
            content="测试内容",
            content_type="文本",
            style_preset="经典黑白"
        )
        
        assert config.content == "测试内容"
        assert config.content_type == "文本"
        assert config.fill_color == "#000000"
        
        print("✅ 配置创建成功")
        return True
    except Exception as e:
        print(f"❌ 配置创建失败: {e}")
        return False


def test_style_management():
    """测试样式管理"""
    print("\n🔍 测试样式管理...")
    try:
        from app import QRCodeStyle
        
        # 测试获取颜色
        fill, back = QRCodeStyle.get_colors("商务蓝")
        assert fill == "#1E3A8A"
        assert back == "#F0F9FF"
        
        # 测试获取描述
        desc = QRCodeStyle.get_description("自然绿")
        assert "清新" in desc
        
        print("✅ 样式管理正常")
        return True
    except Exception as e:
        print(f"❌ 样式管理失败: {e}")
        return False


def test_qr_generation():
    """测试二维码生成"""
    print("\n🔍 测试二维码生成...")
    try:
        from app import QRCodeConfig, QRCodeGenerator
        
        config = QRCodeConfig(
            content="https://github.com",
            content_type="网址",
            style_preset="经典黑白",
            box_size=10,
            border=1,
            dpi=150
        )
        
        generator = QRCodeGenerator(config)
        qr_image = generator.generate()
        
        assert qr_image is not None
        assert qr_image.size[0] > 0
        assert qr_image.size[1] > 0
        
        print(f"✅ 二维码生成成功 (尺寸: {qr_image.size})")
        return True
    except Exception as e:
        print(f"❌ 二维码生成失败: {e}")
        return False


def test_url_encoding():
    """测试URL编码"""
    print("\n🔍 测试URL编码...")
    try:
        from app import QRCodeConfig, QRCodeGenerator
        
        config = QRCodeConfig(
            content="Hello World",
            content_type="文本",
            style_preset="商务蓝",
            fill_color="#1E3A8A",
            box_size=15,
            dpi=300
        )
        
        generator = QRCodeGenerator(config)
        encoded_url = generator.generate_encoded_url()
        
        assert "content=" in encoded_url
        assert "type=" in encoded_url
        assert "style=" in encoded_url
        
        print(f"✅ URL编码成功")
        print(f"   示例: {encoded_url[:80]}...")
        return True
    except Exception as e:
        print(f"❌ URL编码失败: {e}")
        return False


def test_vcard_builder():
    """测试名片构建"""
    print("\n🔍 测试名片构建...")
    try:
        from app import VCardBuilder
        
        vcard_data = {
            'name': '张三',
            'tel': '138-0000-0000',
            'email': 'zhangsan@example.com',
            'company': '科技公司'
        }
        
        content = VCardBuilder.build(vcard_data)
        
        assert '张三' in content
        assert '138-0000-0000' in content
        assert 'zhangsan@example.com' in content
        
        print("✅ 名片构建成功")
        print(f"   内容预览:\n{content}")
        return True
    except Exception as e:
        print(f"❌ 名片构建失败: {e}")
        return False


def test_save_to_buffer():
    """测试保存到缓冲区"""
    print("\n🔍 测试保存到缓冲区...")
    try:
        from app import QRCodeConfig, QRCodeGenerator
        
        config = QRCodeConfig(
            content="Buffer Test",
            dpi=150
        )
        
        generator = QRCodeGenerator(config)
        qr_image = generator.generate()
        byte_data = generator.save_to_buffer(qr_image)
        
        assert len(byte_data) > 0
        assert byte_data[:8] == b'\x89PNG\r\n\x1a\n'  # PNG文件头
        
        print(f"✅ 保存到缓冲区成功 (大小: {len(byte_data)} 字节)")
        return True
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False


def test_batch_mode():
    """测试批量模式配置"""
    print("\n🔍 测试批量模式...")
    try:
        from app import QRCodeConfig
        
        config = QRCodeConfig(
            content="url1\nurl2\nurl3",
            content_type="批量网址",
            batch_mode=True
        )
        
        urls = [url.strip() for url in config.content.split('\n') if url.strip()]
        
        assert len(urls) == 3
        assert config.batch_mode == True
        
        print(f"✅ 批量模式配置成功 ({len(urls)} 个URL)")
        return True
    except Exception as e:
        print(f"❌ 批量模式失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🚀 开始运行测试...")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config_creation,
        test_style_management,
        test_qr_generation,
        test_url_encoding,
        test_vcard_builder,
        test_save_to_buffer,
        test_batch_mode
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("📊 测试结果统计")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！代码运行正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息。")
    
    return passed == total


if __name__ == "__main__":
    # 检查依赖
    print("检查依赖包...")
    try:
        import streamlit
        import qrcode
        from PIL import Image
        print("✅ 所有依赖包已安装\n")
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt\n")
        sys.exit(1)
    
    # 运行测试
    success = run_all_tests()
    sys.exit(0 if success else 1)
