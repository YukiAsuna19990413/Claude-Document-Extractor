"""
文档提取器主模块
整合所有核心功能，提供统一的 API 接口
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

from .config import config
from .capture import ScreenCapture
from .ocr import OCRProcessor
from .scrolling import DocumentScroller


class DocExtractor:
    """文档提取器主类"""

    def __init__(self, config_file: str = None):
        # 初始化配置
        if config_file:
            config = config.__init__(config_file)

        # 初始化各个模块
        self.capture = ScreenCapture()
        self.ocr = OCRProcessor(config)
        self.scroller = DocumentScroller()

        # 状态变量
        self.current_area = None
        self.screenshots = []
        self.extraction_results = []
        self.is_processing = False

        # 设置日志
        logging.basicConfig(
            level=getattr(logging, config.get("log_level", "INFO")),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def set_extraction_area(self, x: int, y: int, width: int, height: int) -> bool:
        """
        设置提取区域

        Args:
            x: 左上角 X 坐标
            y: 左上角 Y 坐标
            width: 区域宽度
            height: 区域高度

        Returns:
            是否成功设置
        """
        try:
            self.current_area = self.capture.set_area(x, y, width, height)
            # 保存区域配置
            self.capture.save_area_config(self.current_area)
            logging.info(f"提取区域已设置为: {self.current_area}")
            return True
        except Exception as e:
            logging.error(f"设置提取区域失败: {e}")
            return False

    def load_extraction_area(self, filename: str = "area_config.txt") -> bool:
        """
        从文件加载提取区域

        Args:
            filename: 配置文件名

        Returns:
            是否成功加载
        """
        area = self.capture.load_area_config(filename)
        if area:
            self.current_area = area
            logging.info(f"已加载提取区域: {area}")
            return True
        return False

    def select_extraction_area_interactive(self) -> bool:
        """
        交互式选择提取区域

        Returns:
            是否成功选择
        """
        print("\n" + "="*50)
        print("📸 选择提取区域")
        print("="*50)
        print("1. 输入坐标选择（推荐用于精确控制）")
        print("2. 使用可视化工具选择（需要额外工具）")
        print("3. 使用上次配置")

        choice = input("\n请选择 [1-3]: ").strip()

        if choice == "1":
            try:
                print("\n请输入区域坐标（可以先用截图工具测量）:")
                x = int(input("左上角 X: "))
                y = int(input("左上角 Y: "))
                width = int(input("宽度: "))
                height = int(input("高度: "))
                return self.set_extraction_area(x, y, width, height)
            except ValueError:
                print("⚠️ 无效的坐标输入")
                return False

        elif choice == "2":
            # 使用可视化区域选择工具
            print("\n启动可视化区域选择工具...")
            try:
                # 这里可以调用 area_selector.py
                from ..tools.area_selector import AreaSelector
                selector = AreaSelector()
                area = selector.select_area()
                if area:
                    return self.set_extraction_area(*area)
            except ImportError:
                print("⚠️ 可视化选择工具未找到")

        elif choice == "3":
            return self.load_extraction_area()

        else:
            print("⚠️ 无效选择")
            return False

    def configure_ocr_provider(self, provider: str = None) -> bool:
        """
        配置 OCR 提供商

        Args:
            provider: OCR 提供商名称

        Returns:
            是否成功配置
        """
        if not provider:
            print("\n选择 OCR 提供商:")
            print("1. Tesseract (本地)")
            print("2. 智谱 AI (API)")
            print("3. DeepSeek (API)")
            print("4. OpenAI (API)")

            choice = input("请选择 [1-4]: ").strip()
            providers = {
                "1": "tesseract",
                "2": "zhipu",
                "3": "deepseek",
                "4": "openai"
            }
            provider = providers.get(choice, "tesseract")

        # 检查提供商是否支持
        if provider not in self.ocr.supported_providers:
            print(f"⚠️ 不支持的 OCR 提供商: {provider}")
            return False

        # 检查 API 密钥（对于云端提供商）
        if provider != "tesseract" and not config.get("api_key"):
            print(f"\n配置 {provider} API:")
            api_key = input("请输入 API Key: ").strip()
            if not api_key:
                print("⚠️ 未输入 API Key")
                return False
            config.set("api_key", api_key)
            config.set("provider", provider)

        config.set("provider", provider)
        print(f"✅ OCR 提供商已设置为: {provider}")
        return True

    def extract_document(self,
                        scroll_direction: str = "down",
                        scroll_interval: float = 3.0,
                        max_screens: int = 100,
                        auto_ocr: bool = True,
                        output_dir: str = None) -> Dict[str, Any]:
        """
        提取文档内容

        Args:
            scroll_direction: 滚动方向
            scroll_interval: 滚动间隔（秒）
            max_screens: 最大截图数量
            auto_ocr: 是否自动进行 OCR
            output_dir: 输出目录

        Returns:
            提取结果
        """
        if not self.current_area:
            print("⚠️ 请先设置提取区域")
            return {"error": "未设置提取区域"}

        if self.is_processing:
            print("⚠️ 正在处理中，请稍候")
            return {"error": "正在处理中"}

        self.is_processing = True
        start_time = time.time()

        try:
            print("\n" + "="*50)
            print("🚀 开始提取文档")
            print("="*50)

            # 设置滚动参数
            self.scroller.set_scroll_direction(scroll_direction)
            self.scroller.set_scroll_interval(scroll_interval)

            # 创建输出目录
            if not output_dir:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = f"extractions_{timestamp}"
            os.makedirs(output_dir, exist_ok=True)

            # 设置滚动回调
            def on_scroll(scroll_count, direction):
                print(f"📸 已滚动 {scroll_count} 次 ({direction})")

            def on_stop(result):
                print(f"🛑 滚动停止: {result['stopped_by']}")

            self.scroller.register_callbacks(on_scroll=on_scroll, on_stop=on_stop)

            # 自动滚动并截图
            print("开始自动滚动截图...")
            result = self.scroller.scroll_document(
                capture_callback=lambda: self.capture.capture_area(self.current_area),
                check_duplicates=True
            )

            # 保存截图
            screenshot_dir = os.path.join(output_dir, "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)

            # 获取所有截图
            screenshot_files = []
            for i in range(result["total_scrolls"]):
                screenshot_path = os.path.join(screenshot_dir, f"screen_{i:03d}.png")
                if os.path.exists(screenshot_path):
                    screenshot_files.append(screenshot_path)

            if not screenshot_files:
                print("⚠️ 未获取到截图")
                return {"error": "未获取到截图"}

            # 进行 OCR 识别
            if auto_ocr:
                print("\n" + "="*50)
                print("🔍 开始 OCR 识别")
                print("="*50)

                # 获取当前 OCR 提供商
                provider = config.get("provider", "tesseract")

                # 处理截图
                ocr_results = self.ocr.process_images_batch(screenshot_files, provider)

                # 保存 OCR 结果
                extracted_text = self.ocr.save_results(
                    ocr_results,
                    output_dir,
                    format=config.get("output_format", "txt")
                )

                # 整理结果
                extraction_result = {
                    "extraction_id": f"ext_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "timestamp": datetime.now().isoformat(),
                    "area": self.current_area,
                    "scroll_result": result,
                    "ocr_provider": provider,
                    "total_screens": result["total_scrolls"],
                    "screenshots": screenshot_files,
                    "ocr_results": ocr_results,
                    "extracted_text_path": extracted_text,
                    "output_directory": output_dir,
                    "processing_time": time.time() - start_time
                }

                self.extraction_results.append(extraction_result)

                print(f"\n✅ 提取完成!")
                print(f"📁 输出目录: {output_dir}")
                print(f"📄 提取文本: {extracted_text}")

                return extraction_result

            else:
                return {
                    "extraction_id": f"ext_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "timestamp": datetime.now().isoformat(),
                    "area": self.current_area,
                    "scroll_result": result,
                    "screenshots": screenshot_files,
                    "output_directory": output_dir,
                    "processing_time": time.time() - start_time
                }

        except Exception as e:
            logging.error(f"文档提取失败: {e}")
            return {"error": str(e)}
        finally:
            self.is_processing = False

    def quick_extract(self, area: Tuple[int, int, int, int] = None, **kwargs) -> Dict[str, Any]:
        """
        快速提取（设置区域并提取）

        Args:
            area: 提取区域 (x, y, width, height)
            **kwargs: 其他参数

        Returns:
            提取结果
        """
        if area:
            if not self.set_extraction_area(*area):
                return {"error": "设置区域失败"}

        return self.extract_document(**kwargs)

    def batch_extract(self, areas: List[Tuple[int, int, int, int]], **kwargs) -> List[Dict[str, Any]]:
        """
        批量提取多个区域

        Args:
            areas: 区域列表
            **kwargs: 提取参数

        Returns:
            提取结果列表
        """
        results = []
        for i, area in enumerate(areas):
            print(f"\n处理区域 {i+1}/{len(areas)}: {area}")
            result = self.quick_extract(area, **kwargs)
            results.append(result)
            if "error" not in result:
                # 短暂延迟，避免资源竞争
                time.sleep(1)
        return results

    def get_extraction_history(self) -> List[Dict[str, Any]]:
        """获取提取历史"""
        return self.extraction_results

    def get_extraction_result(self, extraction_id: str) -> Optional[Dict[str, Any]]:
        """获取特定的提取结果"""
        for result in self.extraction_results:
            if result.get("extraction_id") == extraction_id:
                return result
        return None

    def export_extraction(self, extraction_id: str, formats: List[str] = None) -> Dict[str, str]:
        """
        导出提取结果

        Args:
            extraction_id: 提取 ID
            formats: 导出格式列表

        Returns:
            导出文件路径
        """
        result = self.get_extraction_result(extraction_id)
        if not result:
            return {"error": "未找到提取结果"}

        if not formats:
            formats = ["txt", "json", "md"]

        exported_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for fmt in formats:
            if "ocr_results" in result:
                output_file = self.ocr.save_results(
                    result["ocr_results"],
                    result["output_directory"],
                    fmt
                )
                exported_files[fmt] = output_file

        return exported_files

    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        return {
            "current_area": self.current_area,
            "ocr_provider": config.get("provider", "tesseract"),
            "config": {
                "scroll_direction": config.get("scroll_direction", "down"),
                "scroll_interval": config.get("scroll_interval", 3.0),
                "output_format": config.get("output_format", "txt"),
                "auto_save": config.get("auto_save", True)
            },
            "extraction_count": len(self.extraction_results),
            "is_processing": self.is_processing
        }

    def validate_setup(self) -> Dict[str, Any]:
        """验证设置是否正确"""
        validation_result = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "info": {}
        }

        # 检查区域设置
        if not self.current_area:
            validation_result["valid"] = False
            validation_result["issues"].append("未设置提取区域")

        # 检查 OCR 提供商
        provider = config.get("provider", "tesseract")
        if provider != "tesseract":
            if not config.get("api_key"):
                validation_result["valid"] = False
                validation_result["issues"].append(f"API 密钥未设置 (提供商: {provider})")

        # 检查屏幕大小
        screen_width, screen_height = self.capture.get_screen_size()
        validation_result["info"]["screen_size"] = f"{screen_width}x{screen_height}"

        # 检查区域是否超出屏幕
        if self.current_area:
            x, y, w, h = self.current_area
            if x + w > screen_width or y + h > screen_height:
                validation_result["warnings"].append(f"提取区域可能超出屏幕范围")

        return validation_result

    def cleanup_temp_files(self, older_than_days: int = 7) -> int:
        """
        清理临时文件

        Args:
            older_than_days: 清理多少天前的文件

        Returns:
            清理的文件数量
        """
        from datetime import timedelta

        cutoff_time = datetime.now() - timedelta(days=older_than_days)
        cleaned_count = 0

        # 清理截图目录
        for capture_dir in ["captures", "extractions"]:
            if os.path.exists(capture_dir):
                for root, dirs, files in os.walk(capture_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.getmtime(file_path) < cutoff_time.timestamp():
                            try:
                                os.remove(file_path)
                                cleaned_count += 1
                            except:
                                pass

        return cleaned_count


# 工具函数
def create_extractor(config_file: str = None) -> DocExtractor:
    """创建文档提取器实例"""
    return DocExtractor(config_file)


def quick_extract_area(x: int, y: int, width: int, height: int, **kwargs) -> Dict[str, Any]:
    """快速提取指定区域"""
    extractor = create_extractor()
    return extractor.quick_extract((x, y, width, height), **kwargs)