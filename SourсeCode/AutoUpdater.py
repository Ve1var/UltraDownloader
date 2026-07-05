import json
import os
import sys
import requests
import zipfile
import shutil
import tempfile
import subprocess
import time
from SecureConfig import SecureConfig

APP_NAME = "UltraDownloader"
APP_DATA = os.getenv('APPDATA')
SETTINGS_DIR = os.path.join(APP_DATA, APP_NAME)

class Updater:
    def __init__(self):
        self.repo_owner = ""
        self.repo_name = ""
        self.current_version = ""
        self.asset_name = ""
        self.app_dir = ""
        self.update_url = ""
        self.checksum = ""
        self._secure_config = SecureConfig()
    
    def load_config(self):
        secure_data = self._secure_config.load_config()
        
        if secure_data:
            repo_config = secure_data.get('repository', {})
            self.repo_owner = repo_config.get('owner', '')
            self.repo_name = repo_config.get('name', '')
            self.asset_name = repo_config.get('asset_name', '')
            self.current_version = secure_data.get('version_tag', '')
            self.update_url = secure_data.get('update_endpoint', 'https://api.github.com')
            
            if all([self.repo_owner, self.repo_name, self.current_version, self.asset_name]):
                if getattr(sys, 'frozen', False):
                    self.app_dir = os.path.dirname(sys.executable)
                else:
                    self.app_dir = os.path.dirname(os.path.abspath(__file__))
                return True
        
        print("[Updater Error] Failed to load configuration from secure storage.")
        return False
    
    def check_for_updates(self):
        if self.update_url == "https://api.github.com":
            url = f"{self.update_url}/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        else:
            url = f"{self.update_url}/api/updates/{self.repo_owner}/{self.repo_name}"
        
        try:
            headers = {
                'User-Agent': f'{APP_NAME}/{self.current_version}',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"[Updater Error] Update server returned status {response.status_code}")
                return None
            
            data = response.json()
            
            if self.update_url == "https://api.github.com":
                latest_version = data.get('tag_name', '')
                assets = data.get("assets", [])
                download_url = None
                
                for asset in assets:
                    if asset.get("name") == self.asset_name:
                        download_url = asset.get("browser_download_url")
                        break
            else:
                latest_version = data.get('version', '')
                download_url = data.get('download_url', '')
                self.checksum = data.get('checksum', '')
            
            if not latest_version:
                print("[Updater Error] Could not determine latest version.")
                return None
            
            if latest_version == self.current_version:
                print(f"[Updater] Already up to date ({self.current_version}).")
                return None
            
            print(f"[Updater] New version available: {latest_version} (current: {self.current_version})")
            
            if not download_url:
                print(f"[Updater Error] Asset '{self.asset_name}' not found in release.")
                return None
            
            return {
                "version": latest_version,
                "download_url": download_url,
                "checksum": self.checksum
            }
            
        except requests.RequestException as e:
            print(f"[Updater Error] Network error: {e}")
            return None
        except Exception as e:
            print(f"[Updater Error] Unexpected error: {e}")
            return None
    
    def _replace_file_with_retry(self, src, dst, max_retries=10, delay=1):
        for attempt in range(max_retries):
            try:
                if os.path.exists(dst):
                    os.remove(dst)
                shutil.copy2(src, dst)
                return True
            except PermissionError as e:
                print(f"[Updater] File locked, retry {attempt + 1}/{max_retries}: {e}")
                time.sleep(delay)
            except Exception as e:
                print(f"[Updater] Error copying file: {e}")
                return False
        return False
    
    def download_and_install(self, update_info):
        try:
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, self.asset_name)
            
            print(f"[Updater] Downloading {self.asset_name}...")
            
            response = requests.get(update_info['download_url'], stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            downloaded_mb = downloaded / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            print(f"\r[Updater] Downloading: {downloaded_mb:.1f}/{total_mb:.1f} MB ({percent:.1f}%)", end="", flush=True)
            
            print()
            print("[Updater] Download complete. Extracting...")
            
            extract_dir = tempfile.mkdtemp()
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            print("[Updater] Waiting for main application to fully close...")
            time.sleep(3)
            
            print("[Updater] Replacing files...")
            
            main_exe_src = None
            main_exe_dst = os.path.join(self.app_dir, "UltraDownloader.exe")
            
            for root_dir, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == "UltraDownloader.exe":
                        main_exe_src = os.path.join(root_dir, file)
                        break
                if main_exe_src:
                    break
            
            if main_exe_src and os.path.exists(main_exe_src):
                print(f"[Updater] Replacing UltraDownloader.exe...")
                if not self._replace_file_with_retry(main_exe_src, main_exe_dst):
                    print("[Updater Error] Failed to replace UltraDownloader.exe")
                    return False
            else:
                print("[Updater Warning] UltraDownloader.exe not found in update archive")
            
            updater_exe_src = None
            updater_exe_dst = os.path.join(self.app_dir, "AutoUpdater.exe")
            
            for root_dir, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file == "AutoUpdater.exe":
                        updater_exe_src = os.path.join(root_dir, file)
                        break
                if updater_exe_src:
                    break
            
            if updater_exe_src and os.path.exists(updater_exe_src):
                print(f"[Updater] Replacing AutoUpdater.exe...")
                if not self._replace_file_with_retry(updater_exe_src, updater_exe_dst):
                    print("[Updater Warning] Failed to replace AutoUpdater.exe")
            
            print("[Updater] Copying additional files...")
            
            for root_dir, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file not in ["UltraDownloader.exe", "AutoUpdater.exe"]:
                        src_path = os.path.join(root_dir, file)
                        rel_path = os.path.relpath(src_path, extract_dir)
                        dst_path = os.path.join(self.app_dir, rel_path)
                        
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        try:
                            shutil.copy2(src_path, dst_path)
                        except Exception as e:
                            print(f"[Updater Warning] Could not copy {file}: {e}")
            
            shutil.rmtree(temp_dir)
            shutil.rmtree(extract_dir)
            
            print("[Updater] Update installed successfully.")
            return True
            
        except requests.RequestException as e:
            print(f"\n[Updater Error] Download failed: {e}")
            return False
        except zipfile.BadZipFile:
            print("\n[Updater Error] Downloaded file is corrupted.")
            return False
        except Exception as e:
            print(f"\n[Updater Error] Installation failed: {e}")
            return False
    
    def _update_version_in_config(self, new_version):
        try:
            secure_data = self._secure_config.load_config()
            if secure_data:
                secure_data['version_tag'] = new_version
                self._secure_config.save_config(secure_data)
                print(f"[Updater] Version updated to {new_version} in configuration.")
                return True
            else:
                print("[Updater Error] Could not load config to update version.")
                return False
        except Exception as e:
            print(f"[Updater Error] Failed to update version: {e}")
            return False
    
    def run(self):
        if not self.load_config():
            print("[Updater] Press Enter to exit...")
            input()
            return
        
        update_info = self.check_for_updates()
        
        if not update_info:
            print("[Updater] Press Enter to exit...")
            input()
            return
        
        print(f"\n[Updater] Version {update_info['version']} is available.")
        answer = input("[Updater] Download and install update? [Y/n]: ").strip().lower()
        
        if answer and answer != 'y':
            print("[Updater] Update cancelled.")
            print("[Updater] Press Enter to exit...")
            input()
            return
        
        if self.download_and_install(update_info):
            if not self._update_version_in_config(update_info['version']):
                print("[Updater Warning] Version update failed, but files were updated.")
            
            print("[Updater] Update completed successfully!")
            print("[Updater] Press Enter to exit and restart UltraDownloader...")
            input()
            
            main_exe = os.path.join(self.app_dir, "UltraDownloader.exe")
            if os.path.exists(main_exe):
                print("[Updater] Starting UltraDownloader...")
                time.sleep(1)
                subprocess.Popen([main_exe])
        else:
            print("[Updater] Update failed.")
            print("[Updater] Press Enter to exit...")
            input()

if __name__ == "__main__":
    updater = Updater()
    updater.run()