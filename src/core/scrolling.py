"""
文档滚动模块
实现自动文档滚动功能，支持智能停止和重复检测
"""

import time
import pyautogui
import keyboard
import logging
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime
from threading import Thread, Event
import numpy as np
from PIL import Image


class DocumentScroller:
    """文档滚动器"""

    def __init__(self):
        self.scroll_direction = "down"  # up | down
        self.scroll_interval = 3.0      # 秒
        self.is_running = False
        self.stop_event = Event()
        self.scroll_method = "page"  # page | wheel | arrow
        self.max_scrolls = 1000       # 最大滚动次数
        self.current_scroll = 0

        # 重复检测相关
        self.detection_threshold = 0.95  # 相似度阈值
        self.consecutive_duplicates = 3  # 连续重复次数
        self.duplicate_count = 0
        self.prev_image_hash = None

        # 回调函数
        self.on_scroll: Optional[Callable] = None
        self.on_stop: Optional[Callable] = None
        self.on_duplicate: Optional[Callable] = None

    def set_scroll_direction(self, direction: str):
        """设置滚动方向"""
        if direction not in ["up", "down"]:
            raise ValueError("滚动方向必须是 'up' 或 'down'")
        self.scroll_direction = direction

    def set_scroll_interval(self, interval: float):
        """设置滚动间隔（秒）"""
        if interval < 0.5:
            raise ValueError("滚动间隔不能小于 0.5 秒")
        self.scroll_interval = interval

    def set_scroll_method(self, method: str):
        """设置滚动方法"""
        if method not in ["page", "wheel", "arrow"]:
            raise ValueError("滚动方法必须是 'page', 'wheel' 或 'arrow'")
        self.scroll_method = method

    def set_duplicate_threshold(self, threshold: float, consecutive_count: int = 3):
        """设置重复检测阈值"""
        if not 0 < threshold <= 1:
            raise ValueError("相似度阈值必须在 0 到 1 之间")
        self.detection_threshold = threshold
        self.consecutive_duplicates = consecutive_count

    def register_callbacks(self, on_scroll: Callable = None, on_stop: Callable = None, on_duplicate: Callable = None):
        """注册回调函数"""
        self.on_scroll = on_scroll
        self.on_stop = on_stop
        self.on_duplicate = on_duplicate

    def scroll_once(self) -> bool:
        """执行一次滚动，返回是否成功"""
        if self.current_scroll >= self.max_scrolls:
            self.stop()
            return False

        try:
            if self.scroll_method == "page":
                if self.scroll_direction == "down":
                    pyautogui.press('pagedown')
                else:
                    pyautogui.press('pageup')

            elif self.scroll_method == "wheel":
                if self.scroll_direction == "down":
                    pyautogui.scroll(-3)  # 向下滚动
                else:
                    pyautogui.scroll(3)   # 向上滚动

            elif self.scroll_method == "arrow":
                if self.scroll_direction == "down":
                    for _ in range(30):  # 模拟按 30 次下箭头
                        pyautogui.press('down')
                        time.sleep(0.01)
                else:
                    for _ in range(30):  # 模拟按 30 次上箭头
                        pyautogui.press('up')
                        time.sleep(0.01)

            self.current_scroll += 1

            # 触发滚动回调
            if self.on_scroll:
                self.on_scroll(self.current_scroll, self.scroll_direction)

            return True

        except Exception as e:
            logging.error(f"滚动失败: {e}")
            return False

    def calculate_image_similarity(self, image1: np.ndarray, image2: np.ndarray) -> float:
        """计算两张图片的相似度"""
        # 将图片调整为相同大小（如果需要）
        if image1.shape != image2.shape:
            # 调整 image2 到 image1 的大小
            from PIL import Image
            img2_pil = Image.fromarray(image2)
            img2_pil = img2_pil.resize((image1.shape[1], image1.shape[0]))
            image2 = np.array(img2_pil)

        # 计算均方误差
        mse = np.mean((image1 - image2) ** 2)
        # 将 MSE 转换为相似度（0-1之间，1表示完全相同）
        similarity = 1 / (1 + mse)
        return similarity

    def check_for_duplicate(self, current_image_hash: int) -> bool:
        """检查是否出现重复内容"""
        if self.prev_image_hash is None:
            self.prev_image_hash = current_image_hash
            return False

        # 检查连续重复
        if current_image_hash == self.prev_image_hash:
            self.duplicate_count += 1
            print(f"检测到重复内容 ({self.duplicate_count}/{self.consecutive_duplicates})")

            # 触发重复检测回调
            if self.on_duplicate:
                self.on_duplicate(self.duplicate_count, self.consecutive_duplicates)

            if self.duplicate_count >= self.consecutive_duplicates:
                print("检测到连续重复，文档可能已到底")
                self.stop()
                return True
        else:
            self.duplicate_count = 0

        self.prev_image_hash = current_image_hash
        return False

    def scroll_document(self, capture_callback: Callable = None, check_duplicates: bool = True) -> Dict[str, Any]:
        """
        自动滚动文档

        Args:
            capture_callback: 截图回调函数，用于获取当前图片
            check_duplicates: 是否检查重复内容

        Returns:
            包含滚动结果的字典
        """
        self.is_running = True
        self.stop_event.clear()
        self.duplicate_count = 0
        self.current_scroll = 0
        self.prev_image_hash = None

        start_time = time.time()
        last_scroll_time = time.time()

        print(f"开始自动滚动 - 方向: {self.scroll_direction}, 间隔: {self.scroll_interval}秒")

        try:
            while self.is_running and self.current_scroll < self.max_scrolls:
                # 检查停止信号
                if self.stop_event.is_set():
                    break

                # 执行滚动
                if not self.scroll_once():
                    break

                # 截图检查重复（如果有回调函数）
                if check_duplicates and capture_callback:
                    try:
                        current_image = capture_callback()
                        if current_image is not None:
                            # 计算图片哈希
                            current_image_hash = hash(current_image.tobytes())

                            # 检查重复
                            if self.check_for_duplicate(current_image_hash):
                                break
                    except Exception as e:
                        logging.error(f"重复检测失败: {e}")

                # 等待滚动间隔
                time.sleep(self.scroll_interval)
                last_scroll_time = time.time()

        except KeyboardInterrupt:
            print("\n用户中断滚动")
        except Exception as e:
            logging.error(f"滚动过程中发生错误: {e}")
        finally:
            self.is_running = False

        end_time = time.time()
        duration = end_time - start_time

        result = {
            "total_scrolls": self.current_scroll,
            "duration": duration,
            "avg_interval": duration / self.current_scroll if self.current_scroll > 0 else 0,
            "stopped_by": "user" if self.stop_event.is_set() else "limit" if self.current_scroll >= self.max_scrolls else "duplicate",
            "scroll_direction": self.scroll_direction,
            "scroll_method": self.scroll_method
        }

        # 触发停止回调
        if self.on_stop:
            self.on_stop(result)

        print(f"滚动完成 - 共滚动 {self.current_scroll} 次，耗时 {duration:.2f} 秒")
        return result

    def start_scrolling(self, capture_callback: Callable = None, check_duplicates: bool = True) -> Thread:
        """在后台线程中开始滚动"""
        if self.is_running:
            logging.warning("滚动已在进行中")
            return None

        def scrolling_thread():
            self.scroll_document(capture_callback, check_duplicates)

        thread = Thread(target=scrolling_thread, daemon=True)
        thread.start()
        return thread

    def stop(self):
        """停止滚动"""
        self.is_running = False
        self.stop_event.set()
        print("停止滚动")

    def pause(self):
        """暂停滚动"""
        self.is_running = False
        print("暂停滚动")

    def resume(self):
        """恢复滚动"""
        if not self.is_running:
            self.is_running = True
            print("恢复滚动")

    def get_scroll_status(self) -> Dict[str, Any]:
        """获取当前滚动状态"""
        return {
            "is_running": self.is_running,
            "current_scroll": self.current_scroll,
            "max_scrolls": self.max_scrolls,
            "scroll_direction": self.scroll_direction,
            "scroll_interval": self.scroll_interval,
            "scroll_method": self.scroll_method,
            "duplicate_count": self.duplicate_count
        }

    def scroll_to_percentage(self, percentage: float, total_height: int, capture_callback: Callable = None) -> bool:
        """滚动到指定百分比位置"""
        if not 0 <= percentage <= 100:
            raise ValueError("百分比必须在 0 到 100 之间")

        target_position = int(total_height * percentage / 100)
        current_position = 0  # 需要通过其他方式获取当前位置

        # 计算需要滚动的次数
        scroll_distance = target_position - current_position
        scrolls_needed = abs(scroll_distance) // 100  # 假设每次滚动约 100 像素

        if scrolls_needed > 0:
            # 临时设置滚动方向
            original_direction = self.scroll_direction
            if scroll_distance < 0:
                self.scroll_direction = "up"
            else:
                self.scroll_direction = "down"

            # 执行滚动
            for i in range(scrolls_needed):
                if not self.is_running:
                    break
                if not self.scroll_once():
                    break
                time.sleep(0.1)  # 快速滚动

            # 恢复原始方向
            self.scroll_direction = original_direction

        return True

    def smart_scroll_until_stable(self, capture_callback: Callable = None, stability_threshold: float = 0.98, max_attempts: int = 10) -> Dict[str, Any]:
        """智能滚动直到内容稳定（不再变化）"""
        if not capture_callback:
            raise ValueError("需要提供截图回调函数")

        attempts = 0
        last_stable_hash = None
        stable_count = 0

        while attempts < max_attempts and stable_count < 3:
            # 滚动一次
            if not self.scroll_once():
                break

            # 获取当前图片
            try:
                current_image = capture_callback()
                if current_image is not None:
                    current_hash = hash(current_image.tobytes())

                    # 检查是否稳定
                    if last_stable_hash is not None:
                        if current_hash == last_stable_hash:
                            stable_count += 1
                            print(f"内容稳定 {stable_count}/3")
                        else:
                            stable_count = 0
                            last_stable_hash = current_hash

                    last_stable_hash = current_hash

            except Exception as e:
                logging.error(f"智能滚动检测失败: {e}")

            attempts += 1
            time.sleep(self.scroll_interval)

        return {
            "attempts": attempts,
            "stable_count": stable_count,
            "reached_end": stable_count >= 3,
            "total_scrolls": self.current_scroll
        }

    def setup_hotkeys(self, start_key: str = 'f1', stop_key: str = 'f2', pause_key: str = 'f3'):
        """设置热键控制"""
        def start_scroll():
            if not self.is_running:
                self.start_scrolling()

        def stop_scroll():
            if self.is_running:
                self.stop()

        def pause_scroll():
            if self.is_running:
                self.pause()
            else:
                self.resume()

        try:
            keyboard.add_hotkey(start_key, start_scroll)
            keyboard.add_hotkey(stop_key, stop_scroll)
            keyboard.add_hotkey(pause_key, pause_scroll)

            print(f"热键已设置: {start_key}=开始, {stop_key}=停止, {pause_key}=暂停")
            print("按 Ctrl+C 退出热键监听")

            # 保持程序运行
            keyboard.wait('ctrl+c')

        except Exception as e:
            logging.error(f"热键设置失败: {e}")
        finally:
            keyboard.remove_all_hotkeys()

    def estimate_document_length(self, capture_callback: Callable, test_scrolls: int = 5) -> Dict[str, Any]:
        """估算文档长度"""
        if not capture_callback:
            raise ValueError("需要提供截图回调函数")

        # 在当前位置截图
        try:
            initial_image = capture_callback()
            if initial_image is None:
                return {"error": "无法获取初始图片"}
        except Exception as e:
            return {"error": str(e)}

        # 向下滚动几次并记录
        scroll_distances = []
        timestamps = []

        for i in range(test_scrolls):
            if not self.scroll_once():
                break

            try:
                new_image = capture_callback()
                if new_image is not None:
                    # 简单估算滚动距离（可以通过像素差异计算）
                    distance = 100  # 简化处理，实际应该计算像素差异
                    scroll_distances.append(distance)
                    timestamps.append(time.time())
            except Exception as e:
                logging.error(f"估算测试滚动失败: {e}")

        # 计算平均滚动距离
        avg_distance = sum(scroll_distances) / len(scroll_distances) if scroll_distances else 100

        # 估算文档总长度（假设屏幕高度为 1000 像素）
        screen_height = 1000  # 需要根据实际屏幕调整
        estimated_pages = avg_distance / screen_height
        estimated_total_scrolls = estimated_pages * 10  # 假设每页需要 10 次滚动

        return {
            "avg_scroll_distance": avg_distance,
            "estimated_pages": estimated_pages,
            "estimated_total_scrolls": estimated_total_scrolls,
            "test_scrolls": len(scroll_distances),
            "screen_height": screen_height
        }