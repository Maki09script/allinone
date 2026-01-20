import subprocess
import hashlib

def get_hwid():
    """Generates a unique Hardware ID based on Motherboard UUID and CPU Serial."""
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        # Get Motherboard UUID via PowerShell
        cmd_uuid = "powershell -NoProfile -Command (Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"
        uuid = subprocess.check_output(cmd_uuid, startupinfo=startupinfo).decode().strip()
        
        # Get CPU ID via PowerShell
        cmd_cpu = "powershell -NoProfile -Command (Get-CimInstance -Class Win32_Processor).ProcessorId"
        cpu_id = subprocess.check_output(cmd_cpu, startupinfo=startupinfo).decode().strip()
        
        raw_id = f"{uuid}-{cpu_id}"
        return hashlib.sha256(raw_id.encode()).hexdigest()
    except Exception:
        # Fallback 
        return "UNKNOWN_HWID_FALLBACK_DEVICE"
