import os
import sys
import uuid
import shutil
import signal
import subprocess
import threading
import queue
from typing import Optional, List, Tuple

import customtkinter


class YouTubeDownloaderApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # State & Threading
        self.shutdown_event = threading.Event()
        self.process_lock = threading.Lock()
        self.current_process: Optional[subprocess.Popen] = None
        self.log_queue = queue.Queue()
        
        # Window Setup
        self.title("Python Youtube Downloader Release 2.0")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{int(screen_width * 0.50)}x{int(screen_height * 0.50)}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Setup Download Directory (PyInstaller safe)
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.download_dir = os.path.join(base_dir, "Downloads")

        # UI Elements
        self.url_input = customtkinter.CTkEntry(self, placeholder_text="Step 1: Enter Target URL here...")
        self.url_input.pack(fill="x", padx=10, pady=(10, 5))

        self.primary_frame = customtkinter.CTkFrame(self)
        self.primary_frame.pack(fill="x", padx=10, pady=5)
        
        self.update_button = customtkinter.CTkButton(
            self.primary_frame, text="Update yt-dlp", command=self.start_update_ytdlp,
            fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE")
        )
        self.update_button.pack(side="left", padx=5, pady=5)

        self.best_button = customtkinter.CTkButton(self.primary_frame, text="Download Best Quality", command=self.start_download_best)
        self.best_button.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.filename_input = customtkinter.CTkEntry(self, placeholder_text="Optional: Enter Video/Playlist Name...")
        self.filename_input.pack(fill="x", padx=10, pady=5)

        self.monitor_frame = customtkinter.CTkTextbox(self, font=("Consolas", 12), wrap="word", state="disabled")
        self.monitor_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.manual_frame = customtkinter.CTkFrame(self)
        self.manual_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.search_button = customtkinter.CTkButton(self.manual_frame, text="List All Formats", command=self.start_search)
        self.search_button.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        self.id_input = customtkinter.CTkEntry(self.manual_frame, placeholder_text="Format ID (e.g., 137+140)...")
        self.id_input.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        self.download_button = customtkinter.CTkButton(self.manual_frame, text="Download by ID", command=self.start_download_manual)
        self.download_button.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.interactive_widgets = (
            self.update_button, self.best_button, self.search_button, 
            self.download_button, self.url_input, self.id_input, self.filename_input
        )

        self._check_dependencies()
        self._process_log_queue()

    # --- Teardown & Process Management ---
    
    def on_closing(self):
        """Hides the UI instantly and gracefully terminates active background processes."""
        self.shutdown_event.set()
        self.withdraw()

        with self.process_lock:
            proc = self.current_process

        if proc is not None and proc.poll() is None:
            threading.Thread(target=self._kill_process_and_exit, args=(proc,), daemon=True).start()
        else:
            self.destroy()
            os._exit(0)

    def _kill_process_and_exit(self, proc: subprocess.Popen):
        """Forcefully terminates the subprocess tree at the OS level."""
        try:
            if os.name == "nt":
                cflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)], creationflags=cflags)
            else:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    proc.kill()
            proc.wait(timeout=1)
        except (subprocess.TimeoutExpired, Exception):
            pass 
        finally:
            os._exit(0)

    def _check_dependencies(self):
        if not shutil.which("yt-dlp"):
            self.log("\n[ERROR] 'yt-dlp' is missing! Click 'Update yt-dlp' or install via pip.\n")
        if not shutil.which("ffmpeg"):
            self.log("\n[WARNING] 'ffmpeg' is missing from PATH! Video and audio may not merge.\n\n")

    # --- GUI Updaters ---
    
    def _set_gui_state(self, state: str):
        if not self.shutdown_event.is_set():
            for widget in self.interactive_widgets:
                widget.configure(state=state)

    def _restore_gui_safe(self):
        if not self.shutdown_event.is_set():
            self.after(0, lambda: self._set_gui_state("normal"))

    def _clear_log(self):
        if self.shutdown_event.is_set():
            return
            
        while not self.log_queue.empty():
            try:
                self.log_queue.get_nowait()
            except queue.Empty:
                break
                
        self.monitor_frame.configure(state="normal")
        self.monitor_frame.delete("1.0", "end")
        self.monitor_frame.configure(state="disabled")

    def log(self, text: str):
        if not self.shutdown_event.is_set():
            self.log_queue.put(text)

    def _process_log_queue(self):
        if self.shutdown_event.is_set():
            return
            
        try:
            lines = []
            while True:
                lines.append(self.log_queue.get_nowait())
        except queue.Empty:
            pass
            
        if lines:
            self.monitor_frame.configure(state="normal")
            self.monitor_frame.insert("end", "".join(lines))
            self.monitor_frame.see("end")
            self.monitor_frame.configure(state="disabled")
            
        self.after(50, self._process_log_queue)

    # --- Utilities ---
    
    def _get_inputs(self) -> Tuple[str, str, str]:
        return (
            self.url_input.get().strip().strip(' "\''),
            self.filename_input.get().strip().strip(' "\''),
            self.id_input.get().strip().strip(' "\'')
        )

    def _sanitize_filename(self, text: str) -> str:
        if not text:
            return ""
        text = text.strip()
        lower_text = text.lower()
        
        for ext in ('.mp4', '.mkv', '.webm', '.mp3', '.m4a'):
            if lower_text.endswith(ext):
                text = text[:-len(ext)]
                break
                
        return "".join(c for c in text if c.isalnum() or c in " -_.").rstrip()

    def _ensure_download_dir(self) -> bool:
        try:
            os.makedirs(self.download_dir, exist_ok=True)
            return True
        except Exception as e:
            self.log(f"Error creating Downloads directory: {e}\n")
            return False

    def _get_subprocess_kwargs(self, capture_stderr: bool = False) -> dict:
        kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE if capture_stderr else subprocess.STDOUT,
            "text": True, 
            "encoding": "utf-8", 
            "errors": "replace"
        }
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
        else:
            kwargs["start_new_session"] = True 
        return kwargs

    def _validate_startup(self, url: str) -> bool:
        if not url:
            self.log("Error: URL cannot be empty.\n")
            return False
        return self._ensure_download_dir()

    # --- Subprocess Execution ---
    
    def run_subprocess(self, command_list: List[str], operation_name: str) -> bool:
        self.log(f"\n--- INITIATING {operation_name} ---\n> {' '.join(command_list)}\n\n")
        try:
            with self.process_lock:
                if self.shutdown_event.is_set():
                    return False
                process = subprocess.Popen(command_list, **self._get_subprocess_kwargs())
                self.current_process = process
            
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    if self.shutdown_event.is_set():
                        break
                    if line:
                        self.log(line)
                process.stdout.close()
                
            process.wait()
            success = (process.returncode == 0)
            
            if not success and "--client" in " ".join(command_list) and not self.shutdown_event.is_set():
                self.log("\n[TIP] If you saw an 'unrecognized arguments' error, click 'Update yt-dlp'.\n")
                
            if not self.shutdown_event.is_set():
                status = "SUCCEEDED" if success else f"FAILED (CODE {process.returncode})"
                self.log(f"\n--- OPERATION {operation_name} {status} ---\n")
            return success
            
        except Exception as e:
            if not self.shutdown_event.is_set():
                self.log(f"\n--- FATAL EXCEPTION DURING {operation_name} ---\n{e}\n")
            return False
        finally:
            with self.process_lock:
                self.current_process = None

    def run_and_capture(self, command_list: List[str], operation_name: str) -> Optional[str]:
        try:
            with self.process_lock:
                if self.shutdown_event.is_set():
                    return None
                process = subprocess.Popen(command_list, **self._get_subprocess_kwargs(capture_stderr=True))
                self.current_process = process
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0 and not self.shutdown_event.is_set():
                self.log(f"\n--- {operation_name} FAILED ---\n{stderr}\n")
                return None
            return stdout.strip()
            
        except Exception as e:
            if not self.shutdown_event.is_set():
                self.log(f"\n--- FATAL EXCEPTION DURING {operation_name} ---\n{e}\n")
            return None
        finally:
            with self.process_lock:
                self.current_process = None

    # --- Thread Starters ---
    
    def start_search(self):
        url, _, _ = self._get_inputs()
        self._clear_log()
        self._set_gui_state("disabled")
        threading.Thread(target=self._run_search_thread, args=(url,), daemon=True).start()

    def start_download_manual(self):
        url, filename, video_id = self._get_inputs()
        self._set_gui_state("disabled")
        threading.Thread(target=self._download_manual_thread, args=(url, video_id, filename), daemon=True).start()

    def start_download_best(self):
        url, filename, _ = self._get_inputs()
        self._clear_log()
        self._set_gui_state("disabled")
        threading.Thread(target=self._download_best_thread, args=(url, filename), daemon=True).start()
        
    def start_update_ytdlp(self):
        self._clear_log()
        self._set_gui_state("disabled")
        threading.Thread(target=self._update_ytdlp_thread, daemon=True).start()

    # --- Core Logic Methods ---
    
    def _update_ytdlp_thread(self):
        try:
            self.log("--- CHECKING FOR YT-DLP UPDATES ---\nThis may take a moment...\n")
            success = self.run_subprocess(["yt-dlp", "-U"], "NATIVE YT-DLP UPDATE")
            
            if not success and not self.shutdown_event.is_set():
                if getattr(sys, 'frozen', False):
                    self.log("\n[ERROR] Native update failed. As a standalone executable, please download the latest release manually.\n")
                else:
                    self.log("Native update unavailable. Attempting pip upgrade...\n")
                    try:
                        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--progress-bar", "off", "yt-dlp"]
                        self.run_subprocess(cmd, "PIP YT-DLP UPDATE")
                    except Exception as pip_err:
                        self.log(f"\n[ERROR] Pip update failed due to environment issues: {pip_err}\n")
        finally:
            self._restore_gui_safe()

    def _run_search_thread(self, url: str):
        try:
            if not url:
                self.log("Error: URL cannot be empty.\n")
                return
            self.run_subprocess(["yt-dlp", "--no-playlist", "--client", "ios,android,tv", "-F", "--", url], "LIST FORMATS")
        finally:
            self._restore_gui_safe()

    def _download_manual_thread(self, url: str, video_id: str, filename: str):
        try:
            if not video_id:
                self.log("Error: Format ID is required for manual download.\n")
                return
            if not self._validate_startup(url):
                return
            
            clean_name = self._sanitize_filename(filename)
            output_template = os.path.join(self.download_dir, f"{clean_name or '%(title)s'}.%(ext)s")
            
            command = [
                "yt-dlp", "--no-playlist", "--newline", "--client", "ios,android,tv", 
                "-f", video_id, "--merge-output-format", "mkv", "-o", output_template, "--", url
            ]
            success = self.run_subprocess(command, "MANUAL DOWNLOAD")
            
            if success and not self.shutdown_event.is_set():
                self.log("\n--- DOWNLOAD COMPLETED SUCCESSFULLY ---\n")
        finally:
            self._restore_gui_safe()

    def _download_best_thread(self, url: str, custom_filename: str):
        try:
            if not self._validate_startup(url):
                return

            self.log("--- ANALYZING URL ---\nChecking if URL is a Playlist...\n")
            check_cmd = ["yt-dlp", "--print", "playlist_title", "--no-warnings", "--playlist-items", "1", "--", url]
            raw_title = self.run_and_capture(check_cmd, "URL ANALYSIS")
            
            if raw_title is None or self.shutdown_event.is_set(): 
                return

            is_playlist = (raw_title != "NA" and bool(raw_title))
            clean_custom_name = self._sanitize_filename(custom_filename)

            base_cmd = ["yt-dlp", "--newline", "--client", "ios,android,tv", 
                        "-f", "bestvideo+bestaudio/best", "--merge-output-format", "mkv"]

            if is_playlist:
                self.log("PLAYLIST DETECTED.\n")
                pl_title = clean_custom_name if clean_custom_name else self._sanitize_filename(raw_title)
                if not pl_title:
                    pl_title = f"Playlist_{uuid.uuid4().hex[:8]}"
                    
                self.log(f"Target Folder: {pl_title}\n")
                name_template = f"{clean_custom_name}_%(autonumber)03d.%(ext)s" if clean_custom_name else "%(title)s.%(ext)s"
                output_template = os.path.join(self.download_dir, pl_title, name_template)
                
                command = base_cmd + ["--yes-playlist", "-o", output_template, "--", url]
                success = self.run_subprocess(command, "PLAYLIST DOWNLOAD")
            else:
                self.log("SINGLE VIDEO DETECTED.\n")
                name_template = f"{clean_custom_name}.%(ext)s" if clean_custom_name else "%(title)s.%(ext)s"
                output_template = os.path.join(self.download_dir, name_template)

                command = base_cmd + ["--no-playlist", "-o", output_template, "--", url]
                success = self.run_subprocess(command, "SINGLE VIDEO DOWNLOAD")

            if success and not self.shutdown_event.is_set():
                self.log("\n--- ALL TASKS COMPLETED SUCCESSFULLY ---\n")
            
        finally:
            self._restore_gui_safe()


if __name__ == "__main__":
    app = YouTubeDownloaderApp()

    app.mainloop()

# The code is rewritten by Gemini 3.1 Pro Preview

