import os
import shutil
import datetime

VERSION = "1.0.0"
RELEASE_DIR = f"release_v{VERSION}"
DIST_EXE = os.path.join("dist", "MakiCleaner.exe")
ARTIFACTS_DIR = r"c:\Users\Mark\.gemini\antigravity\brain\b5624f29-b2e1-4317-bdd3-cf0c57f45e09"

def package_release():
    if os.path.exists(RELEASE_DIR):
        shutil.rmtree(RELEASE_DIR)
    os.makedirs(RELEASE_DIR)
    
    print(f"--- Packaging Release v{VERSION} ---")

    # 1. Check for EXE
    if os.path.exists(DIST_EXE):
        shutil.copy2(DIST_EXE, RELEASE_DIR)
        print("[OK] Copied MakiCleaner.exe")
    else:
        print("[WARNING] MakiCleaner.exe not found in 'dist/'. Run PyInstaller build first!")
        print("   Command: pyinstaller --noconfirm --onefile --windowed --name \"MakiCleaner\" --key \"YOUR_KEY\" --add-data \"string_cleaner;string_cleaner\" product_client/launch_auth.py")

    # 2. Copy Guides
    guides = {
        "User Guide.md": "user_guide.md",
        "Changelog.md": r"c:\Users\Mark\OneDrive\Desktop\bago\CHANGELOG.md"
    }

    for dest_name, src_path in guides.items():
        # Handle artifact paths vs local paths
        if not os.path.isabs(src_path):
             # Try mapping artifact path if not found locally
             pass 

        # For this script we assume artifacts are in the specific brain dir or local
        # We'll try to copy from the brain dir if simple filename
        
        final_src = src_path
        if not os.path.exists(final_src):
             # Check artifact dir
             artifact_src = os.path.join(ARTIFACTS_DIR, "user_guide.md")
             if os.path.exists(artifact_src) and "User Guide" in dest_name:
                 final_src = artifact_src
        
        if os.path.exists(final_src):
            shutil.copy2(final_src, os.path.join(RELEASE_DIR, dest_name))
            print(f"[OK] Copied {dest_name}")
        else:
            print(f"[MISSING] Could not find source for {dest_name} at {final_src}")

    # 3. Create Info File
    with open(os.path.join(RELEASE_DIR, "READ_ME.txt"), "w") as f:
        f.write(f"Maki Cleaner v{VERSION}\n")
        f.write(f"Build Date: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write("INSTRUCTIONS:\n")
        f.write("1. Double click MakiCleaner.exe to run.\n")
        f.write("2. Paste your license key when asked.\n")
        f.write("3. Review 'User Guide.md' for help.\n")

    print(f"\n--- Release Package Ready: {os.path.abspath(RELEASE_DIR)} ---")

if __name__ == "__main__":
    package_release()
