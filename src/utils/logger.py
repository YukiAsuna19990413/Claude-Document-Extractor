"""
日志系统模块
提供结构化的日志记录功能
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class Logger:
    """日志管理器"""

    def __init__(self, name: str = "doc_extractor", level: str = "INFO"):
        self.name = name
        self.level = getattr(logging, level.upper())
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)

        # 避免重复添加处理器
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """设置日志处理器"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # 文件处理器
        log_file = log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(self.level)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)

        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message: str, **kwargs):
        """调试日志"""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """信息日志"""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """警告日志"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """错误日志"""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """严重错误日志"""
        self.logger.critical(message, **kwargs)

    def log_extraction_start(self, area: tuple, provider: str):
        """记录提取开始"""
        self.info(f"开始文档提取 - 区域: {area}, OCR: {provider}")

    def log_extraction_complete(self, total_pages: int, save_dir: str):
        """记录提取完成"""
        self.info(f"提取完成 - 共 {total_pages} 页，保存到: {save_dir}")

    def log_ocr_result(self, provider: str, confidence: float, word_count: int):
        """记录 OCR 结果"""
        self.info(f"OCR 完成 - 提供商: {provider}, 置信度: {confidence:.2f}, 词数: {word_count}")

    def log_error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """记录错误"""
        message = f"错误: {error}"
        if context:
            message += f" - 上下文: {context}"
        self.error(message)

    def log_config_change(self, key: str, old_value: Any, new_value: Any):
        """记录配置变更"""
        self.info(f"配置变更 - {key}: {old_value} -> {new_value}")

    def log_performance(self, operation: str, duration: float, details: Optional[Dict] = None):
        """记录性能数据"""
        message = f"性能 - {operation}: {duration:.2f}秒"
        if details:
            message += f" - 详情: {details}"
        self.info(message)

    def export_logs(self, output_file: str = None, level: str = "INFO") -> str:
        """导出日志到文件"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"log_export_{timestamp}.txt"

        log_level = getattr(logging, level.upper())
        logs = []

        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                try:
                    with open(handler.baseFilename, 'r', encoding='utf-8') as f:
                        for line in f:
                            if self._log_level_match(line, log_level):
                                logs.append(line.strip())
                except Exception as e:
                    self.error(f"读取日志文件失败: {e}")

        # 保存导出的日志
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(logs))

        self.info(f"日志已导出到: {output_file}")
        return output_file

    def _log_level_match(self, line: str, level: int) -> bool:
        """检查日志行是否匹配指定级别"""
        level_names = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        line_level = line.split(' - ')[1] if ' - ' in line else 'INFO'

        try:
            line_level_index = level_names.index(line_level.split()[0])
            return line_level_index >= level_names.index(level_names[level // 10 - 1])
        except (ValueError, IndexError):
            return True  # 默认包含

    def clear_old_logs(self, days: int = 7):
        """清理旧的日志文件"""
        log_dir = Path("logs")
        if not log_dir.exists():
            return

        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)

        for log_file in log_dir.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    self.info(f"已删除旧日志: {log_file}")
                except Exception as e:
                    self.error(f"删除日志文件失败: {log_file} - {e}")

    @staticmethod
    def get_logger(name: str = "doc_extractor") -> 'Logger':
        """获取日志实例（单例模式）"""
        if not hasattr(Logger, '_instances'):
            Logger._instances = {}

        if name not in Logger._instances:
            Logger._instances[name] = Logger(name)

        return Logger._instances[name]


# 全局日志实例
logger = Logger.get_logger()


class PerformanceTimer:
    """性能计时器"""

    def __init__(self, operation: str, logger: Logger = None):
        self.operation = operation
        self.logger = logger or Logger.get_logger()
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()

        details = {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": duration
        }

        self.logger.log_performance(self.operation, duration, details)