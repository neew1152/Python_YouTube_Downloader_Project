# 🐍 Python YouTube Downloader (Release 2.0)

A powerful, modern, and highly resilient YouTube video and playlist downloader built with Python. Evolving from basic scripts to a fully threaded, non-blocking graphical application, this project utilizes `customtkinter`, `yt-dlp`, and `FFmpeg` to deliver the ultimate video acquisition experience. 

---

## ✨ Features (Perfectionism)

Built with strict attention to stability, usability, and clean architecture:

*   **Modern, Responsive UI**: Powered by `customtkinter`, featuring a clean, dark-themed, and intuitive interface that dynamically scales to 50% of your screen resolution.
*   **100% Non-Blocking Architecture**: Fully multi-threaded background processing. The UI remains buttery-smooth and responsive even during heavy downloads or format extraction.
*   **Smart URL Analysis**: Automatically detects whether a URL is a single video or a playlist. 
*   **Advanced Playlist Handling**: Automatically generates dedicated folders for playlists and sequences' filenames seamlessly.
*   **Format Reconnaissance**: List all available video/audio formats for a given URL and manually download specific format IDs (e.g., `137+140`).
*   **Automated Quality Merging**: Fetches the absolute best video and best audio streams independently and merges them natively into a high-quality `.mkv` container using FFmpeg.
*   **One-Click `yt-dlp` Updater**: Built-in update button to seamlessly upgrade `yt-dlp` via native commands or Pip, preventing "unrecognized arguments" or broken extraction errors as YouTube updates its backend.
*   **Bulletproof Process Management**: OS-level thread and subprocess tracking. Closing the app triggers a graceful shutdown, safely terminating active downloads, clearing memory, and preventing ghost processes (`SIGKILL`/`taskkill`).
*   **Sanitized Filesystem Operations**: Intelligent filename sanitization removes illegal characters, preventing OS-level saving errors.
*   **Real-Time Queue-Based Logging**: A built-in terminal monitor that streams subprocess output directly to the UI in real-time, safely managed via thread queues.
*   **Deployment Ready**: Directory structures and base-path logic are strictly designed to be 100% compatible with standalone executable compilers like `PyInstaller`.

---

## ⚙️ Setup & Installation

To run this application natively, you need Python installed on your system along with FFmpeg (for merging audio and video streams) and the required Python packages.

Open your terminal or command prompt (Run as Administrator recommended for Winget) and execute the following:

```powershell
winget install --id Gyan.FFmpeg && pip install customtkinter yt-dlp
```

*Note: Ensure `ffmpeg` is properly added to your system's Environment Variables (PATH). Winget usually handles this automatically, but a terminal restart may be required.*

---

## 📜 Changelogs

### 👑 Release 2.0 (Current)
*   **Perfected by Gemini 3.1 Pro Preview.**
*   Implemented `threading` and `queue` systems to completely eliminate GUI freezing.
*   Added native OS-level subprocess killing (`taskkill` / `SIGKILL`) for instantaneous, clean app exits.
*   Added full Playlist Support (auto-detects, creates subfolders, formats names).
*   Added GUI one-click native `yt-dlp` update utility.
*   Made the script fully `PyInstaller` safe (`sys.frozen` checks).
*   Unified UI aesthetics into a clean, minimal layout with a unified read-only console.

### 💎 Release 1.0
*   **Engineered by Gemini 3 Pro Preview.**
*   Introduced FFmpeg direct pipeline for "Visually Lossless" x264/x265 hardware encoding.
*   Added True Identity verification to secure video titles before downloading.
*   Added UUID-based temporary file generation to prevent overwrite collisions.
*   Implemented dynamic FPS extraction for pristine video reconstruction.
*   Added manual `yt-dlp` advanced flags input bar.

### 🚀 Beta 8.0
*   **Major Refactor by Gemini 2.5 Pro.**
*   *Removed PyTube dependency entirely* (due to constant cipher breakages on YouTube's end). Fully transitioned to pure `yt-dlp`.
*   Codebase highly condensed and optimized for readability.
*   Improved input stripping and empty-field validations.

### 🛠️ Beta 6.5
*   Introduced the ability to manually rename output files prior to downloading.
*   Improved CLI error handling and GUI updates.
*   Streamlined formatting strings to automatically capture `%(title)s.%(ext)s`.

### 🧪 Beta 4.0
*   Implemented initial graphical user interface using `customtkinter`.
*   Integrated dual-library approach (`yt-dlp` for formatting/CLI commands, `pytube` for metadata and progress tracking).
*   Added real-time subprocess stdout monitoring with an Auto-Scroll toggle.
*   Added basic Light/Dark appearance mode switch.

### 🛑 Beta 1.0 - Beta 3.0
*   🗄️ **Status:** *Archive loss / Records lost / Missing.* 
*   *Notes:* Early experimental builds. Source code is lost to the digital void.

---

## 🧠 Sources and Professors (AI)

This project is a testament to the power of human curiosity combined with Artificial Intelligence. 

**AI "Professors" & Code Architects:**
*   🌌 **Gemini 3.1 Pro Preview**: Engineered the final, bulletproof multi-threaded architecture, queue-logging, and graceful OS-level process handling (Release 2.0).
*   🔬 **Gemini 3 Pro Preview**: Introduced advanced FFmpeg encoding pipelines, system reconnaissance, and advanced command list structuring (Release 1.0).
*   🧠 **Gemini 2.5 Pro**: Provided the first major code cleanup, stripping redundant libraries and establishing solid Python logic (Beta 8.0).
*   🤖 **ChatGPT-3.5 & ChatGPT-4o**: Assisted with foundational logic, UI sizing, and early debugging (Beta 4.0 - Beta 6.5).

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
    *   * (Note: Some original tutorial videos have since been deleted or made private.)*
*   https://github.com/yt-dlp/yt-dlp
*   https://github.com/TomSchimansky/CustomTkinter
*   https://www.google.com
