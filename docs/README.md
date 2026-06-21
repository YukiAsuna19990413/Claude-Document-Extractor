# 文档提取工具详细文档

## 项目概述

文档提取工具是一个用于从受限制的云桌面环境（如 VMware Horizon Client）自动提取文档内容的现代化工具。它支持自动截图、OCR 识别、文档滚动等功能，并提供图形界面和命令行两种使用方式。

## 架构设计

### 模块结构

```
src/
├── core/                   # 核心功能模块
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── capture.py         # 屏幕捕获
│   ├── ocr.py            # OCR 处理
│   ├── scrolling.py      # 文档滚动
│   └── doc_extractor.py   # 主提取器
├── gui/                   # 图形界面模块
│   ├── __init__.py
│   ├── app.py            # 主应用
│   ├── styles.py         # 样式系统
│   ├── dialogs.py        # 对话框组件
│   └── components.py     # UI 组件（待实现）
├── utils/                 # 工具模块
│   ├── __init__.py
│   ├── logger.py         # 日志系统
│   └── helpers.py        # 辅助函数
└── tools/                 # 独立工具
    ├── __init__.py
    └── area_selector.py   # 区域选择器
```

### 核心模块说明

#### 1. 配置管理 (config.py)

- `Config` 类：统一配置管理
- 支持多种 OCR 提供商配置
- 用户偏好设置保存
- 配置验证机制

```python
from core.config import config

# 获取配置
provider = config.get("provider")
api_key = config.get("api_key")

# 设置配置
config.set("scroll_interval", 2.5)
```

#### 2. 屏幕捕获 (capture.py)

- `ScreenCapture` 类：屏幕捕获功能
- 支持全屏、区域截图
- 批量截图功能
- 滚动条检测
- 重复图片检测

```python
from core.capture import ScreenCapture

capture = ScreenCapture()
# 设置区域
capture.set_area(100, 100, 800, 600)
# 截图
image = capture.capture_area()
```

#### 3. OCR 处理 (ocr.py)

- `OCRProcessor` 类：OCR 处理引擎
- 支持多种 OCR 提供商
- 批量处理功能
- 结果导出多种格式

```python
from core.ocr import OCRProcessor
from core.config import config

ocr = OCRProcessor(config)
# 处理单张图片
result = ocr.process_image("image.png", provider="zhipu")
# 批量处理
results = ocr.process_directory("screenshots/")
```

#### 4. 文档滚动 (scrolling.py)

- `DocumentScroller` 类：自动滚动控制
- 支持多种滚动方式
- 重复内容检测
- 热键控制

```python
from core.scrolling import DocumentScroller

scroller = DocumentScroller()
# 设置滚动参数
scroller.set_scroll_direction("down")
scroller.set_scroll_interval(3.0)
# 开始滚动
result = scroller.scroll_document(capture_callback)
```

#### 5. 主提取器 (doc_extractor.py)

- `DocExtractor` 类：核心提取逻辑
- 整合所有功能模块
- 提供统一 API 接口

```python
from core.doc_extractor import DocExtractor

extractor = DocExtractor()
# 设置区域
extractor.set_extraction_area(100, 100, 800, 600)
# 开始提取
result = extractor.extract_document()
```

## 安装指南

### 环境要求

- Python 3.8 或更高版本
- macOS / Windows / Linux 操作系统

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/YukiAsuna19990413/Claude-Document-Extractor.git
cd Claude-Document-Extractor
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **安装 Tesseract OCR（可选，用于本地 OCR）**

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
```bash
# 从 https://github.com/UB-Mannheim/tesseract/wiki 下载安装
# 安装后添加到系统 PATH
```

**Linux:**
```bash
sudo apt install tesseract-ocr tesseract-ocr-chi-sim
```

### 开发环境安装

```bash
# 安装开发依赖
pip install -e .[dev]

# 安装代码格式化工具
pip install black flake8 mypy

# 安装测试框架
pip install pytest
```

## 使用方法

### GUI 模式（推荐）

1. **启动 GUI**
```bash
# 方式1：使用主入口
python main.py --mode gui

# 方式2：使用启动脚本
python scripts/run_gui.py

# 方式3：使用安装的命令
doc-extractor-gui
```

2. **界面操作**
   - 选择提取区域（支持手动输入或快速选择）
   - 配置 OCR 提供商和参数
   - 设置滚动参数
   - 点击"开始提取"
   - 查看实时进度和结果

### 命令行模式

1. **基本使用**
```bash
python main.py --mode cli --area 100,100,800,600
```

2. **高级选项**
```bash
# 指定 OCR 提供商
python main.py --mode cli --provider zhipu --scroll-interval 2.0

# 设置输出目录
python main.py --mode cli --output-dir ./extractions

# 启用调试模式
python main.py --mode cli --debug
```

3. **交互式使用**
```bash
python main.py --mode cli
```

### 编程接口

```python
from src.core.doc_extractor import DocExtractor

# 创建提取器实例
extractor = DocExtractor()

# 设置提取区域
extractor.set_extraction_area(100, 100, 800, 600)

# 配置 OCR 提供商
extractor.configure_ocr_provider("zhipu")

# 开始提取
result = extractor.extract_document(
    scroll_direction="down",
    scroll_interval=3.0,
    max_screens=100,
    auto_ocr=True
)

# 获取结果
print(f"提取了 {result['total_screens']} 张图片")
print(f"OCR 提供商: {result['ocr_provider']}")
```

## 配置说明

### API 配置

创建 `config/api_config.json`：

```json
{
  "enabled": true,
  "provider": "zhipu",
  "api_key": "your-api-key-here",
  "base_url": "https://open.bigmodel.cn/api/paas/v4",
  "model": "glm-4v",
  "max_tokens": 4000,
  "temperature": 0.1
}
```

### 提供商配置

#### 智谱 AI
- Base URL: `https://open.bigmodel.cn/api/paas/v4`
- 模型: `glm-4v` (图像识别)
- 成本: ¥12/百万 tokens

#### DeepSeek
- Base URL: `https://api.deepseek.com/v1`
- 模型: `deepseek-chat`
- 成本: ¥1/百万 tokens

#### OpenAI
- Base URL: `https://api.openai.com/v1`
- 模型: `gpt-4-turbo`
- 成本: $10/百万 tokens

#### Tesseract (本地)
- 无需网络连接
- 免费
- 安装语言包: `tesseract-ocr-chi-sim`

## 打包部署

### macOS 应用打包

```bash
# 安装 py2app
pip install py2app

# 构建 .app 应用
python setup.py py2app

# 应用位于 dist/ 目录
open dist/
```

### Windows 可执行文件

```bash
# 安装 pyinstaller
pip install pyinstaller

# 打包单文件
pyinstaller --onefile --windowed main.py

# 打包目录
pyinstaller --windowed main.py
```

### Linux 打包

```bash
# 使用 pyinstaller
pyinstaller --onefile --windowed main.py

# 创建 Debian 包
pip install debuild
debuild -us -uc -b
```

## 开发指南

### 项目结构

```
Claude-Document-Extractor/
├── src/                    # 源代码
│   ├── core/              # 核心功能
│   ├── gui/               # 图形界面
│   ├── utils/             # 工具函数
│   └── tools/             # 独立工具
├── config/                # 配置文件
├── tests/                 # 测试代码
├── docs/                  # 文档
├── scripts/               # 启动脚本
└── assets/                # 资源文件
```

### 代码规范

- 使用 Black 进行代码格式化
- 使用 flake8 进行代码检查
- 使用 mypy 进行类型检查
- 遵循 PEP 8 规范

```bash
# 格式化代码
black src/

# 检查代码
flake8 src/

# 类型检查
mypy src/
```

### 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_capture.py

# 生成覆盖率报告
pytest --cov=src tests/
```

### 添加新功能

1. **添加新的 OCR 提供商**
   - 在 `src/core/ocr.py` 中添加新的处理方法
   - 在 `src/core/config.py` 中添加配置项
   - 更新 GUI 提供商选项

2. **添加新的滚动方式**
   - 在 `src/core/scrolling.py` 中添加新的滚动方法
   - 更新配置选项
   - 更新 GUI 设置

3. **添加新的 UI 组件**
   - 在 `src/gui/components.py` 中创建新组件
   - 在 `src/gui/app.py` 中使用组件

## 故障排除

### 常见问题

1. **无法启动 GUI**
   - 检查 tkinter 是否安装：`python -m tkinter`
   - 确保 Python 版本 >= 3.8

2. **OCR 失败**
   - 检查 API 密钥是否正确
   - 确保网络连接正常
   - 检查 Tesseract 安装

3. **截图失败**
   - 检查屏幕录制权限（macOS）
   - 确认区域坐标正确
   - 检查目标窗口是否可见

4. **滚动不工作**
   - 确保文档有滚动条
   - 检查滚动方向设置
   - 尝试不同的滚动方法

### 日志查看

启用调试模式查看详细日志：

```bash
python main.py --mode cli --debug
```

或通过 GUI 的"运行日志"选项卡查看。

## 性能优化

### 内存管理

- 使用生成器处理大量截图
- 及时释放图像资源
- 定期清理临时文件

### OCR 优化

- 批量处理图片
- 使用适当的图片压缩
- 缓存 API 响应

### 滚动优化

- 调整滚动间隔
- 使用更快的滚动方法
- 启用重复检测

## 贡献指南

### 开发流程

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

### 代码审查

- 所有代码需要经过审查
- 确保 tests 通过
- 更新相关文档

### 提交规范

```bash
git commit -m "feat: 添加新的 OCR 提供商支持"
git commit -m "fix: 修复滚动检测问题"
git commit -m "docs: 更新安装说明"
```

## 更新日志

### v1.0.0 (2024-01-21)
- 初始版本发布
- 支持多种 OCR 引擎
- GUI 和 CLI 双模式
- 自动滚动和截图功能
- 配置管理系统

## 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](../LICENSE) 文件。

## 致谢

- [PyAutoGUI](https://github.com/asweigart/pyautogui) - 屏幕自动化
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR 引擎
- [Pillow](https://python-pillow.org/) - 图像处理
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI 框架