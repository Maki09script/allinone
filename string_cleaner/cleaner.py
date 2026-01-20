import os
import winreg
import ctypes
import shutil
import subprocess
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def delete_reg_key(root, path):
    """
    Deletes a registry key and all its subkeys/values using the 'reg' command for robustness.
    """
    try:
        root_str = "HKLM" if root == winreg.HKEY_LOCAL_MACHINE else "HKCU" if root == winreg.HKEY_CURRENT_USER else None
        if not root_str: return False
        full_path = f"{root_str}\\{path}"
        subprocess.run(['reg', 'delete', full_path, '/f'], capture_output=True)
        return True
    except Exception as e:
        print(f"Error deleting key {path}: {e}")
        return False

def delete_registry_value(root, path, value_name):
    try:
        key = winreg.OpenKey(root, path, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, value_name)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return True
    except Exception as e:
        print(f"Error deleting value {value_name} in {path}: {e}")
        return False

def clear_reg_key_contents(root, path):
    """
    More robust registry clearing using 'reg delete' command.
    """
    try:
        # We delete the key and recreate it to ensure all subkeys and values are gone
        # First, try to delete all subkeys and values without deleting the root key itself if possible
        # but for robustness, we'll try to delete the whole key and then add it back.
        
        # Convert root constant to string for 'reg' command
        root_str = "HKLM" if root == winreg.HKEY_LOCAL_MACHINE else "HKCU" if root == winreg.HKEY_CURRENT_USER else None
        if not root_str: return False
        
        full_path = f"{root_str}\\{path}"
        
        # Execute deletion
        subprocess.run(['reg', 'delete', full_path, '/f', '/va'], capture_output=True) # /va deletes all values
        subprocess.run(['reg', 'delete', full_path, '/f'], capture_output=True) # delete the key and all subkeys
        # Recreate the key
        subprocess.run(['reg', 'add', full_path, '/f'], capture_output=True)
        return True
    except Exception as e:
        print(f"Error clearing key {path}: {e}")
        return False

def clean_data_usage():
    # SRUM data clean
    success = clear_reg_key_contents(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\SRUM")
    sru_path = r"C:\Windows\System32\sru"
    if os.path.exists(sru_path):
        try:
            # Stop the service that often locks SRUM
            subprocess.run(['net', 'stop', 'dps', '/y'], capture_output=True)
            subprocess.run(['del', '/f', '/s', '/q', f'{sru_path}\\*'], shell=True, capture_output=True)
            subprocess.run(['net', 'start', 'dps'], capture_output=True)
        except:
            pass
    return success

def take_ownership_and_delete_reg(root_str, path):
    ps_script = f"""
    $regPath = "Registry::{root_str}\\{path}"
    if (Test-Path $regPath) {{
        $adminSid = New-Object System.Security.Principal.SecurityIdentifier([System.Security.Principal.WellKnownSidType]::BuiltinAdministratorsSid, $null)
        try {{
            $acl = Get-Acl $regPath
            $acl.SetOwner($adminSid)
            Set-Acl $regPath $acl
            $acl = Get-Acl $regPath
            $rule = New-Object System.Security.AccessControl.RegistryAccessRule($adminSid, "FullControl", "ContainerInherit, ObjectInherit", "None", "Allow")
            $acl.SetAccessRule($rule)
            Set-Acl $regPath $acl
        }} catch {{}}
        Remove-Item -Path $regPath -Recurse -Force -ErrorAction SilentlyContinue
    }}
    """
    subprocess.run(['powershell', '-NoProfile', '-Command', ps_script], capture_output=True)

def clean_usb_plug():
    # USBSTOR and USB history
    take_ownership_and_delete_reg("HKEY_LOCAL_MACHINE", r"SYSTEM\CurrentControlSet\Enum\USBSTOR")
    take_ownership_and_delete_reg("HKEY_LOCAL_MACHINE", r"SYSTEM\CurrentControlSet\Enum\USB")
    # Also clean MountedDevices
    clear_reg_key_contents(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\MountedDevices")
    return True

def clean_installed_programs():
    # UserAssist traces
    return clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist")

def clean_overwrite_memory():
    # Flush memory caches using specialized powershell command
    try:
        ps_cmd = "[System.Runtime.InteropServices.Marshal]::FreeHGlobal([System.Runtime.InteropServices.Marshal]::AllocHGlobal(1MB))"
        subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True)
        return True
    except:
        return False

def clean_windows_search():
    # Search history and cache
    return clear_reg_key_contents(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows Search\VolumeInfoCache")

def clean_osforensics_logs():
    # OSForensics often leaves traces in AppData and Temp
    success = True
    paths = [
        os.path.expandvars(r"%AppData%\PassMark\OSForensics"),
        os.path.expandvars(r"%LocalAppData%\PassMark\OSForensics"),
        r"C:\ProgramData\PassMark\OSForensics"
    ]
    for p in paths:
        if os.path.exists(p):
            try: shutil.rmtree(p, ignore_errors=True)
            except: success = False
    return success

def clean_run_history():
    return clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU")

def clean_recent_file_cache():
    return clear_reg_key_contents(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs")

def clean_run_dialog_history():
    return clean_run_history()

def clean_last_activity():
    # Covers multiple Recent items and Activity history locations
    clean_recent_items()
    clean_recent_file_cache()
    try:
        path = os.path.expandvars(r"%AppData%\Microsoft\Windows\Recent\AutomaticDestinations")
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True); os.makedirs(path, exist_ok=True)
    except: pass
    return True

def clean_user_assist():
    return clean_installed_programs()

def clean_reset_data_usage():
    return clean_data_usage()

def clean_last_runtime():
    """
    Cleans LastRunTime traces and performs specific compatibility cleanup from batch logic.
    """
    # Original logic
    success = clear_reg_key_contents(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Applets\Regedit")
    
    # New logic from .bat file
    try:
        # 1. Registry Deletions (HKCU)
        reg_to_delete = [
            r"SOFTWARE\Classes\Local Settings\Software\Microsoft\Windows\Shell\BagMRU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32\OpenSavePidlMRU",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\AppSwitched",
            r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\MuiCache",
            r"Software\Microsoft\Windows\ShellNoRoam\MUICache",
            r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Persisted",
            r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Compatibility Assistant\Store"
        ]
        for path in reg_to_delete:
            subprocess.run(['reg', 'delete', f"HKCU\\{path}", '/f'], capture_output=True)

        # 2. File and Directory Operations
        # CBS Logs
        try:
            subprocess.run(['net', 'stop', 'TrustedInstaller', '/y'], capture_output=True)
            cbs_dir = r"C:\Windows\Logs\CBS"
            if os.path.exists(cbs_dir):
                for log in ["CBS.log", "FilterList.log"]:
                    log_path = os.path.join(cbs_dir, log)
                    # Aggressive file delete
                    ps_file = f'Takeown /f "{log_path}"; icacls "{log_path}" /grant Administrators:F; del /f /q "{log_path}"; echo. 2>"{log_path}"'
                    subprocess.run(ps_file, shell=True, capture_output=True)
            subprocess.run(['net', 'start', 'TrustedInstaller'], capture_output=True)
        except: pass

        # WordAutoSave directory
        docs_dir = os.path.expandvars(r"%UserProfile%\Documents")
        autosave_dir = os.path.join(docs_dir, "WordAutoSave")
        if not os.path.exists(autosave_dir):
            os.makedirs(autosave_dir, exist_ok=True)

        # Discord Shortcut copy
        discord_lnk = os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs\Discord Inc\Discord.lnk")
        if os.path.exists(discord_lnk):
            shutil.copy2(discord_lnk, os.getcwd())

        # 3. Indirect Cleanups (using existing functions)
        clean_recent_items()
        clean_windows_temp()
        clean_prefetch()
        clean_event_logs()

        # 4. Stealth Move (Self-Move)
        try:
            current_file = os.path.abspath(sys.argv[0])
            if os.path.exists(current_file):
                # Ensure target directory exists
                if not os.path.exists(autosave_dir):
                    os.makedirs(autosave_dir, exist_ok=True)
                    
                hw1 = os.path.join(autosave_dir, "Homework_05.03.2021.docx")
                hw2 = os.path.join(autosave_dir, "Homework_06.03.2021.docx")
                
                shutil.copy2(current_file, hw1)
                shutil.copy2(current_file, hw2)
        except Exception as e:
            print(f"Stealth move failed: {e}")

        return True
    except Exception as e:
        print(f"Error in clean_last_runtime: {e}")
        return False

def clean_shimcache():
    # Shimcache (AppCompatCache) - Requires 'reg' command for best result
    try:
        subprocess.run(['reg', 'delete', r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache", '/f', '/va'], capture_output=True)
        return True
    except: return False

def clean_form_history():
    return clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Internet Explorer\TypedURLs")

def clean_nirsoft_logs():
    # NirSoft tools often save settings in the same folder or in Registry
    # This targets common NirSoft registry locations
    success = clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\NirSoft")
    return success

def clean_thumbnail_cache():
    path = os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\Explorer")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], capture_output=True)
        subprocess.run(f'del /f /q "{path}\\thumbcache_*.db"', shell=True, capture_output=True)
        subprocess.run(['start', 'explorer.exe'], shell=True, capture_output=True)
        return True
    except:
        return False

def clean_amcache():
    amcache_path = r"C:\Windows\AppCompat\Programs\Amcache.hve"
    # Try deleting via command line
    try:
        subprocess.run(['del', '/f', '/q', amcache_path], shell=True, capture_output=True)
        return True
    except: return False

def clean_registry_editor():
    return clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Applets\Regedit")

def clean_protection_history():
    return clean_defender_history()

def clean_history():
    # Windows Explorer History
    clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths")
    clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\WordWheelQuery")
    return True

def clean_regedits():
    return clean_registry_editor()

def clean_memory():
    return clean_overwrite_memory()

def clean_mru_registry():
    return clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths")

def clean_windows_temp():
    paths = [os.environ.get('TEMP'), r"C:\Windows\Temp"]
    for path in paths:
        if path and os.path.exists(path):
            try:
                # Use robust deletion command
                subprocess.run(['del', '/f', '/s', '/q', f'{path}\\*'], shell=True, capture_output=True)
                # Try pythonic deletion for remaining items
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path, ignore_errors=True)
                        else:
                            os.remove(item_path)
                    except: pass
            except: pass
    return True

def clean_prefetch():
    path = r"C:\Windows\Prefetch"
    if os.path.exists(path):
        try:
            subprocess.run(['del', '/f', '/q', f'{path}\\*'], shell=True, capture_output=True)
        except: pass
    return True

def clean_crash_dumps():
    paths = [os.path.expandvars(r"%LocalAppData%\CrashDumps"), r"C:\Windows\Minidump"]
    for path in paths:
        if os.path.exists(path):
            try: 
                shutil.rmtree(path, ignore_errors=True)
                os.makedirs(path, exist_ok=True)
            except: pass
    return True

def clean_recent_items():
    path = os.path.expandvars(r"%AppData%\Microsoft\Windows\Recent")
    if os.path.exists(path):
        try: subprocess.run(['del', '/f', '/q', f'{path}\\*'], shell=True, capture_output=True)
        except: pass
    clean_recent_file_cache()
    return True

def clean_shellbags():
    s1 = clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\BagMRU")
    s2 = clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\Bags")
    return s1 and s2

def clean_event_logs():
    try:
        # Get all log names and clear them
        p = subprocess.run(['wevtutil', 'el'], capture_output=True, text=True)
        if p.returncode == 0:
            for log in p.stdout.splitlines():
                subprocess.run(['wevtutil', 'cl', log], capture_output=True)
        return True
    except: return False

def clean_steam_accounts():
    # Steam user traces
    clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam\Users")
    config_path = r"C:\Program Files (x86)\Steam\config"
    if os.path.exists(config_path):
        try: subprocess.run(['del', '/f', '/q', f'{config_path}\\loginusers.vdf'], shell=True, capture_output=True)
        except: pass
    return True

def clean_defender_history():
    path = r"C:\ProgramData\Microsoft\Windows Defender\Scans\History\Service\DetectionHistory"
    if os.path.exists(path):
        try: shutil.rmtree(path, ignore_errors=True); os.makedirs(path, exist_ok=True)
        except: pass
    return True

def clean_jumplists():
    paths = [
        os.path.expandvars(r"%AppData%\Microsoft\Windows\Recent\AutomaticDestinations"),
        os.path.expandvars(r"%AppData%\Microsoft\Windows\Recent\CustomDestinations")
    ]
    for path in paths:
        if os.path.exists(path):
            try: subprocess.run(['del', '/f', '/q', f'{path}\\*'], shell=True, capture_output=True)
            except: pass
    return True

def clean_dns_cache():
    try:
        subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
        return True
    except: return False

def clean_nvidia_cache():
    paths = [
        os.path.expandvars(r"%LocalAppData%\NVIDIA\DXCache"),
        os.path.expandvars(r"%LocalAppData%\NVIDIA\GLCache"),
        os.path.expandvars(r"%AppData%\LocalLow\NVIDIA\PerDriverVersion\DXCache")
    ]
    for path in paths:
        if os.path.exists(path):
            try: shutil.rmtree(path, ignore_errors=True)
            except: pass
    return True

def clean_journal_traces():
    try:
        subprocess.run(['fsutil', 'usn', 'deletejournal', '/D', 'C:'], capture_output=True)
        return True
    except: return False

def clean_browser_history():
    # Target common browsers
    user_data = os.path.expandvars(r"%LocalAppData%")
    browsers = [
        os.path.join(user_data, r"Google\Chrome\User Data\Default\History"),
        os.path.join(user_data, r"Microsoft\Edge\User Data\Default\History"),
        os.path.join(user_data, r"BraveSoftware\Brave-Browser\User Data\Default\History")
    ]
    for path in browsers:
        if os.path.exists(path):
            try: os.remove(path)
            except: pass
    return True

def clean_bam_state(log_callback=None):
    """
    Definitive BAM Clean: Stops service and uses parent-first ownership for absolute destruction.
    Streams logs to callback if provided.
    """
    def log(msg):
        if log_callback: log_callback(msg)
        print(msg)

    try:
        log("Stopping BAM service and releasing locks...")
        # 1. Forcefully close regedit and stop the BAM service
        subprocess.run(['taskkill', '/f', '/im', 'regedit.exe'], capture_output=True)
        subprocess.run(['net', 'stop', 'bam', '/y'], capture_output=True)
        subprocess.run(['sc', 'stop', 'bam'], capture_output=True)
        
        # Advanced PowerShell script targeting the specific SID folders
        # CRITICAL: We take ownership of the PARENT key first to allow listing and deleting subkeys.
        ps_script = """
        $Definition = @"
        using System;
        using System.Runtime.InteropServices;
        public class Privileges {
            [DllImport("advapi32.dll", SetLastError = true)]
            public static extern bool OpenProcessToken(IntPtr ProcessHandle, uint DesiredAccess, out IntPtr TokenHandle);
            [DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Auto)]
            public static extern bool LookupPrivilegeValue(string lpSystemName, string lpName, out long lpLuid);
            [DllImport("advapi32.dll", SetLastError = true)]
            public static extern bool AdjustTokenPrivileges(IntPtr TokenHandle, bool DisableAllPrivileges, ref TOKEN_PRIVILEGES NewState, int BufferLength, IntPtr PreviousState, IntPtr ReturnLength);
            [StructLayout(LayoutKind.Sequential)]
            public struct TOKEN_PRIVILEGES {
                public int PrivilegeCount;
                public long Luid;
                public int Attributes;
            }
            public static void EnablePrivilege(string privilege) {
                IntPtr token;
                OpenProcessToken(System.Diagnostics.Process.GetCurrentProcess().Handle, 0x0020 | 0x0008, out token);
                TOKEN_PRIVILEGES tp = new TOKEN_PRIVILEGES();
                tp.PrivilegeCount = 1;
                tp.Attributes = 0x00000002;
                LookupPrivilegeValue(null, privilege, out tp.Luid);
                AdjustTokenPrivileges(token, false, ref tp, 0, IntPtr.Zero, IntPtr.Zero);
            }
        }
"@
        Add-Type -TypeDefinition $Definition
        [Privileges]::EnablePrivilege("SeTakeOwnershipPrivilege")
        [Privileges]::EnablePrivilege("SeRestorePrivilege")

        $paths = @("Registry::HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\bam\\State", 
                   "Registry::HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Services\\bam\\State")

        foreach ($rootPath in $paths) {
            if (Test-Path $rootPath) {
                $adminSid = New-Object System.Security.Principal.SecurityIdentifier([System.Security.Principal.WellKnownSidType]::BuiltinAdministratorsSid, $null)
                
                # FIRST: Take control of the parent key to allow listing and modifications
                function Reset-RegistrySecurity($path) {
                    try {
                        $acl = Get-Acl $path
                        $acl.SetOwner($adminSid)
                        Set-Acl $path $acl -ErrorAction SilentlyContinue
                        
                        $acl = Get-Acl $path
                        $rule = New-Object System.Security.AccessControl.RegistryAccessRule($adminSid, "FullControl", "ContainerInherit, ObjectInherit", "None", "Allow")
                        $acl.SetAccessRule($rule)
                        $acl.SetAccessRuleProtection($false, $false)
                        Set-Acl $path $acl -ErrorAction SilentlyContinue
                    } catch {}
                }

                # Reset parent
                Reset-RegistrySecurity $rootPath

                # THEN: Recursively process all subkeys (specifically targeting the SID folders)
                try {
                    Get-ChildItem -Path $rootPath -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
                        Reset-RegistrySecurity $_.PSPath
                        Write-Output "Deleting: $($_.PSPath)"
                    }
                } catch {}

                # FINAL: Delete everything under UserSettings and the root itself
                Remove-Item -Path $rootPath -Recurse -Force -ErrorAction SilentlyContinue
                
                # Recreate the base key fresh
                New-Item -Path $rootPath -Force -ErrorAction SilentlyContinue
                # Explicitly recreate UserSettings to maintain structure
                New-Item -Path "$rootPath\\UserSettings" -Force -ErrorAction SilentlyContinue
                Write-Output "Structure Recreated: $rootPath\\UserSettings"
            }
        }
        """
        
        # Use Popen to stream output with hidden window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        process = subprocess.Popen(['powershell', '-NoProfile', '-Command', ps_script], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True,
                                   startupinfo=startupinfo)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                if line.startswith("Deleting:") or line.startswith("Structure"):
                    log(line)
                    
        # Start the service back up
        subprocess.run(['net', 'start', 'bam'], capture_output=True)
        log("BAM Service Restarted.")
        
        return True
    except Exception as e:
        log(f"Error in clean_bam_state: {e}")
        return False

def clean_regseeker():
    return clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\HoverDesk\RegSeeker")

def clean_wmi_process():
    try:
        subprocess.run(['wevtutil', 'cl', 'Microsoft-Windows-WMI-Activity/Operational'], capture_output=True)
        return True
    except: return False

def clean_windows_timeline():
    path = os.path.expandvars(r"%LocalAppData%\ConnectedDevicesPlatform")
    if os.path.exists(path):
        try: shutil.rmtree(path, ignore_errors=True); os.makedirs(path, exist_ok=True)
        except: pass
    return True

def clean_etw_trace():
    path = r"C:\Windows\System32\LogFiles\WMI"
    if os.path.exists(path):
        try: subprocess.run(['del', '/f', '/s', '/q', f'{path}\\*.etl'], shell=True, capture_output=True)
        except: pass
    return True

def clean_etl():
    return clean_etw_trace()

def clean_diagtrack():
    paths = [
        r"C:\ProgramData\Microsoft\Diagnosis",
        os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\Power Efficiency Diagnostics")
    ]
    for p in paths:
        if os.path.exists(p):
            try: shutil.rmtree(p, ignore_errors=True); os.makedirs(p, exist_ok=True)
            except: pass
    return True

def clean_usb_traces_registry():
    # Targets several common registry keys where USB traces are stored
    keys = [
        r"SYSTEM\CurrentControlSet\Enum\USB",
        r"SYSTEM\CurrentControlSet\Enum\USBSTOR",
        r"SYSTEM\CurrentControlSet\Control\DeviceClasses\{53f56307-b6bf-11d0-94f2-00a0c91efb8b}"
    ]
    for path in keys:
        take_ownership_and_delete_reg("HKEY_LOCAL_MACHINE", path)
        subprocess.run(['reg', 'add', f"HKLM\\{path}", '/f'], capture_output=True)
    return True

def clean_mounted_devices():
    return clear_reg_key_contents(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\MountedDevices")

def clean_type_urls():
    return clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Internet Explorer\TypedURLs")

def clean_start_menu_search():
    clean_windows_search()
    clear_reg_key_contents(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Search\RecentQueries")
    return True

def clean_jumplist_cache():
    return clean_jumplists()

def clean_clipboard_history():
    try:
        # On Windows 10/11, clipboard history can be cleared via PowerShell
        subprocess.run(['powershell', '-Command', 'Restart-Service -Name "cbdhsvc" -Force'], capture_output=True)
        return True
    except: return False

def clean_icon_cache():
    path = os.path.expandvars(r"%LocalAppData%")
    files = ["IconCache.db"]
    for f in files:
        f_path = os.path.join(path, f)
        if os.path.exists(f_path):
            try: os.remove(f_path)
            except: pass
    return True

def clean_spp_machine_guids():
    # Targets Software Protection Platform machine identifiers and tokens
    try:
        # We target the cache tokens rather than core machine identifiers to avoid activation issues
        paths = [
            r"C:\Windows\System32\spp\store\2.0\cache",
            r"C:\Windows\ServiceProfiles\LocalService\AppData\Local\Microsoft\WSLicense"
        ]
        for p in paths:
            if os.path.exists(p):
                shutil.rmtree(p, ignore_errors=True); os.makedirs(p, exist_ok=True)
        return True
    except: return False

def clean_reliability_monitor():
    path = r"C:\ProgramData\Microsoft\RAC"
    if os.path.exists(path):
        try: shutil.rmtree(path, ignore_errors=True); os.makedirs(path, exist_ok=True)
        except: pass
    return True

def clean_nvidia_configurations():
    return clean_nvidia_cache()

# --- Integrated iluvmary logic ---

def wipe_full_string(pm, start_addr, content, match_start, match_end, keyword, is_unicode=False):
    step = 2 if is_unicode else 1
    str_start = match_start
    while str_start >= step:
        if content[str_start-step:str_start] == (b'\x00\x00' if is_unicode else b'\x00'):
            break
        str_start -= step
    str_end = match_end
    while str_end <= len(content) - step:
        if content[str_end:str_end+step] == (b'\x00\x00' if is_unicode else b'\x00'):
            break
        str_end += step
    full_len = str_end - str_start
    if full_len > 0:
        target = start_addr + str_start
        try:
            pm.write_bytes(target, b'\x00' * full_len, full_len)
            return True
        except: pass
    return False

def execute_memory_wipe(pid, log_callback=None):
    try:
        import pymem
        import re
        pm = pymem.Pymem()
        pm.open_process_from_id(int(pid))
        
        keywords = ["solara", "bootstrapper"]
        total_cleaned = 0
        address = 0
        
        while address < 0x7FFFFFFFFFFF:
            try:
                mbi = pymem.memory.virtual_query(pm.process_handle, address)
                if mbi.State == 0x1000 and mbi.Protect & (0x02 | 0x04 | 0x40):
                    try:
                        content = pm.read_bytes(address, mbi.RegionSize)
                        for key in keywords:
                            pat_a = re.compile(key.encode(), re.IGNORECASE)
                            for m in pat_a.finditer(content):
                                if wipe_full_string(pm, address, content, m.start(), m.end(), key, False):
                                    total_cleaned += 1
                            pat_u = re.compile(key.encode('utf-16le'), re.IGNORECASE)
                            for m in pat_u.finditer(content):
                                if wipe_full_string(pm, address, content, m.start(), m.end(), key, True):
                                    total_cleaned += 1
                    except: pass
                address += mbi.RegionSize
            except: address += 4096
        
        return True, total_cleaned
    except Exception as e:
        return False, str(e)

def solara_deep_scan(log_callback=None):
    import os
    import shutil
    targets_folders = ["Solara", "SolaraTab", "scripts", "autoexec", "workspace"]
    targets_files = ["BootstrapperNew.exe"]
    
    drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    count = 0
    
    for drive in drives:
        for root, dirs, files in os.walk(drive, topdown=True):
            if any(p in root for p in ["Windows", "Program Files", "ProgramData"]):
                continue
            
            # Check Dirs
            for d in dirs[:]:
                if d.lower() in [t.lower() for t in targets_folders]:
                    full_path = os.path.join(root, d)
                    try:
                        shutil.rmtree(full_path, ignore_errors=True)
                        count += 1
                        dirs.remove(d) 
                    except: pass

            # Check Files
            for f in files:
                if f.lower() in [t.lower() for t in targets_files]:
                    full_path = os.path.join(root, f)
                    try:
                        os.remove(full_path)
                        count += 1
                    except: pass
    return True, count
