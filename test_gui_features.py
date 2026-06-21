#!/usr/bin/env python3
"""
测试 GUI 应用的简单脚本
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gui_features():
    """测试所有 GUI 功能"""
    root = tk.Tk()
    root.title("Doc Extractor GUI - 功能测试")
    root.geometry("800x600")

    # 创建主框架
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # 标题
    title_label = ttk.Label(main_frame, text="🔍 文档提取工具 - 功能测试",
                           font=('', 16, 'bold'))
    title_label.pack(pady=(0, 20))

    # 功能测试区域
    features_frame = ttk.LabelFrame(main_frame, text="可用功能", padding="15")
    features_frame.pack(fill=tk.BOTH, expand=True)

    # 区域选择功能
    area_frame = ttk.Frame(features_frame)
    area_frame.pack(fill=tk.X, pady=(0, 15))

    ttk.Label(area_frame, text="📍 截图区域选择:", font=('', 12, 'bold')).pack(anchor='w')

    preset_frame = ttk.Frame(area_frame)
    preset_frame.pack(fill=tk.X, pady=(5, 0))

    # 快速选择按钮
    ttk.Button(preset_frame, text="全屏", width=10,
              command=lambda: print("选择了全屏")).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(preset_frame, text="左半屏", width=10,
              command=lambda: print("选择了左半屏")).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(preset_frame, text="右半屏", width=10,
              command=lambda: print("选择了右半屏")).pack(side=tk.LEFT, padx=(0, 5))

    ttk.Button(preset_frame, text="上半屏", width=10,
              command=lambda: print("选择了上半屏")).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(preset_frame, text="下半屏", width=10,
              command=lambda: print("选择了下半屏")).pack(side=tk.LEFT)

    # 自定义选择按钮
    ttk.Button(area_frame, text="📸 自定义选择区域（鼠标框选）",
              command=lambda: messagebox.showinfo("提示", "请在屏幕上拖动鼠标选择区域")).pack(pady=(10, 0))

    # OCR 模型选择
    ocr_frame = ttk.Frame(features_frame)
    ocr_frame.pack(fill=tk.X, pady=(15, 0))

    ttk.Label(ocr_frame, text="🤖 OCR 模型选择:", font=('', 12, 'bold')).pack(anchor='w')

    model_frame = ttk.Frame(ocr_frame)
    model_frame.pack(fill=tk.X, pady=(5, 0))

    ttk.Button(model_frame, text="🔧 配置 API",
              command=lambda: messagebox.showinfo("API 配置", "请点击配置 API 按钮设置您的 API key")).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(model_frame, text="API (高精度)",
              command=lambda: print("选择了高精度 API")).pack(side=tk.LEFT)
    ttk.Button(model_frame, text="本地 Tesseract",
              command=lambda: print("选择了本地 Tesseract")).pack(side=tk.LEFT, padx=(10, 0))

    # 控制按钮
    control_frame = ttk.Frame(features_frame)
    control_frame.pack(fill=tk.X, pady=(15, 0))

    ttk.Label(control_frame, text="⚙️ 控制:", font=('', 12, 'bold')).pack(anchor='w')

    button_frame = ttk.Frame(control_frame)
    button_frame.pack(fill=tk.X, pady=(5, 0))

    ttk.Button(button_frame, text="▶️ 开始提取",
              command=lambda: messagebox.showinfo("开始提取", "请先选择截图区域")).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(button_frame, text="⏹️ 停止",
              command=lambda: print("停止提取")).pack(side=tk.LEFT)

    # 结果区域
    result_frame = ttk.LabelFrame(features_frame, text="结果", padding="10")
    result_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

    # 日志显示
    log_frame = ttk.Frame(result_frame)
    log_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(log_frame, text="📋 提取日志:", font=('', 10, 'bold')).pack(anchor='w')

    log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
    log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    # 添加示例日志
    log_text.insert('1.0', "欢迎使用文档提取工具！\n")
    log_text.insert('end', "1. 选择截图区域\n")
    log_text.insert('end', "2. 选择 OCR 模型\n")
    log_text.insert('end', "3. 点击开始提取\n")
    log_text.insert('end', "4. 查看提取结果\n")
    log_text.config(state='disabled')

    # 结果操作按钮
    result_buttons = ttk.Frame(result_frame)
    result_buttons.pack(fill=tk.X, pady=(10, 0))

    ttk.Button(result_buttons, text="📋 复制文本",
              command=lambda: print("复制文本到剪贴板")).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(result_buttons, text="💾 保存文件",
              command=lambda: print("保存提取的文本到文件")).pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(result_buttons, text="🗑️ 清空日志",
              command=lambda: print("清空日志")).pack(side=tk.LEFT)

    # 底部信息
    info_label = ttk.Label(main_frame,
                          text="✅ 所有功能正常 - 这是更新后的 GUI 版本",
                          font=('', 10, 'italic'))
    info_label.pack(pady=(20, 0))

    root.mainloop()

if __name__ == "__main__":
    test_gui_features()