#!/bin/bash

# 启动 GUI 应用程序的脚本

echo "正在启动文档提取工具 GUI 版本..."
echo "当前目录: $(pwd)"
echo "Python 版本: $(python3 --version)"
echo ""

# 检查文件是否存在
if [ ! -f "doc_extractor_gui.py" ]; then
    echo "错误: 找不到 doc_extractor_gui.py 文件"
    exit 1
fi

# 运行程序
python3 doc_extractor_gui.py

echo ""
echo "程序已退出"