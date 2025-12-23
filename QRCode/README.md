# 🚀 快速开始指南

## 本地运行

### 1. 安装依赖
```bash
cd posit_Connect/QRCode
pip install -r requirements.txt
```

### 2. 启动应用
```bash
streamlit run app.py
```

### 3. 访问应用
浏览器自动打开：http://localhost:8501

## 部署到 Posit Connect Cloud

### 1. 准备文件
确保以下文件存在：
- `app.py`
- `requirements.txt`
- `icon.jpg`（可选，默认图标）

### 2. 登录 Posit Connect
访问：https://connect.posit.cloud/

### 3. 创建新应用
1. 点击 "New Content"
2. 选择 "Streamlit"
3. 上传 `app.py` 和 `requirements.txt`
4. 上传 `icon.jpg`（如需默认图标功能）

### 4. 配置部署
- Python版本：3.11+
- 依赖安装：自动从 requirements.txt 读取

### 5. 发布
点击 "Deploy" 按钮，等待部署完成

## 功能测试清单

### ✅ 基础功能
- [ ] 文本内容生成QR码
- [ ] 网址生成QR码
- [ ] 7种预设样式切换
- [ ] 自定义颜色选择
- [ ] DPI选择（72/150/300/600）

### ✅ 图标功能
- [ ] 无图标模式
- [ ] 默认图标模式（需icon.jpg）
- [ ] 上传自定义图标
- [ ] 图标大小调整

### ✅ 高级功能
- [ ] 联系方式/名片生成
- [ ] 批量网址生成（测试3个以上URL）
- [ ] **HTML名片生成** 🆕
  - [ ] 填写信息
  - [ ] 下载HTML
  - [ ] 预览HTML效果
  - [ ] 上传到GitHub Gist
  - [ ] 输入URL生成QR码

## 常见问题

### Q1: icon.jpg找不到怎么办？
**A**: 上传任意图片并重命名为 `icon.jpg`，或使用"上传自定义图标"功能

### Q2: HTML名片预览显示空白？
**A**: 检查是否至少填写了姓名、邮箱或电话字段

### Q3: GitHub Gist链接无法访问？
**A**: 确保点击的是"Raw"按钮获取的链接，而不是Gist主页链接

### Q4: 二维码无法识别？
**A**: 检查：
- 容错级别是否足够高（添加图标需H级）
- 图标大小是否超过30%
- DPI是否太低（建议300+）

## 快速演示：生成HTML名片QR码

### Step 1: 填写信息
```
姓名：张三
职位：高级工程师
邮箱：zhangsan@example.com
电话：138-0000-0000
技能：Python, JavaScript, Docker
```

### Step 2: 下载并上传
1. 点击"下载 HTML 名片"
2. 访问 https://gist.github.com
3. 新建Gist，粘贴HTML内容
4. 文件名改为 `index.html`
5. 点击"Create public gist"
6. 点击"Raw"按钮
7. 复制地址栏URL

### Step 3: 生成QR码
1. 将URL粘贴到"输入HTML页面链接"
2. 预览QR码
3. 点击"下载二维码"
4. 完成！✨

## 性能优化建议

- **批量生成**：建议单次不超过20个URL，避免浏览器卡顿
- **图标大小**：推荐20%，兼顾美观和识别率
- **DPI选择**：屏幕用72，打印用300，海报用600
- **容错级别**：有图标必选H，纯色必选H，其他M即可

## 更新日志

**v2.0 (2025-12-23)**
- 🆕 新增HTML名片/简历生成功能
- 🆕 支持11个字段的完整个人信息
- 🆕 专业响应式HTML模板
- 🆕 内嵌预览和托管平台指引
- 🐛 修复批量生成边距问题

**v1.3 (之前)**
- 批量网址生成
- 联系方式/名片模式
- 默认图标功能
- DPI可选

## 技术支持

遇到问题？欢迎访问：
- 👤 作者主页：https://negiao-pages.share.connect.posit.cloud/
- 📧 反馈邮箱：（待补充）
- 💬 GitHub Issues：（待补充）

---

**享受创作！🎉**
