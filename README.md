# 🎮 The Sims 4 Auto-Saver

A small Windows utility that automatically presses configurable keys at set intervals when The Sims 4 is running. Since auto save is lacking in Sims 4, this program simply presses the escape key at regular intervals, to help remind you to save your game. While this is made with The Sims 4 in mind, if you have other games without auto save, this will work there as well.

## Features

- **Detects The Sims 4** - Only runs when the game is detected
- **Configurable intervals** - From 1 second to 30 minutes
- **Key options** - Escape, F5, F9, Ctrl+S, Ctrl+Shift+S
- **Simple GUI**
- **Test Mode** - Verify functionality without the game running
- **Settings persistence** - Saves your preferences between sessions

## Requirements

- Windows 10/11
- Python 3.8+ (for development)
- The Sims 4 game

## Installation

### Option 1: Pre-built Executable (Recommended)

1. Download the latest `sims-saver.exe` from the releases
2. Run the executable - no installation required

### Option 2: From Source

1. Clone this repository
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Run the application:
   ```bash
   uv run sims-saver
   ```

## Usage

1. Launch the application
2. Set your desired save interval in minutes
3. **Choose the key to press** from the dropdown menu:
   - **Escape** (default) - Opens the game menu, perfect for manual saving
   - **F5** - Common quicksave key in many games
   - **F9** - Alternative quicksave key
   - **Ctrl+S** - Standard save shortcut
   - **Ctrl+Shift+S** - Custom save combination
4. **Optional**: Enable "Test Mode" to press keys regardless of whether The Sims 4 is running (useful for testing)
5. Click "Start Auto-Save"
6. Launch The Sims 4 (unless in Test Mode)
7. The program will automatically press your selected key at the specified intervals
8. Click "Stop Auto-Save" to stop the process

### Key Selection Guide

Choose the best key for your needs:

- **Escape** (Recommended): Opens the game menu without disrupting gameplay. You can then manually choose to save or continue playing.
- **F5/F9**: If The Sims 4 uses these as save keys, they'll trigger an immediate save
- **Ctrl+S/Ctrl+Shift+S**: Standard save shortcuts that many games recognize

### Test Mode

Test Mode allows you to test the key pressing functionality without having The Sims 4 running. This is useful for:
- Verifying the program works correctly
- Testing with different applications that use the same keybinding
- Debugging key press issues
- Setting up the program before playing

## Building from Source

To build a standalone executable:

```bash
# Install PyInstaller
uv add pyinstaller

# Build the executable
uv run pyinstaller sims-saver.spec
```

The executable will be created in the `dist/` directory.

## Technical Details

- Uses `psutil` to detect running processes
- Uses `pynput` for keyboard simulation
- Built with Tkinter for the GUI
- Settings stored in JSON format

## Safety Notes

- Make sure The Sims 4 has focus when saves occur
- The program only sends key presses when The Sims 4 is detected as running
- Settings are saved locally in the same directory as the executable

## Troubleshooting

- If saves aren't working, ensure The Sims 4 is running and has window focus
- Check that Ctrl+Shift+S is indeed the quick-save keybinding in your game
- The program detects The Sims 4 by looking for processes named `ts4.exe`, `the sims 4.exe`, or `ts4_x64.exe`
