# Python YouTube Downloader Project

![Software-Preview.png](https://github.com/user-attachments/assets/e2eb6ea0-94d4-4570-a106-b35088763e6f)

A powerful, modern, and highly resilient YouTube video and playlist downloader built with Python. Evolving from basic scripts to a fully threaded, non-blocking GUI application, this project uses `customtkinter`, `yt-dlp`, and `FFmpeg` to deliver a seamless video-downloading experience. 

## Features

*   **Modern, Responsive UI**: Powered by `customtkinter`, featuring a clean, dark-themed, and intuitive interface that dynamically scales to 50% of your screen resolution.
*   **100% Non-Blocking Architecture**: Fully multi-threaded background processing. The UI remains buttery-smooth and responsive even during heavy downloads or format extraction.
*   **Smart URL Analysis**: Automatically detects whether a URL is a single video or a playlist. 
*   **Advanced Playlist Handling**: Automatically generates dedicated folders for playlists and sequences' filenames seamlessly.
*   **Format Reconnaissance**: Lists all available video/audio formats for a given URL and manually downloads specific format IDs (e.g., `137+140`).
*   **Automated Quality Merging**: Fetches the absolute best video and best audio streams independently and merges them natively into a high-quality `.mkv` container using FFmpeg.
*   **One-Click `yt-dlp` Updater**: Built-in update button to seamlessly upgrade `yt-dlp` via native commands or Pip, preventing "unrecognized arguments" or broken extraction errors as YouTube updates its backend.
*   **Bulletproof Process Management**: OS-level thread and subprocess tracking. Closing the app triggers a graceful shutdown, safely terminating active downloads, clearing memory, and preventing ghost processes (`SIGKILL`/`taskkill`).
*   **Sanitized Filesystem Operations**: Intelligent filename sanitization removes illegal characters, preventing OS-level saving errors.
*   **Real-Time Queue-Based Logging**: A built-in terminal monitor that streams subprocess output directly to the UI in real-time, safely managed via thread queues.
*   **Deployment Ready**: Directory structures and base-path logic are strictly designed to be 100% compatible with standalone executable compilers like `PyInstaller`.

## [Installation](https://github.com/yt-dlp/yt-dlp/wiki/Installation)

```powershell
winget install Gyan.FFmpeg
pip install customtkinter
pip install -U "yt-dlp[default]"
```

## Sources

**AI "Professors" & Code Architects:**
*  **Claude Sonnet 4.5**: Eliminated four critical threading, playlist detection, and log-handling bugs. Ensured TOCTOU safety and robust playlist handling for edge cases (Release 2.5).
*  **Gemini 3.1 Pro Preview**: Engineered the final, bulletproof multi-threaded architecture, queue logging, and graceful OS-level process handling (Release 2.0).
*  **Gemini 3 Pro Preview**: Introduced advanced FFmpeg encoding pipelines, system reconnaissance, and advanced command list structuring (Release 1.0).
*  **Gemini 2.5 Pro**: Provided the first major code cleanup, stripping redundant libraries and establishing solid Python logic (Beta 8.0).
*  **ChatGPT-3.5 & ChatGPT-4o**: Assisted with foundational logic, UI sizing, and early debugging (Beta 4.0 - Beta 6.5).

**Community Sources & Inspiration:**
*   Original syntax logic and CustomTkinter inspiration gathered from various YouTube tutorials, including (but not limited to):
    *   * https://www.youtube.com/watch?v=NI9LXzo0UY0
    *   * https://www.youtube.com/watch?v=Miydkti_QVE
    *   * https://www.youtube.com/watch?v=Envp9yHb2Ho
    *   * https://www.youtube.com/watch?v=EwL2BwEdduE
    *   * https://www.youtube.com/watch?v=a0MVOloNLB4
    *   * https://www.youtube.com/watch?v=GeflXCubyrA
    *   * https://www.youtube.com/watch?v=QRroCuY1Bhc
    *   * https://www.youtube.com/watch?v=df30Qro3Iu4
    *   * (Note: Some original tutorial videos have since been deleted or made private.)
*   https://github.com/yt-dlp/yt-dlp
*   https://github.com/TomSchimansky/CustomTkinter
*   https://www.google.com
