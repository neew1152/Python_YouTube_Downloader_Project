from __future__ import annotations
import os, sys, uuid, shutil, signal, subprocess, threading, queue, re
from typing import Optional
import customtkinter as ctk

_POLL = 50
_MAXLINES = 4000
_FONT = ('Consolas', 12)
_ACC, _ACCH = '#1f538d', '#14375e'
_VEXTS = ('.mp4','.mkv','.webm','.mp3','.m4a')
_NOWIN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
_NT = os.name == 'nt'
_FFMPEG = shutil.which('ffmpeg') is not None
_YTDLP = shutil.which('yt-dlp') is not None
_BAD = re.compile(r'[^\w \-_.]')


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._proc: Optional[subprocess.Popen] = None
        self._q: queue.Queue[str] = queue.Queue()
        self.title('Python Media Downloader 4.0')
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f'{sw//2}x{sh//2}')
        self.protocol('WM_DELETE_WINDOW', self._quit)
        base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        self.dl = os.path.join(base, 'Downloads')
        self._ui()
        self._deps()
        self.after(_POLL, self._drain)

    def _ui(self):
        P = dict(padx=10, pady=5)
        self.url = ctk.CTkEntry(self, placeholder_text='URL'); self.url.pack(fill='x', padx=10, pady=(10,5))
        row = ctk.CTkFrame(self); row.pack(fill='x', **P)
        self.btn_upd = ctk.CTkButton(row, text='Update yt-dlp', command=lambda: self._go(self._update),
                                    fg_color='transparent', border_width=2, text_color=('gray10','#DCE4EE'))
        self.btn_upd.pack(side='left', padx=5, pady=5)
        self.btn_best = ctk.CTkButton(row, text='Download (Best)', command=lambda: self._go(self._best),
                                    fg_color=_ACC, hover_color=_ACCH)
        self.btn_best.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self.name = ctk.CTkEntry(self, placeholder_text='Output name (optional)'); self.name.pack(fill='x', **P)
        self.log = ctk.CTkTextbox(self, font=_FONT, wrap='word', state='disabled'); self.log.pack(fill='both', expand=True, **P)
        row2 = ctk.CTkFrame(self); row2.pack(fill='x', padx=10, pady=(5,10))
        self.btn_ls = ctk.CTkButton(row2, text='List Formats', command=lambda: self._go(self._search))
        self.btn_ls.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self.fid = ctk.CTkEntry(row2, placeholder_text='Format ID'); self.fid.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self.btn_dl = ctk.CTkButton(row2, text='Download (Format ID)', command=lambda: self._go(self._manual))
        self.btn_dl.pack(side='left', fill='x', expand=True, padx=5, pady=5)
        self._btns = (self.btn_upd, self.btn_best, self.btn_ls, self.btn_dl,
                    self.url, self.fid, self.name)

    def _go(self, fn):
        self._clear(); self._state('disabled')
        threading.Thread(target=self._wrap(fn), daemon=True).start()

    def _wrap(self, fn):
        def run():
            try: fn()
            finally:
                if not self._stop.is_set(): self.after(0, lambda: self._state('normal'))
        return run

    def _state(self, s):
        for w in self._btns:
            w.configure(state=s)

    @staticmethod
    def _san(t: str) -> str:
        t = t.strip()
        for e in _VEXTS:
            if t.lower().endswith(e): t = t[:-len(e)]; break
        c = _BAD.sub('', t).rstrip()
        return c if c and c not in ('.','..') else ''

    def _put(self, t: str):
        if not self._stop.is_set(): self._q.put(t)

    def _clear(self):
        try:
            while True: self._q.get_nowait()
        except queue.Empty: pass
        self.log.configure(state='normal'); self.log.delete('1.0','end'); self.log.configure(state='disabled')

    def _drain(self):
        if self._stop.is_set(): return
        buf = []
        try:
            while True: buf.append(self._q.get_nowait())
        except queue.Empty: pass
        if buf:
            self.log.configure(state='normal'); self.log.insert('end',''.join(buf))
            n = int(self.log.index('end-1c').split('.')[0])
            if n > _MAXLINES: self.log.delete('1.0', f'{n-_MAXLINES}.0')
            self.log.see('end'); self.log.configure(state='disabled')
        self.after(_POLL, self._drain)

    @staticmethod
    def _popen_kw(split_err=False) -> dict:
        kw = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE if split_err else subprocess.STDOUT,
                  text=True, encoding='utf-8', errors='replace')
        if _NT: kw['creationflags'] = _NOWIN
        else:   kw['start_new_session'] = True
        return kw

    def _spawn(self, cmd, split_err=False):
        with self._lock:
            if self._stop.is_set(): return None
            self._proc = p = subprocess.Popen(cmd, **self._popen_kw(split_err))
            return p

    def _done(self):
        with self._lock: self._proc = None

    def _run(self, cmd, label) -> bool:
        self._put(f"\n--- {label} ---\n> {' '.join(cmd)}\n\n")
        try:
            p = self._spawn(cmd)
            if p is None: return False
            for line in iter(p.stdout.readline, ''):
                if self._stop.is_set(): break
                self._put(line)
            p.stdout.close()
            rc = p.wait()
            if not self._stop.is_set():
                if rc: self._put("\n[NOTICE] Consider updating yt-dlp.\n")
                self._put(f"\n--- {label}: {'OK' if rc==0 else f'EXIT {rc}'} ---\n")
            return rc == 0
        except Exception as e:
            self._put(f'\n--- ERROR ({label}) ---\n{e}\n'); return False
        finally: self._done()

    def _capture(self, cmd) -> Optional[str]:
        try:
            p = self._spawn(cmd, split_err=True)
            if p is None: return None
            out, err = p.communicate()
            if p.returncode: self._put(f'\n[PROBE FAIL] {err}\n'); return None
            return out.strip()
        except Exception as e:
            self._put(f'\n[PROBE ERROR] {e}\n'); return None
        finally: self._done()

    def _deps(self):
        if not _YTDLP:  self._put("\n[ERROR] yt-dlp not found on PATH.\n")
        if not _FFMPEG: self._put("\n[WARN] ffmpeg missing – limited to pre-merged ≤720p.\n")

    def _update(self):
        if self._run(['yt-dlp','-U'], 'UPDATE'): return
        if getattr(sys,'frozen',False):
            self._put('\n[ERROR] Self-update failed. Update manually.\n')
        else:
            self._run([sys.executable,'-m','pip','install','-U','--progress-bar','off','yt-dlp[default]'], 'PIP UPDATE')

    def _search(self):
        u = self.url.get().strip()
        if not u: self._put('[ERROR] No URL.\n'); return
        self._run(['yt-dlp','--no-playlist','--no-cache-dir','--no-check-certificate','-F','--',u], 'FORMATS')

    def _manual(self):
        u, f = self.url.get().strip(), self.fid.get().strip()
        if not f: self._put('[ERROR] No format ID.\n'); return
        if not u or not self._mkdir(): return
        n = self._san(self.name.get().strip())
        tmpl = os.path.join(self.dl, f"{n or '%(title)s'}.%(ext)s")
        cmd = ['yt-dlp','--no-playlist','--newline','--no-cache-dir','--no-check-certificate','-f',f,'-o',tmpl]
        if _FFMPEG: cmd += ['--merge-output-format','mkv']
        self._run(cmd+['--',u], 'DOWNLOAD')

    def _best(self):
        u = self.url.get().strip()
        if not u or not self._mkdir(): return
        probe = self._capture(['yt-dlp','--print','playlist_title','--no-warnings','--playlist-items','1','--',u])
        if probe is None or self._stop.is_set(): return
        playlist = bool(probe) and probe.strip() != 'NA'
        n = self._san(self.name.get().strip())
        fmt = ['-f','bestvideo+bestaudio/best','--merge-output-format','mkv'] if _FFMPEG else ['-f','best']
        base = ['yt-dlp','--newline','--no-cache-dir','--no-check-certificate',*fmt]
        if playlist:
            folder = n or self._san(probe) or f'playlist_{uuid.uuid4().hex[:8]}'
            tn = f'{n}_%(autonumber)03d.%(ext)s' if n else '%(playlist_index)03d_%(title)s.%(ext)s'
            self._run(base+['--yes-playlist','-o',os.path.join(self.dl,folder,tn),'--',u], 'PLAYLIST')
        else:
            tn = f'{n}.%(ext)s' if n else '%(title)s.%(ext)s'
            self._run(base+['--no-playlist','-o',os.path.join(self.dl,tn),'--',u], 'DOWNLOAD')
        if not self._stop.is_set(): self._put('\n--- DONE ---\n')

    def _mkdir(self) -> bool:
        try: os.makedirs(self.dl, exist_ok=True); return True
        except OSError as e: self._put(f'[ERROR] {e}\n'); return False

    def _quit(self):
        self._stop.set(); self.withdraw()
        with self._lock: p = self._proc
        if p and p.poll() is None:
            threading.Thread(target=self._kill, args=(p,), daemon=True).start()
        else: self.destroy(); sys.exit(0)

    @staticmethod
    def _kill(p):
        try:
            if _NT: subprocess.call(['taskkill','/F','/T','/PID',str(p.pid)], creationflags=_NOWIN)
            else:
                try: os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except OSError: p.kill()
            p.wait(timeout=2)
        except Exception: pass
        finally: os._exit(0)


if __name__ == '__main__':
    App().mainloop()