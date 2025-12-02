import yt_dlp
import json
import os
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

CONFIG_FILE = "app_config.json"
DEFAULT_DIR = ""
DEFAULT_FFMPEG = ""


def load_setting():
    config_dir = os.path.dirname(CONFIG_FILE)
    if config_dir and not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        saved_dir = data.get("dir", DEFAULT_DIR)
        saved_ffmpeg = data.get("ffmpeg_dir", DEFAULT_FFMPEG)

        save_dir = saved_dir if os.path.exists(saved_dir) else DEFAULT_DIR

        ffmpeg_path = saved_ffmpeg if os.path.exists(saved_ffmpeg) else None
        if not ffmpeg_path:
            print("ffmpeg.exe not found at the saved path.")
            print("Make sure the path is correct or set a new one.")

        return save_dir, ffmpeg_path

    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Config file not found or corrupted. Creating default at {os.path.abspath(CONFIG_FILE)}")
        default_config = {
            "dir": DEFAULT_DIR,
            "ffmpeg_dir": DEFAULT_FFMPEG
        }
        config_dir = os.path.dirname(CONFIG_FILE)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        return DEFAULT_DIR, None


def save_setting(new_dir=None, new_ffmpeg=None):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    if new_dir:
        data["dir"] = new_dir
        os.makedirs(new_dir, exist_ok=True)
        print(f"Directory saved: {new_dir}")

    if new_ffmpeg:
        if os.path.exists(new_ffmpeg) and os.path.isfile(new_ffmpeg):
            data["ffmpeg_dir"] = new_ffmpeg
            print(f"FFmpeg path saved: {new_ffmpeg}")
        else:
            print("Invalid FFmpeg path. File does not exist.")
            return False

    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return True


def main_menu(save_dir, ffmpeg_path):
    os.system("color 6")
    print("\n" + "="*50)
    print("\nWelcome to UltraDownloader!")
    print("\n" + "="*50)
    print(f"Save directory: {save_dir}")
    print(f"FFmpeg: {ffmpeg_path or 'Not set'}")
    print("="*50)
    print("Select a service:")
    print("1. VK Video")
    print("2. YouTube Video/Music")
    print("3. Music (exc VK music)")
    print("d. Change Download Directory")
    print("p. Set FFmpeg Path")
    print("q. Exit")
    print("="*50)

    choice = input("Enter choice: ").strip().lower()

    action = {
        "1": lambda: VK_video(save_dir, ffmpeg_path),
        "2": lambda: YT(save_dir, ffmpeg_path),
        "3": lambda: Music(save_dir, ffmpeg_path),
        "d": lambda: dir_change(save_dir, ffmpeg_path),
        "p": lambda: set_ffmpeg_path(save_dir, ffmpeg_path),
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
        main_menu(save_dir, ffmpeg_path)


def yt_download_video(url, save_dir, service_name, ffmpeg_path):
    if not url.strip():
        print("No URL provided.")
        return

    base_download_dir = os.path.join(save_dir, "UD_Downloaded")
    service_dir = os.path.join(base_download_dir, service_name)
    os.makedirs(service_dir, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(service_dir, '%(title)s.%(ext)s'),
        'format': 'best[ext=mp4]/best',
        'quiet': False,
        'no_warnings': True,
        'ffmpeg_location': ffmpeg_path,
        'noplaylist': True,
        'extract_flat': False,
        'progress_hooks': [lambda d: update_progress(d, service_name)]
    }


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\nVideo downloaded.")
    except Exception as e:
        print(f"\nError: {str(e)}")

    main_menu(save_dir, ffmpeg_path)


def yt_download_music(url, save_dir, service_name, ffmpeg_path):
    if not url.strip():
        print("No URL provided.")
        return

    print("Choose download mode:")
    print("1. Only this track")
    print("2. Entire playlist/album")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice not in ['1', '2']:
        print("Invalid choice. Defaulting to 'only this track'.")
        choice = '1'

    base_download_dir = os.path.join(save_dir, "UD_Downloaded")
    music_dir = os.path.join(base_download_dir, service_name)
    os.makedirs(music_dir, exist_ok=True)

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
            else:
                print("Single track detected.")
        except Exception as e:
            print(f"Could not analyze URL: {str(e)}")

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
        'progress_hooks': [lambda d: update_progress(d, f"{service_name} Music")],
        'extract_flat': False,
        'noplaylist': (choice == '1'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\nAudio extraction completed.")
    except Exception as e:
        print(f"\nError during download: {str(e)}")

    main_menu(save_dir, ffmpeg_path)


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

def VK_video(save_dir, ffmpeg_path):
    url = input("Enter VK video URL:\n--> ")
    yt_download_video(url, save_dir, "Video", ffmpeg_path)

def YT(save_dir, ffmpeg_path):
    choice = input("1. Video\n2. Music\n--> ")
    url = input("Enter YouTube URL:\n--> ")

    action = {
        "1": lambda: yt_download_video(url, save_dir, "Video", ffmpeg_path),
        "2": lambda: yt_download_music(url, save_dir, "Music", ffmpeg_path)
    }
    func = action.get(choice)
    if func:
        if choice != "q":
            func()
        else:
            func()
    else:
        print("Invalid choice. Please try again.")
        main_menu(save_dir, ffmpeg_path)

def Music(save_dir, ffmpeg_path):
    url = input("Enter Music URL:\n--> ")
    yt_download_music(url, save_dir, "Music", ffmpeg_path)

def set_ffmpeg_path(save_dir, ffmpeg_path):
    print("Select ffmpeg.exe in the file dialog...")
    new_ffmpeg = filedialog.askopenfilename(
        title="Select ffmpeg.exe",
        filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
    )

    if not new_ffmpeg:
        print("No file selected.")
        main_menu(save_dir, ffmpeg_path)
        return

    success = save_setting(new_ffmpeg=new_ffmpeg)
    if success:
        _, updated_ffmpeg = load_setting()
        print("Restarting menu with new FFmpeg path...")
        main_menu(save_dir, updated_ffmpeg)
    else:
        main_menu(save_dir, ffmpeg_path)

def dir_change(save_dir, ffmpeg_path):
    print("Select download directory in the folder dialog...")
    new_dir = filedialog.askdirectory(
        title="Select Download Folder",
        initialdir=save_dir
    )

    if not new_dir:
        print("No directory selected.")
        main_menu(save_dir, ffmpeg_path)
        return

    if new_dir != save_dir:
        save_setting(new_dir=new_dir)
        print(f"Directory changed to: {new_dir}")
        main_menu(new_dir, ffmpeg_path)
    else:
        print("Directory is already set to this path.")
        main_menu(save_dir, ffmpeg_path)


def main():
    save_dir, ffmpeg_path = load_setting()
    if not ffmpeg_path:
        print("FFmpeg not found. Please select ffmpeg.exe in the dialog.")
        set_ffmpeg_path(save_dir, ffmpeg_path)
    elif not save_dir:
        print("Select main dir")
        dir_change(save_dir, ffmpeg_path)
    else:
        main_menu(save_dir, ffmpeg_path)


if __name__ == "__main__":
    main()
