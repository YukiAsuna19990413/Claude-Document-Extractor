# Word 文档提取工具

从受限制的云桌面环境（如 VMware Horizon Client）提取 Word 文档内容。

## 功能

- 📸 自动截图指定区域
- 🔄 自动滚动文档
- 🔍 OCR 识别文字（支持中英文）
- 💾 保存为文本文件
- 🤖 **支持 API OCR（智谱/DeepSeek）** - 识别率更高，支持表格和公式

---

## 安装依赖

```bash
# 1. 安装 Python 库
pip install pyautogui pytesseract pillow mss pyperclip keyboard openai

# 2. 安装 Tesseract OCR（本地识别备用）
brew install tesseract

# 3. 安装中文语言包（如果需要识别中文）
brew install tesseract-lang
```

---

## 使用方法

### 方式一：使用 API（推荐，识别率高）

1. **配置 API**
   ```bash
   python doc_extractor.py
   ```
   选择 `6. API 配置`

2. **选择 API 提供商**
   - `1. 智谱 AI (GLM)` - 推荐，中文识别优秀
   - `2. DeepSeek` - 性价比高
   - `3. 自定义` - 其他兼容 OpenAI 格式的 API

3. **输入 API Key**
   - 智谱 AI: https://open.bigmodel.cn/usercenter/apikeys
   - DeepSeek: https://platform.deepseek.com/api_keys

4. **正常使用菜单 3 或 5 进行截图和识别**

### 方式二：使用本地 Tesseract

直接使用菜单 3 或 5，会自动使用本地 OCR（需要安装 Tesseract）

---

## 操作流程

```bash
python doc_extractor.py
```

| 选项 | 功能 |
|------|------|
| 1 | 选择截图区域（首次使用） |
| 2 | 使用上次保存的区域 |
| 3 | 开始截图（只截图，不识别） |
| 4 | OCR 识别（需要先截图） |
| 5 | 全自动（截图+OCR） |
| 6 | API 配置（智谱/DeepSeek） |
| 0 | 退出 |

### 使用流程

1. **首次使用**：选择菜单 `1. 选择截图区域`
2. **配置 API**：选择菜单 `6. API 配置`（可选，但推荐）
3. **开始提取**：选择菜单 `5. 全自动`
4. **等待完成**：程序会自动滚动并截图
5. **获取结果**：
   - 截图：`screenshots_YYYYMMDD_HHMMSS/`
   - 文本：`extracted_text_YYYYMMDD_HHMMSS.txt`

---

## API OCR vs 本地 OCR

| 对比项 | 本地 Tesseract | API (智谱/DeepSeek) |
|--------|----------------|---------------------|
| 识别率 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 表格处理 | ❌ 差 | ✅ 很好 |
| 公式识别 | ❌ 无 | ✅ 支持 |
| 格式保留 | ❌ 纯文本 | ✅ Markdown |
| 速度 | 快 | 慢（网络请求） |
| 成本 | 免费 | 按量付费 |

### API 费用参考（2025年）

| 服务 | 价格 | 说明 |
|------|------|------|
| 智谱 GLM-4V | ¥12/百万 tokens | 视觉输入按 tokens 计费 |
| DeepSeek | ¥1/百万 tokens | 极具性价比 |

几十页文档的成本大约 **几毛钱**。

---

## 可视化区域选择（辅助工具）

```bash
python area_selector.py
```

弹出半透明窗口，用鼠标拖动选择区域，坐标自动保存到 `area_config.txt`

---

## 注意事项

- ⚠️ 使用前请确保符合公司 IT 政策
- ⚠️ 避免处理敏感或机密信息
- ⚠️ API 方式需要网络连接
- ⚠️ 滚动速度取决于云桌面响应速度

---

## 配置文件

- `area_config.txt` - 截图区域配置
- `api_config.json` - API 配置（包含 API Key，请勿泄露）