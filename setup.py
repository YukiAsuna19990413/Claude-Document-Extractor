from setuptools import setup

APP = ['doc_extractor_gui.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,  # 可以添加 .icns 图标
    'plist': {
        'CFBundleName': '文档提取工具',
        'CFBundleDisplayName': '文档提取工具',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleIdentifier': 'com.docextractor.app',
        'NSHighResolutionCapable': True,
    },
    'packages': [
        'PIL', 'PIL._tkinter_finder', 'mss', 'openai', 'pyautogui'
    ],
    'includes': [
        'tkinter', 'base64', 'json', 'queue', 'threading',
        'time', 'datetime', 'os'
    ],
    'excludes': [],
}

setup(
    app=APP,
    name='文档提取工具',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)