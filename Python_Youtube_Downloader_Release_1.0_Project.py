# --- 1. Required: pip install customtkinter yt-dlp tk ---
# ffmpeg must be installed and in your system's PATH.

import tkinter
import subprocess
import os
import json
import customtkinter
import shlex
import uuid

# --- 2. Create the main application window ---
app = customtkinter.CTk()
app.title("Python Youtube Downloader Release 1.0 Project")

# --- 3. Set the window size ---
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
gui_width = int(screen_width * 0.50)
gui_height = int(screen_height * 0.50)
app.geometry(f"{gui_width}x{gui_height}")


# --- 4. Define the functions ---
def run_command_in_monitor(command_list: list, operation_name: str):
    # This function is now just for monitoring the process.
    command_str_for_display = " ".join(shlex.quote(s) for s in command_list)
    monitor_frame.insert(
        tkinter.END,
        f"\n--- INITIATING {operation_name} ---\n> {command_str_for_display}\n\n",
    )
    app.update()
    try:
        process = subprocess.Popen(
            command_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        for line in iter(process.stdout.readline, ""):
            monitor_frame.insert(tkinter.END, line)
            monitor_frame.see(tkinter.END)
            app.update()

        process.wait()
        if process.returncode != 0:
            monitor_frame.insert(
                tkinter.END,
                f"\n--- OPERATION {operation_name} FAILED WITH EXIT CODE {process.returncode} ---\n",
            )
            return False
        monitor_frame.insert(
            tkinter.END, f"\n--- OPERATION {operation_name} SUCCEEDED ---\n"
        )
        return True

    except Exception as e:
        monitor_frame.insert(
            tkinter.END,
            f"\n--- A FATAL SYSTEM EXCEPTION OCCURRED DURING {operation_name} ---\n{e}\n",
        )
        return False


def run_search():
    url = url_input.get().strip()
    flags = flags_input.get().strip()
    if not url:
        return
    command = ["yt-dlp"] + shlex.split(flags) + ["-F", url]
    run_command_in_monitor(command, "LIST FORMATS")


def download_manual():
    url = url_input.get().strip()
    video_id = id_input.get().strip()
    filename = filename_input.get().strip()
    flags = flags_input.get().strip()
    if not url or not video_id:
        return
    os.makedirs("Downloads", exist_ok=True)
    output_template = os.path.join("Downloads", f"{filename or '%(title)s'}.%(ext)s")
    command = (
        ["yt-dlp"] + shlex.split(flags) + ["-f", video_id, "-o", output_template, url]
    )
    run_command_in_monitor(command, "MANUAL DOWNLOAD")


def get_fps(url, flags_str):
    monitor_frame.insert(tkinter.END, "--- PERFORMING RECONNAISSANCE (FPS) ---\n")
    app.update()
    try:
        command_list = (
            ["yt-dlp"]
            + shlex.split(flags_str)
            + ["-f", "bestvideo", "--get-filename", "-o", "%(fps)s", url]
        )
        fps = subprocess.check_output(
            command_list, text=True, encoding="utf-8", stderr=subprocess.PIPE
        ).strip()
        if not fps:
            raise ValueError("Could not determine FPS.")
        monitor_frame.insert(
            tkinter.END, f"SUCCESS: Source Intel Acquired. Target FPS: {fps}\n"
        )
        return fps
    except Exception as e:
        monitor_frame.insert(tkinter.END, f"RECON FAILED: {e}\nAborting mission.\n")
        return None


def download_best():
    monitor_frame.delete("1.0", tkinter.END)
    url = url_input.get().strip()
    filename = filename_input.get().strip()
    flags_str = flags_input.get().strip()
    mode = quality_menu.get()

    if not url:
        return
    os.makedirs("Downloads", exist_ok=True)

    # --- STEP 1: ESTABLISH TRUE IDENTITY ---
    if not filename:
        try:
            monitor_frame.insert(tkinter.END, "--- ESTABLISHING TARGET IDENTITY ---\n")
            title_cmd = ["yt-dlp", "--get-filename", "-o", "%(title)s", url]
            filename = subprocess.check_output(
                title_cmd, text=True, encoding="utf-8", stderr=subprocess.PIPE
            ).strip()
            # Sanitize filename for filesystem
            filename = "".join(
                c for c in filename if c.isalnum() or c in (" ", "-", "_")
            ).rstrip()
            monitor_frame.insert(tkinter.END, f"Identity confirmed: {filename}\n")
        except Exception as e:
            monitor_frame.insert(
                tkinter.END,
                f"WARNING: Could not retrieve title. Using fallback ID.\nError: {e}\n",
            )
            filename = f"download_{uuid.uuid4()}"

    final_output_file = os.path.join("Downloads", f"{filename}.mp4")

    if "Visually Lossless" in mode:
        unique_id = uuid.uuid4()
        # We DICTATE the exact temp filenames inside the Downloads folder.
        temp_video_file = os.path.join("Downloads", f"{unique_id}.vid")
        temp_audio_file = os.path.join("Downloads", f"{unique_id}.aud")

        # --- PHASE 1: ACQUISITION ---
        fps = get_fps(url, flags_str)
        if not fps:
            return

        cmd_dl_video = (
            ["yt-dlp"]
            + shlex.split(flags_str)
            + ["-f", "bestvideo", "-o", temp_video_file, url]
        )
        cmd_dl_audio = (
            ["yt-dlp"]
            + shlex.split(flags_str)
            + ["-f", "bestaudio", "-o", temp_audio_file, url]
        )

        if not run_command_in_monitor(cmd_dl_video, "ACQUISITION (VIDEO)"):
            return
        if not run_command_in_monitor(cmd_dl_audio, "ACQUISITION (AUDIO)"):
            return

        # --- PHASE 2: SANITIZATION (DIRECT FFMPEG CALL) ---
        cmd_ffmpeg = []
        operation_name = "SANITIZATION"

        if mode == "Visually Lossless (x264)":
            operation_name += " (FFMPEG H.264)"
            cmd_ffmpeg = [
                "ffmpeg",
                "-i", temp_video_file,
                "-i", temp_audio_file,
                "-c:v", "libx264",
                "-crf", "16",
                "-preset", "slow",
                "-r", str(fps),
                "-c:a", "aac",
                "-b:a", "320k",
                "-pix_fmt", "yuv420p",
                "-threads", "0",
                "-y", final_output_file,
            ]
        elif mode == "Visually Lossless (x265)":
            operation_name += " (FFMPEG H.265)"
            cmd_ffmpeg = [
                "ffmpeg",
                "-i", temp_video_file,
                "-i", temp_audio_file,
                "-c:v", "libx265",
                "-crf", "16",
                "-preset", "slow",
                "-tag:v", "hvc1",
                "-r", str(fps),
                "-c:a", "aac",
                "-b:a", "320k",
                "-pix_fmt", "yuv420p",
                "-threads", "0",
                "-y", final_output_file,
            ]

        if cmd_ffmpeg:
            if not run_command_in_monitor(cmd_ffmpeg, operation_name):
                monitor_frame.insert(tkinter.END, "CRITICAL FAILURE during sanitization.")
            else:
                monitor_frame.insert(
                    tkinter.END, f"SUCCESS. Final file at: {final_output_file}\n"
                )

        # --- PHASE 3: CLEANUP ---
        monitor_frame.insert(tkinter.END, "--- CLEANING UP TEMPORARY FILES ---\n")
        for f in [temp_video_file, temp_audio_file]:
            try:
                if os.path.exists(f):
                    os.remove(f)
                    monitor_frame.insert(tkinter.END, f"Removed {f}\n")
            except Exception as e:
                monitor_frame.insert(
                    tkinter.END, f"Failed to remove temp file {f}: {e}\n"
                )

    elif mode == "Fast Merge":
        # The naming is now unified. It uses the SAME logic.
        command_list = (
            ["yt-dlp"]
            + shlex.split(flags_str)
            + [
                "-f",
                "bestvideo+bestaudio/best",
                "--merge-output-format",
                "mp4",
                "-o",
                final_output_file,
                url,
            ]
        )
        run_command_in_monitor(command_list, "FAST MERGE")


# --- UI ---
url_input = customtkinter.CTkEntry(
    app, placeholder_text="Step 1: Paste Target URL here..."
)
url_input.pack(fill="x", padx=5, pady=5)
primary_frame = customtkinter.CTkFrame(app)
primary_frame.pack(fill="x", padx=5, pady=5)
best_button = customtkinter.CTkButton(
    primary_frame, text="DOWNLOAD", command=download_best
)
best_button.pack(side="left", fill="x", expand=True, padx=5, pady=5)
quality_options = [
    "Visually Lossless (x264)",
    "Visually Lossless (x265)",
    "Fast Merge",
]
quality_menu = customtkinter.CTkOptionMenu(
    primary_frame, values=quality_options
)
quality_menu.set(quality_options[0])
quality_menu.pack(side="left", padx=5, pady=5)
filename_input = customtkinter.CTkEntry(
    app, placeholder_text="Optional: Enter a new filename..."
)
filename_input.pack(fill="x", padx=5, pady=5)
monitor_frame = customtkinter.CTkTextbox(app)
monitor_frame.pack(fill="both", expand=True, padx=5, pady=5)
manual_frame = customtkinter.CTkFrame(app)
manual_frame.pack(fill="x", padx=5, pady=5)
search_button = customtkinter.CTkButton(
    manual_frame, text="List All Formats", command=run_search
)
search_button.pack(side="left", fill="x", expand=True, padx=5, pady=5)
id_input = customtkinter.CTkEntry(manual_frame, placeholder_text="Enter Format 'ID'...")
id_input.pack(side="left", fill="x", expand=True, padx=5, pady=5)
download_button = customtkinter.CTkButton(
    manual_frame, text="Download by ID", command=download_manual
)
download_button.pack(side="left", fill="x", expand=True, padx=5, pady=5)
flags_input = customtkinter.CTkEntry(
    app,
    placeholder_text="Advanced: Add extra yt-dlp flags here (e.g., --cookies-from-browser firefox)",
)
flags_input.pack(fill="x", padx=5, pady=5)

# --- Start Application ---
app.mainloop()

# The code is rewritten by Gemini 2.5 Pro
