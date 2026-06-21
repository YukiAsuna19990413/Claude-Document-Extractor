# 文档提取工具

从受限制的云桌面环境（如 VMware Horizon Client）自动提取文档内容的现代化工具。

## 🌟 特性

- 📸 **智能截图** - 自动捕获指定区域，支持全屏、半屏、自定义选择
- 🔄 **自动滚动** - 智能文档滚动，可调节间隔和方向
- 🔍 **多引擎 OCR** - 支持 Tesseract、智谱 AI、DeepSeek、OpenAI
- 🖥️ **现代 GUI** - 直观的图形界面，实时预览和状态显示
- 💻 **双模式** - GUI 和命令行两种使用方式
- 🚀 **高性能** - 模块化设计，线程安全，内存优化

## 📁 项目结构

```
Claude-Document-Extractor/
├── src/                      # 源代码
│   ├── core/                 # 核心功能
│   │   ├── capture.py       # 屏幕捕获
│   │   ├── ocr.py           # OCR 识别
│   │   ├── scrolling.py     # 文档滚动
│   │   └── config.py        # 配置管理
│   ├── gui/                 # 图形界面
│   │   ├── app.py           # 主应用
│   │   ├── styles.py        # 样式系统
│   │   └── dialogs.py       # 对话框组件
│   ├── utils/               # 工具模块
│   └── tools/               # 独立工具
├── config/                  # 配置文件
├── docs/                    # 详细文档
├── scripts/                 # 启动脚本
└── main.py                  # 主入口
```

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

#### GUI 模式（推荐）
```bash
# 方式1：直接运行
python main.py --mode gui

# 方式2：使用脚本
python scripts/run_gui.py
```

#### 命令行模式
```bash
# 基本使用
python main.py --mode cli --area 100,100,800,600

# 使用特定 OCR 提供商
python main.py --mode cli --provider zhipu --scroll-interval 2.0
```

## 🎯 使用指南

### 1. 截图区域选择

```bash
# 运行区域选择工具
python src/tools/area_selector.py
```

### 2. 配置 API

创建 `config/api_config.json`：
```json
{
  "enabled": true,
  "provider": "zhipu",
  "api_key": "your-api-key",
  "base_url": "https://open.bigmodel.cn/api/paas/v4",
  "model": "glm-4v"
}
```

### 3. 开始提取

1. 启动 GUI 应用
2. 选择截图区域
3. 配置 OCR 设置
4. 点击"开始提取"

## 🔧 配置选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--mode` | 运行模式 (gui/cli) | gui |
| `--area` | 截图区域 (x,y,w,h) | 全屏 |
| `--provider` | OCR 提供商 | tesseract |
| `--scroll-interval` | 滚动间隔（秒） | 3.0 |
| `--scroll-direction` | 滚动方向 (up/down) | down |
| `--output` | 输出目录 | 自动生成 |
| `--debug` | 调试模式 | false |

## 📊 OCR 对比

| 提供商 | 速度 | 精度 | 成本 | 特色 |
|--------|------|------|------|------|
| Tesseract | ⚡ 快 | 📝 中 | 免费 | 本地，无需网络 |
| 智谱 AI | 🐢 中 | 🎯 高 | ¥12/百万 tokens | 支持表格、公式 |
| DeepSeek | 🐢 中 | 🎯 高 | ¥1/百万 tokens | 性价比高 |
| OpenAI | 🐢 慢 | 🎯 最高 | $10/百万 tokens | GPT-4V 质量 |

## 📦 打包应用

### macOS 应用
```bash
# 安装 py2app
pip install py2app

# 打包
python setup.py py2app

# 应用在 dist/ 目录下
open dist/
```

### Windows 可执行文件
```bash
pip install pyinstaller

pyinstaller --onefile --windowed main.py
```

## 📚 文档

- [详细文档](docs/README.md) - 完整的使用说明和 API 文档
- [贡献指南](CONTRIBUTING.md) - 如何参与项目开发
- [更新日志](CHANGELOG.md) - 版本更新记录

## 🔍 高级功能

### 自动检测
- 防重复截图机制
- 文档结束智能检测
- 批量自动处理

### 导出选项
- 文本文件 (.txt)
- Markdown (.md)
- JSON 元数据 (.json)
- 带时间戳的批量保存

### 日志系统
- 详细的操作日志
- 错误追踪和调试
- 可配置的日志级别

## 💡 最佳实践

1. **区域选择**：选择稳定的文档区域，避免包含滚动条
2. **OCR 选择**：重要文档推荐使用 API，质量更高
3. **网络优化**：API 模式确保网络稳定
4. **内存管理**：处理大量文档时注意内存使用

## ⚠️ 注意事项

- 使用前请确保符合公司 IT 政策
- 避免处理敏感或机密信息
- API 需要网络连接，注意配额使用
- 首次运行可能需要授权屏幕录制权限

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [PyAutoGUI](https://github.com/asweigart/pyautogui) - 屏幕自动化
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR 引擎
- [Pillow](https://python-pillow.org/) - 图像处理
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI 框架