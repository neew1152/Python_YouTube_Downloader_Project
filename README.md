# Python YouTube Downloader Project

This project provides a simple GUI for downloading videos from YouTube using `yt-dlp`. It supports various download modes, including best quality, manual download by ID, and more.  It also attempts to utilize ffmpeg if available.

## Prerequisites

*   **Python:** Make sure you have Python installed on your system.
*   **Dependencies:** Install the required Python packages using pip:

    ```bash
    pip install customtkinter yt-dlp tk
    ```
*   **FFmpeg:**  Ensure FFmpeg is installed and accessible in your system's PATH environment variable.  This is *crucial* for the visually lossless modes.  You may need to restart your terminal or IDE after installing FFmpeg.

## Features

*   **Download Best Quality:** Downloads the best available video and audio streams. Options for merging with the best options, with `Fast Merge` and  `Visually Lossless` options via calling external ffmpeg commands.
*   **Manual Download by ID:** Allows specifying the video ID to download specific formats.
*   **List Formats:** Displays available formats for a given URL (useful for manual downloads).
*   **Custom Flags:** Supports adding custom `yt-dlp` flags for advanced control (e.g., specifying cookies, user agents).
*   **Progress Monitoring:** Provides a text box to display download progress, errors, and informational messages.
*   **Automatic Filename:** Attempts to derive the filename from the video title.
*   **Error Handling:** Includes error handling to catch exceptions during the download process and provide informative error messages.

## Usage

1.  **Run the script:**  Execute the Python script (`your_script_name.py`).
2.  **Paste the YouTube URL:** Enter the YouTube video URL in the "Step 1: Paste Target URL here..." field.
3.  **Choose a download method:**  Select an option from the `quality_menu` which offers options, or for specific formatting, select 'List All Formats', copy ID's, then set 'Download By ID'.
4.  **Optional: Add a Custom Filename:** Fill in filename and path here if desired.
5.  **Optional: Advanced Flags:** If required, set advanced options.
6.  **Click a Button:** Use the different buttons.

    *   `DOWNLOAD`: This attempts to retrieve the best options with quality constraints, using `Visually Lossless (x264/x265)`, or Fast Merge.  This attempts to find target names to generate file names from titles or creates its own GUID.  Then, the download process begins on the monitor screen.
    *   `List All Formats`: Displays available formats. Useful for downloading individual video or audio tracks.
    *   `Download By ID`: Downloads the stream by ID.

7.  **Monitor the Progress:** The download progress and any output from `yt-dlp` and `ffmpeg` will be displayed in the text monitor area.
8.  **Downloaded Files:** Downloaded videos will be saved in a "Downloads" directory in the same folder as your Python script or configured to.

## Configuration

*   **FFmpeg Path:** Make sure FFmpeg is correctly installed and its executable is in your system's PATH.

## Troubleshooting

*   **Missing FFmpeg:** If you happen to encounter errors related to FFmpeg, please make sure that FFmpeg is installed and in your system's PATH. You may need to restart your terminal or IDE for the changes to take effect.
*   **Dependencies:**  Double-check that all required Python packages are installed correctly.
*   **Permissions:**  Ensure that your user has the necessary permissions to create files and directories in the "Downloads" directory or whatever directory has been selected.
*   **URL Issues:** Verify that the provided YouTube URL is valid.
*   **Error Messages:** Carefully read any error messages displayed in the output monitor; they usually contain helpful information about the problem.
*   **Internet Connection:** Ensure you have an active internet connection during the download process.

## Known Limitations

*   Requires FFmpeg for "Visually Lossless" and possibly the best output via quality options to operate as expected.
*   The GUI is basic and could be enhanced.
*   Doesn't support all `yt-dlp` features (but custom flags allow flexibility).
*   Error handling, particularly for FFmpeg-related errors, could be improved.
*   Might not work with every single YouTube video, as some may use techniques for bypassing this system, and/or may require special arguments.

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
