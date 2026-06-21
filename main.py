#!/usr/bin/env python3
"""
文档提取工具 - 主入口
支持 GUI 和 CLI 两种运行模式
"""

import sys
import os
import argparse
from typing import Optional

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from core.doc_extractor import DocExtractor
    from core.config import config
    from gui.app import DocExtractorGUI
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保所有依赖已安装: pip install -r requirements.txt")
    sys.exit(1)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='文档提取工具')
    parser.add_argument('--mode', choices=['cli', 'gui'], default='gui',
                       help='运行模式: cli(命令行) 或 gui(图形界面)')
    parser.add_argument('--area', type=str, default=None,
                       help='提取区域坐标 (x,y,width,height)')
    parser.add_argument('--provider', choices=['tesseract', 'zhipu', 'deepseek', 'openai'],
                       default=None, help='OCR 提供商')
    parser.add_argument('--scroll-direction', choices=['up', 'down'],
                       default='down', help='滚动方向')
    parser.add_argument('--scroll-interval', type=float, default=3.0,
                       help='滚动间隔（秒）')
    parser.add_argument('--max-screens', type=int, default=100,
                       help='最大截图数量')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='输出目录')
    parser.add_argument('--config', type=str, default=None,
                       help='配置文件路径')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')
    parser.add_argument('--list-providers', action='store_true',
                       help='列出所有支持的 OCR 提供商')

    return parser.parse_args()


def run_cli_mode(args):
    """运行 CLI 模式"""
    print("🚀 文档提取工具 - CLI 模式")
    print("=" * 50)

    # 创建提取器
    extractor = DocExtractor(args.config)

    # 验证设置
    validation = extractor.validate_setup()
    if not validation['valid']:
        print("❌ 设置验证失败:")
        for issue in validation['issues']:
            print(f"   - {issue}")
        if not args.area:
            return False

    if validation['warnings']:
        print("⚠️ 警告:")
        for warning in validation['warnings']:
            print(f"   - {warning}")

    # 设置提取区域
    if args.area:
        try:
            coords = [int(x) for x in args.area.split(',')]
            if len(coords) != 4:
                raise ValueError("需要 4 个坐标值")
            x, y, width, height = coords
            print(f"📍 设置提取区域: ({x}, {y}) {width}x{height}")
            extractor.set_extraction_area(x, y, width, height)
        except Exception as e:
            print(f"❌ 无效的区域坐标: {e}")
            return False
    else:
        # 交互式选择区域
        if not extractor.select_extraction_area_interactive():
            print("❌ 区域选择失败")
            return False

    # 配置 OCR 提供商
    if args.provider:
        print(f"🔧 设置 OCR 提供商: {args.provider}")
        if not extractor.configure_ocr_provider(args.provider):
            print("❌ OCR 配置失败")
            return False
    else:
        # 使用配置中的提供商
        provider = config.get("provider", "tesseract")
        print(f"🔧 使用 OCR 提供商: {provider}")

    # 显示系统信息
    info = extractor.get_system_info()
    print(f"\n📊 系统信息:")
    print(f"   屏幕分辨率: {info['info']['screen_size']}")
    print(f"   提取区域: {info['current_area']}")
    print(f"   OCR 提供商: {info['config']['ocr_provider']}")
    print(f"   滚动方向: {info['config']['scroll_direction']}")
    print(f"   滚动间隔: {info['config']['scroll_interval']} 秒")

    # 确认开始
    if not args.debug:
        print("\n按 Enter 开始提取，Ctrl+C 取消...")
        input()

    # 开始提取
    try:
        result = extractor.extract_document(
            scroll_direction=args.scroll_direction,
            scroll_interval=args.scroll_interval,
            max_screens=args.max_screens,
            output_dir=args.output_dir
        )

        if "error" in result:
            print(f"❌ 提取失败: {result['error']}")
            return False
        else:
            print(f"\n✅ 提取成功!")
            print(f"   提取 ID: {result['extraction_id']}")
            print(f"   截图数量: {result['total_screens']}")
            print(f"   OCR 提供商: {result['ocr_provider']}")
            print(f"   输出目录: {result['output_directory']}")
            print(f"   处理时间: {result['processing_time']:.2f} 秒")

            # 显示文本预览
            if os.path.exists(result['extracted_text_path']):
                with open(result['extracted_text_path'], 'r', encoding='utf-8') as f:
                    text = f.read()
                    if text:
                        print(f"\n📄 提取文本预览（前 200 字）:")
                        print(text[:200] + "..." if len(text) > 200 else text)

            return True

    except KeyboardInterrupt:
        print("\n⚠️ 用户中断")
        return False
    except Exception as e:
        print(f"❌ 提取过程中发生错误: {e}")
        return False


def run_gui_mode(args):
    """运行 GUI 模式"""
    print("🖥️ 启动图形界面...")

    try:
        import tkinter as tk
        root = tk.Tk()

        # 创建 GUI 应用
        app = DocExtractorGUI(root)

        # 如果指定了区域，预先设置
        if args.area:
            try:
                coords = [int(x) for x in args.area.split(',')]
                if len(coords) == 4:
                    app.set_extraction_area(*coords)
            except:
                pass

        # 运行 GUI
        root.mainloop()

    except ImportError:
        print("❌ 无法启动 GUI - tkinter 未安装")
        print("请安装 tkinter 或使用 CLI 模式: python main.py --mode cli")
        return False
    except Exception as e:
        print(f"❌ GUI 启动失败: {e}")
        return False


def list_providers():
    """列出支持的 OCR 提供商"""
    print("\n🔍 支持的 OCR 提供商:")
    print("=" * 50)

    providers_info = {
        "tesseract": {
            "name": "Tesseract OCR",
            "type": "本地",
            "cost": "免费",
            "speed": "快",
            "accuracy": "中",
            "features": ["离线使用", "支持多语言", "开源免费"]
        },
        "zhipu": {
            "name": "智谱 AI",
            "type": "云端",
            "cost": "¥12/百万 tokens",
            "speed": "中",
            "accuracy": "高",
            "features": ["支持表格识别", "支持公式", "中文优化"]
        },
        "deepseek": {
            "name": "DeepSeek",
            "type": "云端",
            "cost": "¥1/百万 tokens",
            "speed": "中",
            "accuracy": "高",
            "features": ["性价比高", "中文支持好", "API 稳定"]
        },
        "openai": {
            "name": "OpenAI GPT-4V",
            "type": "云端",
            "cost": "$10/百万 tokens",
            "speed": "慢",
            "accuracy": "最高",
            "features": ["GPT-4 质量", "多语言支持", "强大理解能力"]
        }
    }

    for key, info in providers_info.items():
        print(f"\n📌 {info['name']} ({key})")
        print(f"   类型: {info['type']}")
        print(f"   成本: {info['cost']}")
        print(f"   速度: {info['speed']}")
        print(f"   精度: {info['accuracy']}")
        print(f"   特性: {', '.join(info['features'])}")


def main():
    """主函数"""
    args = parse_arguments()

    if args.debug:
        print("🔍 调试模式已启用")
        import logging
        logging.basicConfig(level=logging.DEBUG)

    if args.list_providers:
        list_providers()
        return

    print("📋 文档提取工具")
    print("=" * 60)
    print(f"运行模式: {args.mode.upper()}")

    if args.mode == 'cli':
        success = run_cli_mode(args)
    elif args.mode == 'gui':
        success = run_gui_mode(args)
    else:
        success = False

    if success:
        print("\n🎉 程序执行完成!")
        sys.exit(0)
    else:
        print("\n❌ 程序执行失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()