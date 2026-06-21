"""
GUI 样式系统
提供统一的界面样式和主题
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional, List


class AppStyles:
    """应用程序样式类"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.colors = {
            # iOS 风格配色
            'primary': '#007AFF',      # 蓝色
            'secondary': '#34C759',    # 绿色
            'accent': '#FF9500',       # 橙色
            'destructive': '#FF3B30',  # 红色

            # 背景色
            'bg_primary': '#F2F2F7',   # 浅灰色
            'bg_secondary': '#FFFFFF', # 白色
            'bg_tertiary': '#E5E5EA',  # 中灰色

            # 文字色
            'text_primary': '#000000', # 黑色
            'text_secondary': '#8E8E93', # 深灰色
            'text_tertiary': '#C7C7CC', # 浅灰色

            # 边框色
            'border': '#C6C6C8',      # 边框灰色
            'separator': '#E5E5EA',    # 分隔线
        }

        # 字体配置
        self.fonts = {
            'large': ('SF Pro Display', 20, 'bold'),
            'title': ('SF Pro Display', 18, 'bold'),
            'heading': ('SF Pro Display', 16, 'bold'),
            'subheading': ('SF Pro Display', 14, 'normal'),
            'body': ('SF Pro Text', 13, 'normal'),
            'caption': ('SF Pro Text', 11, 'normal'),
            'small': ('SF Pro Text', 10, 'normal'),
        }

        # 设置主题
        self._apply_theme()

    def _apply_theme(self):
        """应用主题到整个应用程序"""
        # 设置窗口背景
        self.root.configure(bg=self.colors['bg_primary'])

        # 配置 ttk 主题
        style = ttk.Style()

        # 使用 'clam' 主题作为基础
        style.theme_use('clam')

        # 配置各种组件的样式
        self._configure_styles(style)

    def _configure_styles(self, style: ttk.Style):
        """配置 ttk 组件样式"""
        # 主框架样式
        style.configure('Frame.TFrame',
                        background=self.colors['bg_primary'],
                        relief='flat')

        # 标签样式
        style.configure('Title.TLabel',
                        font=self.fonts['title'],
                        background=self.colors['bg_primary'],
                        foreground=self.colors['text_primary'])

        style.configure('Heading.TLabel',
                        font=self.fonts['heading'],
                        background=self.colors['bg_primary'],
                        foreground=self.colors['text_primary'])

        style.configure('Subheading.TLabel',
                        font=self.fonts['subheading'],
                        background=self.colors['bg_primary'],
                        foreground=self.colors['text_secondary'])

        style.configure('Body.TLabel',
                        font=self.fonts['body'],
                        background=self.colors['bg_primary'],
                        foreground=self.colors['text_primary'])

        style.configure('Caption.TLabel',
                        font=self.fonts['caption'],
                        background=self.colors['bg_primary'],
                        foreground=self.colors['text_secondary'])

        # 按钮样式
        self._configure_button_styles(style)

        # 输入框样式
        self._configure_entry_styles(style)

        # 文本框样式
        self._configure_text_styles(style)

        # 进度条样式
        self._configure_progress_style(style)

        # 分隔符样式
        self._configure_separator_style(style)

        # 选项卡样式
        self._configure_notebook_style(style)

    def _configure_button_styles(self, style: ttk.Style):
        """配置按钮样式"""
        # 主要按钮
        style.configure('Primary.TButton',
                        font=self.fonts['subheading'],
                        background=self.colors['primary'],
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        padding=(20, 10))

        style.map('Primary.TButton',
                  background=[('active', '#0051D5'),
                             ('pressed', '#0051D5')])

        # 次要按钮
        style.configure('Secondary.TButton',
                        font=self.fonts['subheading'],
                        background=self.colors['bg_secondary'],
                        foreground=self.colors['primary'],
                        borderwidth=1,
                        focuscolor='none',
                        padding=(20, 10))

        style.map('Secondary.TButton',
                  background=[('active', self.colors['bg_tertiary']),
                             ('pressed', self.colors['bg_tertiary'])],
                  foreground=[('active', self.colors['primary'])])

        # 虚线按钮
        style.configure('Ghost.TButton',
                        font=self.fonts['subheading'],
                        background='transparent',
                        foreground=self.colors['primary'],
                        borderwidth=0,
                        focuscolor='none',
                        padding=(20, 10))

        # 危险按钮
        style.configure('Destructive.TButton',
                        font=self.fonts['subheading'],
                        background=self.colors['destructive'],
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        padding=(20, 10))

        # 圆角按钮
        style.configure('Round.TButton',
                        font=self.fonts['subheading'],
                        background=self.colors['primary'],
                        foreground='white',
                        borderwidth=0,
                        focuscolor='none',
                        padding=(16, 8),
                        relief='flat')

    def _configure_entry_styles(self, style: ttk.Style):
        """配置输入框样式"""
        style.configure('Standard.TEntry',
                        font=self.fonts['body'],
                        background=self.colors['bg_secondary'],
                        foreground=self.colors['text_primary'],
                        borderwidth=1,
                        relief='solid',
                        fieldbackground=self.colors['bg_secondary'],
                        padding=(10, 8))

        style.map('Standard.TEntry',
                  background=[('focus', self.colors['bg_secondary'])],
                  relief=[('focus', 'solid')])

    def _configure_text_styles(self, style: ttk.Style):
        """配置文本框样式"""
        style.configure('Standard.TText',
                        font=self.fonts['body'],
                        background=self.colors['bg_secondary'],
                        foreground=self.colors['text_primary'],
                        borderwidth=1,
                        relief='solid',
                        padding=(10, 8),
                        wrap='word')

        style.map('Standard.TText',
                  background=[('focus', self.colors['bg_secondary'])],
                  relief=[('focus', 'solid')])

    def _configure_progress_style(self, style: ttk.Style):
        """配置进度条样式"""
        style.configure('Standard.TProgressbar',
                        background=self.colors['primary'],
                        troughcolor=self.colors['bg_tertiary'],
                        borderwidth=0,
                        lightcolor=self.colors['primary'],
                        darkcolor=self.colors['primary'])

    def _configure_separator_style(self, style: ttk.Style):
        """配置分隔符样式"""
        style.configure('Separator.TFrame',
                        background=self.colors['separator'])

    def _configure_notebook_style(self, style: ttk.Style):
        """配置选项卡样式"""
        style.configure('Notebook.TNotebook',
                        background=self.colors['bg_primary'],
                        tabposition='top')

        style.configure('Notebook.TNotebook.Tab',
                        background=self.colors['bg_secondary'],
                        foreground=self.colors['text_primary'],
                        padding=(20, 12),
                        font=self.fonts['subheading'])

        style.map('Notebook.TNotebook.Tab',
                  background=[('selected', self.colors['primary']),
                             ('active', self.colors['bg_tertiary'])],
                  foreground=[('selected', 'white'),
                            ('active', self.colors['text_primary'])])

    def create_frame(self, parent, **grid_options) -> tk.Frame:
        """创建样式化的框架"""
        frame = tk.Frame(parent,
                        bg=self.colors['bg_primary'],
                        highlightthickness=0)
        frame.grid(**grid_options, sticky='nsew', padx=10, pady=10)
        return frame

    def create_label(self, parent, text: str, style: str = 'Body', **grid_options) -> tk.Label:
        """创建样式化的标签"""
        label = tk.Label(parent,
                         text=text,
                         font=self.fonts[style.split('.')[0]],
                         bg=self.colors['bg_primary'],
                         fg=self.colors['text_primary'])
        label.grid(**grid_options, sticky='w')
        return label

    def create_button(self, parent, text: str, style: str = 'Secondary', **grid_options) -> ttk.Button:
        """创建样式化的按钮"""
        button = ttk.Button(parent,
                           text=text,
                           style=style,
                           cursor='hand2')
        button.grid(**grid_options, sticky='ew', padx=5)
        return button

    def create_entry(self, parent, **grid_options) -> ttk.Entry:
        """创建样式化的输入框"""
        entry = ttk.Entry(parent,
                         style='Standard.TEntry',
                         font=self.fonts['body'])
        entry.grid(**grid_options, sticky='ew', padx=5, pady=5)
        return entry

    def create_text(self, parent, height: int = 5, **grid_options) -> tk.Text:
        """创建样式化的文本框"""
        text = tk.Text(parent,
                      height=height,
                      font=self.fonts['body'],
                      bg=self.colors['bg_secondary'],
                      fg=self.colors['text_primary'],
                      relief='solid',
                      borderwidth=1,
                      wrap='word')
        text.grid(**grid_options, sticky='nsew', padx=5, pady=5)
        return text

    def create_separator(self, parent, **grid_options) -> tk.Frame:
        """创建分隔符"""
        separator = tk.Frame(parent,
                            height=1,
                            bg=self.colors['separator'])
        separator.grid(**grid_options, sticky='ew', padx=10, pady=5)
        return separator

    def configure_grid(self, parent: tk.Widget, rows: int, cols: int, **options):
        """配置网格布局"""
        options.setdefault('padx', 10)
        options.setdefault('pady', 10)

        for i in range(rows):
            parent.grid_rowconfigure(i, weight=1)
        for j in range(cols):
            parent.grid_columnconfigure(j, weight=1)

    def get_color(self, color_name: str) -> str:
        """获取颜色值"""
        return self.colors.get(color_name, '#000000')

    def get_font(self, style_name: str) -> tuple:
        """获取字体配置"""
        return self.fonts.get(style_name, self.fonts['body'])


class ThemeManager:
    """主题管理器"""

    def __init__(self):
        self.themes = {
            'light': {
                'name': '浅色主题',
                'colors': {
                    'primary': '#007AFF',
                    'secondary': '#34C759',
                    'accent': '#FF9500',
                    'destructive': '#FF3B30',
                    'bg_primary': '#F2F2F7',
                    'bg_secondary': '#FFFFFF',
                    'bg_tertiary': '#E5E5EA',
                    'text_primary': '#000000',
                    'text_secondary': '#8E8E93',
                    'text_tertiary': '#C7C7CC',
                    'border': '#C6C6C8',
                    'separator': '#E5E5EA',
                }
            },
            'dark': {
                'name': '深色主题',
                'colors': {
                    'primary': '#0A84FF',
                    'secondary': '#32D74B',
                    'accent': '#FF9F0A',
                    'destructive': '#FF453A',
                    'bg_primary': '#000000',
                    'bg_secondary': '#1C1C1E',
                    'bg_tertiary': '#2C2C2E',
                    'text_primary': '#FFFFFF',
                    'text_secondary': '#8E8E93',
                    'text_tertiary': '#C7C7CC',
                    'border': '#38383A',
                    'separator': '#38383A',
                }
            }
        }

    def get_theme(self, theme_name: str = 'light') -> Dict[str, Any]:
        """获取主题配置"""
        return self.themes.get(theme_name, self.themes['light'])

    def get_available_themes(self) -> List[str]:
        """获取可用主题列表"""
        return list(self.themes.keys())


# 全局样式实例
_global_styles: Optional[AppStyles] = None


def get_styles(root: tk.Tk = None) -> AppStyles:
    """获取全局样式实例"""
    global _global_styles
    if _global_styles is None and root is not None:
        _global_styles = AppStyles(root)
    return _global_styles


def apply_styles_to_widget(widget: tk.Widget, styles: AppStyles):
    """应用样式到组件"""
    if isinstance(widget, tk.Label):
        widget.configure(
            font=styles.get_font('body'),
            bg=styles.get_color('bg_primary'),
            fg=styles.get_color('text_primary')
        )
    elif isinstance(widget, tk.Button):
        widget.configure(
            font=styles.get_font('subheading'),
            bg=styles.get_color('primary'),
            fg='white',
            activebackground=styles.get_color('primary'),
            cursor='hand2'
        )