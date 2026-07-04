import yt_dlp
import json
import os
import tkinter as tk
import sys
import subprocess
from tkinter import filedialog

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
    
    def load(self):
        default_config = {
            "save_dir": "",
            "ffmpeg_path": "",
            "repo_owner": "Ve1var",
            "repo_name": "UltraDownloader",
            "version_tag": "v1.0.5",
            "asset_name": "UltraDownloader.zip"
        }
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = default_config
            self.is_first_run = True
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        
        self.save_dir = config.get("save_dir", default_config["save_dir"])
        self.ffmpeg_path = config.get("ffmpeg_path", default_config["ffmpeg_path"])
        self.repo_owner = config.get("repo_owner", default_config["repo_owner"])
        self.repo_name = config.get("repo_name", default_config["repo_name"])
        self.version_tag = config.get("version_tag", default_config["version_tag"])
        self.asset_name = config.get("asset_name", default_config["asset_name"])
    
    def save(self):
        config = {
            "save_dir": self.save_dir,
            "ffmpeg_path": self.ffmpeg_path,
            "repo_owner": self.repo_owner,
            "repo_name": self.repo_name,
            "version_tag": self.version_tag,
            "asset_name": self.asset_name
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

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
    
    def download_video(self, url):
        if not LinkChecker.is_allowed(url):
            print("[Downloader Error] Link unsupported")
            return False
        
        output_dir = os.path.join(self.settings.save_dir, "UD_Downloaded", "Video")
        os.makedirs(output_dir, exist_ok=True)
        
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
            'format': 'best[ext=mp4]/best',
            'quiet': False,
            'no_warnings': True,
            'ffmpeg_location': self.settings.ffmpeg_path,
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
                    return [entry['url'] for entry in info['entries'] if entry]
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
    
    def _display_main_menu(self):
        print(f"\nUltraDownloader {self.settings.version_tag}")
        print("--------------")
        print(f"ffmpeg_dir: {self.settings.ffmpeg_path if self.settings.ffmpeg_path else 'Not set (optional)'}")
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
        path = filedialog.askopenfilename(
            parent=root,
            title="Select ffmpeg.exe",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if path:
            self.settings.ffmpeg_path = path
            self.settings.save()
            print("[Settings] FFMPEG path updated.")
    
    def _set_save_dir(self):
        print("[Settings] Select download directory in the folder dialog...")
        path = filedialog.askdirectory(
            parent=root,
            title="Select Download Folder"
        )
        if path:
            self.settings.save_dir = path
            self.settings.save()
            print("[Settings] Download directory updated.")

if __name__ == "__main__":
    settings = Settings()
    settings.load()
    
    menu = Menu(settings)
    menu.run()