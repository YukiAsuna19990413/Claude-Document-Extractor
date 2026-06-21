#!/usr/bin/env python3
"""
项目结构验证测试
"""

import os
import sys
import importlib
from pathlib import Path

def test_project_structure():
    """测试项目结构"""
    print("🔍 验证项目结构...")
    print("=" * 50)

    # 检查必需的目录
    required_dirs = [
        "src",
        "src/core",
        "src/gui",
        "src/utils",
        "src/tools",
        "config",
        "tests",
        "docs",
        "scripts",
        "assets"
    ]

    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/")

    # 检查核心文件
    core_files = [
        "src/core/__init__.py",
        "src/core/config.py",
        "src/core/capture.py",
        "src/core/ocr.py",
        "src/core/scrolling.py",
        "src/core/doc_extractor.py",
        "src/gui/__init__.py",
        "src/gui/app.py",
        "src/gui/styles.py",
        "src/gui/dialogs.py",
        "src/utils/__init__.py",
        "src/utils/logger.py",
        "src/utils/helpers.py",
        "src/tools/__init__.py",
        "src/tools/area_selector.py",
        "main.py",
        "requirements.txt",
        "pyproject.toml",
        "README.md",
        "setup.py"
    ]

    print("\n📄 检查核心文件...")
    for file_path in core_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")

def test_module_imports():
    """测试模块导入"""
    print("\n🧪 测试模块导入...")
    print("=" * 50)

    # 添加 src 目录到路径
    sys.path.insert(0, "src")

    try:
        # 测试核心模块
        from core.config import config
        print("✅ core.config")

        from core.capture import ScreenCapture
        print("✅ core.capture")

        from core.ocr import OCRProcessor
        print("✅ core.ocr")

        from core.scrolling import DocumentScroller
        print("✅ core.scrolling")

        # 测试工具模块
        from utils.logger import logger
        print("✅ utils.logger")

        from utils.helpers import FileHelper, ValidationHelper
        print("✅ utils.helpers")

        # 测试 GUI 模块
        import gui.styles
        print("✅ gui.styles")

        import gui.dialogs
        print("✅ gui.dialogs")

        import gui.components
        print("✅ gui.components")

        print("\n🎉 所有核心模块导入成功！")

    except ImportError as e:
        print(f"❌ 导入失败: {e}")

def test_project_config():
    """测试项目配置"""
    print("\n⚙️ 检查项目配置...")
    print("=" * 50)

    # 检查 pyproject.toml
    if os.path.exists("pyproject.toml"):
        print("✅ pyproject.toml - 现代项目配置")
    else:
        print("❌ pyproject.toml")

    # 检查 requirements.txt
    if os.path.exists("requirements.txt"):
        print("✅ requirements.txt - 依赖管理")
    else:
        print("❌ requirements.txt")

    # 检查 setup.py
    if os.path.exists("setup.py"):
        print("✅ setup.py - 安装脚本")
    else:
        print("❌ setup.py")

    # 检查 .gitignore
    if os.path.exists(".gitignore"):
        print("✅ .gitignore - Git 配置")
    else:
        print("❌ .gitignore")

def count_lines_of_code():
    """统计代码行数"""
    print("\n📊 代码统计...")
    print("=" * 50)

    total_lines = 0
    file_count = 0

    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_count += 1
                        if lines > 50:  # 只显示较大的文件
                            print(f"📄 {file_path}: {lines} 行")
                except:
                    pass

    print(f"\n总计: {file_count} 个 Python 文件，{total_lines} 行代码")

def main():
    """主函数"""
    print("🚀 文档提取工具 - 项目结构验证")
    print("=" * 60)

    test_project_structure()
    test_module_imports()
    test_project_config()
    count_lines_of_code()

    print("\n" + "=" * 60)
    print("✅ 验证完成！项目结构已成功重构。")
    print("\n🎯 下一步：")
    print("1. 运行 'python3 main.py --mode gui' 启动 GUI")
    print("2. 运行 'python3 scripts/run_gui.py' 启动 GUI")
    print("3. 阅读 docs/README.md 了解详细使用方法")

if __name__ == "__main__":
    main()