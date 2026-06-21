# 文档提取工具

从受限制的云桌面环境（如 VMware Horizon Client）提取 Word 文档内容。

## 功能

- 📸 自动截图指定区域
- 🔄 自动滚动文档
- 🔍 OCR 识别文字（支持中英文）
- 💾 保存为文本文件
- 🤖 支持 API OCR（智谱/DeepSeek）- 识别率更高，支持表格和公式
- 🖥️ 图形界面操作

---

## 快速开始（GUI 版本）

### 运行 GUI 版本

```bash
python doc_extractor_gui.py
```

### 打包成 .app 应用

```bash
# 1. 安装 py2app
pip install py2app

# 2. 打包
python setup.py py2app

# 3. 完成！app 在 dist/ 目录下
open dist/
```

将 `文档提取工具.app` 拖到 Applications 文件夹，像普通 Mac 应用一样使用！

---

## 使用说明

### 首次使用

1. **启动应用**
2. **点击「选择区域」**
   - 用鼠标拖动框选你的文档内容区域
   - 松开鼠标完成选择
3. **配置 API（推荐）**
   - 点击「配置 API」
   - 选择提供商（智谱/DeepSeek）
   - 输入 API Key
4. **点击「开始提取」**
   - 5秒倒计时，确保云桌面窗口已激活
   - 自动滚动并截图
   - OCR 识别并显示结果

### 获取 API Key

| 服务 | 获取地址 | 价格 |
|------|----------|------|
| 智谱 AI GLM | https://open.bigmodel.cn | ¥12/百万 tokens |
| DeepSeek | https://platform.deepseek.com | ¥1/百万 tokens |

---

## 界面说明

| 区域 | 功能 |
|------|------|
| 📍 截图区域 | 选择和测试截图区域 |
| 🤖 OCR 设置 | 配置 API 或使用本地 OCR |
| 🚀 操作 | 设置滚动间隔，开始/停止提取 |
| 📊 状态 | 显示当前进度和状态 |
| 📸 预览 | 实时显示截图预览 |
| 📄 结果 | 显示识别结果，可复制或保存 |
| 📝 日志 | 查看操作日志 |

---

## 命令行版本

如果需要命令行版本：

```bash
python doc_extractor.py
```

---

## 安装依赖

```bash
pip install pyautogui pytesseract pillow mss pyperclip keyboard openai
brew install tesseract
```

---

## 注意事项

- ⚠️ 使用前请确保符合公司 IT 政策
- ⚠️ 避免处理敏感或机密信息
- ⚠️ API 方式需要网络连接
- ⚠️ .app 应用首次运行可能需要允许权限

---

## 配置文件

- `area_config.txt` - 截图区域配置
- `api_config.json` - API 配置（包含 API Key，请勿泄露）