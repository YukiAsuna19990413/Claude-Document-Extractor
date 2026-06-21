"""
GUI 主应用
实现图形界面应用程序
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import os
import json
import queue
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

from ..core.doc_extractor import DocExtractor
from ..core.config import config
from .styles import AppStyles
from .dialogs import ConfigDialog, AreaSelectionDialog, ProgressDialog, MessageDialog


class DocExtractorGUI:
    """文档提取工具 GUI 应用"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("文档提取工具")
        self.root.geometry("1100x750")

        # 样式
        self.styles = AppStyles(root)

        # 消息队列
        self.message_queue = queue.Queue()

        # 提取器实例
        self.extractor = DocExtractor()

        # 状态变量
        self.is_processing = False
        self.current_extraction = None
        self.log_messages = []

        # 创建界面
        self._create_menu()
        self._create_main_layout()
        self._create_control_panel()
        self._create_result_panel()
        self._create_status_bar()

        # 配置网格权重
        self.styles.configure_grid(self.root, rows=3, cols=1)

        # 定期检查消息队列
        self._check_messages()

    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存结果", command=self._save_results)
        file_menu.add_command(label="导出日志", command=self._export_logs)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="清除日志", command=self._clear_logs)
        edit_menu.add_command(label="复制文本", command=self._copy_text)

        # 设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="配置设置", command=self._show_config_dialog)
        settings_menu.add_command(label="选择区域", command=self._show_area_dialog)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)

    def _create_main_layout(self):
        """创建主布局"""
        # 主框架
        self.main_frame = tk.Frame(self.root, bg=self.styles.get_color('bg_primary'))
        self.main_frame.grid(row=0, column=0, sticky='nsew')

        # 创建选项卡
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # 控制选项卡
        self.control_tab = tk.Frame(self.notebook, bg=self.styles.get_color('bg_primary'))
        self.notebook.add(self.control_tab, text="控制面板")

        # 结果选项卡
        self.result_tab = tk.Frame(self.notebook, bg=self.styles.get_color('bg_primary'))
        self.notebook.add(self.result_tab, text="提取结果")

        # 日志选项卡
        self.log_tab = tk.Frame(self.notebook, bg=self.styles.get_color('bg_primary'))
        self.notebook.add(self.log_tab, text="运行日志")

    def _create_control_panel(self):
        """创建控制面板"""
        # 左侧框架
        left_frame = tk.Frame(self.control_tab, bg=self.styles.get_color('bg_primary'))
        left_frame.pack(side='left', fill='both', expand=True, padx=(10, 5), pady=10)

        # 右侧框架
        right_frame = tk.Frame(self.control_tab, bg=self.styles.get_color('bg_primary'))
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)

        # 区域设置
        area_frame = tk.Frame(left_frame, bg=self.styles.get_color('bg_primary'))
        area_frame.pack(fill='x', pady=(0, 10))

        tk.Label(area_frame, text="📸 截图区域", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('heading')).pack(anchor='w', pady=(0, 10))

        # 当前区域显示
        self.area_label = tk.Label(area_frame, text="未设置区域",
                                 bg=self.styles.get_color('bg_primary'),
                                 font=self.styles.get_font('body'),
                                 fg=self.styles.get_color('text_secondary'))
        self.area_label.pack(anchor='w', pady=5)

        # 区域按钮
        area_button_frame = tk.Frame(area_frame, bg=self.styles.get_color('bg_primary'))
        area_button_frame.pack(fill='x')

        self.styles.create_button(area_button_frame, "选择区域",
                                command=self._show_area_dialog).pack(side='left', padx=5)
        self.styles.create_button(area_button_frame, "快速选择",
                                command=self._quick_select_area).pack(side='left', padx=5)

        # OCR 设置
        ocr_frame = tk.Frame(left_frame, bg=self.styles.get_color('bg_primary'))
        ocr_frame.pack(fill='x', pady=(0, 10))

        tk.Label(ocr_frame, text="🔍 OCR 设置", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('heading')).pack(anchor='w', pady=(0, 10))

        # OCR 提供商
        self.provider_var = tk.StringVar(value=config.get('provider', 'tesseract'))
        providers = [
            ('Tesseract (本地)', 'tesseract'),
            ('智谱 AI', 'zhipu'),
            ('DeepSeek', 'deepseek'),
            ('OpenAI', 'openai')
        ]

        for text, value in providers:
            rb = tk.Radiobutton(ocr_frame, text=text, variable=self.provider_var, value=value,
                               bg=self.styles.get_color('bg_primary'),
                               font=self.styles.get_font('body'))
            rb.pack(anchor='w', pady=2)

        # 滚动设置
        scroll_frame = tk.Frame(right_frame, bg=self.styles.get_color('bg_primary'))
        scroll_frame.pack(fill='x', pady=(0, 10))

        tk.Label(scroll_frame, text="📄 滚动设置", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('heading')).pack(anchor='w', pady=(0, 10))

        # 滚动方向
        self.scroll_dir_var = tk.StringVar(value=config.get('scroll_direction', 'down'))
        directions_frame = tk.Frame(scroll_frame, bg=self.styles.get_color('bg_primary'))
        directions_frame.pack(fill='x')

        tk.Label(directions_frame, text="方向:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(side='left')
        tk.Radiobutton(directions_frame, text="向下", variable=self.scroll_dir_var, value='down',
                      bg=self.styles.get_color('bg_primary')).pack(side='left', padx=10)
        tk.Radiobutton(directions_frame, text="向上", variable=self.scroll_dir_var, value='up',
                      bg=self.styles.get_color('bg_primary')).pack(side='left', padx=10)

        # 滚动间隔
        interval_frame = tk.Frame(scroll_frame, bg=self.styles.get_color('bg_primary'))
        interval_frame.pack(fill='x', pady=5)

        tk.Label(interval_frame, text="间隔(秒):", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(side='left')
        self.interval_var = tk.StringVar(value=str(config.get('scroll_interval', 3.0)))
        interval_entry = tk.Entry(interval_frame, textvariable=self.interval_var,
                                font=self.styles.get_font('body'), width=10)
        interval_entry.pack(side='left', padx=10)

        # 提取设置
        extract_frame = tk.Frame(left_frame, bg=self.styles.get_color('bg_primary'))
        extract_frame.pack(fill='x', pady=(0, 10))

        tk.Label(extract_frame, text="⚙️ 提取设置", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('heading')).pack(anchor='w', pady=(0, 10))

        # 最大截图数
        max_screens_frame = tk.Frame(extract_frame, bg=self.styles.get_color('bg_primary'))
        max_screens_frame.pack(fill='x')

        tk.Label(max_screens_frame, text="最大截图数:", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('body')).pack(side='left')
        self.max_screens_var = tk.StringVar(value="100")
        max_screens_entry = tk.Entry(max_screens_frame, textvariable=self.max_screens_var,
                                   font=self.styles.get_font('body'), width=10)
        max_screens_entry.pack(side='left', padx=10)

        # 输出格式
        output_frame = tk.Frame(right_frame, bg=self.styles.get_color('bg_primary'))
        output_frame.pack(fill='x', pady=(0, 10))

        tk.Label(output_frame, text="💾 输出设置", bg=self.styles.get_color('bg_primary'),
                font=self.styles.get_font('heading')).pack(anchor='w', pady=(0, 10))

        # 输出格式选择
        self.output_format_var = tk.StringVar(value=config.get('output_format', 'txt'))
        formats_frame = tk.Frame(output_frame, bg=self.styles.get_color('bg_primary'))
        formats_frame.pack(fill='x')

        formats = [
            ('文本 (.txt)', 'txt'),
            ('Markdown (.md)', 'md'),
            ('JSON (.json)', 'json')
        ]

        for text, value in formats:
            rb = tk.Radiobutton(formats_frame, text=text, variable=self.output_format_var, value=value,
                               bg=self.styles.get_color('bg_primary'),
                               font=self.styles.get_font('body'))
            rb.pack(anchor='w', pady=2)

        # 操作按钮
        button_frame = tk.Frame(left_frame, bg=self.styles.get_color('bg_primary'))
        button_frame.pack(fill='x', pady=20)

        self.start_button = self.styles.create_button(button_frame, "🚀 开始提取",
                                                   command=self._start_extraction,
                                                   style='Primary')
        self.start_button.pack(fill='x', pady=5)

        self.stop_button = self.styles.create_button(button_frame, "⏹️ 停止提取",
                                                   command=self._stop_extraction,
                                                   style='Destructive', state='disabled')
        self.stop_button.pack(fill='x', pady=5)

    def _create_result_panel(self):
        """创建结果面板"""
        # 创建文本显示区域
        self.result_text = scrolledtext.ScrolledText(self.result_tab,
                                                     font=self.styles.get_font('body'),
                                                     wrap='word')
        self.result_text.pack(fill='both', expand=True, padx=10, pady=10)

        # 添加操作按钮
        result_button_frame = tk.Frame(self.result_tab, bg=self.styles.get_color('bg_primary'))
        result_button_frame.pack(fill='x', padx=10, pady=(0, 10))

        self.styles.create_button(result_button_frame, "📄 清空文本",
                                command=self._clear_result).pack(side='left', padx=5)
        self.styles.create_button(result_button_frame, "📋 复制文本",
                                command=self._copy_text).pack(side='left', padx=5)
        self.styles.create_button(result_button_frame, "💾 保存文本",
                                command=self._save_result).pack(side='left', padx=5)

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_frame = tk.Frame(self.root, bg=self.styles.get_color('bg_secondary'), relief='sunken', bd=1)
        self.status_frame.grid(row=2, column=0, sticky='ew')

        # 左侧状态
        self.status_label = tk.Label(self.status_frame, text="就绪",
                                   bg=self.styles.get_color('bg_secondary'),
                                   font=self.styles.get_font('caption'))
        self.status_label.pack(side='left', padx=10, pady=5)

        # 右侧状态
        self.status_info = tk.Label(self.status_frame, text="",
                                   bg=self.styles.get_color('bg_secondary'),
                                   font=self.styles.get_font('caption'),
                                   fg=self.styles.get_color('text_secondary'))
        self.status_info.pack(side='right', padx=10, pady=5)

    def _show_config_dialog(self):
        """显示配置对话框"""
        dialog = ConfigDialog(self.root, config.config)
        result = dialog.show()

        if result:
            # 更新配置
            config.config.update(result)
            self._log_message("配置已更新")

    def _show_area_dialog(self):
        """显示区域选择对话框"""
        current_area = self.extractor.current_area
        dialog = AreaSelectionDialog(self.root, current_area)
        result = dialog.show()

        if result:
            self.extractor.set_extraction_area(*result)
            self._update_area_display()
            self._log_message(f"区域已更新: {result}")

    def _quick_select_area(self):
        """快速选择区域"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 提供快速选择选项
        options = {
            "1": ("上半屏", (0, 0, screen_width, screen_height // 2)),
            "2": ("下半屏", (0, screen_height // 2, screen_width, screen_height // 2)),
            "3": ("左半屏", (0, 0, screen_width // 2, screen_height)),
            "4": ("右半屏", (screen_width // 2, 0, screen_width // 2, screen_height)),
            "5": ("全屏", (0, 0, screen_width, screen_height))
        }

        print("\n快速选择区域:")
        for key, (name, area) in options.items():
            print(f"{key}. {name}")

        choice = input("请选择 [1-5]: ").strip()
        if choice in options:
            _, area = options[choice]
            self.extractor.set_extraction_area(*area)
            self._update_area_display()
            self._log_message(f"已选择 {options[choice][0]} 区域")

    def _update_area_display(self):
        """更新区域显示"""
        if self.extractor.current_area:
            x, y, w, h = self.extractor.current_area
            self.area_label.config(text=f"区域: ({x}, {y}) 尺寸: {w}x{h}")

    def _start_extraction(self):
        """开始提取"""
        if self.is_processing:
            MessageDialog.show_warning(self.root, "警告", "提取正在进行中")
            return

        # 验证设置
        if not self.extractor.current_area:
            MessageDialog.show_error(self.root, "错误", "请先设置提取区域")
            return

        # 切换按钮状态
        self.is_processing = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

        # 清空结果
        self.result_text.delete('1.0', tk.END)
        self.log_messages.clear()

        # 启动提取线程
        extraction_thread = threading.Thread(target=self._extract_document)
        extraction_thread.daemon = True
        extraction_thread.start()

    def _extract_document(self):
        """执行文档提取（在后台线程中）"""
        try:
            # 显示进度对话框
            progress = ProgressDialog(self.root, "正在提取文档...")
            progress.show()

            # 设置进度更新回调
            def on_progress(scroll_count, direction):
                progress.update_progress(scroll_count * 2, f"滚动 {scroll_count} 次 ({direction})")

            def on_stop(result):
                progress.close()

            # 设置提取参数
            self.extractor.scroller.register_callbacks(on_scroll=on_progress, on_stop=on_stop)

            # 开始提取
            result = self.extractor.extract_document(
                scroll_direction=self.scroll_dir_var.get(),
                scroll_interval=float(self.interval_var.get()),
                max_screens=int(self.max_screens_var.get()),
                output_format=self.output_format_var.get()
            )

            # 处理结果
            if "error" in result:
                self.message_queue.put(("error", f"提取失败: {result['error']}"))
            else:
                self.current_extraction = result
                text_content = ""

                # 读取提取的文本
                if "extracted_text_path" in result and os.path.exists(result["extracted_text_path"]):
                    with open(result["extracted_text_path"], 'r', encoding='utf-8') as f:
                        text_content = f.read()

                self.message_queue.put(("success", {
                    "extraction_id": result["extraction_id"],
                    "text": text_content,
                    "screenshots": result["total_screens"],
                    "processing_time": result["processing_time"]
                }))

            progress.close()

        except Exception as e:
            self.message_queue.put(("error", f"提取过程中发生错误: {e}"))
        finally:
            progress.close()
            self.message_queue.put(("complete", ""))

    def _stop_extraction(self):
        """停止提取"""
        if self.extractor.is_processing:
            self.extractor.is_processing = False
            self._log_message("正在停止提取...")
            self.stop_button.config(state='disabled')

    def _check_messages(self):
        """检查消息队列"""
        try:
            while True:
                msg_type, msg_data = self.message_queue.get_nowait()

                if msg_type == "error":
                    MessageDialog.show_error(self.root, "错误", msg_data)
                    self.status_label.config(text="提取失败")
                elif msg_type == "success":
                    self._show_extraction_result(msg_data)
                    self.status_label.config(text="提取完成")
                elif msg_type == "complete":
                    self._finish_extraction()

        except queue.Empty:
            pass

        # 继续检查
        self.root.after(100, self._check_messages)

    def _show_extraction_result(self, data):
        """显示提取结果"""
        # 切换到结果选项卡
        self.notebook.select(1)  # 结果选项卡

        # 显示文本
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert('1.0', data["text"])

        # 更新状态
        self.status_info.config(
            text=f"提取 ID: {data['extraction_id']} | "
                 f"截图: {data['screenshots']} | "
                 f"耗时: {data['processing_time']:.1f}秒"
        )

        self._log_message(f"提取完成，共 {data['screenshots']} 张截图")

    def _finish_extraction(self):
        """完成提取"""
        self.is_processing = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')

    def _clear_result(self):
        """清空结果"""
        self.result_text.delete('1.0', tk.END)

    def _copy_text(self):
        """复制文本"""
        text = self.result_text.get('1.0', tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self._log_message("文本已复制到剪贴板")

    def _save_result(self):
        """保存结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extracted_text_{timestamp}.{self.output_format_var.get()}"

        # 选择保存位置
        filepath = FileDialog.ask_save_file(self.root, "保存结果",
                                         [(f"{self.output_format_var.get().upper()} 文件", f"*.{self.output_format_var.get()}")],
                                         filename)

        if filepath:
            text = self.result_text.get('1.0', tk.END)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            self._log_message(f"结果已保存到: {filepath}")

    def _save_results(self):
        """保存所有结果"""
        if not self.current_extraction:
            MessageDialog.show_warning(self.root, "警告", "没有可保存的结果")
            return

        # 保存当前结果
        self._save_result()

    def _export_logs(self):
        """导出日志"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extraction_logs_{timestamp}.txt"

        filepath = FileDialog.ask_save_file(self.root, "导出日志",
                                         [("文本文件", "*.txt")],
                                         filename)

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                for msg in self.log_messages:
                    f.write(f"{msg['time']} - {msg['level']} - {msg['message']}\n")
            self._log_message(f"日志已导出到: {filepath}")

    def _clear_logs(self):
        """清空日志"""
        self.log_messages.clear()
        self._log_message("日志已清空")

    def _log_message(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'time': timestamp,
            'level': level,
            'message': message
        }
        self.log_messages.append(log_entry)

        # 切换到日志选项卡
        self.notebook.select(2)  # 日志选项卡

        # 显示日志
        log_text = f"[{timestamp}] {level}: {message}\n"
        self.result_text.insert(tk.END, log_text)
        self.result_text.see(tk.END)

    def _show_help(self):
        """显示帮助"""
        help_text = """
文档提取工具使用说明

1. 选择提取区域
   - 点击"选择区域"按钮设置要提取的文档区域
   - 或使用"快速选择"选择预设区域

2. 配置 OCR 设置
   - 选择 OCR 提供商（Tesseract/智谱 AI/DeepSeek/OpenAI）
   - 如果使用 API，需要在配置中设置 API 密钥

3. 设置滚动参数
   - 选择滚动方向（上/下）
   - 设置滚动间隔时间

4. 开始提取
   - 点击"开始提取"按钮
   - 程序会自动滚动并截图
   - 进行 OCR 识别并显示结果

5. 查看结果
   - 在"提取结果"选项卡查看识别的文本
   - 可以复制、保存或导出结果

注意事项：
- 确保选择正确的文档区域
- 使用 API 时需要稳定的网络连接
- 大量文档可能需要较长时间处理
        """

        MessageDialog.show_info(self.root, "使用说明", help_text)

    def _show_about(self):
        """显示关于"""
        about_text = """
文档提取工具 v1.0.0

一个用于从受限制的云桌面环境自动提取文档内容的工具。

特性：
- 自动截图和滚动
- 多种 OCR 引擎支持
- 实时进度显示
- 多格式输出

开发：Claude Code Assistant
许可证：MIT
        """

        MessageDialog.show_info(self.root, "关于", about_text)

    def set_extraction_area(self, x: int, y: int, width: int, height: int):
        """设置提取区域"""
        self.extractor.set_extraction_area(x, y, width, height)
        self._update_area_display()


def main():
    """主函数"""
    root = tk.Tk()
    app = DocExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()