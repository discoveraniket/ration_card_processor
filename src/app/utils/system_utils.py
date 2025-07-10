# system_utils.py
import winreg

def is_dark_mode_windows():
    """Detect if Windows is in dark mode."""
    try:
        path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, path)
        value = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
        return value == 0  # 0 = Dark, 1 = Light
    except Exception:
        return False