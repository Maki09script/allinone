import platform
import subprocess
import sys
import os

def check_architecture():
    print(f"[INFO] Python Architecture: {platform.architecture()[0]}")
    is_64bits = sys.maxsize > 2**32
    print(f"[INFO] Python is 64-bit: {is_64bits}")
    
    # Check if we are running in WOW64
    if 'PROCESSOR_ARCHITEW6432' in os.environ:
        print("[WARNING] Running in WOW64 emulation (32-bit process on 64-bit OS). Registry might be redirected!")
    else:
        print("[INFO] Not running in WOW64 emulation.")

def check_bam_service():
    print("\n[INFO] Checking BAM service status...")
    try:
        res = subprocess.run(['sc', 'query', 'bam'], capture_output=True, text=True)
        print(res.stdout)
    except Exception as e:
        print(f"[ERROR] Could not query BAM service: {e}")

def list_bam_keys():
    print("\n[INFO] Current BAM Registry Content (Native reg.exe):")
    paths = [
        r"HKLM\SYSTEM\CurrentControlSet\Services\bam\State\UserSettings",
        r"HKLM\SYSTEM\ControlSet001\Services\bam\State\UserSettings"
    ]
    
    for path in paths:
        print(f"--- Checking {path} ---")
        # Use /reg:64 to force 64-bit view if supported/needed
        cmd = ['reg', 'query', path, '/s'] 
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(res.stdout)
        else:
            print(f"[INFO] Key not found or empty (Code {res.returncode})")
            # print(res.stderr)

def main():
    print("=== BAM DIAGNOSTIC TOOL ===")
    check_architecture()
    check_bam_service()
    list_bam_keys()
    print("===========================")

if __name__ == "__main__":
    main()
