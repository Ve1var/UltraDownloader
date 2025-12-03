# UltraDownloader 🚀

A powerful, user-friendly media downloader application for Windows that supports downloading videos and music from multiple platforms including YouTube, VK, and other music services.

## 📥 Download Latest Version

**[Download UltraDownloader.exe](https://example.com/UltraDownloader.exe)** (Replace with actual download link)

## ✨ Features

### 📹 Video Downloading
- **YouTube**: Download videos in MP4 format with best available quality
- **VK Video**: Support for VK (VKontakte) video content
- **Automatic organization**: Downloads are sorted into organized folders

### 🎵 Music/Audio Downloading
- **YouTube Music**: Download individual tracks or entire playlists
- **Multi-platform music support**: Works with various music platforms (excluding VK music)
- **MP3 conversion**: Automatically converts audio to high-quality MP3 format (192kbps)

### ⚙️ Smart Configuration
- **Persistent settings**: Saves download directory and FFmpeg path between sessions
- **First-run setup**: Guided configuration on first launch
- **Windows AppData integration**: Stores configuration in `%APPDATA%\UltraDownloader\`

### 🎯 User Experience
- **Real-time progress bars**: Visual download progress with speed indicators
- **File size display**: Shows download size in MB during transfer
- **Intuitive menu system**: Easy navigation through numbered options
- **Error handling**: Clear error messages and recovery options

## 🚀 Installation & Setup

### System Requirements
- **Windows** 10 or later
- **FFmpeg**
- **Internet connection**

### First-Time Setup
1. **Download** the `UltraDownloader.exe` file
2. **Run** the executable (no installation required)
3. **Follow the setup prompts**:
   - Select your preferred download directory
   - Set FFmpeg path for audio conversion

### FFmpeg Setup
For audio conversion features:
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/)
2. Extract to a folder
3. In UltraDownloader, select option `p` to set the path to `ffmpeg.exe`

## 📖 How to Use

### Main Menu Options

```cmd
==================================================

Welcome to UltraDownloader!

==================================================
Save directory: C:\Users\YourName\Downloads
FFmpeg: C:\ffmpeg\bin\ffmpeg.exe
==================================================
Select a service:
1. VK Video
2. YouTube Video/Music
3. Music (exc VK music)
d. Change Download Directory
p. Set FFmpeg Path
q. Exit
==================================================
```

### Downloading Videos
1. Select option `1` for VK or `2` for YouTube
2. Choose Video or Music
3. Paste the video URL when prompted
4. Watch the progress bar and wait for completion

### Downloading Music
1. Select option `2` (YouTube) or `3` (Other music)
2. Choose download mode:
   - `1`: Single track only
   - `2`: Entire playlist/album
3. Paste the music URL
4. Audio will be converted to MP3 automatically

## 📁 File Organization

All downloads are saved in a structured format:

```FileOrganization
Your_Selected_Directory/
└── UD_Downloaded/
├── Video/
│ ├── YouTube Video Title.mp4
│ └── VK Video Title.mp4
└── Music/
├── Song Title.mp3
└── Playlist_Name/
├── Track 1.mp3
├── Track 2.mp3
└── ...
```

## ⚠️ Important Notes

### Legal Considerations
- Only download content you have permission to download
- Respect copyright laws and terms of service
- This tool is for personal use only

### Limitations
- VK music is not supported
- Some platforms may have download restrictions
- Playlist downloading depends on source platform support

### Troubleshooting

#### "ffmpeg.exe not found"
- Set FFmpeg path using option `p` in the main menu
- Or download FFmpeg from the official website

#### Download fails
- Check your internet connection
- Verify the URL is correct and accessible
- Ensure you have write permissions in the download directory

#### Progress bar issues
- The terminal window must remain open during downloads
- Do not resize the terminal window while downloading

## 🔧 Technical Details

- **Built with**: Python, yt-dlp, Tkinter
- **Configuration**: JSON-based in `%APPDATA%\UltraDownloader\app_config.json`
- **Dependencies**: FFmpeg
- **Platform**: Windows (standalone EXE)

## 🤝 Contributing

While this is a pre-compiled executable, you can:
1. Report bugs or issues
2. Suggest new features
3. Request support for additional platforms

## 📄 License

This software is provided as-is for personal use. Users are responsible for complying with all applicable laws and terms of service when downloading content.

## 📞 Support

For issues, questions, or suggestions:
- Check the troubleshooting section above
- Ensure you're using the latest version
- Verify your URLs and internet connection

---

**Enjoy downloading with UltraDownloader!** 🎉

*Note: Always respect content creators and copyright holders when downloading media.*