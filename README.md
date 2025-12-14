# KSell - The Forge (Roblox)

<p align="center">
  <img src="icon.png" alt="KSell" width="128" height="128">
</p>

Automation tool for selling items in The Forge on Roblox using image recognition.

## Features

- Automatic item selling with OpenCV image detection
- Customizable hotkey (default: F8) and timer (default: 10 minutes)
- Auto-clicking between sales
- Dark themed GUI with item gallery
- DirectX game support via PyDirectInput

## Installation

```bash
pip install pyautogui pydirectinput keyboard opencv-python pygetwindow pillow
python macro.py
```

Or use the compiled `KSell.exe`

## Setup

1. Create folder structure:
```
KSell/
├── macro.py
└── images/
    ├── stash.png
    ├── sell_items.png
    ├── max.png
    ├── select.png
    ├── accept.png
    ├── yes.png
    ├── x.png
    └── ores/
        └── [your item screenshots]
```

2. Take screenshots of UI buttons and items using Snipping Tool (Win + Shift + S)
3. Save as PNG in correct folders
4. Run the program

## Usage

- **F8** - Start macro
- **F4 / ESC** - Exit
- Add item screenshots to `images/ores/` folder
- Configure hotkey and timer in UI

## How It Works

1. Presses T to open Stash
2. Clicks Stash → Sell Items
3. For each item in `ores/` folder:
   - Finds and clicks item
   - Clicks Max → Select
4. Clicks Accept → Yes → X
5. Auto-clicks screen center every 0.1s between cycles
6. Repeats every X minutes

## Configuration

Edit `config.json`:
```json
{
    "hotkey": "f8",
    "timer_minutes": 10
}
```

## Troubleshooting

**Items not found?**
- Lower confidence in code: `confidence=0.65` → `0.5`
- Enable debug: `save_debug=True`

**Clicks don't work?**
- Game must be in focus
- Uses PyDirectInput for DirectX games

## Build EXE

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "KSell" macro.py
```

Output: `dist/KSell.exe`

## Disclaimer

Use at your own risk. May violate Roblox Terms of Service.
