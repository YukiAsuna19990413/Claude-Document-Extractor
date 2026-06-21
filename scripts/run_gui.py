#!/usr/bin/env python3
"""
GUI 启动脚本
启动文档提取工具的图形界面
"""

import sys
import os
import tkinter as tk

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

def main():
    """主函数"""
    try:
        from gui.app import DocExtractorGUI

        # 创建主窗口
        root = tk.Tk()

        # 创建应用
        app = DocExtractorGUI(root)

        # 运行应用
        root.mainloop()

    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保所有依赖已安装: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()