# UltraDownloader 🚀 [EN]

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

## 📄 License

MIT License — free use and modification of the code

**Enjoy downloading with UltraDownloader!** 🎉

*Note: Always respect content creators and copyright holders when downloading media.*


**=============================================================**


# UltraDownloader 🚀 [RU]

Мощное и удобное приложение для загрузки мультимедиа для Windows, которое поддерживает загрузку видео и музыки с нескольких платформ, включая YouTube, VK и другие музыкальные сервисы.

## 📥 Скачать последнюю версию

**[Скачать UltraDownloader.exe](https://example.com/UltraDownloader.exe)** (Заменить на актуальную ссылку для скачивания)

## ✨ Особенности

### 📹 Загрузка видео
- **YouTube**: Загрузка видео в формате MP4 с наилучшим доступным качеством
- **VK Video**: Поддержка видеоконтента VK (ВКонтакте)
- **Автоматическая организация**: Загрузки сортируются по организованным папкам

### 🎵 Загрузка музыки/аудио
- **YouTube Music**: Загрузка отдельных треков или целых плейлистов
- **Поддержка мультиплатформенной музыки**: Работает с различными музыкальными платформами (за исключением VK music).
- **Преобразование MP3**: Автоматически преобразует аудио в высококачественный формат MP3 (192 Кбит/с)

### ⚙️ Интеллектуальная настройка
- **Постоянные настройки**: Сохраняет каталог загрузки и путь к FFmpeg между сеансами.
- **Настройка при первом запуске**: Управляемая настройка при первом запуске
- **Интеграция с Windows AppData**: Сохраняет конфигурацию в `%APPDATA%\UltraDownloader\`

### 🎯 Удобство работы с пользователем
- ** Индикаторы выполнения в реальном времени **: Визуальный ход загрузки с индикаторами скорости
- **Отображение размера файла**: Показывает размер загружаемого файла в МБ во время передачи
- **Интуитивно понятная система меню**: Простая навигация по пронумерованным параметрам
- **Обработка ошибок**: Четкие сообщения об ошибках и варианты восстановления

## 🚀 Установка и настройка

### Системные требования
- **Windows** 10 или более поздней версии
- **FFmpeg**
- **Подключение к Интернету**

### Настройка при первом запуске
1. **Загрузите** файл `UltraDownloader.exe`
2. **Запустите** исполняемый файл (установка не требуется)
3. **Следуйте инструкциям по установке**:
   - Выберите предпочитаемый каталог загрузки
   - Укажите путь к файлу FFmpeg для преобразования аудио

### Настройка FFmpeg
Для функций преобразования аудио:
1. Загрузите FFmpeg из [ffmpeg.org](https://ffmpeg.org/)
2. Извлеките файл в папку
3. В UltraDownloader выберите опцию `p`, чтобы указать путь к `ffmpeg.exe`

## 📖 как использовать

### Пункты главного меню

```cmd
==================================================

Добро пожаловать в UltraDownloader!

==================================================
Сохранить каталог: C:\Users\YourName\Downloads
FFmpeg: C:\ffmpeg\bin\ffmpeg.exe
==================================================
Выберите сервис:
1. Видео из ВКонтакте
2. Видео/Музыка с YouTube
3. Музыка (кроме музыки из ВКОНТАКТЕ)
d. Измените каталог загрузки
p. Задайте путь к файлу FFmpeg
q. Выйдите
==================================================
```

### Загрузка видео
1. Выберите опцию `1` для VK или `2` для YouTube
2. Выберите Видео или музыку
3. Вставьте URL-адрес видео при появлении запроса
4. Следите за индикатором выполнения и дождитесь завершения

### Загрузка музыки
1. Выберите опцию `2` (YouTube) или `3` (Другая музыка).
2. Выберите режим загрузки:
   - `1`: только один трек
   - `2`: Весь список воспроизведения/альбом
3. Вставьте URL-адрес музыки
4. Аудио будет автоматически преобразовано в MP3

## 📁 Организация файлов

Все загруженные файлы сохраняются в структурированном формате:

```FileOrganization
ваш_выбранный_директорий/
└── UD_Downloaded/
├── Видео/
│ ├── Название видео на YouTube.mp4
│ └── Название видео на VK.mp4
└── Музыка/
├── Название песни.mp3
└── Название плейлиста/
├── Трек 1.mp3
├── Трек 2.mp3
└── ...
```

## ❗️ Важные замечания

### Юридические соображения
- Загружайте только тот контент, на который у вас есть разрешение
- Соблюдайте законы об авторском праве и условия предоставления услуг
- Этот инструмент предназначен только для личного использования

### Ограничения
- Музыка ВКОНТАКТЕ не поддерживается
- На некоторых платформах могут быть ограничения на загрузку
- Загрузка плейлистов зависит от поддержки исходной платформы

### Устранение неполадок

#### "ffmpeg.exe не найдено"
- Укажите путь к файлу FFmpeg, используя опцию `p` в главном меню
- Или загрузите файл FFmpeg с официального веб-сайта

#### Ошибка загрузки
- Проверьте подключение к Интернету
- Убедитесь, что URL указан правильно и доступен
- Убедитесь, что у вас есть разрешения на запись в каталог загрузки

#### Проблемы с индикатором выполнения
- Окно терминала должно оставаться открытым во время загрузки
- Не изменяйте размер окна терминала во время загрузки

## 🔧 Технические подробности

- **Создано с использованием**: Python, yt-dlp, Tkinter
- **Конфигурация**: на основе JSON в `%APPDATA%\UltraDownloader\app_config.json`
- **Зависимости**: FFmpeg
- **Платформа**: Windows (автономный исполняемый файл)

## 📄 Лицензия

Использование и модификация кода без лицензии MIT

**Наслаждайтесь загрузкой с UltraDownloader!** 🎉

*Примечание: Всегда уважайте создателей контента и правообладателей при загрузке мультимедийных материалов.*