"""
配置管理模块
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging


class Config:
    """配置管理类"""

    def __init__(self, config_file: str = None):
        self.config_file = config_file or "config/api_config.json"
        self.default_config = {
            "enabled": False,
            "provider": "zhipu",  # zhipu | deepseek | openai
            "api_key": "",
            "base_url": "",
            "model": "glm-4-air",
            # 用户偏好设置
            "scroll_direction": "down",  # up | down
            "scroll_interval": 3.0,      # 秒
            "auto_save": True,          # 自动保存
            "output_format": "txt",     # txt | md | json
            "log_level": "INFO"         # DEBUG | INFO | WARNING | ERROR
        }

        # 确保配置目录存在
        self.config_dir = Path(self.config_file).parent
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    # 合并默认配置，确保所有必要的键都存在
                    merged_config = self.default_config.copy()
                    merged_config.update(config_data)
                    return merged_config
            except Exception as e:
                logging.error(f"加载配置文件失败: {e}")
                return self.default_config
        else:
            # 如果配置文件不存在，创建默认配置
            self._save_config(self.default_config)
            return self.default_config

    def _save_config(self, config_data: Dict[str, Any]):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value
        self._save_config(self.config)

    def update(self, updates: Dict[str, Any]):
        """批量更新配置"""
        self.config.update(updates)
        self._save_config(self.config)

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """获取特定提供商的配置"""
        provider_configs = {
            "zhipu": {
                "api_key": self.get("api_key"),
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "model": self.get("model", "glm-4-air"),
                "max_tokens": 4000,
                "temperature": 0.1
            },
            "deepseek": {
                "api_key": self.get("api_key"),
                "base_url": "https://api.deepseek.com/v1",
                "model": self.get("model", "deepseek-chat"),
                "max_tokens": 4000,
                "temperature": 0.1
            },
            "openai": {
                "api_key": self.get("api_key"),
                "base_url": "https://api.openai.com/v1",
                "model": self.get("model", "gpt-4-turbo"),
                "max_tokens": 4000,
                "temperature": 0.1
            },
            "tesseract": {
                "config": "--oem 3 --psm 6",
                "lang": "chi_sim+eng"
            }
        }
        return provider_configs.get(provider, {})

    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.get("enabled"):
            return False

        provider = self.get("provider")
        if provider in ["zhipu", "deepseek", "openai"]:
            if not self.get("api_key"):
                logging.error(f"API 密钥未设置: {provider}")
                return False

        return True

    def reload(self):
        """重新加载配置"""
        self.config = self._load_config()


# 全局配置实例
config = Config()


def get_config() -> Config:
    """获取全局配置实例"""
    return config