#!/usr/bin/env python3
"""
安装脚本
用于打包和分发文档提取工具
"""

from setuptools import setup, find_packages
import os

# 读取 README
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# 读取 requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

# macOS 打包配置
def get_macos_config():
    return {
        'app': ['src/gui/app.py'],
        'data_files': [],
        'options': {
            'argv_emulation': False,
            'iconfile': 'assets/icons/app_icon.icns',  # 可选图标
            'plist': {
                'CFBundleName': '文档提取工具',
                'CFBundleDisplayName': '文档提取工具',
                'CFBundleVersion': '1.0.0',
                'CFBundleShortVersionString': '1.0.0',
                'CFBundleIdentifier': 'com.docextractor.app',
                'NSHighResolutionCapable': True,
            },
            'packages': [
                'PIL', 'PIL._tkinter_finder', 'mss', 'openai', 'pyautogui',
                'keyboard', 'pyperclip', 'pytesseract'
            ],
            'includes': [
                'tkinter', 'base64', 'json', 'queue', 'threading',
                'time', 'datetime', 'os', 'sys', 'argparse'
            ],
            'excludes': [],
        }
    }

setup(
    name='doc-extractor',
    version='1.0.0',
    description='从受限制的云桌面环境自动提取文档内容',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Claude Code Assistant',
    author_email='claude@anthropic.com',
    url='https://github.com/YukiAsuna19990413/Claude-Document-Extractor',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires='>=3.8',

    # 入口点
    entry_points={
        'console_scripts': [
            'doc-extractor=main:main',
            'doc-extractor-gui=src.gui.app:main',
        ],
    },

    # 可选依赖
    extras_require={
        'dev': [
            'black>=23.0.0',
            'flake8>=5.0.0',
            'pytest>=7.0.0',
            'mypy>=1.0.0',
        ],
        'gui': [
            'tkinter',
        ],
        'packaging': [
            'py2app>=0.28.6',
            'pyinstaller>=5.0.0',
        ],
    },

    # 分类器
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Multimedia :: Graphics :: Capture',
    ],

    # 关键词
    keywords='ocr document extraction automation screenshot',

    # 许可证
    license='MIT',

    # 项目 URL
    project_urls={
        'Bug Reports': 'https://github.com/YukiAsuna19990413/Claude-Document-Extractor/issues',
        'Source': 'https://github.com/YukiAsuna19990413/Claude-Document-Extractor',
        'Documentation': 'https://github.com/YukiAsuna19990413/Claude-Document-Extractor/blob/main/README.md',
    },
)