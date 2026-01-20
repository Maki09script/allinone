import subprocess
import winreg

def list_bam_contents():
    log = open("bam_content_check.log", "w")
    log.write("Checking BAM Content after cleanup...\n")
    
    paths = [
        r"SYSTEM\CurrentControlSet\Services\bam\State\UserSettings",
        r"SYSTEM\ControlSet001\Services\bam\State\UserSettings"
    ]
    
    try:
        for path_str in paths:
            log.write(f"\nScanning: HKLM\\{path_str}\n")
            try:
                base_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path_str, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                
                # List subkeys (SIDs)
                try:
                    i = 0
                    while True:
                        sid = winreg.EnumKey(base_key, i)
                        log.write(f"  Found SID Folder: {sid}\n")
                        
                        # Open SID key to check values
                        try:
                            sid_key = winreg.OpenKey(base_key, sid, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                            val_count = 0
                            try:
                                j = 0
                                while True:
                                    name, val, type = winreg.EnumValue(sid_key, j)
                                    log.write(f"      - {name}\n")
                                    val_count += 1
                                    j += 1
                            except OSError:
                                pass # End of values
                            
                            log.write(f"    -> Contains {val_count} values/files.\n")
                            if val_count > 0:
                                log.write("      (HISTORY NOT CLEAN!)\n")
                            else:
                                log.write("      (CLEAN)\n")
                                
                        except Exception as e:
                            log.write(f"    [Error opening SID]: {e}\n")
                        
                        i += 1
                except OSError:
                    pass # End of keys
                    
            except FileNotFoundError:
                log.write("  [Path not found - CLEAN]\n")
            except Exception as e:
                log.write(f"  [Error opening Base]: {e}\n")
                
    except Exception as e:
        log.write(f"Fatal error: {e}\n")
    
    log.close()

if __name__ == "__main__":
    list_bam_contents()
