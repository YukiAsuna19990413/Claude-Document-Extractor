"""
OCR 处理模块
支持 Tesseract、智谱 AI、DeepSeek、OpenAI 等多种 OCR 引擎
"""

import pytesseract
import os
import json
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image
import base64
import time
import logging
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OCRProcessor:
    """OCR 处理类"""

    def __init__(self, config):
        self.config = config
        self.supported_providers = ["tesseract", "zhipu", "deepseek", "openai"]

        # 初始化 Tesseract 路径
        self._init_tesseract()

    def _init_tesseract(self):
        """初始化 Tesseract"""
        # 尝试设置 Tesseract 路径（根据操作系统）
        if os.name == 'nt':  # Windows
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        # 设置 OCR 语言
        self.default_lang = "chi_sim+eng"

    def process_image(self, image_path: str, provider: str = None) -> Dict[str, Any]:
        """
        处理单张图片

        Args:
            image_path: 图片路径
            provider: OCR 提供商，None 则使用配置中的默认值

        Returns:
            包含识别结果和元数据的字典
        """
        if provider is None:
            provider = self.config.get("provider", "tesseract")

        if provider not in self.supported_providers:
            raise ValueError(f"不支持的 OCR 提供商: {provider}")

        print(f"🔍 使用 {provider} 进行 OCR 识别...")

        start_time = time.time()

        if provider == "tesseract":
            result = self._ocr_with_tesseract(image_path)
        elif provider == "zhipu":
            result = self._ocr_with_zhipu(image_path)
        elif provider == "deepseek":
            result = self._ocr_with_deepseek(image_path)
        elif provider == "openai":
            result = self._ocr_with_openai(image_path)
        else:
            raise ValueError(f"未实现的 OCR 提供商: {provider}")

        # 添加元数据
        result["metadata"] = {
            "provider": provider,
            "processing_time": time.time() - start_time,
            "image_size": self._get_image_size(image_path),
            "timestamp": datetime.now().isoformat()
        }

        return result

    def _ocr_with_tesseract(self, image_path: str) -> Dict[str, Any]:
        """使用 Tesseract 进行 OCR"""
        try:
            # 加载图片
            image = Image.open(image_path)

            # 获取图片信息
            width, height = image.size
            mode = image.mode

            # Tesseract 配置
            custom_config = f'--oem 3 --psm 6 -l {self.default_lang}'

            # 执行 OCR
            text = pytesseract.image_to_string(image, config=custom_config)

            # 获取详细数据（可选）
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)

            # 统计信息
            words = text.split()
            word_count = len([w for w in words if w.strip()])

            return {
                "text": text.strip(),
                "word_count": word_count,
                "confidence": float(data['conf'].mean()) if data['conf'].size > 0 else 0,
                "engine": "Tesseract",
                "detailed_data": data if len(data['text']) > 0 else None
            }

        except Exception as e:
            logging.error(f"Tesseract OCR 失败: {e}")
            return {
                "text": "",
                "error": str(e),
                "word_count": 0,
                "confidence": 0,
                "engine": "Tesseract"
            }

    def _ocr_with_zhipu(self, image_path: str) -> Dict[str, Any]:
        """使用智谱 AI 进行 OCR"""
        try:
            client = OpenAI(
                api_key=self.config.get("api_key"),
                base_url="https://open.bigmodel.cn/api/paas/v4"
            )

            # 读取图片并转 base64
            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode()

            response = client.chat.completions.create(
                model=self.config.get("model", "glm-4v"),
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
                max_tokens=4000,
                temperature=0.1
            )

            text = response.choices[0].message.content

            return {
                "text": text.strip(),
                "word_count": len(text.split()),
                "confidence": 95,  # API 模式的高置信度估计
                "engine": "Zhipu AI",
                "model_used": self.config.get("model", "glm-4v")
            }

        except Exception as e:
            logging.error(f"智谱 AI OCR 失败: {e}")
            return {
                "text": "",
                "error": str(e),
                "word_count": 0,
                "confidence": 0,
                "engine": "Zhipu AI"
            }

    def _ocr_with_deepseek(self, image_path: str) -> Dict[str, Any]:
        """使用 DeepSeek 进行 OCR"""
        try:
            client = OpenAI(
                api_key=self.config.get("api_key"),
                base_url="https://api.deepseek.com/v1"
            )

            # 读取图片并转 base64
            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode()

            response = client.chat.completions.create(
                model=self.config.get("model", "deepseek-chat"),
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
                max_tokens=4000,
                temperature=0.1
            )

            text = response.choices[0].message.content

            return {
                "text": text.strip(),
                "word_count": len(text.split()),
                "confidence": 95,
                "engine": "DeepSeek",
                "model_used": self.config.get("model", "deepseek-chat")
            }

        except Exception as e:
            logging.error(f"DeepSeek OCR 失败: {e}")
            return {
                "text": "",
                "error": str(e),
                "word_count": 0,
                "confidence": 0,
                "engine": "DeepSeek"
            }

    def _ocr_with_openai(self, image_path: str) -> Dict[str, Any]:
        """使用 OpenAI 进行 OCR"""
        try:
            client = OpenAI(
                api_key=self.config.get("api_key"),
                base_url="https://api.openai.com/v1"
            )

            # 读取图片并转 base64
            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode()

            response = client.chat.completions.create(
                model=self.config.get("model", "gpt-4-turbo"),
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
                max_tokens=4000,
                temperature=0.1
            )

            text = response.choices[0].message.content

            return {
                "text": text.strip(),
                "word_count": len(text.split()),
                "confidence": 98,
                "engine": "OpenAI",
                "model_used": self.config.get("model", "gpt-4-turbo")
            }

        except Exception as e:
            logging.error(f"OpenAI OCR 失败: {e}")
            return {
                "text": "",
                "error": str(e),
                "word_count": 0,
                "confidence": 0,
                "engine": "OpenAI"
            }

    def _get_image_size(self, image_path: str) -> Dict[str, int]:
        """获取图片尺寸"""
        try:
            with Image.open(image_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode
                }
        except:
            return {"width": 0, "height": 0, "mode": "unknown"}

    def process_images_batch(self, image_paths: List[str], provider: str = None) -> List[Dict[str, Any]]:
        """批量处理图片"""
        results = []

        for i, image_path in enumerate(image_paths):
            try:
                result = self.process_image(image_path, provider)
                results.append(result)
                print(f"✅ {i+1}/{len(image_paths)}: {os.path.basename(image_path)}")
            except Exception as e:
                print(f"❌ {i+1}/{len(image_paths)}: {os.path.basename(image_path)} - {e}")
                results.append({
                    "text": "",
                    "error": str(e),
                    "image_path": image_path
                })

        return results

    def process_directory(self, directory: str, provider: str = None) -> List[Dict[str, Any]]:
        """处理目录中的所有图片"""
        # 支持的图片格式
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}

        # 查找所有图片文件
        image_paths = []
        for file in os.listdir(directory):
            if os.path.splitext(file)[1].lower() in image_extensions:
                image_paths.append(os.path.join(directory, file))

        # 按文件名排序
        image_paths.sort()

        if not image_paths:
            print(f"⚠️ 目录中没有找到图片文件: {directory}")
            return []

        print(f"📁 找到 {len(image_paths)} 张图片")
        return self.process_images_batch(image_paths, provider)

    def compare_providers(self, image_path: str, providers: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """比较不同 OCR 提供商的结果"""
        if providers is None:
            providers = ["tesseract", "zhipu", "deepseek", "openai"]

        results = {}

        for provider in providers:
            if provider in self.supported_providers:
                try:
                    result = self.process_image(image_path, provider)
                    results[provider] = result
                except Exception as e:
                    results[provider] = {"error": str(e)}

        return results

    def save_results(self, results: List[Dict[str, Any]], output_dir: str, format: str = "txt") -> str:
        """保存 OCR 结果"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "txt":
            output_file = os.path.join(output_dir, f"ocr_results_{timestamp}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                for i, result in enumerate(results):
                    if "text" in result:
                        f.write(f"=== 第 {i+1} 张图片 ===\n")
                        f.write(result["text"] + "\n\n")

        elif format == "json":
            output_file = os.path.join(output_dir, f"ocr_results_{timestamp}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

        elif format == "md":
            output_file = os.path.join(output_dir, f"ocr_results_{timestamp}.md")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("# OCR 识别结果\n\n")
                for i, result in enumerate(results):
                    f.write(f"## 第 {i+1} 张图片\n\n")
                    if "text" in result:
                        f.write(result["text"] + "\n\n")
                    if "metadata" in result:
                        meta = result["metadata"]
                        f.write(f"- **OCR 引擎**: {meta['provider']}\n")
                        f.write(f"- **处理时间**: {meta['processing_time']:.2f} 秒\n")
                        f.write(f"- **图片尺寸**: {meta['image_size']['width']}x{meta['image_size']['height']}\n\n")

        return output_file

    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """获取 OCR 提供商信息"""
        provider_info = {
            "tesseract": {
                "name": "Tesseract OCR",
                "type": "本地",
                "cost": "免费",
                "speed": "快",
                "accuracy": "中",
                "features": ["离线使用", "支持多语言", "开源免费"]
            },
            "zhipu": {
                "name": "智谱 AI",
                "type": "云端",
                "cost": "¥12/百万 tokens",
                "speed": "中",
                "accuracy": "高",
                "features": ["支持表格识别", "支持公式", "中文优化"]
            },
            "deepseek": {
                "name": "DeepSeek",
                "type": "云端",
                "cost": "¥1/百万 tokens",
                "speed": "中",
                "accuracy": "高",
                "features": ["性价比高", "中文支持好", "API 稳定"]
            },
            "openai": {
                "name": "OpenAI GPT-4V",
                "type": "云端",
                "cost": "$10/百万 tokens",
                "speed": "慢",
                "accuracy": "最高",
                "features": ["GPT-4 质量", "多语言支持", "强大理解能力"]
            }
        }

        return provider_info.get(provider, {})

    def is_api_available(self, provider: str) -> bool:
        """检查 API 提供商是否可用"""
        if provider in ["tesseract"]:
            return True

        # 检查 API 密钥
        if not self.config.get("api_key"):
            return False

        if provider == "openai" and not OPENAI_AVAILABLE:
            return False

        return True