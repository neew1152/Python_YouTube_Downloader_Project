# 🎥 Python YouTube Video Downloader Project

A tool for data liberation.

## Features

*   **One-Click Operation:** No more searching for obscure format codes. Paste a URL, click one button.
*   **Intelligent Encoding:** The system performs reconnaissance before downloading. It scans the source video and audio bitrates and dynamically builds the perfect encoding profile. It doesn't waste your machine's power creating a high-resolution photo of a blurry image.
*   **Professional Editor Compliance:** The re-encoding protocol creates standard H.264/AAC files designed to work flawlessly in professional NLEs like DaVinci Resolve, Premiere Pro, and Final Cut, eliminating "Media Offline" errors caused by web-native formats.
*   **Total Control:** For non-standard cases, the tool retains a manual override system for downloading by specific format ID and a command-line input for injecting any advanced `yt-dlp` flag you require.

## Prerequisites

1.  **Python 3.x:** Must be installed on your system.
2.  **FFmpeg:** **CRITICAL.** `ffmpeg` **must** be installed and accessible in your system's PATH. The merging and re-encoding functions will fail without it. You can get it from [ffmpeg.org](https://ffmpeg.org/download.html).
3.  **Python Libraries:** Install the necessary components using pip.
    ```bash
    pip install customtkinter yt-dlp tk
    ```

## How to Use

1.  Save the code as a Python file.
2.  Run it from your terminal:
    ```bash
    python main.py
    ```
3.  **Primary Workflow:**
    *   Paste the target video URL into the top input box.
    *   (Optional) Provide a custom filename. If left blank, the video's original title will be used.
    *   Choose your encoding protocol from the dropdown menu:
        *   **`Auto-Optimize (Recommended)`:** This is the default and smartest option. It scans the source and applies the appropriate level of quality for a perfect, efficient re-encode. **Use this.**
        *   **`Fast Merge`:** The quickest option. Copies the original video and audio streams into an MP4 container **without re-encoding**. It is fast but may not be compatible with editing software.
        *   **`Near-Lossless Re-encode`:** The brute-force option. Overrides the auto-detection and encodes at the highest possible quality settings, regardless of the source. You can use this if you have a specific reason to.
    *   Click the red **`DOWNLOAD`** button.
4.  Wait for the process to complete in the terminal monitor. Downloaded files will be saved in a `Downloads` folder created in the same directory as the script.

## Sources

The project was inspired by several YouTube tutorials and resources, including:

* https://www.youtube.com/watch?v=NI9LXzo0UY0
* https://www.youtube.com/watch?v=Miydkti_QVE
* https://www.youtube.com/watch?v=Envp9yHb2Ho
* https://www.youtube.com/watch?v=EwL2BwEdduE
* https://www.youtube.com/watch?v=a0MVOloNLB4
* https://www.youtube.com/watch?v=GeflXCubyrA
* https://www.youtube.com/watch?v=QRroCuY1Bhc
* https://www.youtube.com/watch?v=df30Qro3Iu4
* ChatGPT 3.5/GPT-4o
* GitHub
* Google
* Gemini 2.5 Pro
