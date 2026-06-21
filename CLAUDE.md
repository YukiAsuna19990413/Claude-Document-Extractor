# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a document extraction tool designed to automatically extract content from restricted cloud desktop environments (like VMware Horizon Client) using automatic screenshots and OCR. The tool supports both command-line and GUI interfaces with multiple OCR options.

## Architecture

### Core Components

1. **doc_extractor.py** - Command-line interface core
   - Handles screenshot capture using pyautogui and mss
   - Integrates with multiple OCR providers (Tesseract, Zhipu AI, DeepSeek)
   - Manages document scrolling and extraction workflow
   - Uses threading for non-blocking operations

2. **doc_extractor_gui.py** - GUI interface
   - Built with tkinter/ttk for cross-platform compatibility
   - Tabbed interface with control panel and results display
   - Manages API configuration through dialog windows
   - Uses message queue for thread-safe UI updates

3. **area_selector.py** - Visual area selection utility
   - Creates semi-transparent overlay for area selection
   - Outputs coordinates for screenshot regions
   - Standalone tool for precise area definition

### Key Data Structures

- **API Configuration**: Stored in `api_config.json` with provider, API key, base URL, and model settings
- **Screenshot Management**: Stores image data, coordinates, and timestamps in memory
- **Message Queue**: Thread-safe communication between extraction threads and GUI

## Common Commands

### Running the Application

```bash
# GUI version (primary interface)
python3 doc_extractor_gui.py

# Command-line version
python3 doc_extractor.py

# Area selection utility
python3 area_selector.py

# Test GUI features
python3 test_gui_features.py
```

### Building macOS App

```bash
# Install py2app first
pip install py2app

# Build the .app application
python3 setup.py py2app

# The app will be created in dist/ directory
open dist/
```

### Testing

```bash
# Run GUI feature tests
python3 test_gui.py

# Run comprehensive feature test
python3 test_gui_features.py
```

## Configuration

### API Setup

The tool uses `api_config.json` for API configuration:
```json
{
  "enabled": true,
  "provider": "zhipu",
  "api_key": "your-api-key",
  "base_url": "https://open.bigmodel.cn/api/paas/v4",
  "model": "glm-4-air"
}
```

### Supported OCR Providers

1. **Zhipu AI (glm-4-air)** - High accuracy, supports tables and formulas
2. **Tesseract** - Local OCR, no internet required
3. **DeepSeek** - Alternative API provider

## Development Notes

### Dependencies

Core dependencies include:
- `pyautogui` - Screen automation and capture
- `mss` - Fast screen capture
- `PIL/Pillow` - Image processing
- `pytesseract` - Local OCR
- `tkinter` - GUI interface
- `openai` - API client for Zhipu AI

### Threading Model

The GUI uses threading for extraction operations:
- Main thread handles UI updates
- Worker threads perform extraction tasks
- Message queue facilitates thread-safe communication

### UI Architecture

- Left panel: Controls (area selection, OCR settings, extraction controls)
- Right panel: Results display with tabs for logs and extracted text
- Status updates shown in real-time during extraction

### File Organization

- GUI components are self-contained in `doc_extractor_gui.py`
- Helper utilities are separate modules for reusability
- Configuration files are stored in JSON format for easy editing