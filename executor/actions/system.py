import subprocess
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def set_volume(level: int) -> str:
    level = max(0, min(100, int(level)))
    script = f"(New-Object -ComObject WScript.Shell).SendKeys([char]173); $vol = {level}; Set-AudioOutputVolume -Volume ($vol / 100)"
    # WScript approach is unreliable cross-device, use nircmd pattern instead
    _set_volume_nircmd(level)
    return f"Volume set to {level}."


def _set_volume_nircmd(level: int):
    # Windows: use PowerShell to set master volume via COM
    # Range for SetMasterVolumeLevelScalar is 0.0 to 1.0
    scalar = level / 100.0
    script = (
        f"$vol = {scalar};"
        "$obj = New-Object -ComObject WScript.Shell;"
        "Add-Type -TypeDefinition '"
        "using System.Runtime.InteropServices;"
        "[Guid(\"5CDF2C82-841E-4546-9722-0CF74078229A\"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]"
        "public interface IAudioEndpointVolume { void _(); void __(); void ___(); int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext); }"
        "';"
    )
    # Simpler and more reliable: use PowerShell audio module
    ps_script = f"""
    $wshShell = New-Object -ComObject WScript.Shell
    $vol = [math]::Round({level} * 655.35)
    $code = @'
    using System.Runtime.InteropServices;
    [Guid("5CDF2C82-841E-4546-9722-0CF74078229A"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IAudioEndpointVolume {{
        int f(); int g(); int h(); int i();
        int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext);
        int j(); int k(); int l(); int m(); int n();
        int GetMute(out bool pbMute);
    }}
    [Guid("D666063F-1587-4E43-81F1-B948E807363F"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDevice {{
        int Activate(ref System.Guid id, int clsCtx, int activationParams, out IAudioEndpointVolume aev);
    }}
    [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDeviceEnumerator {{
        int f();
        int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
    }}
    [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
    class MMDeviceEnumeratorComObject {{ }}
    public class Audio {{
        static IAudioEndpointVolume Vol() {{
            var enumerator = new MMDeviceEnumeratorComObject() as IMMDeviceEnumerator;
            IMMDevice dev = null;
            Marshal.ThrowExceptionForHR(enumerator.GetDefaultAudioEndpoint(0, 1, out dev));
            IAudioEndpointVolume epv = null;
            var epvid = typeof(IAudioEndpointVolume).GUID;
            Marshal.ThrowExceptionForHR(dev.Activate(ref epvid, 23, 0, out epv));
            return epv;
        }}
        public static void SetVolume(float level) {{ Marshal.ThrowExceptionForHR(Vol().SetMasterVolumeLevelScalar(level, System.Guid.Empty)); }}
    }}
'@
    Add-Type -TypeDefinition $code
    [Audio]::SetVolume({scalar})
    """
    subprocess.run(
        ["powershell", "-NonInteractive", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        timeout=5,
    )


def increase_volume(amount: int = 10) -> str:
    amount = max(1, min(50, int(amount)))
    ps_script = f"""
    Add-Type -TypeDefinition @'
    using System.Runtime.InteropServices;
    [Guid("5CDF2C82-841E-4546-9722-0CF74078229A"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IAudioEndpointVolume {{
        int f(); int g(); int h(); int i();
        int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext);
        int j(); int k(); int l(); int m(); int n();
        int GetMasterVolumeLevelScalar(out float pfLevel);
    }}
    [Guid("D666063F-1587-4E43-81F1-B948E807363F"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDevice {{
        int Activate(ref System.Guid id, int clsCtx, int activationParams, out IAudioEndpointVolume aev);
    }}
    [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDeviceEnumerator {{
        int f();
        int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
    }}
    [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
    class MMDeviceEnumeratorComObject {{ }}
    public class Audio {{
        static IAudioEndpointVolume Vol() {{
            var enumerator = new MMDeviceEnumeratorComObject() as IMMDeviceEnumerator;
            IMMDevice dev = null;
            Marshal.ThrowExceptionForHR(enumerator.GetDefaultAudioEndpoint(0, 1, out dev));
            IAudioEndpointVolume epv = null;
            var epvid = typeof(IAudioEndpointVolume).GUID;
            Marshal.ThrowExceptionForHR(dev.Activate(ref epvid, 23, 0, out epv));
            return epv;
        }}
        public static float GetVolume() {{ float v; Vol().GetMasterVolumeLevelScalar(out v); return v; }}
        public static void SetVolume(float level) {{ Marshal.ThrowExceptionForHR(Vol().SetMasterVolumeLevelScalar(level, System.Guid.Empty)); }}
    }}
'@
    $current = [Audio]::GetVolume()
    $new = [math]::Min(1.0, $current + {amount / 100.0})
    [Audio]::SetVolume($new)
    """
    subprocess.run(
        ["powershell", "-NonInteractive", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        timeout=5,
    )
    return f"Volume increased by {amount}."


def decrease_volume(amount: int = 10) -> str:
    amount = max(1, min(50, int(amount)))
    ps_script = f"""
    Add-Type -TypeDefinition @'
    using System.Runtime.InteropServices;
    [Guid("5CDF2C82-841E-4546-9722-0CF74078229A"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IAudioEndpointVolume {{
        int f(); int g(); int h(); int i();
        int SetMasterVolumeLevelScalar(float fLevel, System.Guid pguidEventContext);
        int j(); int k(); int l(); int m(); int n();
        int GetMasterVolumeLevelScalar(out float pfLevel);
    }}
    [Guid("D666063F-1587-4E43-81F1-B948E807363F"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDevice {{
        int Activate(ref System.Guid id, int clsCtx, int activationParams, out IAudioEndpointVolume aev);
    }}
    [Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"),
     InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    interface IMMDeviceEnumerator {{
        int f();
        int GetDefaultAudioEndpoint(int dataFlow, int role, out IMMDevice endpoint);
    }}
    [ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
    class MMDeviceEnumeratorComObject {{ }}
    public class Audio {{
        static IAudioEndpointVolume Vol() {{
            var enumerator = new MMDeviceEnumeratorComObject() as IMMDeviceEnumerator;
            IMMDevice dev = null;
            Marshal.ThrowExceptionForHR(enumerator.GetDefaultAudioEndpoint(0, 1, out dev));
            IAudioEndpointVolume epv = null;
            var epvid = typeof(IAudioEndpointVolume).GUID;
            Marshal.ThrowExceptionForHR(dev.Activate(ref epvid, 23, 0, out epv));
            return epv;
        }}
        public static float GetVolume() {{ float v; Vol().GetMasterVolumeLevelScalar(out v); return v; }}
        public static void SetVolume(float level) {{ Marshal.ThrowExceptionForHR(Vol().SetMasterVolumeLevelScalar(level, System.Guid.Empty)); }}
    }}
'@
    $current = [Audio]::GetVolume()
    $new = [math]::Max(0.0, $current - {amount / 100.0})
    [Audio]::SetVolume($new)
    """
    subprocess.run(
        ["powershell", "-NonInteractive", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        timeout=5,
    )
    return f"Volume decreased by {amount}."


def tell_time() -> str:
    now = datetime.now()
    return now.strftime("It's %I:%M %p on %A, %B %d.")


def open_application(name: str) -> str:
    name = name.strip().lower()
    known = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "explorer": "explorer.exe",
        "paint": "mspaint.exe",
        "spotify": "spotify.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "code": "code.exe",
        "vs code": "code.exe",
        "vlc": "vlc.exe",
    }
    executable = known.get(name, f"{name}.exe")
    try:
        subprocess.Popen(
            executable,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return f"Opening {name}."
    except Exception as e:
        logger.error("Failed to open application %s: %s", name, e)
        return f"Could not open {name}."


def close_application(name: str) -> str:
    name = name.strip().lower()
    process_map = {
        "notepad": "notepad.exe",
        "calculator": "calculator.exe",
        "spotify": "spotify.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "code": "code.exe",
        "vs code": "code.exe",
        "vlc": "vlc.exe",
    }
    process_name = process_map.get(name, f"{name}.exe")
    result = subprocess.run(
        ["taskkill", "/F", "/IM", process_name],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return f"Closed {name}."
    logger.warning("taskkill failed for %s: %s", process_name, result.stderr)
    return f"Could not find {name} running."