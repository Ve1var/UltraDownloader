import yt_dlp
import json
import os
import tkinter as tk
from tkinter import filedialog

APP_NAME = "UltraDownloader"
APP_DATA = os.getenv('APPDATA')
SETTINGS_DIR = os.path.join(APP_DATA, APP_NAME)
CONFIG_FILE = os.path.join(SETTINGS_DIR, "app_config.json")
DETECTER_FILE = os.path.join(SETTINGS_DIR, "detecter.json") #not use btw

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
    
    def load(self):
        try:
            with open(DETECTER_FILE, 'r', encoding='utf-8') as f:
                self.detecter_links = json.load(f)
        
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"[System Error] Detecter file not found or corrupted. Creating default at {DETECTER_FILE}")
            default_detect = "test"
            with open(DETECTER_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_detect, f, indent=4, ensure_ascii=False)

        finally:
            print("[System] Detecter file completly load")
            
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
            print("[System] Config file completly load")
        
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
        print("\nUltraDownloader v1.0.1a")
        print("--------------")
        print(f"ffmpeg_dir: {settings.ffmpeg_path}")
        print(f"save_dir: {settings.save_dir}")
        print("--------------")
        print("1. Download Video")
        print("2. Download Music")
        print("d. Change directory")
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
                func()
        else:
            print("Invalid choice. Please try again.")
            self.main_menu()
    
    def check_settings(self):
        if settings.save_dir == "" or settings.ffmpeg_path == "":
            print("Directory not set. Please set the directory first.")
            self.set_dirs()
        else:
            self.main_menu()

    def change_dir(self):
        try:
            print("Select download directory in the folder dialog...")
            new_dir = filedialog.askdirectory(
                parent=root,
                title="Select Download Folder",
            )
            settings.save_setting(new_dir=new_dir)
        except:
            new_dir = None

        finally:
            self.main_menu()

    def set_dirs(self):
        if(settings.ffmpeg_path == ""):
            try:
                print("Select ffmpeg.exe in the file dialog...")
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
                print("Select download directory in the folder dialog...")
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
    def yt_download_video(self, save_dir, ffmpeg_path):
        url = input("Enter Video URL: ").strip()
        
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
            print("\nVideo downloaded.")
        except Exception as e:
            print(f"\nError: {str(e)}")
            pass

        UltraDownloader.main_menu(self=None)
    
    def yt_download_music(self, save_dir, ffmpeg_path):
        url = input("Enter Music URL: ").strip()
        
        base_download_dir = os.path.join(save_dir, "UD_Downloaded")
        music_dir = os.path.join(base_download_dir, "Music")
        os.makedirs(music_dir, exist_ok=True)

        print("Choose download mode:")
        print("1. Only this track")
        print("2. Entire playlist/album")
        choice = input("Enter choice (1 or 2): ").strip()

        if choice not in ['1', '2']:
            print("Invalid choice. Defaulting to 'only this track'.")
            choice = '1'

        # Опции для проверки типа ссылки
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
                    print("Single track detected.")
                    entries = [url]
            except Exception as e:
                print(f"Could not analyze URL: {str(e)}")
                entries = [url]

        # Общие опции для скачивания аудио
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
            'noplaylist': True,  # Обрабатываем вручную!
        }

        # Скачивание каждого трека отдельно
        failed_count = 0
        total_count = len(entries)
        print(f"\nStarting download of {total_count} track(s)...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for i, entry_url in enumerate(entries, 1):
                try:
                    print(f"\n\n[{i}/{total_count}] Processing: {entry_url}")
                    ydl.download([entry_url])
                except Exception as e:
                    print(f"\n[Error] Failed to download #{i}: {str(e)}")
                    failed_count += 1
                    continue  # Пропускаем и идём к следующему

        print(f"\nAudio extraction completed. {failed_count}/{total_count} tracks failed.")
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
            print("\rDownload completed.")

if __name__ == "__main__":
    settings = settings()
    settings.load()
    UltraDownloader().check_settings()