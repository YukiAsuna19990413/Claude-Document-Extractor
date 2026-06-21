#!/usr/bin/env python3
"""
辅助工具：可视化选择截图区域
运行此工具后，用鼠标拖动选择区域，程序会输出坐标
"""

import tkinter as tk
from tkinter import messagebox

class AreaSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("截图区域选择器")
        self.root.geometry("400x150")

        self.label = tk.Label(self.root, text="点击下方按钮后，在屏幕上拖动选择区域", wraplength=350)
        self.label.pack(pady=20)

        self.start_btn = tk.Button(self.root, text="开始选择区域", command=self.start_selection, height=2, width=20)
        self.start_btn.pack()

        self.result_label = tk.Label(self.root, text="", fg="blue", wraplength=350)
        self.result_label.pack(pady=10)

        self.copy_btn = tk.Button(self.root, text="复制坐标", command=self.copy_coords, state=tk.DISABLED)
        self.copy_btn.pack()

        self.coords = None
        self.canvas_window = None

    def start_selection(self):
        """隐藏主窗口，显示全屏选择器"""
        self.root.withdraw()

        # 创建全屏窗口
        self.canvas_window = tk.Toplevel(self.root)
        self.canvas_window.attributes('-fullscreen', True)
        self.canvas_window.attributes('-alpha', 0.3)  # 半透明
        self.canvas_window.configure(bg='gray')

        self.canvas = tk.Canvas(self.canvas_window, bg='', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定鼠标事件
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)

        self.start_x = None
        self.start_y = None
        self.rect = None

        # 提示文本
        self.canvas.create_text(
            1000, 50,
            text="用鼠标拖动选择区域，完成后按 ESC 取消或松开鼠标确认",
            fill='white',
            font=('Arial', 14)
        )

        # ESC 键取消
        self.canvas_window.bind('<Escape>', self.cancel_selection)

    def on_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        if self.rect:
            self.canvas.delete(self.rect)

        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=3, fill='blue', stipple='gray25'
        )

    def on_mouse_up(self, event):
        if self.start_x is None:
            return

        end_x = event.x
        end_y = event.y

        # 计算坐标（标准化为左上角、宽度、高度）
        x = min(self.start_x, end_x)
        y = min(self.start_y, end_y)
        width = abs(end_x - self.start_x)
        height = abs(end_y - self.start_y)

        self.coords = f"{x},{y},{width},{height}"

        # 关闭选择窗口
        self.canvas_window.destroy()

        # 恢复主窗口并显示结果
        self.root.deiconify()
        self.result_label.config(text=f"坐标: {self.coords}\n\n请将此坐标输入到主程序中")
        self.copy_btn.config(state=tk.NORMAL)

        # 自动保存到配置文件
        with open("area_config.txt", "w") as f:
            f.write(self.coords)
        self.result_label.config(text=self.result_label.cget("text") + "\n\n已保存到 area_config.txt")

    def cancel_selection(self, event):
        self.canvas_window.destroy()
        self.root.deiconify()

    def copy_coords(self):
        if self.coords:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.coords)
            messagebox.showinfo("成功", "坐标已复制到剪贴板！")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    selector = AreaSelector()
    selector.run()