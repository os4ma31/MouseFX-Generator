import os
import sys
import subprocess
import ctypes
from typing import Dict, Any

class AnimationEngine:
    """
    Handles the generation, compilation, and deployment of the C# Cursor Animator.
    """

    # --- C# Template ---
    CS_TEMPLATE = r"""
using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;
using WinForms = System.Windows.Forms;
using Drawing = System.Drawing;

namespace CursorOverlayApp
{
    public class Program : Application
    {
        [STAThread]
        public static void Main()
        {
            var app = new Program();
            app.Run(new OverlayWindow());
        }
    }

    public class OverlayWindow : Window
    {
        // UI Elements
        private Image _cursorImage;
        private Ellipse _fallbackCursor; 
        private ScaleTransform _scaleTransform;
        private WinForms.NotifyIcon _notifyIcon;
        
        // State
        private IntPtr _currentCursorHandle = IntPtr.Zero;
        private bool _magApiInitialized = false;
        private IntPtr _windowHandle = IntPtr.Zero;
        private double _dpiScaleX = 1.0;
        private double _dpiScaleY = 1.0;

        // Animation State (Physics)
        private double _currentScale = {{GLOBAL_SIZE}};
        private double _velocity = 0; // Current velocity of the scale
        
        // Logic Constants
        private const double BASE_SCALE = {{GLOBAL_SIZE}};
        private const double CLICK_SCALE = {{CLICK_SCALE}}; // Multiplied by Global in logic
        
        // Physics Constants
        // Stiffness (k): How hard the spring pulls back (Animation Speed)
        private const double STIFFNESS = {{STIFFNESS}}; 
        // Damping (c): Friction (Spring Factor). Higher = less bounce.
        private const double DAMPING = {{DAMPING}}; 
        
        private const bool ENABLE_BOUNCE = {{ENABLE_BOUNCE}};
        private const int EXIT_KEY = {{EXIT_KEY}}; 

        public OverlayWindow()
        {
            // Window Configuration
            this.WindowStyle = WindowStyle.None;
            this.AllowsTransparency = true;
            this.Background = Brushes.Transparent;
            this.Topmost = true;
            this.ShowInTaskbar = false;
            this.Opacity = {{OPACITY}}; 
            
            // Full Screen Coverage
            this.Left = SystemParameters.VirtualScreenLeft;
            this.Top = SystemParameters.VirtualScreenTop;
            this.Width = SystemParameters.VirtualScreenWidth;
            this.Height = SystemParameters.VirtualScreenHeight;
            
            // Setup Visuals
            _scaleTransform = new ScaleTransform(_currentScale, _currentScale);
            _cursorImage = new Image
            {
                Stretch = Stretch.None,
                RenderTransform = _scaleTransform,
                RenderTransformOrigin = new Point(0.5, 0.5),
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Top,
                Visibility = Visibility.Visible
            };

            // Fallback Cursor
            _fallbackCursor = new Ellipse
            {
                Width = 10, Height = 10,
                Fill = (SolidColorBrush)(new BrushConverter().ConvertFrom("{{FALLBACK_COLOR}}")),
                Visibility = Visibility.Collapsed,
                HorizontalAlignment = HorizontalAlignment.Left,
                VerticalAlignment = VerticalAlignment.Top
            };

            var canvas = new Canvas();
            canvas.Children.Add(_cursorImage);
            canvas.Children.Add(_fallbackCursor);
            this.Content = canvas;

            this.Loaded += OnLoaded;
            this.Closing += OnClosing;
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            _windowHandle = new WindowInteropHelper(this).Handle;
            int extendedStyle = GetWindowLong(_windowHandle, GWL_EXSTYLE);
            SetWindowLong(_windowHandle, GWL_EXSTYLE, extendedStyle | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_LAYERED);

            var source = PresentationSource.FromVisual(this);
            if (source != null)
            {
                _dpiScaleX = source.CompositionTarget.TransformToDevice.M11;
                _dpiScaleY = source.CompositionTarget.TransformToDevice.M22;
            }

            SetupTrayIcon();
            ToggleSystemCursor(false);

            CompositionTarget.Rendering += OnRendering;
        }

        private void SetupTrayIcon()
        {
            if (!{{SHOW_TRAY}}) return;

            _notifyIcon = new WinForms.NotifyIcon();
            _notifyIcon.Text = "Cursor Animator (Running)";
            _notifyIcon.Visible = true;

            try
            {
                // Try to extract icon from the EXE itself
                var exePath = System.Reflection.Assembly.GetExecutingAssembly().Location;
                var icon = Drawing.Icon.ExtractAssociatedIcon(exePath);
                _notifyIcon.Icon = icon;
            }
            catch { /* Ignore extraction errors */ }

            // FALLBACK: If extraction failed or returned null, use default app icon
            if (_notifyIcon.Icon == null)
            {
                _notifyIcon.Icon = Drawing.SystemIcons.Application;
            }

            var contextMenu = new WinForms.ContextMenuStrip();
            contextMenu.Items.Add("Exit Cursor Animator", null, (s, e) => {
                Application.Current.Shutdown();
            });
            _notifyIcon.ContextMenuStrip = contextMenu;
        }

        private void OnClosing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            if (_notifyIcon != null)
            {
                _notifyIcon.Visible = false;
                _notifyIcon.Dispose();
            }
            ToggleSystemCursor(true);
        }

        private void OnRendering(object sender, EventArgs e)
        {
            // Safety Exit Key Check
            if ((GetAsyncKeyState(EXIT_KEY) & 0x8000) != 0)
            {
                Application.Current.Shutdown();
                return;
            }

            UpdateCursorVisual();
            
            // Z-Order Enforcement (Keep TopMost)
            SetWindowPos(_windowHandle, new IntPtr(-1), 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0010);
        }

        private void UpdateCursorVisual()
        {
            CURSORINFO pci = new CURSORINFO();
            pci.cbSize = Marshal.SizeOf(typeof(CURSORINFO));

            if (GetCursorInfo(ref pci))
            {
                // 1. Position Update
                double finalX = (pci.ptScreenPos.x - SystemParameters.VirtualScreenLeft) / _dpiScaleX;
                double finalY = (pci.ptScreenPos.y - SystemParameters.VirtualScreenTop) / _dpiScaleY;

                Canvas.SetLeft(_cursorImage, finalX);
                Canvas.SetTop(_cursorImage, finalY);
                Canvas.SetLeft(_fallbackCursor, finalX);
                Canvas.SetTop(_fallbackCursor, finalY);

                // 2. Icon Update
                if (pci.hCursor != _currentCursorHandle && pci.hCursor != IntPtr.Zero)
                {
                    _currentCursorHandle = pci.hCursor;
                    try
                    {
                        var bitmapSource = Imaging.CreateBitmapSourceFromHIcon(
                            pci.hCursor,
                            Int32Rect.Empty,
                            BitmapSizeOptions.FromEmptyOptions());
                        
                        _cursorImage.Source = bitmapSource;
                        _cursorImage.Visibility = Visibility.Visible;
                        _fallbackCursor.Visibility = Visibility.Collapsed;
                    }
                    catch 
                    {
                        _cursorImage.Visibility = Visibility.Collapsed;
                        _fallbackCursor.Visibility = Visibility.Visible;
                    }
                }

                // 3. Physics / Animation Logic
                short keyState = GetAsyncKeyState(VK_LBUTTON);
                bool isDown = (keyState & 0x8000) != 0;

                // Determine Target
                // If clicking, shrink (or grow) to target. If released, return to base.
                double target = isDown ? (BASE_SCALE * CLICK_SCALE) : BASE_SCALE;

                if (ENABLE_BOUNCE)
                {
                    // Spring Physics (Hooke's Law + Damping)
                    // F = -kx - cv
                    double displacement = target - _currentScale;
                    double force = displacement * STIFFNESS;
                    double dampingForce = -_velocity * DAMPING;
                    double acceleration = force + dampingForce;

                    _velocity += acceleration;
                    _currentScale += _velocity;
                }
                else
                {
                    // Simple Linear Interpolation (No Bounce)
                    // Scale STIFFNESS down for simple lerp to behave similarly
                    double lerpSpeed = STIFFNESS * 0.5; 
                    if (lerpSpeed > 1.0) lerpSpeed = 1.0;
                    _currentScale += (target - _currentScale) * lerpSpeed;
                }

                // Sanity check to prevent explosion
                if (_currentScale < 0.1) _currentScale = 0.1;
                if (_currentScale > 10.0) _currentScale = 10.0;

                _scaleTransform.ScaleX = _currentScale;
                _scaleTransform.ScaleY = _currentScale;
            }
        }

        #region Magnification API & P/Invoke
        
        private void ToggleSystemCursor(bool show)
        {
            try 
            {
                if (!_magApiInitialized)
                {
                    MagInitialize();
                    _magApiInitialized = true;
                }
                MagShowSystemCursor(show);
            }
            catch { /* Mag API might fail on some systems */ }
        }

        [StructLayout(LayoutKind.Sequential)]
        struct POINT { public int x; public int y; }

        [StructLayout(LayoutKind.Sequential)]
        struct CURSORINFO
        {
            public int cbSize;
            public int flags;
            public IntPtr hCursor;
            public POINT ptScreenPos;
        }

        [DllImport("user32.dll")]
        static extern bool GetCursorInfo(ref CURSORINFO pci);

        [DllImport("user32.dll")]
        static extern short GetAsyncKeyState(int vKey);

        [DllImport("user32.dll", SetLastError = true)]
        static extern int GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll")]
        static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

        [DllImport("user32.dll", SetLastError = true)]
        static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int X, int Y, int cx, int cy, uint uFlags);

        [DllImport("Magnification.dll")]
        static extern bool MagInitialize();

        [DllImport("Magnification.dll")]
        static extern bool MagUninitialize();

        [DllImport("Magnification.dll")]
        static extern bool MagShowSystemCursor(bool fShowCursor);

        const int GWL_EXSTYLE = -20;
        const int WS_EX_TRANSPARENT = 0x00000020;
        const int WS_EX_TOOLWINDOW = 0x00000080;
        const int WS_EX_LAYERED = 0x00080000;
        const int VK_LBUTTON = 0x01;

        #endregion
    }
}
"""

    MANIFEST_TEMPLATE = r"""<?xml version="1.0" encoding="utf-8"?>
<assembly manifestVersion="1.0" xmlns="urn:schemas-microsoft-com:asm.v1">
  <assemblyIdentity version="1.0.0.0" name="CursorAnimator.app"/>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges xmlns="urn:schemas-microsoft-com:asm.v3">
        <requestedExecutionLevel level="asInvoker" uiAccess="true" />
      </requestedPrivileges>
    </security>
  </trustInfo>
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>
"""

    PS_SCRIPT = r"""
# --- PowerShell Deploy Script ---
$ErrorActionPreference = "Stop"

# Force working directory to script location
if ($PSScriptRoot) { Set-Location -Path $PSScriptRoot }

function Pause-Exit {
    Write-Host "`nProcess interrupted. Press Enter to exit..." -ForegroundColor Yellow
    Read-Host
    exit 1
}

try {
    $sourceFile = "CursorAnimator.cs"
    $manifestFile = "app.manifest"
    $exeName = "CursorAnimator.exe"
    $installPath = "C:\Program Files\CursorAnimator"
    $certName = "MouseFXLocalCert"

    # 0. Kill existing process if running
    Write-Host "Checking for running instances..." -ForegroundColor Cyan
    Stop-Process -Name "CursorAnimator" -ErrorAction SilentlyContinue -Force

    # 1. Check Files
    if (-not (Test-Path $sourceFile)) { Write-Error "Missing source file: $sourceFile"; Pause-Exit }

    # 2. Certificate
    Write-Host "Checking Certificate..." -ForegroundColor Cyan
    $cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq "CN=$certName" } | Select-Object -First 1

    if (-not $cert) {
        Write-Host "Generating new Self-Signed Certificate..." -ForegroundColor Yellow
        $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=$certName" -CertStoreLocation Cert:\CurrentUser\My
    }

    # Export and Trust Root (Required for uiAccess=true)
    $pfxPath = "$PWD\tempCert.pfx"
    $password = ConvertTo-SecureString -String "MouseFXPass" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $password
    Import-PfxCertificate -FilePath $pfxPath -CertStoreLocation Cert:\LocalMachine\Root -Password $password

    # 3. Compile
    Write-Host "Compiling..." -ForegroundColor Cyan
    $frameworkPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319"
    $csc = "$frameworkPath\csc.exe"
    $wpf = "$frameworkPath\WPF"

    if (-not (Test-Path $csc)) { Write-Error "C# Compiler not found"; Pause-Exit }

    $args = @(
        "/target:winexe",
        "/out:$exeName",
        "CursorAnimator.cs",
        "/win32manifest:app.manifest",
        "/reference:$wpf\PresentationCore.dll",
        "/reference:$wpf\PresentationFramework.dll",
        "/reference:$wpf\WindowsBase.dll",
        "/reference:$frameworkPath\System.Xaml.dll",
        "/reference:$frameworkPath\System.Windows.Forms.dll",
        "/reference:$frameworkPath\System.Drawing.dll"
    )

    & $csc $args

    if (-not (Test-Path $exeName)) { Write-Error "Compilation Failed - Exe not found"; Pause-Exit }

    # 4. Sign
    Write-Host "Signing..." -ForegroundColor Cyan
    Set-AuthenticodeSignature -FilePath $exeName -Certificate $cert

    # 5. Install
    Write-Host "Installing to $installPath..." -ForegroundColor Cyan
    if (!(Test-Path $installPath)) { New-Item -ItemType Directory -Force -Path $installPath }
    Copy-Item -Path $exeName -Destination $installPath -Force

    # 6. Run
    Write-Host "Launching..." -ForegroundColor Green
    Start-Process "$installPath\$exeName"
}
catch {
    Write-Host "`nCRITICAL ERROR OCCURRED:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Pause-Exit
}
"""

    @staticmethod
    def get_build_dir():
        docs = os.path.expanduser("~/Documents")
        path = os.path.join(docs, "MouseFX_Build")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    @staticmethod
    def map_key_to_vk(key_name: str) -> int:
        """Mapping for function keys and others."""
        k = key_name.upper()
        if k.startswith("F"):
            try:
                f_num = int(k[1:])
                # F1 is 0x70
                return 0x70 + (f_num - 1)
            except: pass
        if k == "ESC": return 0x1B
        if k == "END": return 0x23
        if k == "HOME": return 0x24
        if k == "DELETE": return 0x2E
        return 0x7B # Default F12

    def deploy_and_run(self, config: Dict[str, Any]):
        build_dir = self.get_build_dir()
        
        # Physics Mapping
        # Input Speed (0.01 - 1.0) -> Stiffness
        stiffness = config.get("AnimSpeed", 0.3)
        if stiffness < 0.01: stiffness = 0.01
        
        # Input Spring Factor (0.0 - 1.0) -> Damping
        # High spring factor should mean MORE BOUNCE (LOWER Damping).
        # Slider: 0 (No Bounce/Stiff) to 1 (Very Bouncy).
        # Damping Range: 0.8 (Stiff) to 0.1 (Bouncy).
        factor = config.get("SpringFactor", 0.5)
        damping = 0.8 - (factor * 0.7) 
        if damping < 0.05: damping = 0.05

        csharp_code = self.CS_TEMPLATE
        csharp_code = csharp_code.replace("{{GLOBAL_SIZE}}", str(config.get("GlobalSize", 1.0)))
        csharp_code = csharp_code.replace("{{CLICK_SCALE}}", str(config.get("ClickScale", 0.8)))
        csharp_code = csharp_code.replace("{{STIFFNESS}}", f"{stiffness:.4f}")
        csharp_code = csharp_code.replace("{{DAMPING}}", f"{damping:.4f}")
        csharp_code = csharp_code.replace("{{ENABLE_BOUNCE}}", "true" if config.get("EnableBounce", False) else "false")
        csharp_code = csharp_code.replace("{{OPACITY}}", str(config.get("CursorOpacity", 1.0)))
        csharp_code = csharp_code.replace("{{FALLBACK_COLOR}}", config.get("FallbackColor", "#FF0000"))
        csharp_code = csharp_code.replace("{{SHOW_TRAY}}", "true" if config.get("ShowTray", True) else "false")
        
        vk_code = self.map_key_to_vk(config.get("EmergencyKey", "F12"))
        csharp_code = csharp_code.replace("{{EXIT_KEY}}", str(vk_code))

        # Write Files
        cs_path = os.path.join(build_dir, "CursorAnimator.cs")
        with open(cs_path, "w", encoding="utf-8") as f:
            f.write(csharp_code)

        manifest_path = os.path.join(build_dir, "app.manifest")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(self.MANIFEST_TEMPLATE)

        ps_path = os.path.join(build_dir, "SignAndDeploy.ps1")
        with open(ps_path, "w", encoding="utf-8") as f:
            f.write(self.PS_SCRIPT)

        try:
            cmd = f'powershell.exe -ExecutionPolicy Bypass -File "{ps_path}"'
            ctypes.windll.shell32.ShellExecuteW(None, "runas", "powershell.exe", f'-ExecutionPolicy Bypass -File "{ps_path}"', build_dir, 1)
            return True, "Deployment started. Check the blue window."
        except Exception as e:
            return False, str(e)