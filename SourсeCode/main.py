import yt_dlp
import json
import os
import tkinter as tk
import requests
import sys
from tkinter import filedialog
from pathlib import Path

APP_NAME = "UltraDownloader"
APP_DATA = os.getenv('APPDATA')
SETTINGS_DIR = os.path.join(APP_DATA, APP_NAME)
CONFIG_FILE = os.path.join(SETTINGS_DIR, "app_config.json")
CHECKER_FILE = os.path.join(SETTINGS_DIR, "checker.json")

DEFAULT_DIR = ""
DEFAULT_FFMPEG = ""
detecter_links = []

os.makedirs(SETTINGS_DIR, exist_ok=True)

def create_tk_root():
    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry("0x0+0+0")
    root.attributes("-alpha", 0)
    return root

root = create_tk_root()

class settings:
    def __init__(self):
        self.save_dir = ""
        self.ffmpeg_path = ""
        self.detecter_links = []
        
    def check_updates(self, owner, repo, current_version, asset_name):
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        response = requests.get(url)
        
        if response.status_code != 200:
            print("[Updater] Failed to check for updates.")
            return None

        data = response.json()
        latest_version = data['tag_name']
        
        if current_version == latest_version:
            print("[Updater] You are using the latest version.")
            return None
        else:
            answer = input("New version available [y/n] (default 'y'): ").strip().lower()
            if answer == "n":
                return
            else:
                assets = data.get("assets", [])
                target_asset = None

                for asset in assets:
                    if asset["name"] == asset_name:
                        target_asset = asset
                        break

                if not target_asset:
                    print(f"[Updater Error] Asset {asset_name} not found.")
                    return

                download_url = target_asset["browser_download_url"]
                DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads")
                save_path = os.path.join(DOWNLOADS_DIR, asset_name)                
                print(f"[Updater] Downloading {asset_name}...")

                try:
                    with requests.get(download_url, stream=True) as r:
                        r.raise_for_status()
                        with open(save_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    print(f"[Updater] Download complete: {save_path}")
                    UltraDownloader().main_menu()
                except Exception as e:
                    print(f"[Updater Error] Download error: {e}")
    
    def load(self):
        self.detecter_links = ["youtube", "youtu", "vk"]
        global detecter_links
        detecter_links = self.detecter_links[:]

        try:
            with open(CHECKER_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.detecter_links, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[System Error] Could not write default checker: {e}")

        print("[System] Detecter file loaded (YouTube & VK only)")

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.save_dir = config.get("dir", DEFAULT_DIR)
                self.ffmpeg_path = config.get("ffmpeg_dir", DEFAULT_FFMPEG)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"[System Error] Config file not found or corrupted. Creating default at {CONFIG_FILE}")
            default_config = {"dir": DEFAULT_DIR, "ffmpeg_dir": DEFAULT_FFMPEG}
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
        finally:
            print("[System] Config file completely loaded")

    def save_setting(self, new_dir=None, new_ffmpeg=None):
        try:
            if new_dir:
                self.save_dir = new_dir
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump({"dir": new_dir, "ffmpeg_dir": self.ffmpeg_path}, f, indent=4, ensure_ascii=False)
            if new_ffmpeg:
                self.ffmpeg_path = new_ffmpeg
                with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump({"ffmpeg_dir": new_ffmpeg, "dir": self.save_dir}, f, indent=4, ensure_ascii=False)
        
        finally:
            print("[System] Config file completly saved")

class UltraDownloader:
    def main_menu(self):
        print(f"\nUltraDownloader {current_version}")
        print("--------------")
        print(f"ffmpeg_dir: {settings.ffmpeg_path}")
        print(f"save_dir: {settings.save_dir}")
        print("--------------")
        print("1. Download Video")
        print("2. Download Music")
        print("d. Change directories")
        print("q. Quit")
        choice = input("Enter choice: ").strip().lower()

        action = {
            "1": lambda: yt_downloader.yt_download_video(self=None, save_dir=settings.save_dir, ffmpeg_path=settings.ffmpeg_path),
            "2": lambda: yt_downloader.yt_download_music(self=None, save_dir=settings.save_dir, ffmpeg_path=settings.ffmpeg_path),
            "d": lambda: self.change_dir(),
            "q": lambda: print("Exiting UltraDownloader. Goodbye!")
        }

        func = action.get(choice)
        if func:
            if choice != "q":
                func()
            else:
                print("Exiting UltraDownloader. Goodbye!")
                sys.exit()
        else:
            print("[System] Invalid choice. Please try again.")
            self.main_menu()
    
    def check_settings(self):
        if settings.save_dir == "" or settings.ffmpeg_path == "":
            print("[System] Directory not set. Please set the directory first.")
            self.set_dirs()
        else:
            self.main_menu()

    def change_dir(self):
        print("\n--------------")
        print("1. Change FFMPEG Directory")
        print("2. Change Download Directory")
        print("q. Back to main menu")
        print("--------------")
        choice = input("Enter choice: ").strip().lower()
        action = {
            "1": lambda: self.dir(ffmpeg_path="1", save_dir=""),
            "2": lambda: self.dir(ffmpeg_path="", save_dir="1"),
            "q": lambda: self.main_menu()
        }
        try:
            func = action.get(choice)
            if func:
                if choice != "q":
                    func()
            else:
                func()
            self.main_menu()
        except:
            print("Error")

        finally:
            self.main_menu()

    def dir(self, ffmpeg_path, save_dir):
        if(ffmpeg_path != ""):
            new_ffmpeg = filedialog.askopenfilename(
                    parent=root,
                    title="Select ffmpeg.exe",
                    filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
            )
            settings.save_setting(new_ffmpeg=new_ffmpeg)
        
        elif(save_dir != ""):
            new_dir = filedialog.askdirectory(
                    parent=root,
                    title="Select Download Folder",
            )
            settings.save_setting(new_dir=new_dir)
        
        self.main_menu()

    def set_dirs(self):
        if(settings.ffmpeg_path == ""):
            try:
                print("[Dir Setter] Select ffmpeg.exe in the file dialog...")
                new_ffmpeg = filedialog.askopenfilename(
                    parent=root,
                    title="Select ffmpeg.exe",
                    filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
                )
                settings.save_setting(new_ffmpeg=new_ffmpeg)
            except:
                new_ffmpeg = None
        else:
            pass
        
        if(settings.save_dir == ""):
            try:
                print("[Dir Setter] Select download directory in the folder dialog...")
                new_dir = filedialog.askdirectory(
                    parent=root,
                    title="Select Download Folder",
                )
                settings.save_setting(new_dir=new_dir)
            except:
                new_dir = None
        else:
            pass

        self.main_menu()
    
class yt_downloader:
    def link_check(self, url):
        allowed_domains = [
            'youtube.com', 
            'youtu.be', 
            'vk.com'
        ]
        url_lower = url.lower()
        return any(domain in url_lower for domain in allowed_domains)

    def yt_download_video(self, save_dir, ffmpeg_path):
        url = input("Enter Video URL: ").strip()
        
        if yt_downloader().link_check(url):
            pass
        else:
            print("[Downloader Error] Link unsoported")
            UltraDownloader().main_menu()
        
        base_download_dir = os.path.join(save_dir, "UD_Downloaded")
        service_dir = os.path.join(base_download_dir, "Video")
        os.makedirs(service_dir, exist_ok=True)

        ydl_opts = {
            'outtmpl': os.path.join(service_dir, '%(title)s.%(ext)s'),
            'format': 'best[ext=mp4]/best',
            'quiet': False,
            'no_warnings': True,
            'ffmpeg_location': ffmpeg_path,
            'noplaylist': True,
            'extract_flat': False,
            'progress_hooks': [lambda d: yt_downloader.update_progress(d, "Video")]
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n[Downloader] Video downloaded.")
        except Exception as e:
            print(f"\n[Downloader Error] Error: {str(e)}")

        UltraDownloader.main_menu(self=None)
    
    def yt_download_music(self, save_dir, ffmpeg_path):
        url = input("Enter Music URL: ").strip()

        if yt_downloader().link_check(url):
            pass
        else:
            print("[Downloader Error] Link unsoported")
            UltraDownloader().main_menu()
        
        base_download_dir = os.path.join(save_dir, "UD_Downloaded")
        music_dir = os.path.join(base_download_dir, "Music")
        os.makedirs(music_dir, exist_ok=True)

        print("Choose download mode:")
        print("1. Only this track")
        print("2. Entire playlist/album")
        choice = input("Enter choice (1 or 2): ").strip()

        if choice not in ['1', '2']:
            print("[System] Invalid choice. Defaulting to 'only this track'.")
            choice = '1'

        ydl_opts_probe = {
            'quiet': True,
            'extract_flat': True,
            'noplaylist': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts_probe) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if info.get('_type') == 'playlist' or info.get('playlist_count'):
                    playlist_title = info.get('title', 'Playlist')
                    video_count = info.get('playlist_count', len(info.get('entries', [])))
                    print(f"Found playlist: '{playlist_title}' | {video_count} tracks")
                    entries = [entry['url'] for entry in info['entries'] if entry]
                else:
                    print("[Downloader] Single track detected.")
                    entries = [url]
            except Exception as e:
                print(f"[Downloader Error] Could not analyze URL: {str(e)}")
                entries = [url]

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(music_dir, '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
            'ffmpeg_location': ffmpeg_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [lambda d: yt_downloader.update_progress(d, "Music")],
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
                    continue

        print(f"\n[Downloader] Audio extraction completed. {failed_count}/{total_count} tracks failed.")
        UltraDownloader.main_menu(self=None)


    def update_progress(d, service_name):
        bar_length = 10
        terminal_width = 100

        if d['status'] == 'downloading':
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

        elif d['status'] == 'finished':
            print("\r" + " " * terminal_width, end="", flush=True)
            print("\r[Downloader] Download completed.")

if __name__ == "__main__":
    owner = "Ve1var"
    repo = "UltraDownloader"
    current_version = "v1.0.4"
    asset_name = "UltraDownloader.zip"

    settings = settings()
    settings.load()
    settings.check_updates(owner, repo, current_version, asset_name)
    UltraDownloader().check_settings()