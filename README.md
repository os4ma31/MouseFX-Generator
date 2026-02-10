# 🖱️ MouseFX Generator

Transform your mouse cursor into something special! MouseFX Generator is a Windows application that brings your mouse to life with visual and audio effects.

## ✨ Overview

MouseFX Generator gives you a simple, visual way to add cool effects to your mouse cursor. Add satisfying click sounds, glowing highlights, animated ripples, and even spotlight effects that follow your cursor around the screen!

The app generates AutoHotkey v2 scripts that run in the background, adding all these effects without slowing down your computer. Plus, there's an experimental cursor animator that uses physics-based animations for that extra smooth feel.

Save up to three different effect profiles and switch between them instantly. The interface is clean and available in both English and Arabic. 🌍

## 📦 Current Version

`v1.1.0`

## 🎯 Features

### 🔊 Audio Effects
- Satisfying click sounds for left and right mouse buttons
- Master volume slider to get it just right
- Sync mode to use the same sound for both clicks
- Bring your own sounds - use any audio file you want!

### 🎨 Visual Effects
- **Cursor Highlight**: A glowing halo that follows your cursor everywhere
- **Click Effects**: Choose from 5 different shapes (Circle Ripple, Solid Circle, Square, Diamond, Static Circle)
- **Full Customization**: Pick your favorite colors, adjust sizes, and control opacity
- **Spotlight Mode**: Dim everything except a circle around your cursor - perfect for presentations!

### 🚀 Cursor Animator (Experimental)
- Smooth, physics-based cursor animations with spring dynamics
- Make your cursor bounce and wobble with adjustable stiffness and damping
- Scale your cursor up or down to your preferred size
- Built using the Windows Magnification API for native performance
- Automatically generates and compiles optimized C# code

### ⚙️ General Features
- **3 Profile Slots**: Save your favorite configurations and switch between them instantly
- **Global Hotkeys**: Toggle effects on and off without opening the app
- **Performance Options**: Adjust refresh rate to balance smoothness and CPU usage
- **Live Preview**: See your effects in action before applying them
- **Theme Support**: Choose between Light and Dark modes
- **Bilingual**: Full support for English and Arabic 🌐

## 💾 Installation

### What You'll Need

- **Operating System**: Windows 10 or later
- **AutoHotkey v2**: This is what powers the mouse effects! 🎮
  - 👉 Download from: https://www.autohotkey.com/v2/
- **Python 3.8+**: Only needed if you're running from source code
- **.NET Framework 4.0+**: Required for the fancy cursor animator feature

### Python Dependencies

Running from source? Install these packages first:

```bash
pip install PyQt6 qfluentwidgets
```

### 🎬 Getting Started

#### Option 1: Using the Executable
Just double-click `MouseFXGenerator.exe` and you're good to go! 🎉

#### Option 2: Running from Source
```bash
python mousefx_ui.py
```

## 🎮 Usage

### Getting Your Effects Up and Running

1. **Launch** the application 🚀
2. **Pick a profile** (1, 2, or 3) from the top menu - these are your save slots!
3. **Customize** your effects using the tabs:
   - **🔊 Audio**: Turn on sound effects and adjust volume
   - **⌨️ Shortcuts**: Set up hotkeys to toggle effects on the fly
   - **🖱️ Cursor**: Customize your highlight glow
   - **✨ Feedback**: Choose your click animation style
   - **💡 Spotlight**: Configure the screen dimming effect
   - **⚙️ System**: Tweak performance settings
   - **🎬 Animator**: Try out the experimental physics-based cursor (optional)
4. Hit **"Apply & Run Engine"** and watch the magic happen! ✨

### 📁 Where Things Are Saved

- **AutoHotkey Script**: `mousefx_engine.ahk` → Your `Documents` folder
- **Your Profiles**: `profiles.json` → `%APPDATA%/MouseFX Generator/`
- **Sound Files**: `sounds/` → `%APPDATA%/MouseFX Generator/`
- **Animator Files**: `Documents/MouseFX_Build/` (when using the animator)

### 🛑 How to Stop Effects

#### For AutoHotkey Effects
- Use your hotkeys to toggle effects on/off
- Right-click the AutoHotkey icon in your system tray and select "Exit"
- Press your emergency exit key (F12 by default)

#### For Cursor Animator
- Right-click the tray icon and choose "Exit"
- Press your emergency exit key

## ⚙️ Configuration

Your settings and profiles are automatically saved in these locations:

- **📋 Profile Data**: `%APPDATA%/MouseFX Generator/profiles.json`
- **🔊 Sound Files**: `%APPDATA%/MouseFX Generator/sounds/`
- **🎨 App Settings**: Stored in Windows Registry via QSettings
- **📝 Generated Scripts**: `~/Documents/mousefx_engine.ahk`
- **🔨 Animator Files**: `~/Documents/MouseFX_Build/`

### What's in a Profile?

Each profile remembers all your preferences:
- Audio settings (on/off, volume, sound files)
- Your custom hotkeys
- Highlight appearance (color, size, thickness, opacity)
- Click effect styles (shapes, colors, sync settings)
- Spotlight configuration (radius, opacity, color, animations)
- Performance tweaks

## 📝 Changelog

### v1.1.0 - Bug Fix Release 🐛
- Fixed audio not working after app closure
- Sounds now extracted to permanent location (`%APPDATA%/MouseFX Generator/`)

### v1.0.0 - Initial Release 🎉
- Everything is new and shiny!

## 🙏 Credits / Acknowledgements

### Sound Effects
The click audio used in this project is sourced from: https://github.com/spreyo/clicket

### Awesome Libraries & Tools
- **PyQt6**: The GUI framework that makes everything look good
- **qfluentwidgets**: Beautiful Fluent Design components
- **AutoHotkey v2**: The powerful scripting engine behind the effects
- **.NET Framework**: Powers the cursor animator compilation

---

## 📄 License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

Made with ❤️ for everyone who wants a more fun mouse cursor experience!
