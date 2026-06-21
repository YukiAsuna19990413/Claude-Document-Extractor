"""
辅助函数模块
提供各种工具函数和帮助类
"""

import os
import json
import hashlib
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
import datetime


class FileHelper:
    """文件操作助手"""

    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """确保目录存在"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def get_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
        """计算文件哈希值"""
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    @staticmethod
    def copy_file_with_backup(src: Union[str, Path], dst: Union[str, Path]) -> Path:
        """复制文件并创建备份"""
        src = Path(src)
        dst = Path(dst)

        if dst.exists():
            backup = dst.with_suffix(f'.bak.{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}')
            shutil.copy2(dst, backup)

        FileHelper.ensure_directory(dst.parent)
        shutil.copy2(src, dst)
        return dst

    @staticmethod
    def find_files(directory: Union[str, Path], extensions: List[str] = None, recursive: bool = True) -> List[Path]:
        """查找文件"""
        directory = Path(directory)
        if extensions is None:
            extensions = ['*']
        else:
            extensions = [f'*.{ext.lstrip(".")}' for ext in extensions]

        if recursive:
            files = []
            for ext in extensions:
                files.extend(directory.rglob(ext))
            return files
        else:
            return [f for ext in extensions for f in directory.glob(ext)]

    @staticmethod
    def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
        """获取文件信息"""
        file_path = Path(file_path)
        if not file_path.exists():
            return {}

        stat = file_path.stat()
        return {
            "name": file_path.name,
            "size": stat.st_size,
            "created": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": file_path.suffix,
            "parent": str(file_path.parent)
        }

    @staticmethod
    def safe_json_load(file_path: Union[str, Path]) -> Optional[Dict]:
        """安全加载 JSON 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    @staticmethod
    def safe_json_save(data: Dict, file_path: Union[str, Path], indent: int = 2) -> bool:
        """安全保存 JSON 文件"""
        try:
            FileHelper.ensure_directory(Path(file_path).parent)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            return True
        except Exception:
            return False


class ValidationHelper:
    """验证助手"""

    @staticmethod
    def is_valid_coordinates(x: int, y: int, width: int, height: int, screen_width: int = None, screen_height: int = None) -> bool:
        """验证坐标是否有效"""
        if width <= 0 or height <= 0:
            return False

        if screen_width is not None and (x + width > screen_width or x < 0):
            return False

        if screen_height is not None and (y + height > screen_height or y < 0):
            return False

        return True

    @staticmethod
    def is_valid_api_key(key: str, provider: str = None) -> bool:
        """验证 API 密钥格式"""
        if not key or len(key) < 10:
            return False

        # 基本的格式检查
        patterns = {
            'openai': r'^sk-[a-zA-Z0-9]{20,}$',
            'zhipu': r'^[a-f0-9]{32}$',
            'deepseek': r'^sk-[a-zA-Z0-9]{20,}$'
        }

        if provider and provider in patterns:
            import re
            return bool(re.match(patterns[provider], key))

        # 通用检查
        return any(char.isalnum() for char in key)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """验证 URL 格式"""
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证配置字典"""
        errors = []

        # 必需字段检查
        required_fields = ['enabled', 'provider']
        for field in required_fields:
            if field not in config:
                errors.append(f"缺少必需字段: {field}")

        # 提供商检查
        provider = config.get('provider')
        if provider not in ['tesseract', 'zhipu', 'deepseek', 'openai']:
            errors.append(f"不支持的提供商: {provider}")

        # API 密钥检查
        if provider != 'tesseract' and not config.get('api_key'):
            errors.append("API 提供商需要配置 api_key")

        # 数字字段验证
        for field in ['scroll_interval', 'max_tokens', 'similarity_threshold']:
            if field in config:
                try:
                    value = float(config[field])
                    if value <= 0:
                        errors.append(f"{field} 必须大于 0")
                except ValueError:
                    errors.append(f"{field} 必须是数字")

        return len(errors) == 0, errors


class TextHelper:
    """文本处理助手"""

    @staticmethod
    def clean_text(text: str) -> str:
        """清理文本"""
        # 移除多余的空白
        text = ' '.join(text.split())
        # 移除特殊字符（可选）
        # text = re.sub(r'[^\w\s一-鿿]', '', text)
        return text.strip()

    @staticmethod
    def truncate_text(text: str, max_length: int = 200, suffix: str = '...') -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def count_words(text: str) -> int:
        """统计词数"""
        import re
        words = re.findall(r'\b\w+\b', text)
        return len(words)

    @staticmethod
    def count_characters(text: str, include_spaces: bool = True) -> int:
        """统计字符数"""
        if include_spaces:
            return len(text)
        else:
            return len(text.replace(' ', '').replace('\n', '').replace('\t', ''))

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """提取邮箱地址"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """提取 URL"""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)


class FormatHelper:
    """格式转换助手"""

    @staticmethod
    def format_duration(seconds: float) -> str:
        """格式化持续时间"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining = seconds % 60
            return f"{minutes}分{remaining:.1f}秒"
        else:
            hours = int(seconds // 3600)
            remaining = seconds % 3600
            minutes = int(remaining // 60)
            return f"{hours}小时{minutes}分"

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f}{size_names[i]}"

    @staticmethod
    def format_timestamp(timestamp: Union[datetime.datetime, str], format_str: str = None) -> str:
        """格式化时间戳"""
        if isinstance(timestamp, str):
            timestamp = datetime.datetime.fromisoformat(timestamp)

        if format_str is None:
            format_str = "%Y-%m-%d %H:%M:%S"

        return timestamp.strftime(format_str)


class ProgressHelper:
    """进度助手"""

    @staticmethod
    def create_progress_bar(current: int, total: int, width: int = 50, prefix: str = "", suffix: str = "") -> str:
        """创建进度条字符串"""
        if total == 0:
            return ""

        percent = current / total
        filled_width = int(width * percent)
        bar = '█' * filled_width + '-' * (width - filled_width)

        return f"{prefix}[{bar}] {percent:.1%} {suffix}"

    @staticmethod
    def format_eta(current: int, total: int, elapsed: float) -> str:
        """格式化预估剩余时间"""
        if current >= total or current == 0:
            return "计算中..."

        remaining = (elapsed / current) * (total - current)
        return FormatHelper.format_duration(remaining)


class DataHelper:
    """数据处理助手"""

    @staticmethod
    def merge_dictionaries(dict1: Dict, dict2: Dict) -> Dict:
        """合并字典"""
        result = dict1.copy()
        result.update(dict2)
        return result

    @staticmethod
    def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """扁平化字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(DataHelper.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    @staticmethod
    def remove_empty_values(d: Dict) -> Dict:
        """移除空值"""
        return {k: v for k, v in d.items() if v is not None and v != '' and v != []}

    @staticmethod
    def filter_dict(d: Dict, keys: List[str]) -> Dict:
        """过滤字典"""
        return {k: d[k] for k in keys if k in d}


class SystemHelper:
    """系统助手"""

    @staticmethod
    def get_screen_resolution() -> Tuple[int, int]:
        """获取屏幕分辨率"""
        try:
            import tkinter as tk
            root = tk.Tk()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()
            root.destroy()
            return width, height
        except:
            return 1920, 1080

    @staticmethod
    def is_admin() -> bool:
        """检查是否管理员权限"""
        try:
            import os
            return os.getuid() == 0
        except:
            return False

    @staticmethod
    def get_python_version() -> str:
        """获取 Python 版本"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """检查依赖是否安装"""
        dependencies = {
            'pyautogui': False,
            'PIL': False,
            'mss': False,
            'pytesseract': False,
            'keyboard': False,
            'pyperclip': False,
            'openai': False,
            'tkinter': False
        }

        try:
            import pyautogui
            dependencies['pyautogui'] = True
        except:
            pass

        try:
            from PIL import Image
            dependencies['PIL'] = True
        except:
            pass

        try:
            import mss
            dependencies['mss'] = True
        except:
            pass

        try:
            import pytesseract
            dependencies['pytesseract'] = True
        except:
            pass

        try:
            import keyboard
            dependencies['keyboard'] = True
        except:
            pass

        try:
            import pyperclip
            dependencies['pyperclip'] = True
        except:
            pass

        try:
            import openai
            dependencies['openai'] = True
        except:
            pass

        try:
            import tkinter
            dependencies['tkinter'] = True
        except:
            pass

        return dependencies