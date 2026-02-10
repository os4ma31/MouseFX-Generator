import sys
import os
import shutil
import subprocess
from enum import Enum
from PyQt6.QtCore import Qt, QSize, QPoint, QTimer, QUrl, pyqtSignal, QRect, QSettings
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QAction, QDesktopServices, QFont, QIcon, QPixmap, QMovie
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, 
    QLabel, QFrame, QSizePolicy, QScrollArea, QGraphicsOpacityEffect
)
from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

# Import Fluent Widgets
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CaptionLabel, StrongBodyLabel,
    CardWidget, SwitchButton, Slider, ColorPickerButton,
    ComboBox, PrimaryPushButton, PushButton, RadioButton,
    FluentIcon as FIF, InfoBar, InfoBarPosition,
    setTheme, Theme, isDarkTheme, setThemeColor,
    TransparentToolButton, RoundMenu, Action, 
    SegmentedWidget, CheckBox, MSFluentWindow, NavigationItemPosition,
    MessageBox, HyperlinkButton
)

from mousefx_logic import ProfileManager, ScriptGenerator
from mousefx_animation import AnimationEngine

# --- Helper for PyInstaller Single File ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if not relative_path:
        return ""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

# --- Localization & Text Manager ---
class Localizer:
    TRANS = {
        "en": {
            "AppTitle": "MouseFX Generator",
            "Audio": "Audio",
            "SoundFx": "Sound Effects",
            "SoundDesc": "Plays sounds when you click.",
            "MasterVol": "Master Volume",
            "SyncAudio": "Sync Left & Right Sounds",
            "LeftClick": "Left Click",
            "RightClick": "Right Click",
            "Shortcuts": "Shortcuts",
            "GlobalHotkeys": "Global Hotkeys",
            "HotkeysDesc": "Shortcuts work in background.",
            "ToggleSound": "Toggle Sound",
            "ToggleHl": "Toggle Highlight",
            "ToggleFx": "Toggle Click FX",
            "SpotlightHk": "Spotlight Hotkey",
            "Cursor": "Cursor",
            "Highlight": "Highlight",
            "HlDesc": "Permanent halo around cursor.",
            "Color": "Color",
            "Size": "Size",
            "Thickness": "Thickness",
            "Opacity": "Opacity",
            "Feedback": "Feedback",
            "ClickFx": "Click Effects",
            "ClickFxDesc": "Visual ripple on click.",
            "SyncFx": "Sync Left & Right Effects",
            "LeftClickFx": "Left Click",
            "RightClickFx": "Right Click",
            "Spotlight": "Spotlight",
            "MouseSpot": "Mouse Spotlight",
            "SpotDesc": "Dims screen except circle.",
            "SpotRadius": "Spotlight Radius",
            "AnimSpeed": "Animation Speed",
            "BgOpacity": "Background Opacity",
            "BgColor": "Background Color",
            "AnimStyle": "Animation Style",
            "System": "System",
            "RefreshRate": "Refresh Rate",
            "Preview": "Preview",
            "InteractivePrev": "\n\nInteractive Preview\nClick anywhere to test",
            "InteractivePrevAr": "\n\nمعاينة تفاعلية\nانقر في أي مكان للتجربة",
            "Profiles": "Profiles:",
            "Ready": "Ready",
            "GenConfig": "Generating configuration...",
            "SuccessTitle": "Success",
            "SuccessMsg": "Engine script generated and started successfully.",
            "EngineRun": "Engine Running!",
            "ApplyBtn": "Apply & Run Engine",
            "KillEngine": "How to Stop the Engine",
            "KillAnimator": "How to Stop the Animator",
            "Settings": "Settings",
            "Personalization": "Personalization",
            "AppTheme": "Application Theme",
            "AccentColor": "Accent Color",
            "SyncSystem": "Sync with System",
            "Language": "Language",
            "Light": "Light",
            "Dark": "Dark",
            "AppPerformance": "App Performance",
            "DisablePreview": "Disable Interactive Preview",
            "DisableAnim": "Disable Animations",
            "AHKTitle": "AutoHotkey v2 Required",
            "AHKMsg": "This program requires AutoHotkey v2 to run the generated script.\nDo you have AutoHotkey v2 installed?",
            "Download": "Download AHK v2",
            "IHaveIt": "I have it",
            "Info": "Info & Help",
            "CheckUpdates": "Check for Updates",
            "FAQ": "Frequently Asked Questions",
            "Q1": "Where is the AHK script saved?",
            "A1": "The 'mousefx_engine.ahk' file is saved in your Documents folder.",
            "Q2": "Where are my settings saved?",
            "A2": "Profiles are saved in %APPDATA%/MouseFX Generator/profiles.json.",
            "Q3": "Does this impact performance?",
            "A3": "No. The engine is extremely lightweight (0-3% CPU, ~5MB RAM). It does not affect gaming performance.",
            "Version": "Version 1.0.0 | By: os4ma31",
            # --- Animation Tab Strings ---
            "Animator": "Animator",
            "AnimWarning": "EXPERIMENTAL FEATURE",
            "AnimHeaderDesc": "This feature utilizes a C# engine with the native Windows Magnification API to overlay a custom, animated cursor.\n\nImportant: This hides the actual system cursor. If recording your screen (e.g., OBS), ensure you disable cursor capture to avoid conflicts.",
            "AnimPhysics": "Animation Physics",
            "ClickScale": "Click Scale Target",
            "ClickScaleTooltip": "Controls cursor size when clicked.\nValues < 1.0 shrink the cursor (e.g. 0.8).\nValues > 1.0 enlarge it.",
            "AnimStiffness": "Animation Speed",
            "AnimStiffnessTooltip": "Controls the spring stiffness.\nLower = Loose, slow spring.\nHigher = Tight, fast spring.",
            "EnableBounce": "Enable Bounce",
            "BounceTooltip": "Adds a spring/overshoot effect.",
            "SpringFactor": "Spring Factor",
            "SpringTooltip": "Controls the bounciness (Damping).\nLow = Rigid/No overshoot.\nHigh = Wobbly/High overshoot.",
            "AppearanceSize": "Appearance & Size",
            "GlobalSize": "Global Size Multiplier",
            "GlobalSizeTooltip": "Scales the overall cursor size.\n1.0 = Original Size.\n> 1.0 = Larger, < 1.0 = Smaller.",
            "CursorOpacity": "Opacity",
            "OpacityTooltip": "Controls cursor transparency.\n0.1 = Almost invisible.\n1.0 = Fully visible.",
            "FallbackColor": "Fallback Color",
            "SystemBehavior": "System Behavior",
            "EmergencyKey": "Emergency Exit Key",
            "ShowTray": "Show Tray Icon",
            "TrayTooltip": "Show icon in system tray.",
            "DeployRun": "Deploy & Run",
            "Reset": "Reset Defaults"
        },
        "ar": {
            "AppTitle": "مولد تأثيرات الماوس",
            "Audio": "الصوت",
            "SoundFx": "المؤثرات الصوتية",
            "SoundDesc": "تشغيل أصوات عند النقر.",
            "MasterVol": "مستوى الصوت الرئيسي",
            "SyncAudio": "مزامنة الأصوات (يسار/يمين)",
            "LeftClick": "نقرة يسار",
            "RightClick": "نقرة يمين",
            "Shortcuts": "الاختصارات",
            "GlobalHotkeys": "مفاتيح الاختصار العامة",
            "HotkeysDesc": "تعمل الاختصارات في الخلفية.",
            "ToggleSound": "تبديل الصوت",
            "ToggleHl": "تبديل التمييز",
            "ToggleFx": "تبديل التأثيرات",
            "SpotlightHk": "مفتاح الكشاف",
            "Cursor": "المؤشر",
            "Highlight": "التمييز",
            "HlDesc": "هالة دائمة حول المؤشر.",
            "Color": "اللون",
            "Size": "الحجم",
            "Thickness": "السمك",
            "Opacity": "الشفافية",
            "Feedback": "التغذية البصرية",
            "ClickFx": "تأثيرات النقر",
            "ClickFxDesc": "تموج مرئي عند النقر.",
            "SyncFx": "مزامنة التأثيرات (يسار/يمين)",
            "LeftClickFx": "نقرة يسار",
            "RightClickFx": "نقرة يمين",
            "Spotlight": "الكشاف",
            "MouseSpot": "كشاف الماوس",
            "SpotDesc": "تعتيم الشاشة ما عدا المؤشر.",
            "SpotRadius": "نصف قطر الكشاف",
            "AnimSpeed": "سرعة الحركة",
            "BgOpacity": "شفافية الخلفية",
            "BgColor": "لون الخلفية",
            "AnimStyle": "نمط الحركة",
            "System": "النظام",
            "RefreshRate": "معدل التحديث",
            "Preview": "المعاينة",
            "InteractivePrev": "\n\nمعاينة تفاعلية\nانقر في أي مكان للتجربة",
            "InteractivePrevAr": "\n\nمعاينة تفاعلية\nانقر في أي مكان للتجربة",
            "Profiles": "الملفات الشخصية:",
            "Ready": "جاهز",
            "GenConfig": "جاري إنشاء التكوين...",
            "SuccessTitle": "تم بنجاح",
            "SuccessMsg": "تم إنشاء وتشغيل المحرك بنجاح.",
            "EngineRun": "المحرك يعمل!",
            "ApplyBtn": "تطبيق وتشغيل",
            "KillEngine": "كيفية إيقاف المحرك",
            "KillAnimator": "كيفية إيقاف الرسوم",
            "Settings": "الإعدادات",
            "Personalization": "التخصيص",
            "AppTheme": "مظهر التطبيق",
            "AccentColor": "لون التمييز",
            "SyncSystem": "مزامنة مع النظام",
            "Language": "اللغة",
            "Light": "فاتح",
            "Dark": "داكن",
            "AppPerformance": "أداء التطبيق",
            "DisablePreview": "تعطيل المعاينة التفاعلية",
            "DisableAnim": "تعطيل الرسوم المتحركة",
            "AHKTitle": "مطلوب AutoHotkey v2",
            "AHKMsg": "هذا البرنامج يتطلب AutoHotkey v2 لتشغيل السكربت المولد.\nهل لديك AutoHotkey v2 مثبت؟",
            "Download": "تحميل AHK v2",
            "IHaveIt": "لدي البرنامج",
            "Info": "معلومات ومساعدة",
            "CheckUpdates": "التحقق من التحديثات",
            "FAQ": "الأسئلة الشائعة",
            "Q1": "أين يتم حفظ ملف السكربت؟",
            "A1": "يتم حفظ ملف 'mousefx_engine.ahk' في مجلد المستندات.",
            "Q2": "أين يتم حفظ إعداداتي؟",
            "A2": "يتم حفظ الملفات الشخصية في %APPDATA%/MouseFX Generator/profiles.json.",
            "Q3": "هل يؤثر هذا على الأداء؟",
            "A3": "لا. المحرك خفيف جداً (0-3% معالج، ~5 ميجابايت رام). ولا يؤثر على أداء الألعاب.",
            "Version": "الإصدار 1.0.0 | بواسطة: أُسامة",
            # --- Animation Tab Strings ---
            "Animator": "Animator",
            "AnimWarning": "EXPERIMENTAL FEATURE",
            "AnimHeaderDesc": "This feature utilizes a C# engine with the native Windows Magnification API to overlay a custom, animated cursor.\n\nImportant: This hides the actual system cursor. If recording your screen (e.g., OBS), ensure you disable cursor capture to avoid conflicts.",
            "AnimPhysics": "Animation Physics",
            "ClickScale": "Click Scale Target",
            "ClickScaleTooltip": "Controls cursor size when clicked.\nValues < 1.0 shrink the cursor (e.g. 0.8).\nValues > 1.0 enlarge it.",
            "AnimStiffness": "Animation Speed",
            "AnimStiffnessTooltip": "Controls the spring stiffness.\nLower = Loose, slow spring.\nHigher = Tight, fast spring.",
            "EnableBounce": "Enable Bounce",
            "BounceTooltip": "Adds a spring/overshoot effect.",
            "SpringFactor": "Spring Factor",
            "SpringTooltip": "Controls the bounciness (Damping).\nLow = Rigid/No overshoot.\nHigh = Wobbly/High overshoot.",
            "AppearanceSize": "Appearance & Size",
            "GlobalSize": "Global Size Multiplier",
            "GlobalSizeTooltip": "Scales the overall cursor size.\n1.0 = Original Size.\n> 1.0 = Larger, < 1.0 = Smaller.",
            "CursorOpacity": "Opacity",
            "OpacityTooltip": "Controls cursor transparency.\n0.1 = Almost invisible.\n1.0 = Fully visible.",
            "FallbackColor": "Fallback Color",
            "SystemBehavior": "System Behavior",
            "EmergencyKey": "Emergency Exit Key",
            "ShowTray": "Show Tray Icon",
            "TrayTooltip": "Show icon in system tray.",
            "DeployRun": "Deploy & Run",
            "Reset": "Reset Defaults"
        },
        "ar": {
            "AppTitle": "مولد تأثيرات الماوس",
            "Audio": "الصوت",
            "SoundFx": "المؤثرات الصوتية",
            "SoundDesc": "تشغيل أصوات عند النقر.",
            "MasterVol": "مستوى الصوت الرئيسي",
            "SyncAudio": "مزامنة الأصوات (يسار/يمين)",
            "LeftClick": "نقرة يسار",
            "RightClick": "نقرة يمين",
            "Shortcuts": "الاختصارات",
            "GlobalHotkeys": "مفاتيح الاختصار العامة",
            "HotkeysDesc": "تعمل الاختصارات في الخلفية.",
            "ToggleSound": "تبديل الصوت",
            "ToggleHl": "تبديل التمييز",
            "ToggleFx": "تبديل التأثيرات",
            "SpotlightHk": "مفتاح الكشاف",
            "Cursor": "المؤشر",
            "Highlight": "التمييز",
            "HlDesc": "هالة دائمة حول المؤشر.",
            "Color": "اللون",
            "Size": "الحجم",
            "Thickness": "السمك",
            "Opacity": "الشفافية",
            "Feedback": "التغذية البصرية",
            "ClickFx": "تأثيرات النقر",
            "ClickFxDesc": "تموج مرئي عند النقر.",
            "SyncFx": "مزامنة التأثيرات (يسار/يمين)",
            "LeftClickFx": "نقرة يسار",
            "RightClickFx": "نقرة يمين",
            "Spotlight": "الكشاف",
            "MouseSpot": "كشاف الماوس",
            "SpotDesc": "تعتيم الشاشة ما عدا المؤشر.",
            "SpotRadius": "نصف قطر الكشاف",
            "AnimSpeed": "سرعة الحركة",
            "BgOpacity": "شفافية الخلفية",
            "BgColor": "لون الخلفية",
            "AnimStyle": "نمط الحركة",
            "System": "النظام",
            "RefreshRate": "معدل التحديث",
            "Preview": "المعاينة",
            "InteractivePrev": "\n\nمعاينة تفاعلية\nانقر في أي مكان للتجربة",
            "InteractivePrevAr": "\n\nمعاينة تفاعلية\nانقر في أي مكان للتجربة",
            "Profiles": "الملفات الشخصية:",
            "Ready": "جاهز",
            "GenConfig": "جاري إنشاء التكوين...",
            "SuccessTitle": "تم بنجاح",
            "SuccessMsg": "تم إنشاء وتشغيل المحرك بنجاح.",
            "EngineRun": "المحرك يعمل!",
            "ApplyBtn": "تطبيق وتشغيل",
            "KillEngine": "كيفية إيقاف المحرك",
            "KillAnimator": "كيفية إيقاف الرسوم",
            "Settings": "الإعدادات",
            "Personalization": "التخصيص",
            "AppTheme": "مظهر التطبيق",
            "AccentColor": "لون التمييز",
            "SyncSystem": "مزامنة مع النظام",
            "Language": "اللغة",
            "Light": "فاتح",
            "Dark": "داكن",
            "AppPerformance": "أداء التطبيق",
            "DisablePreview": "تعطيل المعاينة التفاعلية",
            "DisableAnim": "تعطيل الرسوم المتحركة",
            "AHKTitle": "مطلوب AutoHotkey v2",
            "AHKMsg": "هذا البرنامج يتطلب AutoHotkey v2 لتشغيل السكربت المولد.\nهل لديك AutoHotkey v2 مثبت؟",
            "Download": "تحميل AHK v2",
            "IHaveIt": "لدي البرنامج",
            "Info": "معلومات ومساعدة",
            "CheckUpdates": "التحقق من التحديثات",
            "FAQ": "الأسئلة الشائعة",
            "Q1": "أين يتم حفظ ملف السكربت؟",
            "A1": "يتم حفظ ملف 'mousefx_engine.ahk' في مجلد المستندات.",
            "Q2": "أين يتم حفظ إعداداتي؟",
            "A2": "يتم حفظ الملفات الشخصية في %APPDATA%/MouseFX Generator/profiles.json.",
            "Q3": "هل يؤثر هذا على الأداء؟",
            "A3": "لا. المحرك خفيف جداً (0-3% معالج، ~5 ميجابايت رام). ولا يؤثر على أداء الألعاب.",
            "Version": "الإصدار 1.0.0 | بواسطة: أُسامة",
            # --- Animation Tab Strings (Auto-translated placeholders) ---
            "Animator": "محرك الرسوم",
            "AnimWarning": "ميزة تجريبية",
            "AnimHeaderDesc": "تستخدم هذه الميزة محرك C# مع واجهة تكبير Windows الأصلية لإضافة مؤشر متحرك.\n\nهام: تخفي هذه الميزة مؤشر النظام الفعلي. عند تسجيل الشاشة، تأكد من تعطيل التقاط المؤشر لتجنب التعارض.",
            "AnimPhysics": "فيزياء الحركة",
            "ClickScale": "حجم النقر المستهدف",
            "ClickScaleTooltip": "ما مدى صغر حجم المؤشر عند النقر.",
            "AnimStiffness": "سرعة الحركة",
            "AnimStiffnessTooltip": "صلابة الرسوم المتحركة.",
            "EnableBounce": "تفعيل الارتداد",
            "BounceTooltip": "يضيف تأثير الزنبرك/التجاوز.",
            "SpringFactor": "عامل الزنبرك",
            "SpringTooltip": "التحكم في الارتداد.",
            "AppearanceSize": "المظهر والحجم",
            "GlobalSize": "مضاعف الحجم العام",
            "GlobalSizeTooltip": "إجبار المؤشر ليكون أكبر/أصغر.",
            "CursorOpacity": "الشفافية",
            "OpacityTooltip": "شفافية المؤشر.",
            "FallbackColor": "لون احتياطي",
            "SystemBehavior": "سلوك النظام",
            "EmergencyKey": "مفتاح الخروج الطوارئ",
            "ShowTray": "إظهار أيقونة النظام",
            "TrayTooltip": "إظهار الأيقونة في شريط المهام.",
            "DeployRun": "نشر وتشغيل",
            "Reset": "إعادة تعيين الافتراضيات"
        }
    }

    current_lang = "en"

    @classmethod
    def get(cls, key):
        return cls.TRANS.get(cls.current_lang, cls.TRANS["en"]).get(key, key)

# --- Video Player Window ---
class VideoPlayerWindow(QWidget):
    """Simple video player window for tutorial videos"""
    def __init__(self, video_path, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        # 16:9 aspect ratio: 800x450 for video + 50 for controls = 500 total height
        self.resize(800, 500)
        
        # Make it a standalone window
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinMaxButtonsHint)
        
        # Center on screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video Widget
        self.video_widget = QVideoWidget()
        layout.addWidget(self.video_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 5, 10, 10)
        
        self.btn_play = PushButton("Pause")
        self.btn_play.setFixedWidth(80)
        self.btn_play.clicked.connect(self.toggle_play)
        
        self.btn_restart = PushButton("Restart")
        self.btn_restart.setFixedWidth(80)
        self.btn_restart.clicked.connect(self.restart_video)
        
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_restart)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Media Player
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Set video source and auto-play
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        
        # Connect signals
        self.media_player.playbackStateChanged.connect(self.on_state_changed)
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        
        # Auto-play when window is shown
        QTimer.singleShot(100, self.media_player.play)
        
    def toggle_play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def restart_video(self):
        self.media_player.setPosition(0)
        self.media_player.play()
    
    def on_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_play.setText("Pause")
        else:
            self.btn_play.setText("Play")
    
    def on_media_status_changed(self, status):
        """Auto-replay when video ends"""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.media_player.setPosition(0)
            self.media_player.play()
    
    def closeEvent(self, event):
        self.media_player.stop()
        event.accept()

# --- Hotkey Capture Dialog ---
class HotkeyDialog(MessageBox):
    """Dialog to capture hotkey presses"""
    def __init__(self, parent=None):
        super().__init__("Capture Hotkey", "Press any key combination...\n\n(Press ESC to cancel)", parent)
        self.hotkey = ""
        self.key_sequence = []
        
    def keyPressEvent(self, event):
        """Capture key press event"""
        # Handle ESC to cancel
        if event.key() == Qt.Key.Key_Escape:
            self.hotkey = ""
            self.reject()
            return
            
        # Build key sequence
        modifiers = []
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            modifiers.append("Ctrl")
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            modifiers.append("Alt")
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            modifiers.append("Shift")
        if event.modifiers() & Qt.KeyboardModifier.MetaModifier:
            modifiers.append("Win")
        
        # Get the key name
        key = event.key()
        key_name = ""
        
        # Function keys
        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12:
            key_name = f"F{key - Qt.Key.Key_F1 + 1}"
        # Letter keys
        elif Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            key_name = chr(key)
        # Number keys
        elif Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            key_name = chr(key)
        # Special keys
        elif key == Qt.Key.Key_Space:
            key_name = "Space"
        elif key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            key_name = "Enter"
        elif key == Qt.Key.Key_Tab:
            key_name = "Tab"
        elif key == Qt.Key.Key_Backspace:
            key_name = "Backspace"
        elif key == Qt.Key.Key_Delete:
            key_name = "Delete"
        elif key == Qt.Key.Key_Insert:
            key_name = "Insert"
        elif key == Qt.Key.Key_Home:
            key_name = "Home"
        elif key == Qt.Key.Key_End:
            key_name = "End"
        elif key == Qt.Key.Key_PageUp:
            key_name = "PageUp"
        elif key == Qt.Key.Key_PageDown:
            key_name = "PageDown"
        elif key == Qt.Key.Key_Up:
            key_name = "Up"
        elif key == Qt.Key.Key_Down:
            key_name = "Down"
        elif key == Qt.Key.Key_Left:
            key_name = "Left"
        elif key == Qt.Key.Key_Right:
            key_name = "Right"
        
        # Only accept if we have a valid key name and it's not just a modifier
        if key_name and key not in [Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift, Qt.Key.Key_Meta]:
            # Build the hotkey string
            if modifiers:
                self.hotkey = "+".join(modifiers) + "+" + key_name
            else:
                self.hotkey = key_name
            self.accept()
    
    def get_hotkey(self):
        """Return the captured hotkey string"""
        return self.hotkey

class MouseFXWidget(QWidget):
    """
    The main dashboard content containing the 4-column layout.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MouseFXWidget")
        
        self.profile_manager = ProfileManager()
        
        # Keep track of labels to update text dynamically
        self.ui_texts = {} 
        
        # Audio Player
        self.sound_effect = QSoundEffect()
        
        # Use a Grid Layout for the 4 columns
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(12)

        # --- Header ---
        self.header_layout = QHBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setPixmap(FIF.GAME.icon(color=Qt.GlobalColor.white).pixmap(20, 20)) 
        self.title_label = SubtitleLabel("MouseFX Generator")
        self.ui_texts["AppTitle"] = self.title_label
        
        self.header_layout.addWidget(self.icon_label)
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch(1)
        
        # Add Header to row 0, spanning all columns
        self.main_layout.addLayout(self.header_layout, 0, 0, 1, 4)

        # --- Column 1: Audio & Shortcuts ---
        self.col1_widget = QWidget()
        self.col1_layout = QVBoxLayout(self.col1_widget)
        self.col1_layout.setContentsMargins(0, 0, 0, 0)
        self.col1_layout.setSpacing(15)
        
        self.create_audio_card()
        self.create_shortcuts_card()
        
        self.col1_layout.addStretch(1)
        self.main_layout.addWidget(self.col1_widget, 1, 0)

        # --- Column 2: Visuals ---
        self.col2_widget = QWidget()
        self.col2_layout = QVBoxLayout(self.col2_widget)
        self.col2_layout.setContentsMargins(0, 0, 0, 0)
        self.col2_layout.setSpacing(15)

        self.create_highlight_card()
        self.create_clickfx_card()

        self.col2_layout.addStretch(1)
        self.main_layout.addWidget(self.col2_widget, 1, 1)

        # --- Column 3: Spotlight & System ---
        self.col3_widget = QWidget()
        self.col3_layout = QVBoxLayout(self.col3_widget)
        self.col3_layout.setContentsMargins(0, 0, 0, 0)
        self.col3_layout.setSpacing(15)

        self.create_spotlight_card()
        self.create_system_card()

        self.col3_layout.addStretch(1)
        self.main_layout.addWidget(self.col3_widget, 1, 2)

        # --- Column 4: Preview ---
        self.create_preview_section()
        self.main_layout.addWidget(self.preview_container, 1, 3)

        # --- Footer ---
        self.create_footer()
        self.main_layout.addWidget(self.footer_frame, 2, 0, 1, 4)

        # Connect signals for preview updates
        self.connect_signals()
        
        # Apply initial text and theme
        self.update_texts()
        self.update_theme_styles()
        
        # NOTE: Profile is loaded by the Main Window after initializing to handle QSettings

    def update_texts(self):
        """Updates all UI text based on current language"""
        for key, widget in self.ui_texts.items():
            if isinstance(widget, (QLabel, CheckBox, PushButton, SwitchButton, RadioButton)):
                widget.setText(Localizer.get(key))
            elif isinstance(widget, TransparentToolButton):
                widget.setToolTip(Localizer.get(key))
        
        # Refresh preview cache for text update
        self.preview_widget.refresh_cache()

    def update_theme_styles(self):
        """Updates stylesheets that depend on the theme (Footer, Preview)"""
        dark = isDarkTheme()
        
        # Footer Style
        footer_bg = QColor(40, 40, 40).name() if dark else QColor(248, 248, 248).name()
        footer_border = QColor(60, 60, 60).name() if dark else QColor(220, 220, 220).name()
        
        self.footer_frame.setStyleSheet(f"""
            QFrame#FooterFrame {{
                background-color: {footer_bg};
                border-top: 1px solid {footer_border};
            }}
        """)

        # Preview Frame Style
        prev_bg = QColor(32, 32, 32).name() if dark else QColor(240, 240, 240).name()
        prev_border = QColor(50, 50, 50).name() if dark else QColor(200, 200, 200).name()
        
        if hasattr(self, 'preview_frame'):
            self.preview_frame.setStyleSheet(f"""
                QFrame#PreviewFrame {{
                    background-color: {prev_bg};
                    border: 1px solid {prev_border};
                    border-radius: 10px;
                }}
            """)
        
        icon_color = Qt.GlobalColor.white if dark else Qt.GlobalColor.black
        self.icon_label.setPixmap(FIF.GAME.icon(color=icon_color).pixmap(20, 20))

    def bind_toggle_to_content(self, switch, content_widget):
        effect = QGraphicsOpacityEffect(content_widget)
        content_widget.setGraphicsEffect(effect)
        def handler(checked):
            content_widget.setEnabled(checked)
            effect.setOpacity(1.0 if checked else 0.5)
        switch.checkedChanged.connect(handler)
        handler(switch.isChecked())

    def create_card_header(self, icon, title_key, tooltip_key, switch=None):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_btn = TransparentToolButton(icon)
        icon_btn.setFixedSize(24, 24)
        
        title_lbl = StrongBodyLabel(Localizer.get(title_key))
        self.ui_texts[title_key] = title_lbl
        
        help_btn = TransparentToolButton(FIF.HELP)
        help_btn.setToolTip(Localizer.get(tooltip_key))
        help_btn.setFixedSize(24, 24)
        self.ui_texts[tooltip_key] = help_btn

        header_layout.addWidget(icon_btn)
        header_layout.addWidget(title_lbl)
        header_layout.addWidget(help_btn)
        header_layout.addStretch(1)
        
        if switch:
            header_layout.addWidget(switch)
        return header_widget

    def create_audio_card(self):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0,0,0,0)
        
        lbl = StrongBodyLabel(Localizer.get("Audio"))
        self.ui_texts["Audio"] = lbl
        layout.addWidget(lbl)
        
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        
        self.audio_switch = SwitchButton()
        self.audio_switch.setChecked(True)
        self.audio_switch.setOnText("On")
        self.audio_switch.setOffText("Off")
        
        header = self.create_card_header(FIF.MUSIC, "SoundFx", "SoundDesc", self.audio_switch)
        card_layout.addWidget(header)
        
        self.audio_content = QWidget()
        content_layout = QVBoxLayout(self.audio_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        vol_layout = QHBoxLayout()
        lbl_vol = CaptionLabel(Localizer.get("MasterVol"))
        self.ui_texts["MasterVol"] = lbl_vol
        vol_layout.addWidget(lbl_vol)
        self.vol_slider = Slider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_slider.setFixedWidth(100)
        vol_layout.addStretch(1)
        vol_layout.addWidget(self.vol_slider)
        content_layout.addLayout(vol_layout)

        sync_layout = QHBoxLayout()
        self.chk_sync_audio = CheckBox(Localizer.get("SyncAudio"))
        self.ui_texts["SyncAudio"] = self.chk_sync_audio
        self.chk_sync_audio.setChecked(True)
        sync_layout.addWidget(self.chk_sync_audio)
        sync_layout.addStretch(1)
        content_layout.addLayout(sync_layout)

        lbl_lc = CaptionLabel(Localizer.get("LeftClick"))
        self.ui_texts["LeftClick"] = lbl_lc
        content_layout.addWidget(lbl_lc)
        
        lc_layout = QHBoxLayout()
        self.cmb_left_sound = ComboBox()
        
        # Populate with full sound list from C# version
        sound_files = [
            ("Bloody V8.wav", "sounds/Bloody V8.wav"),
            ("Glorious Model O.wav", "sounds/Glorious Model O.wav"),
            ("IntelliMouse Optical.wav", "sounds/IntelliMouse Optical USB and PS2 Compatible.wav"),
            ("Logitech G203.wav", "sounds/Logitech G203.wav"),
            ("Logitech Superlight.wav", "sounds/Logitech Superlight.wav"),
            ("Rapture Venom.wav", "sounds/Rapture Venom.wav"),
            ("Razer DeathAdder V2 Pro.wav", "sounds/Razer DeathAdder V2 Pro.wav"),
            ("Trust GXT 152.wav", "sounds/Trust GXT 152.wav"),
            ("Windows Navigation Start.wav", r"C:\Windows\Media\Windows Navigation Start.wav"),
            ("Windows Feed Discovered.wav", r"C:\Windows\Media\Windows Feed Discovered.wav"),
            ("Windows Pop-up Blocked.wav", r"C:\Windows\Media\Windows Pop-up Blocked.wav")
        ]
        
        for name, path in sound_files:
            self.cmb_left_sound.addItem(name, userData=path)

        self.cmb_left_sound.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_test_left = TransparentToolButton(FIF.PLAY)
        self.btn_test_left.clicked.connect(lambda: self.play_sound(self.cmb_left_sound.currentData())) # Connect play
        lc_layout.addWidget(self.cmb_left_sound)
        lc_layout.addWidget(self.btn_test_left)
        content_layout.addLayout(lc_layout)

        self.lbl_right_click = CaptionLabel(Localizer.get("RightClick"))
        self.ui_texts["RightClick"] = self.lbl_right_click
        content_layout.addWidget(self.lbl_right_click)
        
        rc_layout = QHBoxLayout()
        self.cmb_right_sound = ComboBox()
        
        # Right Click sound list (C# used Recycle/Balloon by default for Windows sounds, keeping consistent)
        rc_sound_files = [
            ("Bloody V8.wav", "sounds/Bloody V8.wav"),
            ("Glorious Model O.wav", "sounds/Glorious Model O.wav"),
            ("IntelliMouse Optical.wav", "sounds/IntelliMouse Optical USB and PS2 Compatible.wav"),
            ("Logitech G203.wav", "sounds/Logitech G203.wav"),
            ("Logitech Superlight.wav", "sounds/Logitech Superlight.wav"),
            ("Rapture Venom.wav", "sounds/Rapture Venom.wav"),
            ("Razer DeathAdder V2 Pro.wav", "sounds/Razer DeathAdder V2 Pro.wav"),
            ("Trust GXT 152.wav", "sounds/Trust GXT 152.wav"),
            ("Windows Recycle.wav", r"C:\Windows\Media\Windows Recycle.wav"),
            ("Windows Balloon.wav", r"C:\Windows\Media\Windows Balloon.wav")
        ]
        
        for name, path in rc_sound_files:
            self.cmb_right_sound.addItem(name, userData=path)

        self.cmb_right_sound.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cmb_right_sound.setEnabled(False) 
        self.btn_test_right = TransparentToolButton(FIF.PLAY)
        self.btn_test_right.clicked.connect(lambda: self.play_sound(self.cmb_right_sound.currentData())) # Connect play
        rc_layout.addWidget(self.cmb_right_sound)
        rc_layout.addWidget(self.btn_test_right)
        content_layout.addLayout(rc_layout)
        
        card_layout.addWidget(self.audio_content)
        self.bind_toggle_to_content(self.audio_switch, self.audio_content)
        layout.addWidget(card)
        self.col1_layout.addWidget(wrapper)

    def play_sound(self, path):
        """Plays the sound file using QSoundEffect for volume control support."""
        if not path or not self.audio_switch.isChecked():
            return
        
        # Resolve relative paths (For UI preview, we can use the bundled path)
        if not os.path.isabs(path):
            path = resource_path(path)
            
        if os.path.exists(path):
            try:
                target = QUrl.fromLocalFile(path)
                # Optimization: Only reload source if it changed
                if self.sound_effect.source() != target:
                    self.sound_effect.setSource(target)
                
                # Set Volume (0.0 to 1.0) based on slider (0 to 100)
                self.sound_effect.setVolume(self.vol_slider.value() / 100.0)
                self.sound_effect.play()
            except Exception as e:
                print(f"Error playing sound: {e}")
        else:
            print(f"Sound file not found: {path}")

    def on_preview_clicked(self, is_left):
        """Called when interactive preview is clicked"""
        if self.chk_sync_audio.isChecked() or is_left:
            self.play_sound(self.cmb_left_sound.currentData())
        else:
            self.play_sound(self.cmb_right_sound.currentData())

    def capture_hotkey(self, button):
        """Capture a hotkey press and update the button text"""
        # Create a simple dialog to capture key press
        dialog = HotkeyDialog(self)
        if dialog.exec():
            hotkey = dialog.get_hotkey()
            if hotkey:
                button.setText(hotkey)

    def create_shortcuts_card(self):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0,0,0,0)
        
        lbl = StrongBodyLabel(Localizer.get("Shortcuts"))
        self.ui_texts["Shortcuts"] = lbl
        layout.addWidget(lbl)
        
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        
        header = self.create_card_header(FIF.FOLDER, "GlobalHotkeys", "HotkeysDesc")
        card_layout.addWidget(header)
        
        def add_hotkey_row(key_id, key_default, btn_var_name):
            row = QHBoxLayout()
            lbl = CaptionLabel(Localizer.get(key_id))
            self.ui_texts[key_id] = lbl
            row.addWidget(lbl)
            btn = PushButton(key_default)
            btn.setFixedWidth(100)
            btn.clicked.connect(lambda: self.capture_hotkey(btn))
            setattr(self, btn_var_name, btn) # Store btn ref
            row.addStretch(1)
            row.addWidget(btn)
            card_layout.addLayout(row)

        add_hotkey_row("ToggleSound", "F8", "btn_hk_sound")
        add_hotkey_row("ToggleHl", "F9", "btn_hk_hl")
        add_hotkey_row("ToggleFx", "F10", "btn_hk_fx")
        add_hotkey_row("SpotlightHk", "Ctrl+Space", "btn_hk_spot")
        
        layout.addWidget(card)
        self.col1_layout.addWidget(wrapper)

    def create_highlight_card(self):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0,0,0,0)
        
        lbl = StrongBodyLabel(Localizer.get("Cursor"))
        self.ui_texts["Cursor"] = lbl
        layout.addWidget(lbl)
        
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        
        self.highlight_switch = SwitchButton()
        self.highlight_switch.setChecked(True)
        
        header = self.create_card_header(FIF.EDIT, "Highlight", "HlDesc", self.highlight_switch)
        card_layout.addWidget(header)

        self.hl_content = QWidget()
        content_layout = QVBoxLayout(self.hl_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        color_layout = QHBoxLayout()
        lbl_col = CaptionLabel(Localizer.get("Color"))
        self.ui_texts["Color"] = lbl_col
        color_layout.addWidget(lbl_col)
        self.hl_color_picker = ColorPickerButton(QColor("#FFFF00"), Localizer.get("Color"))
        self.hl_color_picker.setFixedSize(60, 30)
        color_layout.addStretch(1)
        color_layout.addWidget(self.hl_color_picker)
        content_layout.addLayout(color_layout)

        def add_slider_row(key_id, min_v, max_v, curr_v, var_name):
            row = QHBoxLayout()
            lbl = CaptionLabel(Localizer.get(key_id))
            self.ui_texts[key_id] = lbl
            row.addWidget(lbl)
            slider = Slider(Qt.Orientation.Horizontal)
            slider.setRange(min_v, max_v)
            slider.setValue(curr_v)
            slider.setFixedWidth(120)
            setattr(self, var_name, slider)
            row.addStretch(1)
            row.addWidget(slider)
            content_layout.addLayout(row)
            return slider

        self.slider_hl_size = add_slider_row("Size", 20, 150, 60, "slider_hl_size")
        self.slider_hl_thick = add_slider_row("Thickness", 0, 10, 0, "slider_hl_thick")
        self.slider_hl_opacity = add_slider_row("Opacity", 0, 100, 50, "slider_hl_opacity")
        
        card_layout.addWidget(self.hl_content)
        self.bind_toggle_to_content(self.highlight_switch, self.hl_content)
        layout.addWidget(card)
        self.col2_layout.addWidget(wrapper)

    def create_clickfx_card(self):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0,0,0,0)
        
        lbl = StrongBodyLabel(Localizer.get("Feedback"))
        self.ui_texts["Feedback"] = lbl
        layout.addWidget(lbl)
        
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        
        self.clickfx_switch = SwitchButton()
        self.clickfx_switch.setChecked(True)
        
        header = self.create_card_header(FIF.GAME, "ClickFx", "ClickFxDesc", self.clickfx_switch)
        card_layout.addWidget(header)

        self.clickfx_content = QWidget()
        content_layout = QVBoxLayout(self.clickfx_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        self.chk_sync_visuals = CheckBox(Localizer.get("SyncFx"))
        self.ui_texts["SyncFx"] = self.chk_sync_visuals
        self.chk_sync_visuals.setChecked(True)
        content_layout.addWidget(self.chk_sync_visuals)

        lbl_lc = CaptionLabel(Localizer.get("LeftClickFx"))
        self.ui_texts["LeftClickFx"] = lbl_lc 
        content_layout.addWidget(lbl_lc)
        
        lc_row = QHBoxLayout()
        self.cmb_lc_shape = ComboBox()
        self.cmb_lc_shape.addItems(["Circle Ripple", "Solid Circle", "Square", "Diamond", "Static Circle"])
        self.cmb_lc_shape.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.lc_color = ColorPickerButton(QColor("#00FFFF"), Localizer.get("Color"))
        self.lc_color.setFixedSize(60, 30)
        
        lc_row.addWidget(self.cmb_lc_shape)
        lc_row.addWidget(self.lc_color)
        content_layout.addLayout(lc_row)

        lbl_rc = CaptionLabel(Localizer.get("RightClickFx"))
        self.ui_texts["RightClickFx"] = lbl_rc
        content_layout.addWidget(lbl_rc)
        
        rc_row = QHBoxLayout()
        self.cmb_rc_shape = ComboBox()
        self.cmb_rc_shape.addItems(["Circle Ripple", "Solid Circle", "Square", "Diamond", "Static Circle"])
        self.cmb_rc_shape.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cmb_rc_shape.setEnabled(False)
        
        self.rc_color = ColorPickerButton(QColor("#FF00FF"), Localizer.get("Color"))
        self.rc_color.setFixedSize(60, 30)
        self.rc_color.setEnabled(False)
        
        rc_row.addWidget(self.cmb_rc_shape)
        rc_row.addWidget(self.rc_color)
        content_layout.addLayout(rc_row)
        
        card_layout.addWidget(self.clickfx_content)
        self.bind_toggle_to_content(self.clickfx_switch, self.clickfx_content)
        layout.addWidget(card)
        self.col2_layout.addWidget(wrapper)

    def create_spotlight_card(self):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0,0,0,0)
        
        lbl = StrongBodyLabel(Localizer.get("Spotlight"))
        self.ui_texts["Spotlight"] = lbl
        layout.addWidget(lbl)
        
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        
        self.spotlight_switch = SwitchButton()
        
        header = self.create_card_header(FIF.SEARCH, "MouseSpot", "SpotDesc", self.spotlight_switch)
        card_layout.addWidget(header)

        self.spotlight_content = QWidget()
        content_layout = QVBoxLayout(self.spotlight_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        def add_spotlight_slider(key_id, min_v, max_v, curr_v, suffix="", var_name=""):
            row_stack = QVBoxLayout()
            lbl_row = QHBoxLayout()
            lbl = CaptionLabel(Localizer.get(key_id))
            self.ui_texts[key_id] = lbl
            lbl_row.addWidget(lbl)
            val_lbl = BodyLabel(f"{curr_v}{suffix}")
            lbl_row.addStretch(1)
            lbl_row.addWidget(val_lbl)
            
            slider = Slider(Qt.Orientation.Horizontal)
            slider.setRange(min_v, max_v)
            slider.setValue(curr_v)
            slider.valueChanged.connect(lambda v: val_lbl.setText(f"{v}{suffix}"))
            setattr(self, var_name, slider)
            
            row_stack.addLayout(lbl_row)
            row_stack.addWidget(slider)
            content_layout.addLayout(row_stack)
            return slider

        self.slider_spot_radius = add_spotlight_slider("SpotRadius", 50, 500, 200, "", "slider_spot_radius")
        self.slider_spot_speed = add_spotlight_slider("AnimSpeed", 1, 200, 20, "", "slider_spot_speed")
        self.slider_spot_opacity = add_spotlight_slider("BgOpacity", 0, 255, 180, "", "slider_spot_opacity")

        bg_row = QHBoxLayout()
        lbl_bg = CaptionLabel(Localizer.get("BgColor"))
        self.ui_texts["BgColor"] = lbl_bg
        bg_row.addWidget(lbl_bg)
        self.spot_color = ColorPickerButton(QColor("#000000"), Localizer.get("Color"))
        self.spot_color.setFixedSize(60, 30)
        bg_row.addStretch(1)
        bg_row.addWidget(self.spot_color)
        content_layout.addLayout(bg_row)

        lbl_style = CaptionLabel(Localizer.get("AnimStyle"))
        self.ui_texts["AnimStyle"] = lbl_style
        content_layout.addWidget(lbl_style)
        self.cmb_spot_anim = ComboBox()
        self.cmb_spot_anim.addItems(["None", "Zoom In/Out", "Fade"])
        content_layout.addWidget(self.cmb_spot_anim)
        
        card_layout.addWidget(self.spotlight_content)
        self.bind_toggle_to_content(self.spotlight_switch, self.spotlight_content)
        layout.addWidget(card)
        self.col3_layout.addWidget(wrapper)

    def create_system_card(self):
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(0,0,0,0)
        
        lbl = StrongBodyLabel(Localizer.get("System"))
        self.ui_texts["System"] = lbl
        layout.addWidget(lbl)
        
        card = CardWidget()
        card_layout = QVBoxLayout(card)
        
        header = QHBoxLayout()
        lbl_ref = StrongBodyLabel(Localizer.get("RefreshRate"))
        self.ui_texts["RefreshRate"] = lbl_ref
        header.addWidget(lbl_ref)
        header.addWidget(TransparentToolButton(FIF.HELP))
        
        self.cmb_refresh = ComboBox()
        self.cmb_refresh.addItems(["30 Hz", "60 Hz", "144 Hz"])
        self.cmb_refresh.setCurrentIndex(1)
        self.cmb_refresh.setFixedWidth(100)
        
        header.addStretch(1)
        header.addWidget(self.cmb_refresh)
        
        card_layout.addLayout(header)
        
        layout.addWidget(card)
        self.col3_layout.addWidget(wrapper)

    def create_preview_section(self):
        self.preview_container = QWidget()
        layout = QVBoxLayout(self.preview_container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        lbl = StrongBodyLabel(Localizer.get("Preview"))
        self.ui_texts["Preview"] = lbl
        layout.addWidget(lbl)
        
        self.preview_widget = InteractivePreviewWidget()
        self.preview_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Connect the preview click signal to the main window's handler
        self.preview_widget.click_signal.connect(self.on_preview_clicked)
        
        self.preview_frame = QFrame()
        self.preview_frame.setObjectName("PreviewFrame")
        # Stylesheet set in update_theme_styles()
        
        frame_layout = QVBoxLayout(self.preview_frame)
        frame_layout.addWidget(self.preview_widget)
        
        layout.addWidget(self.preview_frame)

    def create_footer(self):
        self.footer_frame = QFrame()
        self.footer_frame.setObjectName("FooterFrame")
        # Stylesheet set in update_theme_styles()
        
        layout = QHBoxLayout(self.footer_frame)
        layout.setContentsMargins(20, 10, 20, 10)

        profiles_layout = QHBoxLayout()
        lbl_prof = CaptionLabel(Localizer.get("Profiles"))
        self.ui_texts["Profiles"] = lbl_prof
        profiles_layout.addWidget(lbl_prof)
        self.rb_prof1 = RadioButton("1")
        self.rb_prof1.setChecked(True)
        self.rb_prof1.toggled.connect(lambda: self.on_profile_toggled(0))
        
        self.rb_prof2 = RadioButton("2")
        self.rb_prof2.toggled.connect(lambda: self.on_profile_toggled(1))
        
        self.rb_prof3 = RadioButton("3")
        self.rb_prof3.toggled.connect(lambda: self.on_profile_toggled(2))
        
        profiles_layout.addWidget(self.rb_prof1)
        profiles_layout.addWidget(self.rb_prof2)
        profiles_layout.addWidget(self.rb_prof3)

        self.lbl_status = CaptionLabel(Localizer.get("Ready"))
        self.ui_texts["Ready"] = self.lbl_status
        self.lbl_status.setStyleSheet("color: #888888;")
        
        self.btn_apply = PrimaryPushButton(Localizer.get("ApplyBtn"))
        self.ui_texts["ApplyBtn"] = self.btn_apply
        self.btn_apply.clicked.connect(self.on_apply)
        
        # How to Stop Engine Button
        self.btn_kill = PushButton(Localizer.get("KillEngine"))
        self.ui_texts["KillEngine"] = self.btn_kill
        self.btn_kill.setStyleSheet("QPushButton { color: white; background-color: #5bc0de; border: none; } QPushButton:hover { background-color: #46b8da; }")
        self.btn_kill.clicked.connect(self.on_show_stop_engine_help)

        layout.addLayout(profiles_layout)
        layout.addStretch(1)
        layout.addWidget(self.lbl_status)
        layout.addSpacing(10)
        layout.addWidget(self.btn_kill)
        layout.addSpacing(10)
        layout.addWidget(self.btn_apply)

    def on_show_stop_engine_help(self):
        """Show video tutorial for stopping the engine"""
        video_path = resource_path("Assets/HowToStopEngine.mp4")
        if os.path.exists(video_path):
            self.video_window = VideoPlayerWindow(video_path, "How to Stop Engine", self)
            self.video_window.show()
        else:
            InfoBar.warning(
                title="Video Not Found",
                content="Tutorial video not found in Assets folder.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self
            )

    def connect_signals(self):
        self.chk_sync_audio.stateChanged.connect(
            lambda s: self.cmb_right_sound.setEnabled(s != Qt.CheckState.Checked.value)
        )
        self.chk_sync_visuals.stateChanged.connect(
            lambda s: self.set_visuals_sync(s == Qt.CheckState.Checked.value)
        )
        self.hl_color_picker.colorChanged.connect(lambda c: self.preview_widget.update_settings(hl_color=c))
        self.slider_hl_size.valueChanged.connect(lambda v: self.preview_widget.update_settings(hl_size=v))
        self.slider_hl_thick.valueChanged.connect(lambda v: self.preview_widget.update_settings(hl_thick=v))
        self.slider_hl_opacity.valueChanged.connect(lambda v: self.preview_widget.update_settings(hl_opac=v))
        self.highlight_switch.checkedChanged.connect(lambda c: self.preview_widget.update_settings(hl_enabled=c))
        
        # Click FX Signals
        self.clickfx_switch.checkedChanged.connect(lambda c: self.preview_widget.update_settings(click_enabled=c))
        self.chk_sync_visuals.stateChanged.connect(lambda s: self.preview_widget.update_settings(sync_visuals=(s == Qt.CheckState.Checked.value)))
        self.lc_color.colorChanged.connect(lambda c: self.preview_widget.update_settings(lc_color=c))
        self.rc_color.colorChanged.connect(lambda c: self.preview_widget.update_settings(rc_color=c))
        self.cmb_lc_shape.currentTextChanged.connect(lambda s: self.preview_widget.update_settings(lc_shape=s))
        self.cmb_rc_shape.currentTextChanged.connect(lambda s: self.preview_widget.update_settings(rc_shape=s))

    def set_visuals_sync(self, synced):
        self.cmb_rc_shape.setEnabled(not synced)
        self.rc_color.setEnabled(not synced)

    # --- Profile & Logic Hooks ---

    def on_profile_toggled(self, index):
        # Radio buttons emit toggle twice (once for off, once for on), check if sender is checked
        sender = self.sender()
        if sender.isChecked():
            self.save_current_to_profile(self.profile_manager.current_index)
            self.profile_manager.current_index = index
            self.load_profile_ui(index)
            self.lbl_status.setText(f"Loaded Profile {index + 1}")

    def save_current_to_profile(self, index):
        data = self.get_configuration()
        self.profile_manager.save_profile(index, data)

    def load_profile_ui(self, index):
        p = self.profile_manager.get_profile(index)
        
        # Audio
        self.audio_switch.setChecked(p.get("AudioEnabled", True))
        self.vol_slider.setValue(p.get("MasterVolume", 80))
        self.chk_sync_audio.setChecked(p.get("SyncSounds", True))
        self.cmb_left_sound.setCurrentIndex(p.get("LeftSoundIndex", 1)) # simplistic mapping
        self.cmb_right_sound.setCurrentIndex(p.get("RightSoundIndex", 1))
        
        # Hotkeys
        self.btn_hk_sound.setText(p.get("HotkeySound", "F8"))
        self.btn_hk_hl.setText(p.get("HotkeyHighlight", "F9"))
        self.btn_hk_fx.setText(p.get("HotkeyClickFX", "F10"))
        self.btn_hk_spot.setText(p.get("HotkeySpotlight", "Ctrl+Space"))
        
        # System
        self.cmb_refresh.setCurrentIndex(p.get("RefreshRateIndex", 1))
        
        # Highlight
        hl_enabled = p.get("HighlightEnabled", True)
        hl_color = QColor(p.get("HighlightColorHex", "#FFFF00"))
        hl_size = int(p.get("HighlightSize", 60))
        hl_thick = int(p.get("HighlightThickness", 0))
        hl_opacity = int(p.get("HighlightOpacity", 50))

        self.highlight_switch.setChecked(hl_enabled)
        self.hl_color_picker.setColor(hl_color)
        self.slider_hl_size.setValue(hl_size)
        self.slider_hl_thick.setValue(hl_thick)
        self.slider_hl_opacity.setValue(hl_opacity)
        
        # Click FX
        click_enabled = p.get("ClickFxEnabled", True)
        sync_vis = p.get("SyncVisuals", True)
        lc_col = QColor(p.get("LeftClickColorHex", "#00FFFF"))
        rc_col = QColor(p.get("RightClickColorHex", "#FF00FF"))
        lc_shape = p.get("LeftClickShape", "Circle Ripple")
        rc_shape = p.get("RightClickShape", "Circle Ripple")

        self.clickfx_switch.setChecked(click_enabled)
        self.chk_sync_visuals.setChecked(sync_vis)
        self.lc_color.setColor(lc_col)
        self.rc_color.setColor(rc_col)
        self.cmb_lc_shape.setCurrentText(lc_shape)
        self.cmb_rc_shape.setCurrentText(rc_shape)
        
        # Spotlight
        self.spotlight_switch.setChecked(p.get("SpotlightEnabled", False))
        self.slider_spot_radius.setValue(p.get("SpotlightRadius", 200))
        self.slider_spot_speed.setValue(p.get("SpotlightAnimSpeed", 20))
        self.slider_spot_opacity.setValue(p.get("SpotlightOpacity", 180))
        self.spot_color.setColor(QColor(p.get("SpotlightColorHex", "#000000")))
        
        anim_style = p.get("SpotlightAnimStyle", "Zoom")
        if anim_style == "None": self.cmb_spot_anim.setCurrentIndex(0)
        elif anim_style == "Zoom": self.cmb_spot_anim.setCurrentIndex(1)
        elif anim_style == "Fade": self.cmb_spot_anim.setCurrentIndex(2)

        # Update preview manually to reflect changes immediately
        self.preview_widget.update_settings(
            hl_color=hl_color, hl_size=hl_size, hl_thick=hl_thick, hl_opac=hl_opacity, hl_enabled=hl_enabled,
            click_enabled=click_enabled, sync_visuals=sync_vis,
            lc_color=lc_col, rc_color=rc_col, lc_shape=lc_shape, rc_shape=rc_shape
        )

    def get_configuration(self):
        data = {}
        data["AudioEnabled"] = self.audio_switch.isChecked()
        data["MasterVolume"] = self.vol_slider.value()
        data["SyncSounds"] = self.chk_sync_audio.isChecked()
        
        # Getting Paths from Item Data or Text
        data["LeftSoundPath"] = self.cmb_left_sound.currentData() or ""
        data["RightSoundPath"] = self.cmb_right_sound.currentData() or ""
        data["LeftSoundIndex"] = self.cmb_left_sound.currentIndex()
        data["RightSoundIndex"] = self.cmb_right_sound.currentIndex()
        
        data["HotkeySound"] = self.btn_hk_sound.text()
        data["HotkeyHighlight"] = self.btn_hk_hl.text()
        data["HotkeyClickFX"] = self.btn_hk_fx.text()
        data["HotkeySpotlight"] = self.btn_hk_spot.text()
        
        data["RefreshRateIndex"] = self.cmb_refresh.currentIndex()
        
        data["HighlightEnabled"] = self.highlight_switch.isChecked()
        data["HighlightColorHex"] = self.hl_color_picker.color.name()
        data["HighlightSize"] = self.slider_hl_size.value()
        data["HighlightThickness"] = self.slider_hl_thick.value()
        data["HighlightOpacity"] = self.slider_hl_opacity.value()
        
        data["ClickFxEnabled"] = self.clickfx_switch.isChecked()
        data["SyncVisuals"] = self.chk_sync_visuals.isChecked()
        data["LeftClickColorHex"] = self.lc_color.color.name()
        data["RightClickColorHex"] = self.rc_color.color.name()
        data["LeftClickShape"] = self.cmb_lc_shape.currentText()
        data["RightClickShape"] = self.cmb_rc_shape.currentText()
        
        data["SpotlightEnabled"] = self.spotlight_switch.isChecked()
        data["SpotlightRadius"] = self.slider_spot_radius.value()
        data["SpotlightAnimSpeed"] = self.slider_spot_speed.value()
        data["SpotlightOpacity"] = self.slider_spot_opacity.value()
        data["SpotlightColorHex"] = self.spot_color.color.name()
        
        idx = self.cmb_spot_anim.currentIndex()
        if idx == 0: data["SpotlightAnimStyle"] = "None"
        elif idx == 2: data["SpotlightAnimStyle"] = "Fade"
        else: data["SpotlightAnimStyle"] = "Zoom"
        
        return data

    def ensure_persistent_assets(self):
        """Copies bundled sounds to persistent storage so AHK can access them after App closes."""
        # 1. Source Directory (Temp/Bundled)
        source_sounds_dir = resource_path("sounds")
        
        # 2. Destination Directory (AppData)
        dest_sounds_dir = os.path.join(os.environ["APPDATA"], "MouseFX Generator", "sounds")
        
        if not os.path.exists(dest_sounds_dir):
            os.makedirs(dest_sounds_dir)
            
        # 3. Copy files if present in bundle
        if os.path.exists(source_sounds_dir):
            for filename in os.listdir(source_sounds_dir):
                if filename.lower().endswith(".wav"):
                    src_file = os.path.join(source_sounds_dir, filename)
                    dst_file = os.path.join(dest_sounds_dir, filename)
                    
                    # Only copy if destination doesn't exist to save IO
                    if not os.path.exists(dst_file):  # <--- This check prevents re-copying
                        try:
                            shutil.copy2(src_file, dst_file)
                        except Exception as e:
                            print(f"Error copying {filename}: {e}")
        return dest_sounds_dir

    def on_apply(self):
        # Save current state first
        self.save_current_to_profile(self.profile_manager.current_index)
        
        self.lbl_status.setText(Localizer.get("GenConfig"))

        # --- KEY FIX: Ensure sounds exist persistently ---
        persistent_sound_dir = self.ensure_persistent_assets()
        
        config = self.get_configuration()
        
        try:
            # Resolve relative paths to absolute PERSISTENT paths for AHK logic
            # (Instead of resource_path which points to Temp)
            
            def resolve_ahk_sound_path(path):
                if not path: return ""
                # If absolute (Windows sounds), keep it
                if os.path.isabs(path): return path
                # If relative (bundled), point to AppData
                filename = os.path.basename(path)
                return os.path.join(persistent_sound_dir, filename)

            config["LeftSoundPath"] = resolve_ahk_sound_path(config["LeftSoundPath"])
            config["RightSoundPath"] = resolve_ahk_sound_path(config["RightSoundPath"])

            # Generate Script Content
            ahk_content = ScriptGenerator.generate_ahk_script(config)
            
            # Save Script File
            script_path = self.profile_manager.script_path
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(ahk_content)
                
            # Execute
            # Assuming .ahk is associated with AutoHotkey v2
            if sys.platform == 'win32':
                os.startfile(script_path)
            else:
                # Fallback for testing on non-windows (though AHK is windows only)
                pass 

            InfoBar.success(
                title=Localizer.get("SuccessTitle"),
                content=Localizer.get("SuccessMsg"),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self
            )
            QTimer.singleShot(2000, lambda: self.lbl_status.setText(Localizer.get("EngineRun")))
            
        except Exception as e:
            InfoBar.error(
                title="Error",
                content=str(e),
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=5000,
                parent=self
            )
            self.lbl_status.setText("Error")

class AnimationInterface(QWidget):
    """
    Dedicated Interface for Experimental C# Animation features.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AnimationInterface")
        self.ui_texts = {}
        self.anim_engine = AnimationEngine() # Init Engine
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 20, 0, 0) # Adjusted margins for footer
        self.main_layout.setSpacing(0)

        # Content Widget for scrolling/margins
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 0, 20, 20)
        self.content_layout.setSpacing(20)

        self.create_header()
        
        # --- Physics Section ---
        self.create_physics_card()
        
        # --- Appearance Section ---
        self.create_appearance_card()
        
        # --- System Section ---
        self.create_system_card()
        
        self.content_layout.addStretch(1)

        # Scroll Area for Content
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent;")

        self.main_layout.addWidget(self.scroll_area)

        # --- Footer ---
        self.create_footer()
        self.main_layout.addWidget(self.footer_frame)

        # Apply initial texts and style
        self.update_texts()
        # Initial style application (will be updated by window signal later)
        if parent:
            self.update_theme_styles()

    def update_theme_styles(self):
        """Updates stylesheets that depend on the theme (Footer)"""
        dark = isDarkTheme()
        footer_bg = QColor(40, 40, 40).name() if dark else QColor(248, 248, 248).name()
        footer_border = QColor(60, 60, 60).name() if dark else QColor(220, 220, 220).name()
        
        if hasattr(self, 'footer_frame'):
            self.footer_frame.setStyleSheet(f"""
                QFrame#FooterFrame {{
                    background-color: {footer_bg};
                    border-top: 1px solid {footer_border};
                }}
            """)

    def create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(20)

        # Icon
        icon_path = resource_path(os.path.join("Assets", "AnimationIcon.png"))
        self.icon_lbl = QLabel()
        if os.path.exists(icon_path):
             self.icon_lbl.setPixmap(QPixmap(icon_path).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
             # Fallback if image missing
             self.icon_lbl.setPixmap(FIF.VIDEO.icon(color=Qt.GlobalColor.white).pixmap(64, 64))

        # Text Layout Container
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)

        # Warning Label (Bold Red)
        self.lbl_warning = StrongBodyLabel(Localizer.get("AnimWarning"))
        self.ui_texts["AnimWarning"] = self.lbl_warning
        self.lbl_warning.setStyleSheet("color: #d9534f; font-weight: bold; font-size: 14px;")
        
        # Description
        self.lbl_desc = BodyLabel(Localizer.get("AnimHeaderDesc"))
        self.ui_texts["AnimHeaderDesc"] = self.lbl_desc
        self.lbl_desc.setWordWrap(True)

        text_layout.addWidget(self.lbl_warning)
        text_layout.addWidget(self.lbl_desc)

        header_layout.addWidget(self.icon_lbl, 0, Qt.AlignmentFlag.AlignTop)
        header_layout.addWidget(text_widget, 1) # Stretch text

        self.content_layout.addWidget(header_widget)

    def create_physics_card(self):
        lbl = StrongBodyLabel(Localizer.get("AnimPhysics"))
        self.ui_texts["AnimPhysics"] = lbl
        self.content_layout.addWidget(lbl)

        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        # Helper to create float sliders
        def add_float_slider(key, min_f, max_f, default_f, tooltip_key, scale_factor=100, var_name=""):
            row = QHBoxLayout()
            lbl_w = CaptionLabel(Localizer.get(key))
            self.ui_texts[key] = lbl_w
            
            # Tooltip Helper
            btn_help = TransparentToolButton(FIF.HELP)
            btn_help.setFixedSize(24, 24)
            btn_help.setToolTip(Localizer.get(tooltip_key))
            self.ui_texts[tooltip_key] = btn_help # To update tooltip text
            
            val_lbl = BodyLabel(f"{default_f}")
            
            slider = Slider(Qt.Orientation.Horizontal)
            slider.setRange(int(min_f * scale_factor), int(max_f * scale_factor))
            slider.setValue(int(default_f * scale_factor))
            slider.setFixedWidth(150)
            
            # Update label on change
            slider.valueChanged.connect(lambda v: val_lbl.setText(f"{v / scale_factor:.2f}"))
            
            # Store slider ref
            if var_name:
                setattr(self, var_name, slider)

            row.addWidget(lbl_w)
            row.addWidget(btn_help)
            row.addStretch(1)
            row.addWidget(val_lbl)
            row.addSpacing(10)
            row.addWidget(slider)
            
            layout.addLayout(row)
            return slider

        self.slider_click_scale = add_float_slider("ClickScale", 0.1, 2.0, 0.8, "ClickScaleTooltip", 100, "slider_click_scale")
        self.slider_anim_speed = add_float_slider("AnimStiffness", 0.01, 1.0, 0.3, "AnimStiffnessTooltip", 100, "slider_anim_speed")
        self.slider_spring_factor = add_float_slider("SpringFactor", 0.0, 1.0, 0.5, "SpringTooltip", 100, "slider_spring_factor")

        # Enable Bounce
        row_bounce = QHBoxLayout()
        lbl_bounce = CaptionLabel(Localizer.get("EnableBounce"))
        self.ui_texts["EnableBounce"] = lbl_bounce
        
        btn_help_bounce = TransparentToolButton(FIF.HELP)
        btn_help_bounce.setFixedSize(24, 24)
        btn_help_bounce.setToolTip(Localizer.get("BounceTooltip"))
        self.ui_texts["BounceTooltip"] = btn_help_bounce
        
        self.switch_bounce = SwitchButton()
        self.switch_bounce.setOnText("On")
        self.switch_bounce.setOffText("Off")
        
        row_bounce.addWidget(lbl_bounce)
        row_bounce.addWidget(btn_help_bounce)
        row_bounce.addStretch(1)
        row_bounce.addWidget(self.switch_bounce)
        
        layout.addLayout(row_bounce)
        self.content_layout.addWidget(card)

    def create_appearance_card(self):
        lbl = StrongBodyLabel(Localizer.get("AppearanceSize"))
        self.ui_texts["AppearanceSize"] = lbl
        self.content_layout.addWidget(lbl)

        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        # Helper reuse
        def add_float_slider(key, min_f, max_f, default_f, tooltip_key, scale_factor=100, var_name=""):
            row = QHBoxLayout()
            lbl_w = CaptionLabel(Localizer.get(key))
            self.ui_texts[key] = lbl_w
            
            btn_help = TransparentToolButton(FIF.HELP)
            btn_help.setFixedSize(24, 24)
            btn_help.setToolTip(Localizer.get(tooltip_key))
            self.ui_texts[tooltip_key] = btn_help
            
            val_lbl = BodyLabel(f"{default_f}")
            
            slider = Slider(Qt.Orientation.Horizontal)
            slider.setRange(int(min_f * scale_factor), int(max_f * scale_factor))
            slider.setValue(int(default_f * scale_factor))
            slider.setFixedWidth(150)
            
            slider.valueChanged.connect(lambda v: val_lbl.setText(f"{v / scale_factor:.2f}"))
            
            if var_name:
                setattr(self, var_name, slider)

            row.addWidget(lbl_w)
            row.addWidget(btn_help)
            row.addStretch(1)
            row.addWidget(val_lbl)
            row.addSpacing(10)
            row.addWidget(slider)
            
            layout.addLayout(row)
            return slider

        self.slider_global_size = add_float_slider("GlobalSize", 0.5, 4.0, 1.0, "GlobalSizeTooltip", 10, "slider_global_size")
        self.slider_opacity = add_float_slider("CursorOpacity", 0.1, 1.0, 1.0, "OpacityTooltip", 100, "slider_opacity")

        # Fallback Color
        row_color = QHBoxLayout()
        lbl_color = CaptionLabel(Localizer.get("FallbackColor"))
        self.ui_texts["FallbackColor"] = lbl_color
        
        self.picker_color = ColorPickerButton(QColor("#FF0000"), Localizer.get("FallbackColor"))
        self.picker_color.setFixedSize(60, 30)
        
        row_color.addWidget(lbl_color)
        row_color.addStretch(1)
        row_color.addWidget(self.picker_color)
        
        layout.addLayout(row_color)
        self.content_layout.addWidget(card)

    def create_system_card(self):
        lbl = StrongBodyLabel(Localizer.get("SystemBehavior"))
        self.ui_texts["SystemBehavior"] = lbl
        self.content_layout.addWidget(lbl)

        card = CardWidget()
        layout = QVBoxLayout(card)
        layout.setSpacing(10)

        # Emergency Exit
        row_key = QHBoxLayout()
        lbl_key = CaptionLabel(Localizer.get("EmergencyKey"))
        self.ui_texts["EmergencyKey"] = lbl_key
        
        self.btn_exit_key = PushButton("F12")
        self.btn_exit_key.setFixedWidth(100)
        self.btn_exit_key.clicked.connect(lambda: self.capture_animator_hotkey(self.btn_exit_key))
        
        row_key.addWidget(lbl_key)
        row_key.addStretch(1)
        row_key.addWidget(self.btn_exit_key)
        
        layout.addLayout(row_key)

        # Tray Icon
        row_tray = QHBoxLayout()
        lbl_tray = CaptionLabel(Localizer.get("ShowTray"))
        self.ui_texts["ShowTray"] = lbl_tray
        
        btn_help_tray = TransparentToolButton(FIF.HELP)
        btn_help_tray.setFixedSize(24, 24)
        btn_help_tray.setToolTip(Localizer.get("TrayTooltip"))
        self.ui_texts["TrayTooltip"] = btn_help_tray
        
        self.switch_tray = SwitchButton()
        self.switch_tray.setChecked(True)
        self.switch_tray.setOnText("On")
        self.switch_tray.setOffText("Off")
        
        row_tray.addWidget(lbl_tray)
        row_tray.addWidget(btn_help_tray)
        row_tray.addStretch(1)
        row_tray.addWidget(self.switch_tray)
        
        layout.addLayout(row_tray)
        self.content_layout.addWidget(card)

    def create_footer(self):
        self.footer_frame = QFrame()
        self.footer_frame.setObjectName("FooterFrame")
        
        layout = QHBoxLayout(self.footer_frame)
        layout.setContentsMargins(20, 10, 20, 10)

        # Reset Button
        self.btn_reset = TransparentToolButton(FIF.SYNC) # Using SYNC icon as a placeholder for "Reset"
        self.btn_reset.setToolTip(Localizer.get("Reset"))
        self.ui_texts["Reset"] = self.btn_reset
        self.btn_reset.clicked.connect(self.reset_defaults)
        
        # How to Stop Button
        self.btn_kill = PushButton(Localizer.get("KillAnimator"))
        self.ui_texts["KillAnimator"] = self.btn_kill
        self.btn_kill.setStyleSheet("QPushButton { color: white; background-color: #5bc0de; border: none; } QPushButton:hover { background-color: #46b8da; }")
        self.btn_kill.clicked.connect(self.on_show_stop_animator_help)

        # Deploy Button
        self.btn_deploy = PrimaryPushButton(Localizer.get("DeployRun"))
        self.ui_texts["DeployRun"] = self.btn_deploy
        self.btn_deploy.clicked.connect(self.on_deploy_clicked)

        layout.addWidget(self.btn_reset)
        layout.addStretch(1)
        layout.addWidget(self.btn_kill)
        layout.addSpacing(10)
        layout.addWidget(self.btn_deploy)

    def on_show_stop_animator_help(self):
        """Show video tutorial for stopping the animator"""
        video_path = resource_path("Assets/HowToStopAnimator.mp4")
        if os.path.exists(video_path):
            self.video_window = VideoPlayerWindow(video_path, "How to Stop Animator", self)
            self.video_window.show()
        else:
            InfoBar.warning(
                title="Video Not Found",
                content="Tutorial video not found in Assets folder.",
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=3000,
                parent=self
            )

    def reset_defaults(self):
        # Reset to initial defaults
        self.slider_click_scale.setValue(80) # 0.8 * 100
        self.slider_anim_speed.setValue(30) # 0.3 * 100
        self.slider_spring_factor.setValue(50) # 0.5 * 100
        self.switch_bounce.setChecked(False)
        self.slider_global_size.setValue(10) # 1.0 * 10
        self.slider_opacity.setValue(100) # 1.0 * 100
        self.picker_color.setColor(QColor("#FF0000"))
        self.btn_exit_key.setText("F12")
        self.switch_tray.setChecked(True)
        
        InfoBar.info(
            title="Reset",
            content="Animation settings reset to defaults.",
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.BOTTOM_RIGHT,
            duration=2000,
            parent=self
        )

    def on_deploy_clicked(self):
        # 1. Gather Settings
        config = {
            "ClickScale": self.slider_click_scale.value() / 100.0,
            "AnimSpeed": self.slider_anim_speed.value() / 100.0,
            "SpringFactor": self.slider_spring_factor.value() / 100.0,
            "EnableBounce": self.switch_bounce.isChecked(),
            "GlobalSize": self.slider_global_size.value() / 10.0, # scale_factor was 10 for this one
            "CursorOpacity": self.slider_opacity.value() / 100.0,
            "FallbackColor": self.picker_color.color.name(),
            "EmergencyKey": self.btn_exit_key.text(),
            "ShowTray": self.switch_tray.isChecked()
        }
        
        # 2. Call Engine
        self.btn_deploy.setEnabled(False)
        self.btn_deploy.setText("Deploying...")
        
        success, msg = self.anim_engine.deploy_and_run(config)
        
        self.btn_deploy.setEnabled(True)
        self.btn_deploy.setText(Localizer.get("DeployRun"))
        
        if success:
            InfoBar.success(
                title=Localizer.get("SuccessTitle"),
                content=msg,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=5000,
                parent=self
            )
        else:
            InfoBar.error(
                title="Error",
                content=msg,
                orient=Qt.Orientation.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=8000,
                parent=self
            )

    def capture_animator_hotkey(self, button):
        """Capture a hotkey press and update the button text"""
        dialog = HotkeyDialog(self)
        if dialog.exec():
            hotkey = dialog.get_hotkey()
            if hotkey:
                button.setText(hotkey)

    def update_texts(self):
        """Updates text elements dynamically."""
        for key, widget in self.ui_texts.items():
            if isinstance(widget, (QLabel, CheckBox, PushButton, SwitchButton, RadioButton, ColorPickerButton)):
                widget.setText(Localizer.get(key))
            elif isinstance(widget, TransparentToolButton):
                widget.setToolTip(Localizer.get(key))


class SettingsInterface(QWidget):
    """
    Dedicated Settings Interface for the application.
    """
    # Signals to notify main window of changes
    themeChanged = pyqtSignal()
    langChanged = pyqtSignal()
    previewToggled = pyqtSignal(bool)
    animToggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsInterface")
        
        self.ui_texts = {}
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        self.lbl_title = SubtitleLabel(Localizer.get("Settings"))
        layout.addWidget(self.lbl_title)
        
        self.lbl_personal = StrongBodyLabel(Localizer.get("Personalization"))
        self.ui_texts["Personalization"] = self.lbl_personal
        layout.addWidget(self.lbl_personal)
        
        # Theme Card
        card = CardWidget()
        card.setFixedHeight(70) 
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(20, 0, 20, 0)
        
        self.lbl_theme = BodyLabel(Localizer.get("AppTheme"))
        self.ui_texts["AppTheme"] = self.lbl_theme
        card_layout.addWidget(self.lbl_theme)
        card_layout.addStretch(1)
        
        self.theme_combo = ComboBox()
        self.theme_combo.addItems([Localizer.get("Light"), Localizer.get("Dark")])
        self.theme_combo.setCurrentText(Localizer.get("Dark") if isDarkTheme() else Localizer.get("Light"))
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        self.theme_combo.setFixedWidth(150)
        
        card_layout.addWidget(self.theme_combo)
        layout.addWidget(card)

        # Accent Color Card
        card_accent = CardWidget()
        card_accent.setFixedHeight(70)
        accent_layout = QHBoxLayout(card_accent)
        accent_layout.setContentsMargins(20, 0, 20, 0)

        self.lbl_accent = BodyLabel(Localizer.get("AccentColor"))
        self.ui_texts["AccentColor"] = self.lbl_accent
        accent_layout.addWidget(self.lbl_accent)
        accent_layout.addStretch(1)

        # Sync Button
        self.btn_sync_accent = TransparentToolButton(FIF.SYNC)
        self.btn_sync_accent.setToolTip(Localizer.get("SyncSystem"))
        self.ui_texts["SyncSystem"] = self.btn_sync_accent
        self.btn_sync_accent.clicked.connect(self.sync_accent_color)

        accent_layout.addWidget(self.btn_sync_accent)
        accent_layout.addSpacing(10)

        # Color Picker for Accent
        self.accent_color_picker = ColorPickerButton(QColor("#009faa"), Localizer.get("AccentColor"))
        self.accent_color_picker.setFixedSize(60, 30)
        self.accent_color_picker.colorChanged.connect(self.on_accent_color_changed)
        
        accent_layout.addWidget(self.accent_color_picker)
        
        layout.addWidget(card_accent)

        # Language Card
        card_lang = CardWidget()
        card_lang.setFixedHeight(70) 
        lang_layout = QHBoxLayout(card_lang)
        lang_layout.setContentsMargins(20, 0, 20, 0)
        
        self.lbl_lang = BodyLabel(Localizer.get("Language"))
        self.ui_texts["Language"] = self.lbl_lang
        lang_layout.addWidget(self.lbl_lang)
        lang_layout.addStretch(1)
        
        self.lang_combo = ComboBox()
        self.lang_combo.addItems(["English", "العربية"])
        self.lang_combo.setCurrentIndex(0)
        self.lang_combo.currentTextChanged.connect(self.on_lang_changed)
        self.lang_combo.setFixedWidth(150)
        
        lang_layout.addWidget(self.lang_combo)
        layout.addWidget(card_lang)

        # Performance Section
        self.lbl_perf = StrongBodyLabel(Localizer.get("AppPerformance"))
        self.ui_texts["AppPerformance"] = self.lbl_perf
        layout.addWidget(self.lbl_perf)

        # Disable Preview Card
        card_prev = CardWidget()
        card_prev.setFixedHeight(70)
        layout_prev = QHBoxLayout(card_prev)
        layout_prev.setContentsMargins(20, 0, 20, 0)
        
        self.lbl_disable_prev = BodyLabel(Localizer.get("DisablePreview"))
        self.ui_texts["DisablePreview"] = self.lbl_disable_prev
        
        self.switch_disable_prev = SwitchButton()
        self.switch_disable_prev.checkedChanged.connect(self.previewToggled.emit)
        
        layout_prev.addWidget(self.lbl_disable_prev)
        layout_prev.addStretch(1)
        layout_prev.addWidget(self.switch_disable_prev)
        
        layout.addWidget(card_prev)

        # Disable Animations Card
        card_anim = CardWidget()
        card_anim.setFixedHeight(70)
        layout_anim = QHBoxLayout(card_anim)
        layout_anim.setContentsMargins(20, 0, 20, 0)
        
        self.lbl_disable_anim = BodyLabel(Localizer.get("DisableAnim"))
        self.ui_texts["DisableAnim"] = self.lbl_disable_anim
        
        self.switch_disable_anim = SwitchButton()
        self.switch_disable_anim.checkedChanged.connect(self.animToggled.emit)
        
        layout_anim.addWidget(self.lbl_disable_anim)
        layout_anim.addStretch(1)
        layout_anim.addWidget(self.switch_disable_anim)
        
        layout.addWidget(card_anim)

        layout.addStretch(1)
        
        # Try to sync accent color on startup if on Windows
        if sys.platform == 'win32':
             QTimer.singleShot(100, self.sync_accent_color)

    def update_texts(self):
        self.lbl_title.setText(Localizer.get("Settings"))
        for key, widget in self.ui_texts.items():
            if isinstance(widget, TransparentToolButton):
                widget.setToolTip(Localizer.get(key))
            else:
                widget.setText(Localizer.get(key))
            
        # Update combo items safely by saving index
        idx = self.theme_combo.currentIndex()
        self.theme_combo.clear()
        self.theme_combo.addItems([Localizer.get("Light"), Localizer.get("Dark")])
        self.theme_combo.setCurrentIndex(idx)

    def on_theme_changed(self, text):
        # We check index because text changes with language
        is_light = self.theme_combo.currentIndex() == 0
        setTheme(Theme.LIGHT if is_light else Theme.DARK)
        self.themeChanged.emit()

    def on_accent_color_changed(self, color):
        setThemeColor(color)
        
    def sync_accent_color(self):
        color = self.get_windows_accent_color()
        self.accent_color_picker.setColor(color)
        setThemeColor(color)

    def get_windows_accent_color(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM")
            value, _ = winreg.QueryValueEx(key, "AccentColor")
            # Format: 0x00BBGGRR
            r = value & 0xFF
            g = (value >> 8) & 0xFF
            b = (value >> 16) & 0xFF
            return QColor(r, g, b)
        except Exception:
            return QColor("#009faa") # Default fallback

    def on_lang_changed(self, text):
        if text == "العربية":
            Localizer.current_lang = "ar"
        else:
            Localizer.current_lang = "en"
        
        self.update_texts()
        self.langChanged.emit()

class FAQCard(CardWidget):
    """
    A collapsible card for FAQ items.
    """
    def __init__(self, question_key, answer_key, parent=None):
        super().__init__(parent)
        self.question_key = question_key
        self.answer_key = answer_key
        self.is_expanded = False
        
        # Enable mouse tracking to capture clicks for expansion
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)

        # --- Header (Always Visible) ---
        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_question = StrongBodyLabel(Localizer.get(question_key))
        self.lbl_question.setWordWrap(True)
        
        # Use Caret icons as they are more likely to be consistent if Chevron naming varies
        self.btn_expand = TransparentToolButton(FIF.CARE_DOWN_SOLID)
        self.btn_expand.setFixedSize(30, 30)
        self.btn_expand.clicked.connect(self.toggle_expand)
        
        self.header_layout.addWidget(self.lbl_question, 1) # Stretch factor 1
        self.header_layout.addWidget(self.btn_expand)
        
        self.main_layout.addWidget(self.header_widget)
        
        # --- Content (Collapsible) ---
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 15, 0, 0) # Top margin for separation
        
        self.lbl_answer = BodyLabel(Localizer.get(answer_key))
        self.lbl_answer.setWordWrap(True)
        self.lbl_answer.setStyleSheet("color: #888888;") # Slightly dimmer for answer
        
        self.content_layout.addWidget(self.lbl_answer)
        self.main_layout.addWidget(self.content_widget)
        
        # Initial State
        self.content_widget.setVisible(False)
        
    def mousePressEvent(self, event):
        # Toggle if top part is clicked
        if event.pos().y() < self.header_widget.height() + 20:
             self.toggle_expand()
        super().mousePressEvent(event)

    def toggle_expand(self):
        self.is_expanded = not self.is_expanded
        self.content_widget.setVisible(self.is_expanded)
        
        # Update Icon
        icon = FIF.CARE_UP_SOLID if self.is_expanded else FIF.CARE_DOWN_SOLID
        self.btn_expand.setIcon(icon)

    def update_texts(self):
        self.lbl_question.setText(Localizer.get(self.question_key))
        self.lbl_answer.setText(Localizer.get(self.answer_key))

class InfoInterface(QWidget):
    """
    Dedicated Info & Help Interface.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InfoInterface")
        self.ui_texts = {}
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)
        
        # Title
        self.lbl_title = SubtitleLabel(Localizer.get("Info"))
        self.ui_texts["Info"] = self.lbl_title
        layout.addWidget(self.lbl_title)
        
        # Version
        self.lbl_version = BodyLabel(Localizer.get("Version"))
        self.ui_texts["Version"] = self.lbl_version
        layout.addWidget(self.lbl_version)
        
        # Update Button
        self.btn_update = PrimaryPushButton(Localizer.get("CheckUpdates"))
        self.ui_texts["CheckUpdates"] = self.btn_update
        self.btn_update.setFixedWidth(200)
        self.btn_update.clicked.connect(self.check_updates)
        layout.addWidget(self.btn_update)
        
        layout.addSpacing(20)
        
        # FAQ Title
        self.lbl_faq = StrongBodyLabel(Localizer.get("FAQ"))
        self.ui_texts["FAQ"] = self.lbl_faq
        layout.addWidget(self.lbl_faq)
        
        # FAQ Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        faq_widget = QWidget()
        faq_layout = QVBoxLayout(faq_widget)
        faq_layout.setSpacing(10)
        faq_layout.setContentsMargins(0, 0, 20, 0)
        faq_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # FAQ Items
        self.faq_cards = []
        
        def add_qa(q_key, a_key):
            card = FAQCard(q_key, a_key)
            self.faq_cards.append(card)
            faq_layout.addWidget(card)
            
        add_qa("Q1", "A1")
        add_qa("Q2", "A2")
        add_qa("Q3", "A3")
        
        scroll.setWidget(faq_widget)
        layout.addWidget(scroll)

    def check_updates(self):
        url = QUrl("https://github.com/os4ma31/MouseFX-Generator/releases/latest")
        QDesktopServices.openUrl(url)

    def update_texts(self):
        for key, widget in self.ui_texts.items():
            widget.setText(Localizer.get(key))
        
        # Update FAQ cards
        for card in self.faq_cards:
            card.update_texts()

class MouseFXWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MouseFX Generator")
        
        # Set App Icon
        # Resolves path relative to the script file location
        icon_path = resource_path(os.path.join("Assets", "AppIcon.png"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.resize(1240, 760)
        
        # Force Dark Theme by default
        setTheme(Theme.DARK)
        
        # Create the dashboard widget
        self.dashboard = MouseFXWidget(self)
        self.settings_interface = SettingsInterface(self)
        self.animation_interface = AnimationInterface(self)
        self.info_interface = InfoInterface(self)
        
        # Connect signals
        self.settings_interface.themeChanged.connect(self.dashboard.update_theme_styles)
        self.settings_interface.themeChanged.connect(self.animation_interface.update_theme_styles) # Connect animation interface
        self.settings_interface.langChanged.connect(self.on_language_changed)
        self.settings_interface.previewToggled.connect(self.on_preview_toggled)
        self.settings_interface.animToggled.connect(self.on_anim_toggled)
        
        # Add interfaces
        self.addSubInterface(self.dashboard, FIF.GAME, "Home")
        # Add Animation Tab next to Home (NavigationItemPosition.TOP is default, so order matters)
        self.addSubInterface(self.animation_interface, FIF.VIDEO, "Animator", position=NavigationItemPosition.TOP)
        self.addSubInterface(self.settings_interface, FIF.SETTING, "Settings", position=NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.info_interface, FIF.INFO, "Info", position=NavigationItemPosition.BOTTOM)
        
        # Initial text update
        self.on_language_changed()
        
        # Restore saved window geometry and last profile if available
        self.restore_app_state()
        
        # Check AHK on startup (delayed)
        QTimer.singleShot(500, self.check_ahk_first_run)

    def get_settings_obj(self):
        # Create/Open settings.ini in AppData
        app_data = os.path.join(os.environ["APPDATA"], "MouseFX Generator")
        if not os.path.exists(app_data):
            os.makedirs(app_data)
        settings_path = os.path.join(app_data, "settings.ini")
        return QSettings(settings_path, QSettings.Format.IniFormat)

    def restore_app_state(self):
        settings = self.get_settings_obj()
        
        # Restore geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        # Restore last used profile index
        last_profile_idx = settings.value("lastProfile", 0, type=int)
        
        # Set the UI state for the profile buttons manually to match logic
        if last_profile_idx == 1:
            self.dashboard.rb_prof2.setChecked(True)
        elif last_profile_idx == 2:
            self.dashboard.rb_prof3.setChecked(True)
        else:
            self.dashboard.rb_prof1.setChecked(True)
            
        # Explicitly load the profile data into the UI
        self.dashboard.profile_manager.current_index = last_profile_idx
        self.dashboard.load_profile_ui(last_profile_idx)

    def closeEvent(self, event):
        # Save current profile data to disk
        if hasattr(self, 'dashboard'):
            self.dashboard.save_current_to_profile(self.dashboard.profile_manager.current_index)
        
        # Save window geometry and current profile index
        settings = self.get_settings_obj()
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("lastProfile", self.dashboard.profile_manager.current_index)
        
        super().closeEvent(event)

    def check_ahk_first_run(self):
        settings = self.get_settings_obj()
        if not settings.value("AhkChecked", False, type=bool):
            # Show Dialog
            msg_box = MessageBox(
                Localizer.get("AHKTitle"),
                Localizer.get("AHKMsg"),
                self
            )
            msg_box.yesButton.setText(Localizer.get("IHaveIt"))
            msg_box.cancelButton.setText(Localizer.get("Download"))
            
            if msg_box.exec():
                settings.setValue("AhkChecked", True)
            else:
                # Open URL
                QDesktopServices.openUrl(QUrl("https://www.autohotkey.com/"))

    def on_language_changed(self):
        # Update Dashboard Text
        self.dashboard.update_texts()
        self.info_interface.update_texts()
        self.animation_interface.update_texts()
        
        # Update Window Navigation Text (Home/Settings)
        # Note: MSFluentWindow items are tricky to update dynamically without digging into internals,
        # but we can try simply re-adding or accessing widgets. 
        # For simplicity in this demo, we assume sidebar items stay English or generic icons.
        
        # Handle RTL Layout
        if Localizer.current_lang == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    def on_preview_toggled(self, disabled):
        self.dashboard.preview_frame.setVisible(not disabled)

    def on_anim_toggled(self, disabled):
        self.dashboard.preview_widget.set_animations_enabled(not disabled)

class InteractivePreviewWidget(QWidget):
    click_signal = pyqtSignal(bool) # Signal for click event, bool represents is_left_click

    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.hl_color = QColor("#FFFF00")
        self.hl_size = 60
        self.hl_thick = 0
        self.hl_opac = 50
        self.hl_enabled = True
        self.mouse_pos = QPoint(150, 150) # Default center-ish
        
        # Click FX State
        self.click_enabled = True
        self.sync_visuals = True
        self.lc_color = QColor("#00FFFF")
        self.rc_color = QColor("#FF00FF")
        self.lc_shape = "Circle Ripple"
        self.rc_shape = "Circle Ripple"
        
        self.click_anims = [] # list of dicts
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate_step)
        
        self.animations_active = True
        
        # Cache for static background
        self.static_pixmap = None

    def set_animations_enabled(self, enabled):
        self.animations_active = enabled
        if not enabled:
            self.anim_timer.stop()
            self.click_anims.clear()
            self.update()

    def refresh_cache(self):
        """Regenerates the static background (text)"""
        self.static_pixmap = QPixmap(self.size())
        # Fill with transparent so parent background shows through
        self.static_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(self.static_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw Text
        painter.setPen(QColor(150, 150, 150))
        text = Localizer.get("InteractivePrevAr" if Localizer.current_lang == "ar" else "InteractivePrev")
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, text)
        painter.end()
        self.update()

    def resizeEvent(self, event):
        self.refresh_cache()
        super().resizeEvent(event)

    def update_settings(self, hl_color=None, hl_size=None, hl_thick=None, hl_opac=None, hl_enabled=None, 
                        click_enabled=None, lc_color=None, lc_shape=None, rc_color=None, rc_shape=None, sync_visuals=None):
        if hl_color: self.hl_color = hl_color
        if hl_size is not None: self.hl_size = hl_size
        if hl_thick is not None: self.hl_thick = hl_thick
        if hl_opac is not None: self.hl_opac = hl_opac
        if hl_enabled is not None: self.hl_enabled = hl_enabled
        
        if click_enabled is not None: self.click_enabled = click_enabled
        if lc_color: self.lc_color = lc_color
        if lc_shape: self.lc_shape = lc_shape
        if rc_color: self.rc_color = rc_color
        if rc_shape: self.rc_shape = rc_shape
        if sync_visuals is not None: self.sync_visuals = sync_visuals
        
        self.update()

    def mousePressEvent(self, event):
        is_left = event.button() == Qt.MouseButton.LeftButton
        is_right = event.button() == Qt.MouseButton.RightButton
        
        if is_left or is_right:
            # Emit signal to play sound
            self.click_signal.emit(is_left)

        if not self.click_enabled:
            return
        
        if not (is_left or is_right):
            return

        if not self.animations_active:
            return

        # Determine settings
        if self.sync_visuals or is_left:
            color = self.lc_color
            shape = self.lc_shape
        else:
            color = self.rc_color
            shape = self.rc_shape
            
        self.click_anims.append({
            'pos': event.pos(),
            'color': QColor(color),
            'shape': shape,
            'progress': 0.0, # 0.0 to 1.0
            'max_size': 60
        })
        
        if not self.anim_timer.isActive():
            self.anim_timer.start(16) # 16ms = ~60fps

    def animate_step(self):
        if not self.click_anims:
            self.anim_timer.stop()
            return
            
        active_anims = []
        for anim in self.click_anims:
            anim['progress'] += 0.05 # Speed
            if anim['progress'] < 1.0:
                active_anims.append(anim)
        self.click_anims = active_anims
        self.update()

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw Cached Static Background
        if self.static_pixmap:
            painter.drawPixmap(0, 0, self.static_pixmap)
        else:
            self.refresh_cache()
            painter.drawPixmap(0, 0, self.static_pixmap)

        if self.animations_active:
            # Draw Clicks (Behind cursor if needed, or on top? Usually ripples are independent)
            for anim in self.click_anims:
                prog = anim['progress']
                opacity = 1.0 - prog
                size = int(anim['max_size'] * prog) + 10 # Start with some size
                color = QColor(anim['color'])
                color.setAlphaF(opacity)
                
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(Qt.PenStyle.NoPen)
                
                shape = anim['shape']
                center = anim['pos']
                
                if shape == "Circle Ripple":
                    pen = QPen(color)
                    pen.setWidth(2)
                    painter.setPen(pen)
                    radius = size // 2
                    painter.drawEllipse(center, radius, radius)
                elif shape == "Solid Circle":
                    painter.setBrush(QBrush(color))
                    radius = size // 2
                    painter.drawEllipse(center, radius, radius)
                elif shape == "Square":
                    painter.setBrush(QBrush(color))
                    rect = QRect(0, 0, size, size)
                    rect.moveCenter(center)
                    painter.drawRect(rect)
                elif shape == "Diamond":
                    painter.setBrush(QBrush(color))
                    painter.save()
                    painter.translate(center)
                    painter.rotate(45)
                    painter.drawRect(-size//2, -size//2, size, size)
                    painter.restore()
                elif shape == "Static Circle":
                    pen = QPen(color)
                    pen.setWidth(2)
                    painter.setPen(pen)
                    # Use Highlight Size (radius) instead of animation size
                    radius = self.hl_size // 2 
                    painter.drawEllipse(center, radius, radius)

        if self.hl_enabled:
            # Draw Highlight
            c = QColor(self.hl_color)
            if self.hl_thick > 0:
                # Ring style
                c.setAlpha(int(self.hl_opac * 2.55)) 
                pen = QPen(c)
                pen.setWidth(self.hl_thick)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
            else:
                # Solid style
                c.setAlpha(int(self.hl_opac * 2.55))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(c)

            size = self.hl_size
            painter.drawEllipse(self.mouse_pos, size//2, size//2)

        # Draw Mouse Cursor (Simple arrow)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(Qt.GlobalColor.white)
        
        path = [
            QPoint(0, 0), QPoint(0, 18), QPoint(5, 14),
            QPoint(9, 23), QPoint(11, 22), QPoint(7, 13), QPoint(13, 13)
        ]
        # Shift cursor to mouse position
        translated_path = [p + self.mouse_pos for p in path]
        painter.drawPolygon(*translated_path)

if __name__ == '__main__':
    # Enable High DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    window = MouseFXWindow()
    window.show()
    sys.exit(app.exec())
