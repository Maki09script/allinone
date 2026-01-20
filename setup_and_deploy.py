import os
import subprocess
import sys

def run_cmd(cmd):
    print(f"[$] {cmd}")
    subprocess.run(cmd, shell=True, check=False)

def main():
    print("--- Maki License System: Auto-Setup ---")
    
    # 1. Environment Check
    if not os.path.exists("requirements.txt"):
        print("[!] requirements.txt not found!")
        return

    # 2. Git Initialization
    print("\n--- 1. Initializing Git Repository ---")
    if not os.path.exists(".git"):
        run_cmd("git init")
        run_cmd("git add .")
        run_cmd("git commit -m \"Initial commit: Complete License System\"")
        print("[+] Git Repo initialized.")
    else:
        print("[.] Git already initialized.")

    # 3. GitHub Instructions
    print("\n--- 2. GitHub Push ---")
    
    # User provided specific URL
    remote_url = "https://github.com/Maki09script/allinone.git"
    print(f"[INFO] Using Repository: {remote_url}")

    # FIX: Nuclear Option - Re-init Git to clear ALL history of secrets
    print("\n[INFO] Re-initializing Git to clear secret history...")
    
    # Remove .git folder (Windows requires shell=True for rmdir /s /q equivalent in Python usually, but shutil is better)
    import shutil
    if os.path.exists(".git"):
        # On Windows, sometimes files are locked. subprocess is safer for simple scripts
        run_cmd("rmdir /s /q .git") 
    
    run_cmd("git init")
    run_cmd("git add .")
    run_cmd("git commit -m \"Initial commit: Secure and Clean\"")
    run_cmd("git branch -M main")
    run_cmd(f"git remote add origin {remote_url}")

    print("\n[INFO] Pushing to GitHub (Force)...")
    run_cmd("git push -u origin main --force")

    # 4. Render Instructions
    print("\n--- 3. Render Deployment ---")
    print("This project includes a 'render.yaml' Blueprint for one-click setup.")
    print("Steps to deploy:")
    print("  1. Go to https://dashboard.render.com/")
    print("  2. Click 'New +' -> 'Blueprint'")
    print("  3. Connect your GitHub repository: maki-license")
    print("  4. Click 'Apply'")
    print("\n[IMPORTANT] Render will ask for these secrets. Use the values you saved:")
    print("  - DISCORD_TOKEN")
    
    print("\n[SUCCESS] Setup automation complete.")

if __name__ == "__main__":
    main()
