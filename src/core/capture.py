"""
屏幕捕获模块
"""

import mss
import pyautogui
from PIL import Image
import os
import time
from typing import Tuple, Optional, List, Dict
from datetime import datetime
import numpy as np


class ScreenCapture:
    """屏幕捕获类"""

    def __init__(self):
        self.mss = mss.mss()
        self.screenshots: List[dict] = []
        self.current_area: Optional[Tuple[int, int, int, int]] = None
        self.captures_dir = "captures"

        # 确保捕获目录存在
        os.makedirs(self.captures_dir, exist_ok=True)

    def set_area(self, x: int, y: int, width: int, height: int):
        """设置截图区域"""
        self.current_area = (x, y, width, height)
        return self.current_area

    def get_area(self) -> Optional[Tuple[int, int, int, int]]:
        """获取当前截图区域"""
        return self.current_area

    def save_area_config(self, area: Tuple[int, int, int, int], filename: str = "area_config.txt"):
        """保存区域配置到文件"""
        with open(filename, "w") as f:
            f.write(f"{area[0]},{area[1]},{area[2]},{area[3]}")

    def load_area_config(self, filename: str = "area_config.txt") -> Optional[Tuple[int, int, int, int]]:
        """从文件加载区域配置"""
        try:
            with open(filename, "r") as f:
                coords = f.read().strip().split(",")
                if len(coords) == 4:
                    return tuple(map(int, coords))
        except FileNotFoundError:
            pass
        return None

    def capture_full_screen(self, save_dir: str = None) -> Image.Image:
        """捕获全屏"""
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])  # 主屏幕
            image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            if save_dir:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"fullscreen_{timestamp}.png")
                image.save(save_path)
                return save_path

            return image

    def capture_area(self, area: Tuple[int, int, int, int] = None, save_dir: str = None) -> Image.Image:
        """捕获指定区域"""
        if area is None:
            area = self.current_area
            if area is None:
                raise ValueError("未指定截图区域")

        x, y, width, height = area

        with mss.mss() as sct:
            monitor = {
                "top": y,
                "left": x,
                "width": width,
                "height": height
            }
            screenshot = sct.grab(monitor)
            image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

            if save_dir:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"area_{timestamp}.png")
                image.save(save_path)
                return save_path

            return image

    def capture_multiple_areas(self, areas: List[Tuple[int, int, int, int]], save_dir: str = None) -> List[Image.Image]:
        """捕获多个区域"""
        images = []
        for area in areas:
            image = self.capture_area(area, save_dir)
            images.append(image)
        return images

    def detect_scrollbars(self, image: Image.Image) -> Dict[str, float]:
        """检测滚动条位置"""
        # 将图像转换为灰度
        gray = image.convert('L')
        width, height = gray.size

        # 检测右侧滚动条
        scrollbar_area = gray.crop((width - 20, 0, width, height))
        scrollbar_pixels = list(scrollbar_area.getdata())

        # 计算右侧非白色像素的比例
        scrollbar_ratio = sum(1 for p in scrollbar_pixels if p < 250) / len(scrollbar_pixels)

        return {
            "scrollbar_ratio": scrollbar_ratio,
            "has_scrollbar": scrollbar_ratio > 0.1
        }

    def is_duplicate(self, image1: Image.Image, image2: Image.Image, threshold: int = 1000) -> bool:
        """检查两张图像是否相同"""
        if image1.size != image2.size:
            return False

        # 转换为numpy数组进行比较
        arr1 = np.array(image1)
        arr2 = np.array(image2)

        # 计算像素差异
        diff = np.sum(np.abs(arr1 - arr2))

        return diff < threshold

    def capture_with_scroll_detection(self, area: Tuple[int, int, int, int],
                                    max_attempts: int = 10,
                                    save_dir: str = None) -> List[Image.Image]:
        """带滚动检测的截图"""
        images = []
        prev_image = None
        duplicate_count = 0

        for i in range(max_attempts):
            # 截图
            current_image = self.capture_area(area, save_dir)

            # 检查是否重复
            if prev_image is not None and self.is_duplicate(prev_image, current_image):
                duplicate_count += 1
                if duplicate_count >= 3:
                    print(f"检测到连续 {duplicate_count} 张重复图片，文档可能已到底")
                    break
            else:
                duplicate_count = 0
                images.append(current_image)
                prev_image = current_image

            # 检测滚动条
            scrollbar_info = self.detect_scrollbars(current_image)
            if scrollbar_info["has_scrollbar"]:
                print(f"第 {i+1} 次截图检测到滚动条")

        return images

    def scroll_page(self, direction: str = "down", amount: int = 1) -> None:
        """滚动页面"""
        if direction == "down":
            # 使用 PageDown 键
            for _ in range(amount):
                pyautogui.press('pagedown')
        elif direction == "up":
            # 使用 PageUp 键
            for _ in range(amount):
                pyautogui.press('pageup')
        elif direction == "scroll_down":
            # 使用鼠标滚轮
            pyautogui.scroll(-3 * amount)
        elif direction == "scroll_up":
            # 使用鼠标滚轮
            pyautogui.scroll(3 * amount)

    def auto_capture_scroll(self, area: Tuple[int, int, int, int],
                          scroll_direction: str = "down",
                          scroll_interval: float = 3.0,
                          max_screens: int = 100,
                          save_dir: str = None) -> Tuple[List[Image.Image], str]:
        """自动滚动并截图"""
        if save_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_dir = os.path.join(self.captures_dir, f"capture_{timestamp}")
            os.makedirs(save_dir, exist_ok=True)

        images = []
        prev_image = None
        duplicate_count = 0
        screen_count = 0

        try:
            while screen_count < max_screens:
                # 截图
                current_image = self.capture_area(area, save_dir)
                images.append(current_image)

                # 检查重复
                if prev_image is not None and self.is_duplicate(prev_image, current_image):
                    duplicate_count += 1
                    if duplicate_count >= 3:
                        print(f"文档已到底，共截图 {len(images)} 张")
                        break
                else:
                    duplicate_count = 0
                    prev_image = current_image

                screen_count += 1
                print(f"已截图 {screen_count} 张")

                # 滚动
                if screen_count < max_screens:
                    self.scroll_page(scroll_direction)
                    time.sleep(scroll_interval)

        except KeyboardInterrupt:
            print(f"\n用户中断，已截图 {len(images)} 张")

        return images, save_dir

    def capture_window(self, window_title: str, save_dir: str = None) -> Optional[Image.Image]:
        """捕获指定窗口"""
        # 获取窗口位置（这里需要根据实际窗口管理器调整）
        try:
            # 使用 pyautogui 的 locateOnScreen 可能不是最好的方法
            # 更好的方法是使用 Windows API 或 macOS 的 AppleScript
            window = pyautogui.getWindowsWithTitle(window_title)
            if window:
                window = window[0]
                x, y, width, height = window.left, window.top, window.width, window.height
                return self.capture_area((x, y, width, height), save_dir)
        except:
            pass
        return None

    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        width, height = pyautogui.size()
        return width, height

    def __del__(self):
        """清理资源"""
        if hasattr(self, 'mss'):
            self.mss.close()