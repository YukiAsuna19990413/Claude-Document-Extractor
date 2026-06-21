#!/usr/bin/env python3
"""
Word 文档提取工具 - GUI 版本
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
import os
import json
import base64
from datetime import datetime
from PIL import Image, ImageTk
import mss
import pyautogui
import time

try:
    from openai import OpenAI
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False


class DocExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("文档提取工具")
        self.root.geometry("1000x750")
        self.root.minsize(850, 650)

        # 应用图标和样式
        self.setup_styles()

        # 数据
        self.screenshot_area = None
        self.api_config = self.load_api_config()
        self.screenshots = []
        self.screenshot_dir = None
        self.is_running = False

        # 消息队列（用于线程通信）
        self.message_queue = queue.Queue()

        # 构建 UI
        self.build_ui()

        # 检查消息队列
        self.root.after(100, self.check_message_queue)

    def setup_styles(self):
        """设置样式"""
        self.style = ttk.Style()

        # 使用系统默认主题或兼容的主题
        available_themes = self.style.theme_names()
        if 'modern' in available_themes:
            self.style.theme_use('modern')
        elif 'clam' in available_themes:
            self.style.theme_use('clam')
        else:
            self.style.theme_use('default')

        # 配色方案
        self.colors = {
            'primary': '#4A90E2',
            'success': '#5CB85C',
            'warning': '#F0AD4E',
            'danger': '#D9534F',
            'bg': '#F5F5F5',
            'card': '#FFFFFF',
        }

    def build_ui(self):
        """构建主界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧面板（控制）
        left_panel = ttk.Frame(main_frame, width=320, padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        # 右侧面板（预览和结果）
        right_panel = ttk.Frame(main_frame, padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # ====== 左侧：控制面板 ======
        ttk.Label(left_panel, text="⚙️ 控制面板", font=('', 14, 'bold')).pack(pady=(0, 15), anchor='w')

        # 区域设置
        self.create_section(left_panel, "📍 截图区域", [
            self.create_area_controls(left_panel)
        ])

        # 滚动设置
        self.create_section(left_panel, "⏱️ 滚动设置", [
            self.create_scroll_controls(left_panel)
        ])

        # OCR 设置
        self.create_section(left_panel, "🤖 OCR 设置", [
            self.create_ocr_controls(left_panel)
        ])

        # 操作按钮
        self.create_section(left_panel, "🚀 操作", [
            self.create_action_buttons(left_panel)
        ])

        # 状态信息
        self.create_section(left_panel, "📊 状态", [
            self.create_status_panel(left_panel)
        ])

        # ====== 右侧：预览和结果 ======
        # 标签页
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 预览页
        self.create_preview_tab()

        # 结果页
        self.create_result_tab()

        # 日志页
        self.create_log_tab()

    def create_section(self, parent, title, widgets):
        """创建一个章节"""
        frame = ttk.LabelFrame(parent, text=title, padding=12)
        frame.pack(fill=tk.X, pady=(0, 12))
        for widget in widgets:
            widget.pack(fill=tk.X, pady=4)
        return frame

    def create_area_controls(self, parent):
        """创建区域控制组件"""
        frame = ttk.Frame(parent)

        # 显示当前区域
        self.area_label = ttk.Label(frame, text="未设置区域", foreground='gray', font=('', 10))
        self.area_label.pack(anchor='w', pady=(0, 8))

        # 固定区域选项
        ttk.Label(frame, text="快速选择:", font=('', 9)).pack(anchor='w')

        preset_frame = ttk.Frame(frame)
        preset_frame.pack(fill=tk.X, pady=(4, 8))

        ttk.Button(preset_frame, text="全屏", width=8, command=lambda: self.set_area_fullscreen()).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(preset_frame, text="左半屏", width=8, command=lambda: self.set_area_halfscreen('left')).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(preset_frame, text="右半屏", width=8, command=lambda: self.set_area_halfscreen('right')).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(preset_frame, text="上半屏", width=8, command=lambda: self.set_area_halfscreen('top')).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(preset_frame, text="下半屏", width=8, command=lambda: self.set_area_halfscreen('bottom')).pack(side=tk.LEFT)

        # 自定义选择
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(8, 8))
        ttk.Button(
            frame,
            text="📸 自定义选择区域（鼠标框选）",
            command=self.start_area_selection
        ).pack(fill=tk.X, pady=(0, 4))

        ttk.Button(frame, text="👁️ 测试截图", command=self.test_screenshot).pack(fill=tk.X)

        return frame

    def create_scroll_controls(self, parent):
        """创建滚动控制组件"""
        frame = ttk.Frame(parent)

        # 滚动间隔
        ttk.Label(frame, text="滚动间隔（秒）:").pack(anchor='w')

        scroll_frame = ttk.Frame(frame)
        scroll_frame.pack(fill=tk.X, pady=(4, 0))

        self.scroll_pause = ttk.Spinbox(scroll_frame, from_=0.5, to=5.0, increment=0.5, width=10)
        self.scroll_pause.set(1.5)
        self.scroll_pause.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(scroll_frame, text="（云桌面响应慢可以调大）", font=('', 8), foreground='gray').pack(side=tk.LEFT)

        return frame

    def create_ocr_controls(self, parent):
        """创建 OCR 控制组件"""
        frame = ttk.Frame(parent)

        # OCR 方式选择
        ttk.Label(frame, text="OCR 方式:").pack(anchor='w')

        self.ocr_mode = tk.StringVar(value="api" if self.api_config.get("enabled") else "local")

        mode_frame = ttk.Frame(frame)
        mode_frame.pack(fill=tk.X, pady=(4, 8))

        ttk.Radiobutton(mode_frame, text="API (高精度)", variable=self.ocr_mode, value="api").pack(anchor='w')
        ttk.Radiobutton(mode_frame, text="本地 Tesseract", variable=self.ocr_mode, value="local").pack(anchor='w')

        # API 配置按钮
        ttk.Button(frame, text="🔧 配置 API", command=self.open_api_config).pack(fill=tk.X, pady=(0, 4))

        # API 状态
        self.api_status_label = ttk.Label(frame, text=self.get_api_status(), font=('', 9))
        self.api_status_label.pack(anchor='w')

        return frame

    def create_action_buttons(self, parent):
        """创建操作按钮"""
        frame = ttk.Frame(parent)

        # 主按钮
        self.start_btn = tk.Button(
            frame,
            text="▶️ 开始提取",
            bg=self.colors['primary'],
            fg='white',
            font=('', 12, 'bold'),
            relief='flat',
            padx=15,
            pady=12,
            cursor='hand2',
            command=self.start_extraction
        )
        self.start_btn.pack(fill=tk.X, pady=(0, 8))

        self.stop_btn = tk.Button(
            frame,
            text="⏹️ 停止",
            bg=self.colors['danger'],
            fg='white',
            font=('', 12, 'bold'),
            relief='flat',
            padx=15,
            pady=12,
            cursor='hand2',
            command=self.stop_extraction,
            state=tk.DISABLED
        )
        self.stop_btn.pack(fill=tk.X)

        return frame

    def create_status_panel(self, parent):
        """创建状态面板"""
        frame = ttk.Frame(parent)

        self.status_label = ttk.Label(frame, text="就绪", foreground='green', font=('', 10))
        self.status_label.pack(anchor='w', pady=(0, 4))

        self.progress_label = ttk.Label(frame, text="", font=('', 9))
        self.progress_label.pack(anchor='w', pady=(0, 8))

        # 进度条
        self.progress = ttk.Progressbar(frame, mode='determinate')
        self.progress.pack(fill=tk.X)

        return frame

    def create_preview_tab(self):
        """创建预览标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📸 预览")

        # 图片容器
        self.preview_frame = ttk.Frame(tab)
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.preview_label = ttk.Label(
            self.preview_frame,
            text="截图预览将显示在这里\n\n「快速选择」或「自定义选择」后\n点击「测试截图」查看效果",
            font=('', 11),
            foreground='gray'
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor='center')

    def create_result_tab(self):
        """创建结果标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📄 结果")

        # 工具栏
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, padx=10, pady=(10, 0))

        ttk.Button(toolbar, text="📋 复制文本", command=self.copy_result).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(toolbar, text="💾 保存文件", command=self.save_result).pack(side=tk.LEFT)

        # 文本区域
        self.result_text = scrolledtext.ScrolledText(
            tab,
            wrap=tk.WORD,
            font=('Menlo', 11),
            padx=10,
            pady=10
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_log_tab(self):
        """创建日志标签页"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📝 日志")

        # 工具栏
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill=tk.X, padx=10, pady=(10, 0))

        ttk.Button(toolbar, text="🗑️ 清空日志", command=self.clear_log).pack(side=tk.LEFT)

        # 文本区域
        self.log_text = scrolledtext.ScrolledText(
            tab,
            wrap=tk.WORD,
            font=('Menlo', 10),
            bg='#1E1E1E',
            fg='#D4D4D4',
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ====== 区域选择 ======

    def set_area_fullscreen(self):
        """设置全屏区域"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.screenshot_area = {
            'x': 0,
            'y': 0,
            'width': screen_width,
            'height': screen_height
        }
        self.area_label.config(text=f"区域: 全屏 ({self.screenshot_area['width']}x{self.screenshot_area['height']})")
        self.save_area_config()
        self.log(f"已设置为全屏")

    def set_area_halfscreen(self, position):
        """设置半屏区域"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        if position == 'left':
            area = {'x': 0, 'y': 0, 'width': screen_width // 2, 'height': screen_height}
            label = "左半屏"
        elif position == 'right':
            area = {'x': screen_width // 2, 'y': 0, 'width': screen_width // 2, 'height': screen_height}
            label = "右半屏"
        elif position == 'top':
            area = {'x': 0, 'y': 0, 'width': screen_width, 'height': screen_height // 2}
            label = "上半屏"
        elif position == 'bottom':
            area = {'x': 0, 'y': screen_height // 2, 'width': screen_width, 'height': screen_height // 2}
            label = "下半屏"
        else:
            return

        self.screenshot_area = area
        self.area_label.config(text=f"区域: {label} ({area['width']}x{area['height']})")
        self.save_area_config()
        self.log(f"已设置为{label}")

    def start_area_selection(self):
        """开始选择区域"""
        self.log("正在打开区域选择窗口...")
        self.log("💡 提示：用鼠标拖动框选你的文档内容区域")

        # 延迟一下，让用户看到提示
        self.root.after(500, self.do_area_selection)

    def do_area_selection(self):
        """执行区域选择"""
        # 隐藏主窗口
        self.root.withdraw()

        # 创建选择窗口
        selector = AreaSelectorWindow(self.root, self.on_area_selected)
        selector.show()

    def on_area_selected(self, area):
        """区域选择完成回调"""
        if area:
            self.screenshot_area = area
            self.area_label.config(text=f"区域: {area['width']}x{area['height']} @ ({area['x']}, {area['y']})")
            self.save_area_config()
            self.log(f"区域已选择: {area['width']}x{area['height']} @ ({area['x']}, {area['y']})")
        else:
            self.log("区域选择已取消")

        self.root.deiconify()

    def save_area_config(self):
        """保存区域配置"""
        if self.screenshot_area:
            with open("area_config.txt", "w") as f:
                f.write(f"{self.screenshot_area['x']},{self.screenshot_area['y']},{self.screenshot_area['width']},{self.screenshot_area['height']}")

    def load_area_config(self):
        """加载区域配置"""
        try:
            with open("area_config.txt", "r") as f:
                coords = f.read().strip().split(",")
                return {
                    "x": int(coords[0]),
                    "y": int(coords[1]),
                    "width": int(coords[2]),
                    "height": int(coords[3])
                }
        except:
            return None

    def test_screenshot(self):
        """测试截图"""
        if not self.screenshot_area:
            area = self.load_area_config()
            if not area:
                messagebox.showwarning("提示", "请先选择截图区域")
                return
            self.screenshot_area = area
            self.area_label.config(text=f"区域: {area['width']}x{area['height']} @ ({area['x']}, {area['y']})")

        try:
            image = self.capture_area()
            self.show_preview(image)
            self.log("测试截图成功")
        except Exception as e:
            self.log(f"截图失败: {e}")
            messagebox.showerror("错误", f"截图失败: {e}")

    def capture_area(self):
        """截图指定区域"""
        with mss.mss() as sct:
            monitor = {
                "top": self.screenshot_area['y'],
                "left": self.screenshot_area['x'],
                "width": self.screenshot_area['width'],
                "height": self.screenshot_area['height']
            }
            screenshot = sct.grab(monitor)
            return Image.frombytes("RGB", screenshot.size, screenshot.rgb)

    def show_preview(self, image):
        """显示预览"""
        # 调整图片大小以适应预览区域
        preview_width = self.preview_frame.winfo_width() - 40
        preview_height = self.preview_frame.winfo_height() - 40

        if preview_width > 100 and preview_height > 100:
            ratio = min(preview_width / image.width, preview_height / image.height)
            if ratio < 1:
                new_width = int(image.width * ratio)
                new_height = int(image.height * ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(image)
        self.preview_label.config(image=photo, text="")
        self.preview_label.image = photo  # 保持引用

    # ====== API 配置 ======

    def load_api_config(self):
        """加载 API 配置"""
        config = {
            "enabled": False,
            "provider": "zhipu",
            "api_key": "",
            "base_url": "",
            "model": ""
        }
        if os.path.exists("api_config.json"):
            try:
                with open("api_config.json", "r", encoding="utf-8") as f:
                    config.update(json.load(f))
            except:
                pass
        return config

    def save_api_config(self):
        """保存 API 配置"""
        with open("api_config.json", "w", encoding="utf-8") as f:
            json.dump(self.api_config, f, indent=2, ensure_ascii=False)

    def get_api_status(self):
        """获取 API 状态文本"""
        if not API_AVAILABLE:
            return "⚠️ 未安装 openai 库"
        if self.api_config.get("enabled"):
            provider = self.api_config.get("provider", "unknown")
            model = self.api_config.get("model", "unknown")
            return f"✅ {provider} / {model}"
        return "未配置"

    def open_api_config(self):
        """打开 API 配置窗口"""
        dialog = tk.Toplevel(self.root)
        dialog.title("API 配置")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (450 // 2)
        dialog.geometry(f"500x450+{x}+{y}")

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # 提供商选择
        ttk.Label(frame, text="API 提供商:", font=('', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=(0, 10))
        provider_var = tk.StringVar(value=self.api_config.get("provider", "zhipu"))

        provider_frame = ttk.Frame(frame)
        provider_frame.grid(row=0, column=1, sticky='w', pady=(0, 10), columnspan=2)

        providers = {
            "zhipu": "智谱 AI",
            "deepseek": "DeepSeek",
            "custom": "自定义"
        }

        for i, (value, label) in enumerate(providers.items()):
            row = i // 2
            col = (i % 2) * 2
            ttk.Radiobutton(
                provider_frame,
                text=label,
                variable=provider_var,
                value=value,
                command=lambda v=value: self.update_api_fields(v, base_url_entry, model_entry)
            ).grid(row=row, column=col, sticky='w', padx=(0, 20))

        # Base URL
        ttk.Label(frame, text="Base URL:").grid(row=1, column=0, sticky='w', pady=(0, 10))
        base_url_entry = ttk.Entry(frame, width=35)
        base_url_entry.grid(row=1, column=1, columnspan=2, sticky='ew', pady=(0, 10))

        # 模型
        ttk.Label(frame, text="模型:").grid(row=2, column=0, sticky='w', pady=(0, 10))
        model_entry = ttk.Entry(frame, width=35)
        model_entry.grid(row=2, column=1, columnspan=2, sticky='ew', pady=(0, 10))

        # 常用模型提示
        model_hint = ttk.Label(frame, text="提示: glm-4-air(便宜) / glm-4v(高精度) / deepseek-chat", font=('', 8), foreground='gray')
        model_hint.grid(row=3, column=1, columnspan=2, sticky='w', pady=(0, 10))

        # API Key
        ttk.Label(frame, text="API Key:", font=('', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=(0, 10))
        api_key_entry = ttk.Entry(frame, width=35, show="*")
        api_key_entry.grid(row=4, column=1, columnspan=2, sticky='ew', pady=(0, 10))

        # 填充现有配置
        if self.api_config.get("api_key"):
            provider_var.set(self.api_config.get("provider", "zhipu"))
            base_url_entry.insert(0, self.api_config.get("base_url", ""))
            model_entry.insert(0, self.api_config.get("model", ""))
            api_key_entry.insert(0, self.api_config.get("api_key", ""))

        self.update_api_fields(provider_var.get(), base_url_entry, model_entry)

        # 按钮
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=(20, 0))

        def save():
            self.api_config = {
                "enabled": True,
                "provider": provider_var.get(),
                "base_url": base_url_entry.get().strip(),
                "model": model_entry.get().strip(),
                "api_key": api_key_entry.get().strip()
            }
            self.save_api_config()
            self.api_status_label.config(text=self.get_api_status())
            self.log(f"API 配置已更新: {provider_var.get()} / {model_entry.get()}")
            messagebox.showinfo("成功", "API 配置已保存！")
            dialog.destroy()

        ttk.Button(btn_frame, text="保存", command=save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT)

    def update_api_fields(self, provider, base_url_entry, model_entry):
        """根据提供商更新字段"""
        configs = {
            "zhipu": {
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "model": "glm-4-air"
            },
            "deepseek": {
                "base_url": "https://api.deepseek.com/v1",
                "model": "deepseek-chat"
            },
            "custom": {
                "base_url": "",
                "model": ""
            }
        }

        config = configs.get(provider, {})
        base_url_entry.delete(0, tk.END)
        base_url_entry.insert(0, config.get("base_url", ""))

        model_entry.delete(0, tk.END)
        model_entry.insert(0, config.get("model", ""))

    # ====== 提取流程 ======

    def start_extraction(self):
        """开始提取"""
        # 检查区域
        if not self.screenshot_area:
            area = self.load_area_config()
            if not area:
                messagebox.showwarning("提示", "请先选择截图区域\n\n可以使用「快速选择」或「自定义选择」")
                return
            self.screenshot_area = area
            self.area_label.config(text=f"区域: {area['width']}x{area['height']} @ ({area['x']}, {area['y']})")

        # 检查 API
        use_api = self.ocr_mode.get() == "api"
        if use_api:
            if not API_AVAILABLE:
                messagebox.showerror("错误", "未安装 openai 库\n请运行: pip install openai")
                return
            if not self.api_config.get("enabled"):
                messagebox.showwarning("提示", "请先配置 API")
                return

        # 启动提取线程
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="运行中...", foreground='blue')

        # 在新线程中运行提取
        thread = threading.Thread(target=self.extraction_thread, args=(use_api,))
        thread.daemon = True
        thread.start()

    def stop_extraction(self):
        """停止提取"""
        self.is_running = False
        self.log("正在停止...")
        self.status_label.config(text="停止中...", foreground='orange')

    def extraction_thread(self, use_api):
        """提取线程"""
        try:
            # 准备
            scroll_pause = float(self.scroll_pause.get())
            max_screens = 100

            # 创建保存目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.screenshot_dir = f"screenshots_{timestamp}"
            os.makedirs(self.screenshot_dir, exist_ok=True)

            self.put_message(("log", f"开始提取，间隔: {scroll_pause}秒"))
            self.put_message(("log", "5秒后开始，请确保云桌面窗口已激活"))

            time.sleep(5)

            screen_count = 0
            prev_image = None
            duplicate_count = 0
            self.screenshots = []

            while self.is_running and screen_count < max_screens:
                # 截图
                image = self.capture_area()
                screenshot_path = os.path.join(self.screenshot_dir, f"screen_{screen_count:03d}.png")
                image.save(screenshot_path)
                self.screenshots.append(image)

                self.put_message(("progress", screen_count + 1))
                self.put_message(("preview", image))

                # 检查重复
                if prev_image is not None:
                    diff = sum(abs(a - b) for a, b in zip(image.tobytes(), prev_image.tobytes()))
                    if diff < 1000:
                        duplicate_count += 1
                        self.put_message(("log", f"检测到重复内容 ({duplicate_count}/3)"))
                        if duplicate_count >= 3:
                            self.put_message(("log", "文档已到底，停止截图"))
                            break
                    else:
                        duplicate_count = 0

                prev_image = image
                screen_count += 1

                # 滚动
                if self.is_running and screen_count < max_screens:
                    pyautogui.press('pagedown')
                    time.sleep(scroll_pause)

            self.put_message(("log", f"截图完成，共 {len(self.screenshots)} 张"))

            # OCR
            if self.is_running:
                self.put_message(("log", "开始 OCR 识别..."))
                self.put_message(("status", "OCR 识别中...", "blue"))

                all_text = []
                for i, image in enumerate(self.screenshots):
                    if not self.is_running:
                        break

                    screenshot_path = os.path.join(self.screenshot_dir, f"screen_{i:03d}.png")
                    self.put_message(("log", f"识别中 {i+1}/{len(self.screenshots)}"))

                    if use_api:
                        text = self.ocr_with_api(screenshot_path)
                        if text is None:
                            self.put_message(("log", f"图片 {i+1} API 失败"))
                            continue
                    else:
                        # 本地 OCR（需要 pytesseract）
                        try:
                            import pytesseract
                            text = pytesseract.image_to_string(image, lang="chi_sim+eng")
                        except:
                            text = f"[图片 {i+1} - 本地 OCR 未配置]"

                    all_text.append(text)
                    self.put_message(("progress_ocr", i + 1, len(self.screenshots)))

                result = "\n\n".join(all_text)

                # 保存结果
                output_file = f"extracted_text_{timestamp}.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(result)

                self.put_message(("result", result, output_file))
                self.put_message(("log", f"结果已保存到: {output_file}"))

            self.put_message(("finish", len(self.screenshots)))

        except Exception as e:
            self.put_message(("error", str(e)))

    def ocr_with_api(self, image_path):
        """使用 API 进行 OCR"""
        try:
            client = OpenAI(
                api_key=self.api_config["api_key"],
                base_url=self.api_config["base_url"]
            )

            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode()

            response = client.chat.completions.create(
                model=self.api_config["model"],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请识别这张图片中的所有文字内容。如果包含表格，请用 Markdown 表格格式输出。如果包含公式，请用 LaTeX 格式输出。只输出文字内容，不要有其他说明。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000
            )

            return response.choices[0].message.content
        except Exception as e:
            return None

    def put_message(self, msg):
        """发送消息到队列"""
        self.message_queue.put(msg)

    def check_message_queue(self):
        """检查消息队列"""
        while not self.message_queue.empty():
            msg = self.message_queue.get()

            if msg[0] == "log":
                self.log(msg[1])

            elif msg[0] == "preview":
                self.show_preview(msg[1])

            elif msg[0] == "progress":
                count = msg[1]
                self.progress_label.config(text=f"截图: {count} 张")

            elif msg[0] == "progress_ocr":
                current, total = msg[1], msg[2]
                pct = (current / total) * 100
                self.progress['value'] = pct
                self.progress_label.config(text=f"OCR: {current}/{total}")

            elif msg[0] == "status":
                self.status_label.config(text=msg[1], foreground=msg[2])

            elif msg[0] == "result":
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(1.0, msg[1])
                self.notebook.select(1)  # 切换到结果页

            elif msg[0] == "finish":
                self.is_running = False
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.status_label.config(text=f"完成！共提取 {msg[1]} 页", foreground='green')
                self.progress_label.config(text="")
                self.progress['value'] = 0

            elif msg[0] == "error":
                self.log(f"错误: {msg[1]}")
                messagebox.showerror("错误", msg[1])
                self.is_running = False
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
                self.status_label.config(text="出错", foreground='red')

        self.root.after(100, self.check_message_queue)

    def log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def copy_result(self):
        """复制结果"""
        text = self.result_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.log("已复制到剪贴板")

    def save_result(self):
        """保存结果"""
        text = self.result_text.get(1.0, tk.END)
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("Markdown", "*.md"), ("所有文件", "*.*")]
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            self.log(f"已保存到: {filepath}")


class AreaSelectorWindow:
    """区域选择窗口"""

    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.window = None
        self.canvas = None
        self.start_x = None
        self.start_y = None
        self.rect = None

    def show(self):
        """显示选择窗口"""
        # 创建全屏窗口
        self.window = tk.Toplevel(self.parent)
        self.window.attributes('-fullscreen', True)
        self.window.attributes('-alpha', 0.3)
        self.window.configure(bg='gray')

        self.canvas = tk.Canvas(self.window, bg='', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定事件
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        self.window.bind('<Escape>', self.on_cancel)

        # 显示提示文本
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        self.canvas.create_text(
            screen_width // 2,
            screen_height // 2,
            text="用鼠标拖动选择区域\n完成后按 ESC 取消或松开鼠标确认",
            fill='white',
            font=('Arial', 18),
            justify='center'
        )

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

        x = min(self.start_x, event.x)
        y = min(self.start_y, event.y)
        width = abs(event.x - self.start_x)
        height = abs(event.y - self.start_y)

        self.window.destroy()

        if width > 10 and height > 10:
            self.callback({
                'x': x,
                'y': y,
                'width': width,
                'height': height
            })
        else:
            self.callback(None)

    def on_cancel(self, event):
        self.window.destroy()
        self.callback(None)


def main():
    root = tk.Tk()
    app = DocExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()