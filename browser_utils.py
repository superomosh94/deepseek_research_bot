import os
import winreg
from pathlib import Path

def detect_installed_browsers():
    """
    Detect common Chromium-based browsers installed on Windows.
    Returns a list of dicts with 'name', 'path', and 'type'.
    """
    browsers = []
    
    # Common search paths for browsers
    search_paths = [
        # Google Chrome
        {
            "name": "Google Chrome",
            "type": "chrome",
            "paths": [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe")
            ]
        },
        # Microsoft Edge
        {
            "name": "Microsoft Edge",
            "type": "edge",
            "paths": [
                os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe")
            ]
        },
        # Brave Browser
        {
            "name": "Brave Browser",
            "type": "brave",
            "paths": [
                os.path.expandvars(r"%ProgramFiles%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\BraveSoftware\Brave-Browser\Application\brave.exe"),
                os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe")
            ]
        }
    ]
    
    for browser_info in search_paths:
        for path in browser_info["paths"]:
            if os.path.exists(path):
                browsers.append({
                    "name": browser_info["name"],
                    "path": path,
                    "type": browser_info["type"]
                })
                break # Found one path for this browser type, move to next
                
    return browsers

def get_browser_choice(browsers):
    """Format browser list for display"""
    if not browsers:
        return None
    
    choices = {}
    for i, b in enumerate(browsers, 1):
        choices[str(i)] = b
        
    return choices
