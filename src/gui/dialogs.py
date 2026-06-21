"""
GUI 对话框模块
实现各种对话框和弹窗组件
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional, Tuple, Callable
import os
import json
from datetime import datetime

from .styles import AppStyles


class ConfigDialog:
    """配置对话框"""

    def __init__(self, parent, config: Dict[str, Any]):
        self.parent = parent
        self.config = config.copy()
        self.result = None
        self.dialog = None
        self.styles = AppStyles(parent)

    def show(self) -> Optional[Dict[str, Any]]:
        """显示配置对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("配置设置")
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)

        # 设置模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 创建主框架
        main_frame = self.styles.create_frame(self.dialog)
        main_frame.pack(fill='both', expand=True)

        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # API 配置选项卡
        api_frame = self._create_api_tab(notebook)
        notebook.add(api_frame, text="API 配置")

        # 偏好设置选项卡
        pref_frame = self._create_preferences_tab(notebook)
        notebook.add(pref_frame, text="偏好设置")

        # 高级选项卡
        adv_frame = self._create_advanced_tab(notebook)
        notebook.add(adv_frame, text="高级")

        # 按钮区域
        button_frame = tk.Frame(self.dialog, bg=self.styles.get_color('bg_primary'))
        button_frame.pack(fill='x', padx=10, pady=10)

        self.styles.create_button(button_frame, "取消", "Secondary",
                                command=self._cancel).pack(side='right', padx=5)
        self.styles.create_button(button_frame, "应用", "Primary",
                                command=self._apply).pack(side='right', padx=5)

        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # 等待对话框关闭
        self.dialog.wait_window()

        return self.result

    def _create_api_tab(self, parent) -> tk.Frame:
        """创建 API 配置选项卡"""
        frame = tk.Frame(parent, bg=self.styles.get_color('bg_primary'))

        # 启用 API
        enabled_var = tk.BooleanVar(value=self.config.get('enabled', False))
        cb_enabled = tk.Checkbutton(frame, text="启用 API OCR", variable=enabled_var,
                                   bg=self.styles.get_color('bg_primary'),
                                   font=self.styles.get_font('subheading'))
        cb_enabled.pack(anchor='w', padx=20, pady=10)

        # 提供商选择
        tk.Label(frame, text="OCR 提供商:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        provider_var = tk.StringVar(value=self.config.get('provider', 'tesseract'))
        providers = [
            ('Tesseract (本地)', 'tesseract'),
            ('智谱 AI', 'zhipu'),
            ('DeepSeek', 'deepseek'),
            ('OpenAI', 'openai')
        ]

        for text, value in providers:
            rb = tk.Radiobutton(frame, text=text, variable=provider_var, value=value,
                               bg=self.styles.get_color('bg_primary'),
                               font=self.styles.get_font('body'))
            rb.pack(anchor='w', padx=40, pady=2)

        # API 密钥
        tk.Label(frame, text="API 密钥:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(15, 0))

        api_key_var = tk.StringVar(value=self.config.get('api_key', ''))
        entry_api_key = tk.Entry(frame, textvariable=api_key_var, show='*',
                                font=self.styles.get_font('body'), width=40)
        entry_api_key.pack(anchor='w', padx=40, pady=5)

        # 模型选择
        tk.Label(frame, text="模型名称:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        model_var = tk.StringVar(value=self.config.get('model', ''))
        entry_model = tk.Entry(frame, textvariable=model_var,
                              font=self.styles.get_font('body'), width=40)
        entry_model.pack(anchor='w', padx=40, pady=5)

        # Base URL
        tk.Label(frame, text="Base URL (可选):", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        base_url_var = tk.StringVar(value=self.config.get('base_url', ''))
        entry_base_url = tk.Entry(frame, textvariable=base_url_var,
                                  font=self.styles.get_font('body'), width=40)
        entry_base_url.pack(anchor='w', padx=40, pady=5)

        # 存储变量
        self._api_vars = {
            'enabled': enabled_var,
            'provider': provider_var,
            'api_key': api_key_var,
            'model': model_var,
            'base_url': base_url_var
        }

        return frame

    def _create_preferences_tab(self, parent) -> tk.Frame:
        """创建偏好设置选项卡"""
        frame = tk.Frame(parent, bg=self.styles.get_color('bg_primary'))

        # 滚动设置
        tk.Label(frame, text="滚动设置", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('heading')).pack(anchor='w', padx=20, pady=(10, 5))

        # 滚动方向
        tk.Label(frame, text="滚动方向:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        scroll_dir_var = tk.StringVar(value=self.config.get('scroll_direction', 'down'))
        directions = [('向下', 'down'), ('向上', 'up')]
        for text, value in directions:
            rb = tk.Radiobutton(frame, text=text, variable=scroll_dir_var, value=value,
                               bg=self.styles.get_color('bg_primary'),
                               font=self.styles.get_font('body'))
            rb.pack(anchor='w', padx=40, pady=2)

        # 滚动间隔
        tk.Label(frame, text="滚动间隔 (秒):", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        scroll_interval_var = tk.StringVar(value=str(self.config.get('scroll_interval', 3.0)))
        entry_interval = tk.Entry(frame, textvariable=scroll_interval_var,
                                  font=self.styles.get_font('body'), width=10)
        entry_interval.pack(anchor='w', padx=40, pady=5)

        # 输出设置
        tk.Label(frame, text="输出设置", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('heading')).pack(anchor='w', padx=20, pady=(20, 5))

        # 输出格式
        tk.Label(frame, text="输出格式:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        output_format_var = tk.StringVar(value=self.config.get('output_format', 'txt'))
        formats = [('文本 (.txt)', 'txt'), ('Markdown (.md)', 'md'), ('JSON (.json)', 'json')]
        for text, value in formats:
            rb = tk.Radiobutton(frame, text=text, variable=output_format_var, value=value,
                               bg=self.styles.get_color('bg_primary'),
                               font=self.styles.get_font('body'))
            rb.pack(anchor='w', padx=40, pady=2)

        # 自动保存
        auto_save_var = tk.BooleanVar(value=self.config.get('auto_save', True))
        cb_auto_save = tk.Checkbutton(frame, text="自动保存结果", variable=auto_save_var,
                                    bg=self.styles.get_color('bg_primary'),
                                    font=self.styles.get_font('body'))
        cb_auto_save.pack(anchor='w', padx=40, pady=10)

        # 日志级别
        tk.Label(frame, text="日志级别:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        log_level_var = tk.StringVar(value=self.config.get('log_level', 'INFO'))
        levels = [('调试', 'DEBUG'), ('信息', 'INFO'), ('警告', 'WARNING'), ('错误', 'ERROR')]
        for text, value in levels:
            rb = tk.Radiobutton(frame, text=text, variable=log_level_var, value=value,
                               bg=self.styles.get_color('bg_primary'),
                               font=self.styles.get_font('body'))
            rb.pack(anchor='w', padx=40, pady=2)

        # 存储变量
        self._pref_vars = {
            'scroll_direction': scroll_dir_var,
            'scroll_interval': scroll_interval_var,
            'output_format': output_format_var,
            'auto_save': auto_save_var,
            'log_level': log_level_var
        }

        return frame

    def _create_advanced_tab(self, parent) -> tk.Frame:
        """创建高级选项卡"""
        frame = tk.Frame(parent, bg=self.styles.get_color('bg_primary'))

        # OCR 设置
        tk.Label(frame, text="OCR 设置", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('heading')).pack(anchor='w', padx=20, pady=(10, 5))

        # Tesseract 语言
        tk.Label(frame, text="Tesseract 语言:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        tesseract_lang_var = tk.StringVar(value=self.config.get('tesseract_lang', 'chi_sim+eng'))
        entry_tesseract_lang = tk.Entry(frame, textvariable=tesseract_lang_var,
                                       font=self.styles.get_font('body'), width=30)
        entry_tesseract_lang.pack(anchor='w', padx=40, pady=5)

        # 最大 tokens
        tk.Label(frame, text="最大 tokens (API):", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        max_tokens_var = tk.StringVar(value=str(self.config.get('max_tokens', 4000)))
        entry_max_tokens = tk.Entry(frame, textvariable=max_tokens_var,
                                  font=self.styles.get_font('body'), width=10)
        entry_max_tokens.pack(anchor='w', padx=40, pady=5)

        # 重复检测
        tk.Label(frame, text="重复检测设置", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('heading')).pack(anchor='w', padx=20, pady=(20, 5))

        # 相似度阈值
        tk.Label(frame, text="相似度阈值:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        similarity_threshold_var = tk.StringVar(value=str(self.config.get('similarity_threshold', 0.95)))
        entry_similarity = tk.Entry(frame, textvariable=similarity_threshold_var,
                                    font=self.styles.get_font('body'), width=10)
        entry_similarity.pack(anchor='w', padx=40, pady=5)

        # 连续重复次数
        tk.Label(frame, text="连续重复次数:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(anchor='w', padx=20, pady=(10, 0))

        duplicate_count_var = tk.StringVar(value=str(self.config.get('duplicate_count', 3)))
        entry_duplicate = tk.Entry(frame, textvariable=duplicate_count_var,
                                  font=self.styles.get_font('body'), width=10)
        entry_duplicate.pack(anchor='w', padx=40, pady=5)

        # 存储变量
        self._adv_vars = {
            'tesseract_lang': tesseract_lang_var,
            'max_tokens': max_tokens_var,
            'similarity_threshold': similarity_threshold_var,
            'duplicate_count': duplicate_count_var
        }

        return frame

    def _apply(self):
        """应用配置"""
        # 更新 API 配置
        self.config.update({
            'enabled': self._api_vars['enabled'].get(),
            'provider': self._api_vars['provider'].get(),
            'api_key': self._api_vars['api_key'].get(),
            'model': self._api_vars['model'].get(),
            'base_url': self._api_vars['base_url'].get()
        })

        # 更新偏好设置
        try:
            self.config.update({
                'scroll_direction': self._pref_vars['scroll_direction'].get(),
                'scroll_interval': float(self._pref_vars['scroll_interval'].get()),
                'output_format': self._pref_vars['output_format'].get(),
                'auto_save': self._pref_vars['auto_save'].get(),
                'log_level': self._pref_vars['log_level'].get()
            })
        except ValueError:
            messagebox.showerror("错误", "滚动间隔必须是数字")
            return

        # 更新高级设置
        try:
            self.config.update({
                'tesseract_lang': self._adv_vars['tesseract_lang'].get(),
                'max_tokens': int(self._adv_vars['max_tokens'].get()),
                'similarity_threshold': float(self._adv_vars['similarity_threshold'].get()),
                'duplicate_count': int(self._adv_vars['duplicate_count'].get())
            })
        except ValueError:
            messagebox.showerror("错误", "高级设置必须是数字")
            return

        self.result = self.config
        self.dialog.destroy()

    def _cancel(self):
        """取消配置"""
        self.result = None
        self.dialog.destroy()


class AreaSelectionDialog:
    """区域选择对话框"""

    def __init__(self, parent, current_area: Optional[Tuple[int, int, int, int]] = None):
        self.parent = parent
        self.result = None
        self.dialog = None
        self.styles = AppStyles(parent)
        self.current_area = current_area

    def show(self) -> Optional[Tuple[int, int, int, int]]:
        """显示区域选择对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("选择提取区域")
        self.dialog.geometry("450x300")
        self.dialog.resizable(False, False)

        # 设置模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 创建主框架
        main_frame = self.styles.create_frame(self.dialog)
        main_frame.pack(fill='both', expand=True)

        # 输入区域
        input_frame = tk.Frame(main_frame, bg=self.styles.get_color('bg_primary'))
        input_frame.pack(fill='x', padx=20, pady=20)

        # 坐标输入
        tk.Label(input_frame, text="区域坐标:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('heading')).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # X 坐标
        tk.Label(input_frame, text="X:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).grid(row=1, column=0, sticky='e', padx=5)
        self.x_var = tk.StringVar(value=str(self.current_area[0]) if self.current_area else "0")
        entry_x = tk.Entry(input_frame, textvariable=self.x_var, font=self.styles.get_font('body'), width=10)
        entry_x.grid(row=1, column=1, sticky='w', padx=5)

        # Y 坐标
        tk.Label(input_frame, text="Y:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).grid(row=2, column=0, sticky='e', padx=5)
        self.y_var = tk.StringVar(value=str(self.current_area[1]) if self.current_area else "0")
        entry_y = tk.Entry(input_frame, textvariable=self.y_var, font=self.styles.get_font('body'), width=10)
        entry_y.grid(row=2, column=1, sticky='w', padx=5)

        # 宽度
        tk.Label(input_frame, text="宽度:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).grid(row=3, column=0, sticky='e', padx=5)
        self.width_var = tk.StringVar(value=str(self.current_area[2]) if self.current_area else "800")
        entry_width = tk.Entry(input_frame, textvariable=self.width_var, font=self.styles.get_font('body'), width=10)
        entry_width.grid(row=3, column=1, sticky='w', padx=5)

        # 高度
        tk.Label(input_frame, text="高度:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).grid(row=4, column=0, sticky='e', padx=5)
        self.height_var = tk.StringVar(value=str(self.current_area[3]) if self.current_area else "600")
        entry_height = tk.Entry(input_frame, textvariable=self.height_var, font=self.styles.get_font('body'), width=10)
        entry_height.grid(row=4, column=1, sticky='w', padx=5)

        # 快速选择按钮
        quick_frame = tk.Frame(main_frame, bg=self.styles.get_color('bg_primary'))
        quick_frame.pack(fill='x', padx=20, pady=10)

        tk.Label(quick_frame, text="快速选择:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(side='left')

        quick_buttons = [
            ("上半屏", self._set_half_top),
            ("下半屏", self._set_half_bottom),
            ("左半屏", self._set_half_left),
            ("右半屏", self._set_half_right),
            ("全屏", self._set_fullscreen)
        ]

        for text, command in quick_buttons:
            self.styles.create_button(quick_frame, text, "Secondary", command=command).pack(side='left', padx=5)

        # 按钮
        button_frame = tk.Frame(self.dialog, bg=self.styles.get_color('bg_primary'))
        button_frame.pack(fill='x', padx=10, pady=10)

        self.styles.create_button(button_frame, "取消", "Secondary",
                                command=self._cancel).pack(side='right', padx=5)
        self.styles.create_button(button_frame, "确定", "Primary",
                                command=self._confirm).pack(side='right', padx=5)

        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # 等待对话框关闭
        self.dialog.wait_window()

        return self.result

    def _set_half_top(self):
        """设置上半屏"""
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set(str(screen_width))
        self.height_var.set(str(screen_height // 2))

    def _set_half_bottom(self):
        """设置下半屏"""
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        self.x_var.set("0")
        self.y_var.set(str(screen_height // 2))
        self.width_var.set(str(screen_width))
        self.height_var.set(str(screen_height // 2))

    def _set_half_left(self):
        """设置左半屏"""
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set(str(screen_width // 2))
        self.height_var.set(str(screen_height))

    def _set_half_right(self):
        """设置右半屏"""
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        self.x_var.set(str(screen_width // 2))
        self.y_var.set("0")
        self.width_var.set(str(screen_width // 2))
        self.height_var.set(str(screen_height))

    def _set_fullscreen(self):
        """设置全屏"""
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        self.x_var.set("0")
        self.y_var.set("0")
        self.width_var.set(str(screen_width))
        self.height_var.set(str(screen_height))

    def _confirm(self):
        """确认选择"""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            width = int(self.width_var.get())
            height = int(self.height_var.get())

            if width <= 0 or height <= 0:
                messagebox.showerror("错误", "宽度和高度必须大于 0")
                return

            self.result = (x, y, width, height)
            self.dialog.destroy()

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def _cancel(self):
        """取消选择"""
        self.result = None
        self.dialog.destroy()


class ProgressDialog:
    """进度对话框"""

    def __init__(self, parent, title: str = "处理中..."):
        self.parent = parent
        self.dialog = None
        self.title = title
        self.styles = AppStyles(parent)

    def show(self):
        """显示进度对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)

        # 设置模态
        self.dialog.transient(self.parent)
        self.dialog.grab_set()

        # 创建主框架
        main_frame = self.styles.create_frame(self.dialog)
        main_frame.pack(fill='both', expand=True)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var,
                                          maximum=100, style='Standard.TProgressbar')
        self.progress_bar.pack(fill='x', padx=20, pady=20)

        # 进度文本
        self.progress_label = tk.Label(main_frame, text="准备中...",
                                     bg=self.styles.get_color('bg_primary'),
                                     font=self.styles.get_font('body'))
        self.progress_label.pack(pady=10)

        # 详情文本
        self.detail_label = tk.Label(main_frame, text="",
                                   bg=self.styles.get_color('bg_primary'),
                                   font=self.styles.get_font('caption'),
                                   fg=self.styles.get_color('text_secondary'))
        self.detail_label.pack(pady=5)

        # 取消按钮
        self.cancel_button = self.styles.create_button(main_frame, "取消", "Secondary",
                                                     command=self._cancel)
        self.cancel_button.pack(pady=10)

        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # 初始化变量
        self.should_cancel = False

    def update_progress(self, value: float, detail: str = ""):
        """更新进度"""
        if self.dialog:
            self.progress_var.set(value)
            if detail:
                self.detail_label.config(text=detail)
            self.dialog.update()

    def set_title(self, title: str):
        """设置标题"""
        if self.dialog:
            self.dialog.title(title)

    def set_progress_text(self, text: str):
        """设置进度文本"""
        if self.dialog:
            self.progress_label.config(text=text)

    def should_cancel_operation(self) -> bool:
        """检查是否应该取消操作"""
        return self.should_cancel

    def close(self):
        """关闭进度对话框"""
        if self.dialog:
            self.dialog.destroy()
            self.dialog = None

    def _cancel(self):
        """取消操作"""
        self.should_cancel = True
        self.progress_label.config(text="正在取消...")


class MessageDialog:
    """消息对话框"""

    @staticmethod
    def show_info(parent, title: str, message: str):
        """显示信息对话框"""
        messagebox.showinfo(title, message)

    @staticmethod
    def show_error(parent, title: str, message: str):
        """显示错误对话框"""
        messagebox.showerror(title, message)

    @staticmethod
    def show_warning(parent, title: str, message: str):
        """显示警告对话框"""
        messagebox.showwarning(title, message)

    @staticmethod
    def show_question(parent, title: str, message: str) -> bool:
        """显示确认对话框"""
        return messagebox.askyesno(title, message)


class FileDialog:
    """文件对话框"""

    @staticmethod
    def ask_save_file(parent, title: str, filetypes: list = None, initialfile: str = None) -> Optional[str]:
        """选择保存文件"""
        if filetypes is None:
            filetypes = [("所有文件", "*.*")]

        filename = filedialog.asksaveasfilename(
            parent=parent,
            title=title,
            filetypes=filetypes,
            initialfile=initialfile
        )
        return filename if filename else None

    @staticmethod
    def ask_open_file(parent, title: str, filetypes: list = None) -> Optional[str]:
        """选择打开文件"""
        if filetypes is None:
            filetypes = [("所有文件", "*.*")]

        filename = filedialog.askopenfilename(
            parent=parent,
            title=title,
            filetypes=filetypes
        )
        return filename if filename else None

    @staticmethod
    def ask_open_directory(parent, title: str) -> Optional[str]:
        """选择打开目录"""
        directory = filedialog.askdirectory(
            parent=parent,
            title=title
        )
        return directory if directory else None