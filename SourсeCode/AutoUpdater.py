import json
import os
import sys
import requests
import zipfile
import shutil
import tempfile
import subprocess
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
    
    def download_update(self, download_url):
        try:
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, self.asset_name)
            
            print(f"[Updater] Downloading {self.asset_name}...")
            
            response = requests.get(download_url, stream=True, timeout=300)
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
            
            print("[Updater] Replacing files...")
            
            update_files = ['UltraDownloader.exe', 'AutoUpdater.exe', 'SecureConfig.py', '_internal']
            
            for item in os.listdir(extract_dir):
                src = os.path.join(extract_dir, item)
                dst = os.path.join(self.app_dir, item)
                
                if item in update_files:
                    if os.path.isdir(src):
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
            
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
            input("Press Enter to exit...")
            return
        
        update_info = self.check_for_updates()
        
        if not update_info:
            input("Press Enter to exit...")
            return
        
        print(f"\nVersion {update_info['version']} is available.")
        answer = input("Download and install update? [Y/n]: ").strip().lower()
        
        if answer and answer != 'y':
            print("[Updater] Update cancelled.")
            input("Press Enter to exit...")
            return
        
        if self.download_update(update_info['download_url']):
            if not self._update_version_in_config(update_info['version']):
                print("[Updater Warning] Version update failed, but files were updated.")
            
            print("[Updater] Restarting application...")
            
            main_exe = os.path.join(self.app_dir, "UltraDownloader.exe")
            if os.path.exists(main_exe):
                subprocess.Popen([main_exe])
            else:
                print("[Updater] Could not find main executable to restart.")
            
            sys.exit(0)
        else:
            print("[Updater] Update failed.")
            input("Press Enter to exit...")

if __name__ == "__main__":
    updater = Updater()
    updater.run()