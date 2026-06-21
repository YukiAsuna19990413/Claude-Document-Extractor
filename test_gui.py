#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import sys

# 确认我们是否在正确的目录
print(f"当前工作目录: {sys.path[0]}")
print(f"是否包含新功能: {'全屏' in open('doc_extractor_gui.py').read()}")

# 创建简单的测试窗口
root = tk.Tk()
root.title("测试 - 新 GUI")
root.geometry("800x600")

# 添加一些新功能的标记
frame = ttk.Frame(root, padding=20)
frame.pack(fill=tk.BOTH, expand=True)

# 检查是否有新按钮
try:
    # 这应该在新版本中存在
    area_btn = tk.Button(frame, text="📍 截图区域", bg='red', fg='white', height=3)
    area_btn.pack(fill=tk.X, pady=5)
    print("✅ 找到截图区域按钮")
except:
    print("❌ 未找到截图区域按钮")

try:
    # 这应该在新版本中存在
    api_btn = tk.Button(frame, text="🔧 配置 API", bg='blue', fg='white', height=3)
    api_btn.pack(fill=tk.X, pady=5)
    print("✅ 找到配置 API 按钮")
except:
    print("❌ 未找到配置 API 按钮")

try:
    # 这应该在新版本中存在
    custom_btn = tk.Button(frame, text="📸 自定义选择区域", bg='green', fg='white', height=3)
    custom_btn.pack(fill=tk.X, pady=5)
    print("✅ 找到自定义选择按钮")
except:
    print("❌ 未找到自定义选择按钮")

root.mainloop()