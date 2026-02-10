import os
import json
import subprocess
import datetime
from PyQt6.QtGui import QColor

class ProfileManager:
    def __init__(self):
        # Use %APPDATA%/MouseFX Generator/ for profiles (hidden settings)
        app_data = os.path.join(os.environ["APPDATA"], "MouseFX Generator")
        if not os.path.exists(app_data):
            os.makedirs(app_data)
            
        self.profiles_path = os.path.join(app_data, "profiles.json")
        
        # Save the engine script to Documents so the user can easily find/edit it
        docs = os.path.expanduser("~/Documents")
        self.script_path = os.path.join(docs, "mousefx_engine.ahk")
        
        self.profiles = []
        self.current_index = 0
        self.load_profiles()

    def load_profiles(self):
        if os.path.exists(self.profiles_path):
            try:
                with open(self.profiles_path, 'r') as f:
                    self.profiles = json.load(f)
            except:
                self.profiles = []
        
        # Ensure we have 3 profiles
        if len(self.profiles) != 3:
            self.profiles = [self.get_default_profile() for _ in range(3)]

    def get_default_profile(self):
        return {
            "AudioEnabled": True,
            "MasterVolume": 80,
            "SyncSounds": True,
            "LeftSoundPath": "", 
            "RightSoundPath": "",
            "LeftSoundIndex": 1,
            "RightSoundIndex": 1,
            "HotkeySound": "F8",
            "HotkeyHighlight": "F9",
            "HotkeyClickFX": "F10",
            "HotkeySpotlight": "Ctrl+Space",
            "RefreshRateIndex": 2, 
            "HighlightEnabled": True,
            "HighlightColorHex": "#FFFF00",
            "HighlightSize": 60,
            "HighlightThickness": 0,
            "HighlightOpacity": 50,
            "ClickFxEnabled": True,
            "SyncVisuals": True,
            "LeftClickShape": "Circle Ripple",
            "LeftClickColorHex": "#00FFFF",
            "RightClickShape": "Circle Ripple",
            "RightClickColorHex": "#FF00FF",
            "SpotlightEnabled": False,
            "SpotlightRadius": 200,
            "SpotlightAnimSpeed": 20,
            "SpotlightOpacity": 180,
            "SpotlightColorHex": "#000000",
            "SpotlightAnimStyle": "Zoom"
        }

    def save_profile(self, index, data):
        if 0 <= index < len(self.profiles):
            self.profiles[index] = data
            try:
                with open(self.profiles_path, 'w') as f:
                    json.dump(self.profiles, f, indent=4)
            except Exception as e:
                print(f"Error saving profiles: {e}")

    def get_profile(self, index):
        if 0 <= index < len(self.profiles):
            return self.profiles[index]
        return self.get_default_profile()

class ScriptGenerator:
    @staticmethod
    def color_to_bgr(qcolor):
        return f"{qcolor.blue():02X}{qcolor.green():02X}{qcolor.red():02X}"

    @staticmethod
    def color_to_rgb_str(qcolor):
        return f"{qcolor.red():02X}{qcolor.green():02X}{qcolor.blue():02X}"
    
    @staticmethod
    def convert_hotkey(hotkey_str):
        if not hotkey_str: return ""
        return hotkey_str.replace("Ctrl+", "^").replace("Alt+", "!").replace("Shift+", "+").replace("Win+", "#")

    @staticmethod
    def escape_path(path):
        if not path: return ""
        return path.replace("\\", "\\\\")

    @staticmethod
    def generate_ahk_script(config):
        audio_enabled = config.get('AudioEnabled', False)
        hl_enabled = config.get('HighlightEnabled', False)
        click_fx_enabled = config.get('ClickFxEnabled', False)
        spotlight_enabled = config.get('SpotlightEnabled', False)
        
        left_sound = ScriptGenerator.escape_path(config.get('LeftSoundPath', ''))
        right_sound = ScriptGenerator.escape_path(config.get('RightSoundPath', ''))
        
        hl_color = QColor(config.get('HighlightColorHex', '#FFFF00'))
        left_click_color = QColor(config.get('LeftClickColorHex', '#00FFFF'))
        right_click_color = QColor(config.get('RightClickColorHex', '#FF00FF'))
        
        hl_size = config.get('HighlightSize', 60)
        hl_thickness = config.get('HighlightThickness', 0)
        hl_opacity = config.get('HighlightOpacity', 50)
        
        left_click_shape = config.get('LeftClickShape', 'Circle Ripple')
        right_click_shape = config.get('RightClickShape', 'Circle Ripple')
        
        refresh_rate_idx = config.get('RefreshRateIndex', 1)
        refresh_map = {0: 33, 1: 16, 2: 7}
        refresh_rate_ms = refresh_map.get(refresh_rate_idx, 16)
        
        sync_sounds = config.get('SyncSounds', True)
        sync_visuals = config.get('SyncVisuals', True)
        volume = config.get('MasterVolume', 80)
        
        hk_sound = config.get('HotkeySound', 'F8')
        hk_hl = config.get('HotkeyHighlight', 'F9')
        hk_click = config.get('HotkeyClickFX', 'F10')
        hk_spotlight = config.get('HotkeySpotlight', 'Ctrl+Space')
        
        spot_radius = config.get('SpotlightRadius', 200)
        spot_opacity = config.get('SpotlightOpacity', 180)
        spot_color = QColor(config.get('SpotlightColorHex', '#000000'))
        spot_anim_speed = config.get('SpotlightAnimSpeed', 20)
        spot_anim_style = config.get('SpotlightAnimStyle', 'Zoom')

        lines = []
        lines.append("; AutoHotkey v2 - MouseFX Engine")
        lines.append(f"; Generated by MouseFX Generator Python Port")
        lines.append(f"; Generation Time: {datetime.datetime.now()}")
        lines.append("")
        lines.append("#Requires AutoHotkey v2.0")
        lines.append("#SingleInstance Force")
        lines.append('CoordMode "Mouse", "Screen"')
        lines.append('DllCall("SetThreadDpiAwarenessContext", "Ptr", -4, "Ptr")')
        lines.append("")
        
        lines.append("; CONFIGURATION")
        lines.append(f"global audioEnabled := {str(audio_enabled).lower()}")
        lines.append(f"global highlightEnabled := {str(hl_enabled).lower()}")
        lines.append(f"global clickFxEnabled := {str(click_fx_enabled).lower()}")
        lines.append(f"global spotlightEnabled := {str(spotlight_enabled).lower()}")
        lines.append("")
        
        # Always define highlightRadius (needed by Static Circle even if highlight is disabled)
        lines.append(f"global highlightRadius := {int(hl_size / 2)}")
        
        if hl_enabled:
            lines.append("; Highlight Config")
            lines.append(f"global highlightColor := 0x{ScriptGenerator.color_to_bgr(hl_color)}")
            lines.append(f"global highlightThickness := {int(hl_thickness)}")
            lines.append(f"global highlightOpacity := {int(hl_opacity * 2.55)}")
            lines.append("")
            
        if click_fx_enabled:
            lines.append("; Click FX Config")
            lines.append(f"global leftClickColor := 0x{ScriptGenerator.color_to_bgr(left_click_color)}")
            lines.append(f"global leftClickShape := \"{left_click_shape}\"")
            
            if sync_visuals:
                lines.append(f"global rightClickColor := 0x{ScriptGenerator.color_to_bgr(left_click_color)}")
                lines.append(f"global rightClickShape := \"{left_click_shape}\"")
            else:
                lines.append(f"global rightClickColor := 0x{ScriptGenerator.color_to_bgr(right_click_color)}")
                lines.append(f"global rightClickShape := \"{right_click_shape}\"")
                
            lines.append("global clickAnimationDuration := 300")
            lines.append("global clickAnimationMaxRadius := 50")
            lines.append("")
            
        if audio_enabled:
            lines.append("; Audio Config")
            # Ensure path is escaped properly for AHK strings
            lines.append(f"global leftSoundFile := \"{left_sound}\"")
            if sync_sounds:
                lines.append(f"global rightSoundFile := \"{left_sound}\"")
            else:
                lines.append(f"global rightSoundFile := \"{right_sound}\"")
            
            lines.append(f"global soundVolume := {volume * 10}")
            lines.append("global soundCounter := 0")
            lines.append("")
            
        if spotlight_enabled:
            lines.append("; Spotlight Config")
            lines.append(f"global spotlightRadius := {spot_radius}")
            final_speed = spot_anim_speed
            if spot_anim_style == "Fade":
                final_speed = max(1, int((spot_anim_speed / 200.0) * 30))
            lines.append(f"global spotlightAnimSpeed := {final_speed}")
            lines.append(f"global spotlightOpacity := {spot_opacity}")
            lines.append(f"global spotlightColor := \"{ScriptGenerator.color_to_rgb_str(spot_color)}\"")
            lines.append(f"global spotlightAnimStyle := \"{spot_anim_style}\"")
            lines.append("")
            
        lines.append(f"global refreshRate := {refresh_rate_ms}")
        lines.append("")
        
        lines.append("; GUI INIT")
        if hl_enabled:
            lines.append('global highlightGui := Gui("+AlwaysOnTop -Caption +ToolWindow +E0x80000 +E0x20")')
            lines.append('highlightGui.Show("NA w100 h100")')
            lines.append("")
            
        if click_fx_enabled:
            lines.append('global clickGui := Gui("+AlwaysOnTop -Caption +ToolWindow +E0x80000 +E0x20")')
            lines.append('global isAnimating := false')
            lines.append('global animationStartTime := 0')
            lines.append('global clickType := ""')
            lines.append('global clickX := 0')
            lines.append('global clickY := 0')
            lines.append("")
            
        if spotlight_enabled:
            lines.append('global spotlightGui := unset')
            lines.append('global spCurrentRadius := 0')
            lines.append('global spCurrentOpacity := 0')
            lines.append('global spTargetState := 0')
            lines.append('global spMaxDist := 0')
            lines.append("")
            
        lines.append("; HOTKEYS")
        
        def add_hotkey(ui_key, func_name):
            ahk_key = ScriptGenerator.convert_hotkey(ui_key)
            if ahk_key:
                lines.append(f"{ahk_key}::{func_name}()")
                
        if audio_enabled: add_hotkey(hk_sound, "ToggleAudio")
        if hl_enabled: add_hotkey(hk_hl, "ToggleHighlight")
        if click_fx_enabled: add_hotkey(hk_click, "ToggleClickFx")
        if spotlight_enabled: add_hotkey(hk_spotlight, "ToggleSpotlight")
        lines.append("")
        
        lines.append("~LButton::{")
        if click_fx_enabled: lines.append('    ShowClickAnimation("left")')
        if audio_enabled: lines.append('    PlayClickSound("left")')
        lines.append("}")
        lines.append("")
        
        lines.append("~RButton::{")
        if click_fx_enabled: lines.append('    ShowClickAnimation("right")')
        if audio_enabled: lines.append('    PlayClickSound("right")')
        lines.append("}")
        lines.append("")
        
        if hl_enabled or click_fx_enabled:
            lines.append(f"SetTimer(UpdateEffects, {refresh_rate_ms})")
            
        lines.append('ToolTip("MouseFX Engine Started!")')
        lines.append('SetTimer(() => ToolTip(), -2000)')
        lines.append("")
        
        lines.append("; FUNCTIONS")
        
        if audio_enabled:
            lines.append("ToggleAudio() {")
            lines.append("    global audioEnabled")
            lines.append("    audioEnabled := !audioEnabled")
            lines.append('    ToolTip("Audio Effects: " . (audioEnabled ? "ON" : "OFF"))')
            lines.append('    SetTimer(() => ToolTip(), -1000)')
            lines.append("}")
            
        if hl_enabled:
            lines.append("ToggleHighlight() {")
            lines.append("    global highlightEnabled, highlightGui")
            lines.append("    highlightEnabled := !highlightEnabled")
            lines.append("    if (!highlightEnabled) {")
            lines.append("        highlightGui.Hide()")
            lines.append("    }")
            lines.append('    ToolTip("Highlight: " . (highlightEnabled ? "ON" : "OFF"))')
            lines.append('    SetTimer(() => ToolTip(), -1000)')
            lines.append("}")
            
        if click_fx_enabled:
            lines.append("ToggleClickFx() {")
            lines.append("    global clickFxEnabled, clickGui")
            lines.append("    clickFxEnabled := !clickFxEnabled")
            lines.append("    if (!clickFxEnabled) {")
            lines.append("        clickGui.Hide()")
            lines.append("    }")
            lines.append('    ToolTip("Click Effects: " . (clickFxEnabled ? "ON" : "OFF"))')
            lines.append('    SetTimer(() => ToolTip(), -1000)')
            lines.append("}")
            
        if spotlight_enabled:
            lines.append("""
ToggleSpotlight() {
    global spotlightGui, spCurrentRadius, spTargetState, spMaxDist, spCurrentOpacity
    global spotlightRadius, spotlightColor, spotlightOpacity, spotlightAnimStyle
    
    vWidth := SysGet(78)
    vHeight := SysGet(79)
    spMaxDist := Sqrt(vWidth**2 + vHeight**2) + 50
    
    if !IsSet(spotlightGui) {
        spotlightGui := Gui("+AlwaysOnTop +ToolWindow -Caption +E0x20")
        spotlightGui.BackColor := spotlightColor
        
        if (spotlightAnimStyle == "Fade") {
            WinSetTransparent(0, spotlightGui)
            spCurrentOpacity := 0
            spCurrentRadius := spotlightRadius
        } else {
            WinSetTransparent(spotlightOpacity, spotlightGui)
            if (spotlightAnimStyle == "None") {
                 spCurrentRadius := spotlightRadius
            } else {
                 spCurrentRadius := spMaxDist
            }
        }
        
        vLeft := SysGet(76)
        vTop := SysGet(77)
        spotlightGui.Show("x" vLeft " y" vTop " w" vWidth " h" vHeight " NoActivate")
        
        spTargetState := 1
        SetTimer(UpdateSpotlight, 10)
    } else {
        if (spTargetState == 1) {
            spTargetState := 0
            if (spotlightAnimStyle == "None") {
                spotlightGui.Destroy()
                spotlightGui := unset
                SetTimer(UpdateSpotlight, 0)
            } else {
                SetTimer(UpdateSpotlight, 10)
            }
        } else {
            spTargetState := 1
            SetTimer(UpdateSpotlight, 10)
        }
    }
}

UpdateSpotlight() {
    global spotlightGui, spCurrentRadius, spTargetState, spMaxDist, spCurrentOpacity
    global spotlightRadius, spotlightAnimSpeed, spotlightAnimStyle, spotlightOpacity
    
    if !IsSet(spotlightGui)
        return
        
    if (spotlightAnimStyle == "Fade") {
        if (spTargetState == 1) {
            if (spCurrentOpacity < spotlightOpacity) {
                spCurrentOpacity += spotlightAnimSpeed
                if (spCurrentOpacity > spotlightOpacity)
                    spCurrentOpacity := spotlightOpacity
                try WinSetTransparent(spCurrentOpacity, spotlightGui)
            }
        } else {
            if (spCurrentOpacity > 0) {
                spCurrentOpacity -= spotlightAnimSpeed
                if (spCurrentOpacity <= 0) {
                    spotlightGui.Destroy()
                    spotlightGui := unset
                    SetTimer(UpdateSpotlight, 0)
                    return
                }
                try WinSetTransparent(spCurrentOpacity, spotlightGui)
            }
        }
    } else {
        if (spTargetState == 1) {
            if (spCurrentRadius > spotlightRadius) {
                spCurrentRadius -= spotlightAnimSpeed
                if (spCurrentRadius < spotlightRadius)
                    spCurrentRadius := spotlightRadius
            }
        } else {
            if (spCurrentRadius < spMaxDist) {
                spCurrentRadius += spotlightAnimSpeed
                if (spCurrentRadius >= spMaxDist) {
                    spotlightGui.Destroy()
                    spotlightGui := unset
                    SetTimer(UpdateSpotlight, 0)
                    return
                }
            }
        }
    }
    
    MouseGetPos(&mX, &mY)
    spotlightGui.GetPos(,, &wW, &wH)
    vLeft := SysGet(76)
    vTop := SysGet(77)
    relX := mX - vLeft
    relY := mY - vTop
    
    hRgnFull := DllCall("Gdi32.dll\\CreateRectRgn", "Int", 0, "Int", 0, "Int", wW, "Int", wH, "Ptr")
    hRgnHole := DllCall("Gdi32.dll\\CreateEllipticRgn", "Int", relX - spCurrentRadius, "Int", relY - spCurrentRadius, "Int", relX + spCurrentRadius, "Int", relY + spCurrentRadius, "Ptr")
    
    DllCall("Gdi32.dll\\CombineRgn", "Ptr", hRgnFull, "Ptr", hRgnFull, "Ptr", hRgnHole, "Int", 3)
    DllCall("SetWindowRgn", "Ptr", spotlightGui.Hwnd, "Ptr", hRgnFull, "Int", 1)
    
    DllCall("Gdi32.dll\\DeleteObject", "Ptr", hRgnHole)
    DllCall("Gdi32.dll\\DeleteObject", "Ptr", hRgnFull)
}
""")

        if hl_enabled or click_fx_enabled:
            lines.append("UpdateEffects() {")
            if hl_enabled:
                lines.append("""
    global highlightEnabled, highlightGui, highlightRadius, highlightColor, highlightThickness, highlightOpacity
    
    if (highlightEnabled) {
        POINT := Buffer(8)
        DllCall("GetCursorPos", "Ptr", POINT)
        mouseX := NumGet(POINT, 0, "Int")
        mouseY := NumGet(POINT, 4, "Int")
        
        guiSize := highlightRadius * 2 + 10
        guiX := mouseX - guiSize // 2
        guiY := mouseY - guiSize // 2
        
        highlightGui.Show("NA x" guiX " y" guiY " w" guiSize " h" guiSize)
        DrawCircleWithOpacity(highlightGui, guiSize // 2, guiSize // 2, highlightRadius, highlightColor, highlightThickness, highlightOpacity)
    }
""")
            if click_fx_enabled:
                lines.append("""
    global isAnimating
    if (isAnimating) {
        UpdateClickAnimation()
    }
""")
            lines.append("}")
            lines.append("")

        if audio_enabled:
            lines.append("""
PlayClickSound(clickType) {
    global audioEnabled, leftSoundFile, rightSoundFile, soundCounter, soundVolume
    
    if (!audioEnabled) {
        return
    }
    
    soundFile := (clickType = "left") ? leftSoundFile : rightSoundFile
    
    if (!FileExist(soundFile)) {
        return
    }
    
    soundCounter++
    alias := "clicksound" . soundCounter
    
    try {
        currentVolume := Buffer(4)
        DllCall("winmm\\waveOutGetVolume", "Ptr", 0, "Ptr", currentVolume)
        savedVolume := NumGet(currentVolume, 0, "UInt")
        
        volumeLevel := (soundVolume * 65535) // 1000
        newVolume := volumeLevel | (volumeLevel << 16)
        DllCall("winmm\\waveOutSetVolume", "Ptr", 0, "UInt", newVolume)
        
        DllCall("winmm\\mciSendString", "Str", "open `"" . soundFile . "`" type waveaudio alias " . alias, "Ptr", 0, "UInt", 0, "Ptr", 0)
        DllCall("winmm\\mciSendString", "Str", "play " . alias . " from 0", "Ptr", 0, "UInt", 0, "Ptr", 0)
        
        SetTimer(() => (
            DllCall("winmm\\waveOutSetVolume", "Ptr", 0, "UInt", savedVolume),
            DllCall("winmm\\mciSendString", "Str", "close " . alias, "Ptr", 0, "UInt", 0, "Ptr", 0)
        ), -500)
    }
}
""")

        if click_fx_enabled:
            lines.append("""
ShowClickAnimation(type) {
    global clickFxEnabled, isAnimating, animationStartTime, clickType, clickX, clickY
    global clickGui, leftClickShape, rightClickShape, highlightRadius
    
    if (!clickFxEnabled) {
        return
    }
    
    ; Get new click position
    POINT := Buffer(8)
    DllCall("GetCursorPos", "Ptr", POINT)
    clickX := NumGet(POINT, 0, "Int")
    clickY := NumGet(POINT, 4, "Int")
    
    isAnimating := true
    animationStartTime := A_TickCount
    clickType := type
    
    ; Immediately position GUI at the new click location to prevent glitchy travel effect
    shape := (type = "left") ? leftClickShape : rightClickShape
    if (shape = "Static Circle") {
        guiSize := Integer(highlightRadius * 2 + 10)
    } else {
        guiSize := 60
    }
    
    guiX := Integer(clickX - guiSize // 2)
    guiY := Integer(clickY - guiSize // 2)
    clickGui.Show("NA x" guiX " y" guiY " w" guiSize " h" guiSize)
}

UpdateClickAnimation() {
    global isAnimating, animationStartTime, clickAnimationDuration, clickGui
    global clickType, clickX, clickY, clickAnimationMaxRadius, clickFxEnabled
    global leftClickColor, rightClickColor, leftClickShape, rightClickShape
    global highlightRadius
    
    if (!clickFxEnabled) {
        isAnimating := false
        clickGui.Hide()
        return
    }
    
    elapsed := A_TickCount - animationStartTime
    
    color := (clickType = "left") ? leftClickColor : rightClickColor
    shape := (clickType = "left") ? leftClickShape : rightClickShape
    
    ; Static Circle special behavior: follows cursor while button held
    if (shape = "Static Circle") {
        ; Check if mouse button is still pressed
        buttonPressed := (clickType = "left") ? GetKeyState("LButton", "P") : GetKeyState("RButton", "P")
        
        if (buttonPressed) {
            ; Button still held - update position to follow cursor
            POINT := Buffer(8)
            DllCall("GetCursorPos", "Ptr", POINT)
            clickX := NumGet(POINT, 0, "Int")
            clickY := NumGet(POINT, 4, "Int")
            
            currentRadius := highlightRadius
            opacity := 255
            guiSize := Integer(highlightRadius * 2 + 10)
        } else {
            ; Button released - hide immediately
            isAnimating := false
            clickGui.Hide()
            return
        }
    } else {
        ; Regular animated shapes
        if (elapsed >= clickAnimationDuration) {
            isAnimating := false
            clickGui.Hide()
            return
        }
        
        progress := elapsed / clickAnimationDuration
        progress := 1 - (1 - progress) ** 2
        
        currentRadius := clickAnimationMaxRadius * progress
        opacity := Integer(255 * (1 - progress))
        guiSize := Integer(currentRadius * 2 + 10)
    }
    
    if (guiSize < 10) {
        guiSize := 10
    }
    guiX := Integer(clickX - guiSize // 2)
    guiY := Integer(clickY - guiSize // 2)
    
    clickGui.Show("NA x" guiX " y" guiY " w" guiSize " h" guiSize)
    DrawShape(clickGui, guiSize // 2, guiSize // 2, currentRadius, color, shape, opacity)
}
""")

        if hl_enabled or click_fx_enabled:
            lines.append("""
DrawCircleWithOpacity(guiObj, centerX, centerY, radius, color, thickness, opacity) {
    static pToken := 0
    static Startup := 0
    
    if (radius <= 0 || opacity <= 0) {
        return
    }
    
    if (!Startup) {
        si := Buffer(24, 0)
        NumPut("UInt", 1, si)
        DllCall("gdiplus\\GdiplusStartup", "Ptr*", &pToken, "Ptr", si, "Ptr", 0)
        Startup := 1
    }
    
    hwnd := guiObj.Hwnd
    
    RECT := Buffer(16)
    DllCall("GetClientRect", "Ptr", hwnd, "Ptr", RECT)
    width := NumGet(RECT, 8, "Int")
    height := NumGet(RECT, 12, "Int")
    
    if (width <= 0 || height <= 0) {
        return
    }
    
    hdc := DllCall("GetDC", "Ptr", hwnd, "Ptr")
    memDC := DllCall("CreateCompatibleDC", "Ptr", hdc, "Ptr")
    
    BITMAPINFO := Buffer(40, 0)
    NumPut("UInt", 40, BITMAPINFO, 0)
    NumPut("Int", width, BITMAPINFO, 4)
    NumPut("Int", -height, BITMAPINFO, 8)
    NumPut("UShort", 1, BITMAPINFO, 12)
    NumPut("UShort", 32, BITMAPINFO, 14)
    NumPut("UInt", 0, BITMAPINFO, 16)
    
    hBitmap := DllCall("CreateDIBSection", "Ptr", memDC, "Ptr", BITMAPINFO, "UInt", 0, "Ptr*", &pBits:=0, "Ptr", 0, "UInt", 0, "Ptr")
    DllCall("SelectObject", "Ptr", memDC, "Ptr", hBitmap)
    
    DllCall("gdiplus\\GdipCreateFromHDC", "Ptr", memDC, "Ptr*", &pGraphics:=0)
    DllCall("gdiplus\\GdipSetSmoothingMode", "Ptr", pGraphics, "Int", 4)
    DllCall("gdiplus\\GdipGraphicsClear", "Ptr", pGraphics, "UInt", 0x00000000)
    
    r := (color >> 0) & 0xFF
    g := (color >> 8) & 0xFF
    b := (color >> 16) & 0xFF
    argbColor := (Integer(opacity) << 24) | (r << 16) | (g << 8) | b
    
    x := Float(centerX - radius)
    y := Float(centerY - radius)
    w := Float(radius * 2)
    h := Float(radius * 2)
    
    if (thickness > 0) {
        DllCall("gdiplus\\GdipCreatePen1", "UInt", argbColor, "Float", Float(thickness), "Int", 2, "Ptr*", &pPen:=0)
        DllCall("gdiplus\\GdipDrawEllipse", "Ptr", pGraphics, "Ptr", pPen, "Float", x, "Float", y, "Float", w, "Float", h)
        DllCall("gdiplus\\GdipDeletePen", "Ptr", pPen)
    } else {
        DllCall("gdiplus\\GdipCreateSolidFill", "UInt", argbColor, "Ptr*", &pBrush:=0)
        DllCall("gdiplus\\GdipFillEllipse", "Ptr", pGraphics, "Ptr", pBrush, "Float", x, "Float", y, "Float", w, "Float", h)
        DllCall("gdiplus\\GdipDeleteBrush", "Ptr", pBrush)
    }
    
    DllCall("gdiplus\\GdipFlush", "Ptr", pGraphics, "Int", 1)
    
    POINT := Buffer(8, 0)
    SIZE := Buffer(8)
    NumPut("Int", width, SIZE, 0)
    NumPut("Int", height, SIZE, 4)
    BLENDFUNCTION := Buffer(4)
    NumPut("UChar", 0, BLENDFUNCTION, 0)
    NumPut("UChar", 0, BLENDFUNCTION, 1)
    NumPut("UChar", 255, BLENDFUNCTION, 2)
    NumPut("UChar", 1, BLENDFUNCTION, 3)
    
    DllCall("UpdateLayeredWindow", "Ptr", hwnd, "Ptr", hdc, "Ptr", 0, "Ptr", SIZE, "Ptr", memDC, "Ptr", POINT, "UInt", 0, "Ptr", BLENDFUNCTION, "UInt", 2)
    
    DllCall("gdiplus\\GdipDeleteGraphics", "Ptr", pGraphics)
    DllCall("DeleteObject", "Ptr", hBitmap)
    DllCall("DeleteDC", "Ptr", memDC)
    DllCall("ReleaseDC", "Ptr", hwnd, "Ptr", hdc)
}

DrawShape(guiObj, centerX, centerY, size, color, shape, opacity) {
    static pToken := 0
    static Startup := 0
    
    if (size <= 0 || opacity <= 0) {
        return
    }
    
    if (!Startup) {
        si := Buffer(24, 0)
        NumPut("UInt", 1, si)
        DllCall("gdiplus\\GdiplusStartup", "Ptr*", &pToken, "Ptr", si, "Ptr", 0)
        Startup := 1
    }
    
    hwnd := guiObj.Hwnd
    
    RECT := Buffer(16)
    DllCall("GetClientRect", "Ptr", hwnd, "Ptr", RECT)
    width := NumGet(RECT, 8, "Int")
    height := NumGet(RECT, 12, "Int")
    
    if (width <= 0 || height <= 0) {
        return
    }
    
    hdc := DllCall("GetDC", "Ptr", hwnd, "Ptr")
    memDC := DllCall("CreateCompatibleDC", "Ptr", hdc, "Ptr")
    
    BITMAPINFO := Buffer(40, 0)
    NumPut("UInt", 40, BITMAPINFO, 0)
    NumPut("Int", width, BITMAPINFO, 4)
    NumPut("Int", -height, BITMAPINFO, 8)
    NumPut("UShort", 1, BITMAPINFO, 12)
    NumPut("UShort", 32, BITMAPINFO, 14)
    NumPut("UInt", 0, BITMAPINFO, 16)
    
    hBitmap := DllCall("CreateDIBSection", "Ptr", memDC, "Ptr", BITMAPINFO, "UInt", 0, "Ptr*", &pBits:=0, "Ptr", 0, "UInt", 0, "Ptr")
    DllCall("SelectObject", "Ptr", memDC, "Ptr", hBitmap)
    
    DllCall("gdiplus\\GdipCreateFromHDC", "Ptr", memDC, "Ptr*", &pGraphics:=0)
    DllCall("gdiplus\\GdipSetSmoothingMode", "Ptr", pGraphics, "Int", 4)
    DllCall("gdiplus\\GdipGraphicsClear", "Ptr", pGraphics, "UInt", 0x00000000)
    
    r := (color >> 0) & 0xFF
    g := (color >> 8) & 0xFF
    b := (color >> 16) & 0xFF
    argbColor := (Integer(opacity) << 24) | (r << 16) | (g << 8) | b
    
    switch shape {
        case "Circle Ripple":
        {
            DllCall("gdiplus\\GdipCreatePen1", "UInt", argbColor, "Float", Float(3), "Int", 2, "Ptr*", &pPen:=0)
            x := Float(centerX - size)
            y := Float(centerY - size)
            DllCall("gdiplus\\GdipDrawEllipse", "Ptr", pGraphics, "Ptr", pPen, "Float", x, "Float", y, "Float", size*2, "Float", size*2)
            DllCall("gdiplus\\GdipDeletePen", "Ptr", pPen)
        }
        case "Solid Circle":
        {
            DllCall("gdiplus\\GdipCreateSolidFill", "UInt", argbColor, "Ptr*", &pBrush:=0)
            x := Float(centerX - size)
            y := Float(centerY - size)
            DllCall("gdiplus\\GdipFillEllipse", "Ptr", pGraphics, "Ptr", pBrush, "Float", x, "Float", y, "Float", size*2, "Float", size*2)
            DllCall("gdiplus\\GdipDeleteBrush", "Ptr", pBrush)
        }
        case "Square":
        {
            DllCall("gdiplus\\GdipCreateSolidFill", "UInt", argbColor, "Ptr*", &pBrush:=0)
            x := Float(centerX - size)
            y := Float(centerY - size)
            DllCall("gdiplus\\GdipFillRectangle", "Ptr", pGraphics, "Ptr", pBrush, "Float", x, "Float", y, "Float", size*2, "Float", size*2)
            DllCall("gdiplus\\GdipDeleteBrush", "Ptr", pBrush)
        }
        case "Diamond":
        {
            DllCall("gdiplus\\GdipCreateSolidFill", "UInt", argbColor, "Ptr*", &pBrush:=0)
            DllCall("gdiplus\\GdipCreatePath", "Int", 0, "Ptr*", &pPath:=0)
            
            points := Buffer(32)
            NumPut("Float", Float(centerX), points, 0)
            NumPut("Float", Float(centerY - size), points, 4)
            NumPut("Float", Float(centerX + size), points, 8)
            NumPut("Float", Float(centerY), points, 12)
            NumPut("Float", Float(centerX), points, 16)
            NumPut("Float", Float(centerY + size), points, 20)
            NumPut("Float", Float(centerX - size), points, 24)
            NumPut("Float", Float(centerY), points, 28)
            
            DllCall("gdiplus\\GdipAddPathPolygon", "Ptr", pPath, "Ptr", points, "Int", 4)
            DllCall("gdiplus\\GdipFillPath", "Ptr", pGraphics, "Ptr", pBrush, "Ptr", pPath)
            
            DllCall("gdiplus\\GdipDeletePath", "Ptr", pPath)
            DllCall("gdiplus\\GdipDeleteBrush", "Ptr", pBrush)
        }
        case "Static Circle":
        {
            DllCall("gdiplus\\GdipCreatePen1", "UInt", argbColor, "Float", Float(3), "Int", 2, "Ptr*", &pPen:=0)
            x := Float(centerX - size)
            y := Float(centerY - size)
            DllCall("gdiplus\\GdipDrawEllipse", "Ptr", pGraphics, "Ptr", pPen, "Float", x, "Float", y, "Float", size*2, "Float", size*2)
            DllCall("gdiplus\\GdipDeletePen", "Ptr", pPen)
        }
    }
    
    DllCall("gdiplus\\GdipFlush", "Ptr", pGraphics, "Int", 1)
    
    POINT := Buffer(8, 0)
    SIZE := Buffer(8)
    NumPut("Int", width, SIZE, 0)
    NumPut("Int", height, SIZE, 4)
    BLENDFUNCTION := Buffer(4)
    NumPut("UChar", 0, BLENDFUNCTION, 0)
    NumPut("UChar", 0, BLENDFUNCTION, 1)
    NumPut("UChar", 255, BLENDFUNCTION, 2)
    NumPut("UChar", 1, BLENDFUNCTION, 3)
    
    DllCall("UpdateLayeredWindow", "Ptr", hwnd, "Ptr", hdc, "Ptr", 0, "Ptr", SIZE, "Ptr", memDC, "Ptr", POINT, "UInt", 0, "Ptr", BLENDFUNCTION, "UInt", 2)
    
    DllCall("gdiplus\\GdipDeleteGraphics", "Ptr", pGraphics)
    DllCall("DeleteObject", "Ptr", hBitmap)
    DllCall("DeleteDC", "Ptr", memDC)
    DllCall("ReleaseDC", "Ptr", hwnd, "Ptr", hdc)
}
""")

        return "\n".join(lines)