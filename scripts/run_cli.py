#!/usr/bin/env python3
"""
CLI 启动脚本
启动文档提取工具的命令行界面
"""

import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

def main():
    """主函数"""
    try:
        # 导入主模块
        from main import main as cli_main

        # 运行 CLI
        sys.argv.insert(0, 'main.py')  # 模拟命令行参数
        sys.argv.insert(1, '--mode')
        sys.argv.insert(2, 'cli')

        cli_main()

    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
        print("请确保所有依赖已安装: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()