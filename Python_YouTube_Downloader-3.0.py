from __future__ import annotations
import os
import sys
import uuid
import shutil
import signal
import subprocess
import threading
import queue
from typing import Optional, List, Tuple
import customtkinter as ctk
_POLL_MS = 50
_MAX_LOG_LINES = 4000
_LOG_FONT = ('Consolas', 12)
_ACCENT = '#1f538d'
_ACCENT_HOVER = '#14375e'
_BORDER_FG = ('gray10', '#DCE4EE')
_STRIP_CHARS = ' "\''
_SAFE_CHARS = frozenset(' -_.')
_VIDEO_EXTS = ('.mp4', '.mkv', '.webm', '.mp3', '.m4a')
_CREATE_NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 134217728)
_IS_NT = os.name == 'nt'
_HAS_FFMPEG: bool = shutil.which('ffmpeg') is not None
_HAS_YTDLP: bool = shutil.which('yt-dlp') is not None
_KEEP = ''.join((chr(i) for i in range(128) if chr(i).isalnum() or chr(i) in _SAFE_CHARS))
_TRANSLATE_MAP = {i: None for i in range(128) if chr(i) not in _KEEP}
_YTDLP_BASE = ('yt-dlp', '--newline', '--no-cache-dir', '--no-check-certificate')
_YTDLP_FMT_FFMPEG = ('-f', 'bestvideo+bestaudio/best', '--merge-output-format', 'mkv')
_YTDLP_FMT_NOFFMPEG = ('-f', 'best')

class YouTubeDownloaderApp(ctk.CTk):

    def __init__(self) -> None:
        super().__init__()
        self.shutdown_event = threading.Event()
        self.process_lock = threading.Lock()
        self.current_process: Optional[subprocess.Popen] = None
        self.log_queue: queue.Queue[str] = queue.Queue()
        self.title('Python YouTube Downloader 3.0')
        sw, sh = (self.winfo_screenwidth(), self.winfo_screenheight())
        self.geometry(f'{sw // 2}x{sh // 2}')
        self.protocol('WM_DELETE_WINDOW', self._on_closing)
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        self.download_dir = os.path.join(base_dir, 'Downloads')
        self._build_ui()
        self._check_dependencies()
        self.after(_POLL_MS, self._drain_log_queue)

    def _build_ui(self) -> None:
        pad = {'padx': 10, 'pady': 5}
        self.url_input = ctk.CTkEntry(self, placeholder_text='Step 1: Paste Target URL (Video, Playlist)...')
        self.url_input.pack(fill='x', padx=10, pady=(10, 5))
        primary = ctk.CTkFrame(self)
        primary.pack(fill='x', **pad)
        self.update_button = ctk.CTkButton(primary, text='Update yt-dlp', command=self._start_update, fg_color='transparent', border_width=2, text_color=_BORDER_FG)
        self.update_button.pack(side='left', padx=5, pady=5)
        self.best_button = ctk.CTkButton(primary, text='DOWNLOAD BEST QUALITY', command=self._start_best, fg_color=_ACCENT, hover_color=_ACCENT_HOVER)
        self.best_button.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self.filename_input = ctk.CTkEntry(self, placeholder_text='Optional: Enter Video/Playlist Name...')
        self.filename_input.pack(fill='x', **pad)
        self.monitor = ctk.CTkTextbox(self, font=_LOG_FONT, wrap='word', state='disabled')
        self.monitor.pack(fill='both', expand=True, **pad)
        manual = ctk.CTkFrame(self)
        manual.pack(fill='x', padx=10, pady=(5, 10))
        self.search_button = ctk.CTkButton(manual, text='List All Formats', command=self._start_search)
        self.search_button.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self.id_input = ctk.CTkEntry(manual, placeholder_text='Format ID (e.g., 137+140)...')
        self.id_input.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self.download_button = ctk.CTkButton(manual, text='Download by ID', command=self._start_manual)
        self.download_button.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self._widgets = (self.update_button, self.best_button, self.search_button, self.download_button, self.url_input, self.id_input, self.filename_input)

    @property
    def _alive(self) -> bool:
        return not self.shutdown_event.is_set()

    def _inputs(self) -> Tuple[str, str, str]:
        return (self.url_input.get().strip(_STRIP_CHARS), self.filename_input.get().strip(_STRIP_CHARS), self.id_input.get().strip(_STRIP_CHARS))

    @staticmethod
    def _sanitize(text: str) -> str:
        if not text:
            return ''
        text = text.strip()
        low = text.lower()
        for ext in _VIDEO_EXTS:
            if low.endswith(ext):
                text = text[:-len(ext)]
                break
        clean = text.translate(_TRANSLATE_MAP).rstrip()
        return clean if clean not in ('.', '..') else 'Invalid_Name'

    def _ensure_dir(self) -> bool:
        try:
            os.makedirs(self.download_dir, exist_ok=True)
            return True
        except OSError as exc:
            self._log(f'Error creating Downloads directory: {exc}\n')
            return False

    def _set_gui(self, state: str) -> None:
        for w in self._widgets:
            w.configure(state=state)

    def _restore_gui(self) -> None:
        if self._alive:
            self.after(0, lambda: self._set_gui('normal'))

    def _log(self, text: str) -> None:
        if self._alive:
            self.log_queue.put(text)

    def _clear_log(self) -> None:
        try:
            while True:
                self.log_queue.get_nowait()
        except queue.Empty:
            pass
        self.monitor.configure(state='normal')
        self.monitor.delete('1.0', 'end')
        self.monitor.configure(state='disabled')

    def _drain_log_queue(self) -> None:
        if not self._alive:
            return
        q = self.log_queue
        chunks: list[str] = []
        while True:
            try:
                chunks.append(q.get_nowait())
            except queue.Empty:
                break
        if chunks:
            self.monitor.configure(state='normal')
            self.monitor.insert('end', ''.join(chunks))
            line_count = int(self.monitor.index('end-1c').split('.')[0])
            if line_count > _MAX_LOG_LINES:
                overflow = line_count - _MAX_LOG_LINES
                self.monitor.delete('1.0', f'{overflow}.0')
            self.monitor.see('end')
            self.monitor.configure(state='disabled')
        self.after(_POLL_MS, self._drain_log_queue)

    @staticmethod
    def _popen_kwargs(capture_stderr: bool=False) -> dict:
        kw = {'stdout': subprocess.PIPE, 'stderr': subprocess.PIPE if capture_stderr else subprocess.STDOUT, 'text': True, 'encoding': 'utf-8', 'errors': 'replace'}
        if _IS_NT:
            kw['creationflags'] = _CREATE_NO_WINDOW
        else:
            kw['start_new_session'] = True
        return kw

    def _spawn(self, cmd: List[str], *, capture_stderr: bool=False) -> Optional[subprocess.Popen]:
        with self.process_lock:
            if not self._alive:
                return None
            proc = subprocess.Popen(cmd, **self._popen_kwargs(capture_stderr))
            self.current_process = proc
        return proc

    def _finish(self) -> None:
        with self.process_lock:
            self.current_process = None

    def _run(self, cmd: List[str], label: str) -> bool:
        self._log(f"\n--- INITIATING {label} ---\n> {' '.join(cmd)}\n\n")
        try:
            proc = self._spawn(cmd)
            if proc is None:
                return False
            stdout = proc.stdout
            if stdout:
                for line in iter(stdout.readline, ''):
                    if not self._alive:
                        break
                    self._log(line)
                stdout.close()
            rc = proc.wait()
            if self._alive:
                if rc != 0:
                    self._log("\n[TIP] If the download failed, try 'Update yt-dlp'.\n")
                status = 'SUCCEEDED' if rc == 0 else f'FAILED (CODE {rc})'
                self._log(f'\n--- OPERATION {label} {status} ---\n')
            return rc == 0
        except Exception as exc:
            if self._alive:
                self._log(f'\n--- FATAL EXCEPTION DURING {label} ---\n{exc}\n')
            return False
        finally:
            self._finish()

    def _run_capture(self, cmd: List[str], label: str) -> Optional[str]:
        try:
            proc = self._spawn(cmd, capture_stderr=True)
            if proc is None:
                return None
            stdout, stderr = proc.communicate()
            if proc.returncode != 0:
                if self._alive:
                    self._log(f'\n--- {label} FAILED ---\n{stderr}\n')
                return None
            return stdout.strip()
        except Exception as exc:
            if self._alive:
                self._log(f'\n--- FATAL EXCEPTION DURING {label} ---\n{exc}\n')
            return None
        finally:
            self._finish()

    def _check_dependencies(self) -> None:
        if not _HAS_YTDLP:
            self._log("\n[ERROR] 'yt-dlp' is missing! Click 'Update yt-dlp' or install via pip.\n")
        if not _HAS_FFMPEG:
            self._log("\n[WARNING] 'ffmpeg' is missing from PATH! Downloads limited to pre-merged formats (max 720p).\n\n")

    def _start_search(self) -> None:
        url, _, _ = self._inputs()
        self._clear_log()
        self._set_gui('disabled')
        threading.Thread(target=self._search_worker, args=(url,), daemon=True).start()

    def _start_manual(self) -> None:
        url, name, fid = self._inputs()
        self._clear_log()
        self._set_gui('disabled')
        threading.Thread(target=self._manual_worker, args=(url, fid, name), daemon=True).start()

    def _start_best(self) -> None:
        url, name, _ = self._inputs()
        self._clear_log()
        self._set_gui('disabled')
        threading.Thread(target=self._best_worker, args=(url, name), daemon=True).start()

    def _start_update(self) -> None:
        self._clear_log()
        self._set_gui('disabled')
        threading.Thread(target=self._update_worker, daemon=True).start()

    def _update_worker(self) -> None:
        try:
            self._log('--- CHECKING FOR YT-DLP UPDATES ---\nThis may take a moment...\n')
            ok = self._run(['yt-dlp', '-U'], 'NATIVE YT-DLP UPDATE')
            if not ok and self._alive:
                if getattr(sys, 'frozen', False):
                    self._log('\n[ERROR] Native update failed. Download the latest release manually.\n')
                else:
                    self._log('Native update unavailable. Attempting pip upgrade...\n')
                    self._run([sys.executable, '-m', 'pip', 'install', '--upgrade', '--progress-bar', 'off', 'yt-dlp'], 'PIP YT-DLP UPDATE')
        finally:
            self._restore_gui()

    def _search_worker(self, url: str) -> None:
        try:
            if not url:
                self._log('Error: URL cannot be empty.\n')
                return
            cmd = ['yt-dlp', '--no-playlist', '--no-cache-dir', '--no-check-certificate', '-F', '--', url]
            self._run(cmd, 'LIST FORMATS')
        finally:
            self._restore_gui()

    def _manual_worker(self, url: str, fmt_id: str, filename: str) -> None:
        try:
            if not fmt_id:
                self._log('Error: Format ID is required.\n')
                return
            if not url or not self._ensure_dir():
                return
            clean = self._sanitize(filename)
            tmpl = os.path.join(self.download_dir, f"{clean or '%(title)s'}.%(ext)s")
            cmd = ['yt-dlp', '--no-playlist', '--newline', '--no-cache-dir', '--no-check-certificate', '-f', fmt_id, '-o', tmpl]
            if _HAS_FFMPEG:
                cmd += ['--merge-output-format', 'mkv']
            cmd += ['--', url]
            if self._run(cmd, 'MANUAL DOWNLOAD'):
                self._log('\n--- DOWNLOAD COMPLETED SUCCESSFULLY ---\n')
        finally:
            self._restore_gui()

    def _best_worker(self, url: str, custom_name: str) -> None:
        try:
            if not url or not self._ensure_dir():
                return
            self._log('--- ANALYZING URL ---\nChecking if URL is a Playlist...\n')
            probe = self._run_capture(['yt-dlp', '--print', 'playlist_title', '--no-warnings', '--playlist-items', '1', '--', url], 'URL ANALYSIS')
            if probe is None or not self._alive:
                return
            is_playlist = bool(probe) and probe.strip() != 'NA'
            clean = self._sanitize(custom_name)
            fmt_args = list(_YTDLP_FMT_FFMPEG) if _HAS_FFMPEG else list(_YTDLP_FMT_NOFFMPEG)
            base = [*_YTDLP_BASE, *fmt_args]
            if is_playlist:
                self._log('PLAYLIST DETECTED.\n')
                folder = clean or self._sanitize(probe)
                if not folder or folder == 'Invalid_Name':
                    folder = f'Playlist_{uuid.uuid4().hex[:8]}'
                self._log(f'Target Folder: {folder}\n')
                tmpl_name = f'{clean}_%(autonumber)03d.%(ext)s' if clean else '%(playlist_index)03d_%(title)s.%(ext)s'
                cmd = base + ['--yes-playlist', '-o', os.path.join(self.download_dir, folder, tmpl_name), '--', url]
                ok = self._run(cmd, 'PLAYLIST DOWNLOAD')
            else:
                self._log('SINGLE VIDEO DETECTED.\n')
                tmpl_name = f'{clean}.%(ext)s' if clean else '%(title)s.%(ext)s'
                cmd = base + ['--no-playlist', '-o', os.path.join(self.download_dir, tmpl_name), '--', url]
                ok = self._run(cmd, 'SINGLE VIDEO DOWNLOAD')
            if ok and self._alive:
                self._log('\n--- ALL TASKS COMPLETED SUCCESSFULLY ---\n')
        finally:
            self._restore_gui()

    def _on_closing(self) -> None:
        self.shutdown_event.set()
        self.withdraw()
        with self.process_lock:
            proc = self.current_process
        if proc is not None and proc.poll() is None:
            threading.Thread(target=self._kill_and_exit, args=(proc,), daemon=True).start()
        else:
            self.destroy()
            sys.exit(0)

    @staticmethod
    def _kill_and_exit(proc: subprocess.Popen) -> None:
        try:
            if _IS_NT:
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)], creationflags=_CREATE_NO_WINDOW)
            else:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except OSError:
                    proc.kill()
            proc.wait(timeout=2)
        except Exception:
            pass
        finally:
            os._exit(0)
if __name__ == '__main__':
    app = YouTubeDownloaderApp()
    app.mainloop()
