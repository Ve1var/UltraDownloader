import yt_dlp
import json
import os
import tkinter as tk
import sys
import subprocess
from tkinter import filedialog
from SecureConfig import SecureConfig

APP_NAME = "UltraDownloader"
APP_DATA = os.getenv('APPDATA')
SETTINGS_DIR = os.path.join(APP_DATA, APP_NAME)
CONFIG_FILE = os.path.join(SETTINGS_DIR, "app_config.json")

os.makedirs(SETTINGS_DIR, exist_ok=True)

def create_tk_root():
    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry("0x0+0+0")
    root.attributes("-alpha", 0)
    return root

root = create_tk_root()

class Settings:
    def __init__(self):
        self.save_dir = ""
        self.ffmpeg_path = ""
        self.repo_owner = ""
        self.repo_name = ""
        self.version_tag = ""
        self.asset_name = ""
        self.is_first_run = False
        self._secure_config = SecureConfig()
    
    def load(self):
        secure_data = self._secure_config.load_config()
        
        if secure_data:
            self.save_dir = secure_data.get('save_dir', '')
            self.ffmpeg_path = secure_data.get('ffmpeg_path', '')
            
            repo_config = secure_data.get('repository', {})
            self.repo_owner = repo_config.get('owner', '')
            self.repo_name = repo_config.get('name', '')
            self.version_tag = secure_data.get('version_tag', '')
            self.asset_name = repo_config.get('asset_name', '')
            
            if self.save_dir:
                return
        
        default_config = self._create_default_config()
        self._secure_config.save_config(default_config)
        
        self.save_dir = default_config.get('save_dir', '')
        self.ffmpeg_path = default_config.get('ffmpeg_path', '')
        repo_config = default_config.get('repository', {})
        self.repo_owner = repo_config.get('owner', '')
        self.repo_name = repo_config.get('name', '')
        self.version_tag = default_config.get('version_tag', '')
        self.asset_name = repo_config.get('asset_name', '')
        self.is_first_run = True
    
    def _create_default_config(self):
        return {
            'save_dir': '',
            'ffmpeg_path': '',
            'version_tag': '',
            'repository': {
                'owner': '',
                'name': '',
                'asset_name': ''
            }
        }
    
    def save(self):
        config_data = {
            'save_dir': self.save_dir,
            'ffmpeg_path': self.ffmpeg_path,
            'version_tag': self.version_tag,
            'repository': {
                'owner': self.repo_owner,
                'name': self.repo_name,
                'asset_name': self.asset_name
            }
        }
        self._secure_config.save_config(config_data)

class LinkChecker:
    ALLOWED_DOMAINS = ['youtube.com', 'youtu.be', 'vk.com']
    
    @classmethod
    def is_allowed(cls, url):
        url_lower = url.lower()
        return any(domain in url_lower for domain in cls.ALLOWED_DOMAINS)

class ProgressDisplay:
    @staticmethod
    def create_hook(service_name):
        def hook(d):
            if d['status'] == 'downloading':
                ProgressDisplay._render_progress(d, service_name)
            elif d['status'] == 'finished':
                ProgressDisplay._render_finished()
        return hook
    
    @staticmethod
    def _render_progress(d, service_name):
        bar_length = 10
        terminal_width = 100
        
        filename = os.path.basename(d.get('filename', 'Unknown'))
        display_name = (filename[:45] + '...') if len(filename) > 48 else filename
        
        downloaded = d.get('downloaded_bytes', 0)
        total = d.get('total_bytes_estimate', 0) or d.get('total_bytes', 1)
        speed = d.get('speed', 0)
        percent = (downloaded / total) * 100
        
        filled = int(bar_length * percent // 100)
        bar = '|' * filled + '-' * (bar_length - filled)
        
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        speed_mb = (speed or 0) / (1024 * 1024)
        
        progress_str = (
            f"{service_name} | {display_name:<50} "
            f"[{bar} {percent:6.2f}%] | "
            f"{downloaded_mb:6.1f}/{total_mb:6.1f} MB | "
            f"{speed_mb:5.2f} MB/s"
        )
        
        padding = max(0, terminal_width - len(progress_str))
        progress_str = progress_str + ' ' * padding
        
        print(f"\r{progress_str}", end="", flush=True)
    
    @staticmethod
    def _render_finished():
        terminal_width = 100
        print("\r" + " " * terminal_width, end="", flush=True)
        print("\r[Downloader] Download completed.")

class Downloader:
    def __init__(self, settings):
        self.settings = settings
    
    def _check_ffmpeg(self):
        if not self.settings.ffmpeg_path:
            print("[Downloader Warning] FFmpeg not configured. Audio conversion may fail.")
            return False
        if not os.path.exists(self.settings.ffmpeg_path):
            print(f"[Downloader Warning] FFmpeg not found at: {self.settings.ffmpeg_path}")
            return False
        if not os.path.isfile(self.settings.ffmpeg_path):
            print(f"[Downloader Warning] FFmpeg path is not a file: {self.settings.ffmpeg_path}")
            return False
        return True
    
    def download_video(self, url):
        if not LinkChecker.is_allowed(url):
            print("[Downloader Error] Link unsupported")
            return False
        
        output_dir = os.path.join(self.settings.save_dir, "UD_Downloaded", "Video")
        os.makedirs(output_dir, exist_ok=True)
        
        ffmpeg_location = None
        if self._check_ffmpeg():
            ffmpeg_location = self.settings.ffmpeg_path
        
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'format': 'best[ext=mp4]/best',
            'quiet': False,
            'no_warnings': True,
            'ffmpeg_location': ffmpeg_location,
            'noplaylist': True,
            'extract_flat': False,
            'progress_hooks': [ProgressDisplay.create_hook("Video")]
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n[Downloader] Video downloaded.")
            return True
        except Exception as e:
            print(f"\n[Downloader Error] {str(e)}")
            return False
    
    def download_audio(self, url):
        if not LinkChecker.is_allowed(url):
            print("[Downloader Error] Link unsupported")
            return False
        
        output_dir = os.path.join(self.settings.save_dir, "UD_Downloaded", "Music")
        os.makedirs(output_dir, exist_ok=True)
        
        if not self._check_ffmpeg():
            print("[Downloader Error] FFmpeg is required for audio conversion.")
            print("[Downloader] Please configure FFmpeg path using option 'd' in main menu.")
            return False
        
        print("Choose download mode:")
        print("1. Single track")
        print("2. Entire playlist/album")
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == '2':
            entries = self._resolve_playlist(url)
        else:
            entries = [url]
        
        if not entries:
            print("[Downloader Error] No tracks found.")
            return False
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
            'ffmpeg_location': self.settings.ffmpeg_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [ProgressDisplay.create_hook("Music")],
            'extract_flat': False,
            'noplaylist': True,
        }
        
        failed_count = 0
        total_count = len(entries)
        print(f"\n[Downloader] Starting download of {total_count} track(s)...")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for i, entry_url in enumerate(entries, 1):
                try:
                    print(f"\n\n[{i}/{total_count}] Processing: {entry_url}")
                    ydl.download([entry_url])
                except Exception as e:
                    print(f"\n[Downloader Error] Failed to download #{i}: {str(e)}")
                    failed_count += 1
        
        print(f"\n[Downloader] Audio extraction completed. {failed_count}/{total_count} tracks failed.")
        return True
    
    def _resolve_playlist(self, url):
        ydl_opts_probe = {
            'quiet': True,
            'extract_flat': True,
            'noplaylist': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts_probe) as ydl:
                info = ydl.extract_info(url, download=False)
                if info.get('_type') == 'playlist' or info.get('playlist_count'):
                    playlist_title = info.get('title', 'Playlist')
                    video_count = info.get('playlist_count', len(info.get('entries', [])))
                    print(f"Found playlist: '{playlist_title}' | {video_count} tracks")
                    entries = []
                    for entry in info['entries']:
                        if entry:
                            if 'url' in entry:
                                entries.append(entry['url'])
                            elif 'webpage_url' in entry:
                                entries.append(entry['webpage_url'])
                    return entries
                else:
                    print("[Downloader] Single track detected.")
                    return [url]
        except Exception as e:
            print(f"[Downloader Error] Could not analyze URL: {str(e)}")
            return [url]

class Menu:
    def __init__(self, settings):
        self.settings = settings
        self.downloader = Downloader(settings)
    
    def run(self):
        self._ensure_settings()
        while True:
            self._display_main_menu()
            choice = input("Enter choice: ").strip().lower()
            
            if choice == '1':
                self._handle_video_download()
            elif choice == '2':
                self._handle_audio_download()
            elif choice == 'd':
                self._handle_change_directories()
            elif choice == 'u':
                self._run_updater()
            elif choice == 'q':
                print("Exiting UltraDownloader. Goodbye!")
                sys.exit(0)
            else:
                print("[System] Invalid choice. Please try again.")
    
    def _ensure_settings(self):
        if not self.settings.save_dir:
            print("[System] Download directory not set.")
            self._set_save_dir()
        
        if not self.settings.ffmpeg_path:
            self._prompt_ffmpeg()
    
    def _prompt_ffmpeg(self):
        print("\n[Settings] FFmpeg is required for audio conversion and video processing.")
        print("Would you like to specify the FFmpeg directory now?")
        print("1. Yes, select ffmpeg.exe")
        print("2. Skip (you can set it later from the menu)")
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == '1':
            self._set_ffmpeg_path()
        else:
            print("[Settings] FFmpeg path skipped. You can set it later using option 'd' in main menu.")
    
    def _display_main_menu(self):
        print(f"\nUltraDownloader {self.settings.version_tag}")
        print("--------------")
        ffmpeg_status = "Not set" if not self.settings.ffmpeg_path else "Set"
        print(f"ffmpeg_dir: {self.settings.ffmpeg_path if self.settings.ffmpeg_path else 'Not set'}")
        print(f"save_dir: {self.settings.save_dir}")
        print("--------------")
        print("1. Download Video")
        print("2. Download Music")
        print("d. Change directories")
        print("u. Check for updates")
        print("q. Quit")
    
    def _handle_video_download(self):
        url = input("Enter Video URL: ").strip()
        if url:
            self.downloader.download_video(url)
    
    def _handle_audio_download(self):
        url = input("Enter Music URL: ").strip()
        if url:
            self.downloader.download_audio(url)
    
    def _handle_change_directories(self):
        while True:
            print("\n--------------")
            print("1. Change FFMPEG Directory")
            print("2. Change Download Directory")
            print("q. Back to main menu")
            print("--------------")
            choice = input("Enter choice: ").strip().lower()
            
            if choice == '1':
                self._set_ffmpeg_path()
            elif choice == '2':
                self._set_save_dir()
            elif choice == 'q':
                break
            else:
                print("[System] Invalid choice.")
    
    def _run_updater(self):
        updater_path = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__)), "AutoUpdater.exe")
        
        if not os.path.exists(updater_path):
            print(f"[System] Updater not found at: {updater_path}")
            return
        
        print("[System] Launching updater...")
        try:
            subprocess.Popen([updater_path])
            print("[System] Updater launched. Close this application to complete the update.")
        except Exception as e:
            print(f"[System Error] Failed to launch updater: {e}")
    
    def _set_ffmpeg_path(self):
        print("[Settings] Select ffmpeg.exe in the file dialog...")
        print("[Settings] If you want to skip, close the file dialog without selecting.")
        
        try:
            path = filedialog.askopenfilename(
                parent=root,
                title="Select ffmpeg.exe",
                filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
            )
            if path:
                if os.path.exists(path) and os.path.isfile(path):
                    self.settings.ffmpeg_path = path
                    self.settings.save()
                    print(f"[Settings] FFMPEG path updated: {path}")
                else:
                    print("[Settings] Invalid file selected. Path not changed.")
            else:
                print("[Settings] FFMPEG path not changed.")
        except Exception as e:
            print(f"[Settings Error] Failed to open file dialog: {e}")
            print("[Settings] You can set FFMPEG path later using option 'd' in main menu.")
    
    def _set_save_dir(self):
        print("[Settings] Select download directory in the folder dialog...")
        print("[Settings] If you want to skip, close the folder dialog without selecting.")
        
        try:
            path = filedialog.askdirectory(
                parent=root,
                title="Select Download Folder"
            )
            if path:
                self.settings.save_dir = path
                self.settings.save()
                print(f"[Settings] Download directory updated: {path}")
            else:
                print("[Settings] Download directory not changed.")
        except Exception as e:
            print(f"[Settings Error] Failed to open folder dialog: {e}")
            print("[Settings] You can set download directory later using option 'd' in main menu.")

if __name__ == "__main__":
    settings = Settings()
    settings.load()
    
    menu = Menu(settings)
    menu.run()