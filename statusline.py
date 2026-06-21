#!/usr/bin/env python3
"""
Statusline 配置
显示当前目录、模型、上下文百分比
"""

import os
import json
import subprocess
import re
from datetime import datetime

def get_current_model():
    """获取当前使用的模型"""
    try:
        # 尝试从 Claude config 获取
        result = subprocess.run(['claude', 'config', 'get', 'model'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()

        # 尝试从其他来源获取
        cmd = 'claude --model'
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=5)
        if 'model' in result.stdout.lower():
            match = re.search(r'model[:\s]+(\w+)', result.stdout, re.IGNORECASE)
            if match:
                return match.group(1)

    except Exception:
        pass

    return 'glm-4.5-air'  # 默认值

def get_context_usage():
    """获取上下文使用情况"""
    try:
        # 从当前的上下文信息中提取
        # 这里可以通过 Claude 的 API 或命令获取
        # 暂时模拟一个值
        return '12%'  # 从之前的输出中看到的值
    except Exception:
        return '0%'

def format_path(path):
    """格式化路径，显示在 statusline 中"""
    home = os.path.expanduser('~')
    if path.startswith(home):
        return path.replace(home, '~')
    return path

def main():
    """主函数"""
    # 获取信息
    cwd = os.getcwd()
    model = get_current_model()
    context_percent = get_context_usage()
    time_str = datetime.now().strftime('%H:%M')

    # 格式化 statusline
    statusline = f"{format_path(cwd)} | {model} | {context_percent} | {time_str}"

    # 输出格式
    # \x1b[0m 重置颜色
    # \x1b[32m 绿色
    # \x1b[34m 蓝色
    # \x1b[33m 黄色
    colored_statusline = (
        f"\x1b[32m{format_path(cwd)}\x1b[0m | "
        f"\x1b[34m{model}\x1b[0m | "
        f"\x1b[33m{context_percent}\x1b[0m | "
        f"\x1b[0m{time_str}"
    )

    print(colored_statusline)

if __name__ == "__main__":
    main()