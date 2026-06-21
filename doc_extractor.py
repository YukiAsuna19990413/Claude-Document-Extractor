#!/usr/bin/env python3
"""
Word 文档自动截图 + OCR 识别工具
用于从受限制的云桌面环境提取文档内容
支持本地 Tesseract 和 API 方式（智谱、DeepSeek 等）
"""

import pyautogui
import pytesseract
import time
import keyboard
from PIL import Image
import mss
import os
from datetime import datetime
import base64
import json

try:
    from openai import OpenAI
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False


class DocExtractor:
    def __init__(self):
        self.screenshots = []
        self.is_running = False
        self.api_config = self.load_api_config()

    def load_api_config(self):
        """加载 API 配置"""
        config = {
            "enabled": False,
            "provider": "zhipu",  # zhipu | deepseek | openai
            "api_key": "",
            "base_url": "",
            "model": ""
        }

        if os.path.exists("api_config.json"):
            try:
                with open("api_config.json", "r", encoding="utf-8") as f:
                    config.update(json.load(f))
            except:
                pass

        return config

    def save_api_config(self):
        """保存 API 配置"""
        with open("api_config.json", "w", encoding="utf-8") as f:
            json.dump(self.api_config, f, indent=2, ensure_ascii=False)

    def setup_api(self):
        """配置 API"""
        print("\n" + "="*50)
        print("🔧 API OCR 配置")
        print("="*50)

        if not API_AVAILABLE:
            print("⚠️ 未安装 openai 库，请先安装:")
            print("   pip install openai")
            return False

        providers = {
            "1": {"name": "智谱 AI (GLM)", "base_url": "https://open.bigmodel.cn/api/paas/v4", "model": "glm-4v"},
            "2": {"name": "DeepSeek", "base_url": "https://api.deepseek.com/v1", "model": "deepseek-chat"},
            "3": {"name": "自定义", "base_url": "", "model": ""},
        }

        print("\n选择 API 提供商:")
        for k, v in providers.items():
            print(f"  {k}. {v['name']}")

        choice = input("\n请选择 [1-3]: ").strip()

        if choice not in providers:
            print("⚠️ 无效选择")
            return False

        provider = providers[choice]

        if choice != "3":
            self.api_config["base_url"] = provider["base_url"]
            self.api_config["model"] = provider["model"]
            self.api_config["provider"] = provider["name"].split(" ")[0]
        else:
            self.api_config["base_url"] = input("请输入 Base URL: ").strip()
            self.api_config["model"] = input("请输入模型名称: ").strip()
            self.api_config["provider"] = "custom"

        api_key = input("\n请输入 API Key: ").strip()
        if not api_key:
            print("⚠️ 未输入 API Key，取消配置")
            return False

        self.api_config["api_key"] = api_key
        self.api_config["enabled"] = True

        self.save_api_config()

        print(f"\n✅ 已配置: {provider['name']}")
        print(f"   模型: {self.api_config['model']}")
        return True

    def ocr_with_api(self, image_path):
        """使用 API 进行 OCR 识别"""
        try:
            client = OpenAI(
                api_key=self.api_config["api_key"],
                base_url=self.api_config["base_url"]
            )

            # 读取图片并转 base64
            with open(image_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode()

            response = client.chat.completions.create(
                model=self.api_config["model"],
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
                max_tokens=4000
            )

            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ API 调用失败: {e}")
            return None

    def select_area(self):
        """交互式选择截图区域"""
        print("\n" + "="*50)
        print("📸 选择截图区域")
        print("="*50)
        print("1. 移动鼠标到区域左上角")
        print("2. 按住鼠标左键拖动到右下角")
        print("3. 松开鼠标完成选择")
        print("\n准备好后按 [Enter] 开始...")

        input()  # 等待用户确认

        # 使用 pyautogui 的 dragSelect
        print("\n现在请用鼠标拖动选择文档内容区域...")

        # 让用户手动操作鼠标选择，然后回车确认
        print("选择完成后，在终端按 [Enter] 继续...")
        input()

        # 简化：让用户输入区域坐标（可以改进为可视化选择）
        print("\n请输入区域坐标（手动测量或后续改进为可视化选择）：")
        print("你可以先截图一张，然后用画图软件查看坐标")
        self.x = int(input("左上角 X: "))
        self.y = int(input("左上角 Y: "))
        self.width = int(input("宽度: "))
        self.height = int(input("高度: "))

        print(f"\n✅ 已选择区域: ({self.x}, {self.y}) 尺寸: {self.width}x{self.height}")

        # 保存区域到文件，下次可以直接使用
        with open("area_config.txt", "w") as f:
            f.write(f"{self.x},{self.y},{self.width},{self.height}")
        print("💾 区域配置已保存到 area_config.txt")

    def load_area(self):
        """从文件加载区域配置"""
        try:
            with open("area_config.txt", "r") as f:
                coords = f.read().strip().split(",")
                self.x, self.y, self.width, self.height = map(int, coords)
                print(f"✅ 已加载区域: ({self.x}, {self.y}) 尺寸: {self.width}x{self.height}")
                return True
        except FileNotFoundError:
            print("⚠️ 未找到区域配置，需要先选择区域")
            return False

    def capture_area(self):
        """截图指定区域"""
        with mss.mss() as sct:
            monitor = {
                "top": self.y,
                "left": self.x,
                "width": self.width,
                "height": self.height
            }
            screenshot = sct.grab(monitor)
            return Image.frombytes("RGB", screenshot.size, screenshot.rgb)

    def scroll_down(self):
        """模拟向下滚动（PageDown 或 鼠标滚轮）"""
        # 方法1: PageDown 键
        pyautogui.press('pagedown')
        # 方法2: 鼠标滚轮（可选）
        # pyautogui.scroll(-3)

    def extract_document(self, scroll_pause=1.5, max_screens=100):
        """
        自动滚动并截图

        Args:
            scroll_pause: 每次滚动后等待的时间（秒）
            max_screens: 最大截图数量（防止无限循环）
        """
        print(f"\n{'='*50}")
        print("🚀 开始提取文档")
        print(f"{'='*50}")
        print(f"区域: ({self.x}, {self.y}) | 尺寸: {self.width}x{self.height}")
        print(f"滚动间隔: {scroll_pause}秒 | 最大截图: {max_screens}")
        print("\n⚠️ 请确保 Horizon Client 窗口已激活")
        print("⚠️ 将鼠标移出文档区域，避免遮挡")
        print("\n5秒后开始，请准备好...")
        time.sleep(5)

        screen_count = 0
        prev_image = None
        duplicate_count = 0

        # 创建截图保存目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = f"screenshots_{timestamp}"
        os.makedirs(save_dir, exist_ok=True)

        print("\n开始截图... (按 [Ctrl+C] 提前停止)")

        try:
            while screen_count < max_screens:
                # 截图
                current_image = self.capture_area()
                screenshot_path = os.path.join(save_dir, f"screen_{screen_count:03d}.png")
                current_image.save(screenshot_path)

                # 检查是否与上一张重复（文档到底了）
                if prev_image is not None:
                    # 简单比较像素差异
                    diff = sum(abs(a - b) for a, b in zip(current_image.tobytes(), prev_image.tobytes()))
                    if diff < 1000:  # 差异很小，认为是重复
                        duplicate_count += 1
                        print(f"⏸️ 检测到重复内容 ({duplicate_count}/3)")
                        if duplicate_count >= 3:
                            print("✅ 文档已到底，停止截图")
                            break
                    else:
                        duplicate_count = 0

                print(f"📸 截图 {screen_count + 1}: {screenshot_path}")
                self.screenshots.append(current_image)
                prev_image = current_image
                screen_count += 1

                # 滚动
                if screen_count < max_screens:
                    self.scroll_down()
                    time.sleep(scroll_pause)

        except KeyboardInterrupt:
            print("\n⚠️ 用户中断")

        print(f"\n✅ 完成！共截图 {len(self.screenshots)} 张")
        return save_dir

    def ocr_screenshots(self, screenshot_dir, lang="chi_sim+eng", use_api=None):
        """
        使用 OCR 识别所有截图

        Args:
            screenshot_dir: 截图保存目录
            lang: OCR 语言，默认中英文
            use_api: 是否使用 API，None 则自动判断
        """
        print(f"\n{'='*50}")
        print("🔍 开始 OCR 识别")
        print(f"{'='*50}")

        # 决定使用哪种方式
        if use_api is None:
            use_api = self.api_config.get("enabled", False) and API_AVAILABLE

        if use_api:
            if not API_AVAILABLE:
                print("⚠️ 未安装 openai 库，切换为本地 OCR")
                use_api = False
            elif not self.api_config.get("enabled"):
                print("⚠️ API 未配置，切换为本地 OCR")
                use_api = False

        method = "API" if use_api else "本地 Tesseract"
        print(f"📌 使用方式: {method}")

        all_text = []
        screenshot_files = sorted([f for f in os.listdir(screenshot_dir) if f.endswith('.png')])

        for i, filename in enumerate(screenshot_files):
            filepath = os.path.join(screenshot_dir, filename)
            print(f"识别中 {i+1}/{len(screenshot_files)}: {filename}", end="")

            if use_api:
                text = self.ocr_with_api(filepath)
                if text is None:
                    print(" ❌ 失败，尝试本地 OCR")
                    image = Image.open(filepath)
                    text = pytesseract.image_to_string(image, lang=lang)
                else:
                    print(" ✅")
            else:
                image = Image.open(filepath)
                text = pytesseract.image_to_string(image, lang=lang)
                print(" ✅")

            all_text.append(text)

            # 进度
            if (i + 1) % 5 == 0:
                print(f"   进度: {i+1}/{len(screenshot_files)}")

        return "\n\n".join(all_text)

    def save_text(self, text, screenshot_dir):
        """保存识别的文本"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"extracted_text_{timestamp}.txt"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"\n✅ 文本已保存到: {output_file}")

        # 同时保存到截图目录
        with open(os.path.join(screenshot_dir, "extracted_text.txt"), "w", encoding="utf-8") as f:
            f.write(text)

        return output_file


def main():
    extractor = DocExtractor()

    print("""
╔════════════════════════════════════════════════════════╗
║        Word 文档自动截图 + OCR 识别工具               ║
╚════════════════════════════════════════════════════════╝
    """)

    while True:
        print("\n【主菜单】")
        print("1. 选择截图区域")
        print("2. 使用上次区域")
        print("3. 开始截图")
        print("4. OCR 识别")
        print("5. 全自动（截图+OCR）")
        print("6. API 配置（智谱/DeepSeek）")
        print("0. 退出")

        choice = input("\n请选择 [0-6]: ").strip()

        if choice == "1":
            extractor.select_area()

        elif choice == "2":
            if not extractor.load_area():
                continue

        elif choice == "3":
            if not hasattr(extractor, 'x'):
                print("⚠️ 请先选择区域")
                continue
            scroll_pause = input("滚动间隔（秒，默认1.5）: ").strip()
            scroll_pause = float(scroll_pause) if scroll_pause else 1.5
            extractor.screenshot_dir = extractor.extract_document(scroll_pause=scroll_pause)

        elif choice == "4":
            if not hasattr(extractor, 'screenshot_dir'):
                print("⚠️ 请先截图")
                continue
            text = extractor.ocr_screenshots(extractor.screenshot_dir)
            extractor.save_text(text, extractor.screenshot_dir)

        elif choice == "5":
            if not hasattr(extractor, 'x'):
                print("⚠️ 请先选择区域")
                continue

            scroll_pause = input("滚动间隔（秒，默认1.5）: ").strip()
            scroll_pause = float(scroll_pause) if scroll_pause else 1.5

            # 截图
            screenshot_dir = extractor.extract_document(scroll_pause=scroll_pause)

            # OCR
            text = extractor.ocr_screenshots(screenshot_dir)

            # 保存
            extractor.save_text(text, screenshot_dir)

            print("\n" + "="*50)
            print("🎉 全部完成！")
            print("="*50)

        elif choice == "6":
            extractor.setup_api()

        elif choice == "0":
            print("👋 再见！")
            break

        else:
            print("⚠️ 无效选择")


if __name__ == "__main__":
    main()