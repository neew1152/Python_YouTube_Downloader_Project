from __future__ import annotations
import os, sys, uuid, shutil, signal, subprocess, threading, queue, re
from typing import Optional
from tkinter import filedialog
import customtkinter as ctk

_POLL, _MAXLINES = 50, 4000
_FONT = ('Consolas', 12)
_ACC, _ACCH = '#1f538d', '#14375e'
_VEXTS = ('.mp4','.mkv','.webm','.mp3','.m4a')
_NOWIN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
_NT = os.name == 'nt'
_HAS_FF = shutil.which('ffmpeg') is not None
_HAS_YT = shutil.which('yt-dlp') is not None
_BAD = re.compile(r'[^\w \-_.]')
_BROWSERS = frozenset({'chrome','firefox','safari','chromium'})


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._proc: Optional[subprocess.Popen] = None
        self._q: queue.Queue[str] = queue.Queue()
        self.title('Python YouTube Downloader 5.0')
        self.geometry(f'{self.winfo_screenwidth()//2}x{self.winfo_screenheight()//2}')
        self.protocol('WM_DELETE_WINDOW', self._quit)
        base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        self.dl = os.path.join(base, 'Downloads')
        self._ui()
        self.after(_POLL, self._drain)

    def _ui(self):
        P = dict(padx=8, pady=3)
        self.url = ctk.CTkEntry(self, placeholder_text='URL')
        self.url.pack(fill='x', padx=8, pady=(8, 3))

        r1 = ctk.CTkFrame(self); r1.pack(fill='x', **P)
        ctk.CTkButton(r1, text='Update', width=70, fg_color='transparent',
                      border_width=1, text_color=('gray10','#DCE4EE'),
                      command=lambda: self._go(self._update)).pack(side='left', padx=4)
        ctk.CTkButton(r1, text='Download Best', fg_color=_ACC, hover_color=_ACCH,
                      command=lambda: self._go(self._best)).pack(side='left', fill='x', expand=True, padx=4)

        self.name = ctk.CTkEntry(self, placeholder_text='Output name (optional)')
        self.name.pack(fill='x', **P)

        rc = ctk.CTkFrame(self); rc.pack(fill='x', **P)
        self._ck = ctk.CTkEntry(rc, placeholder_text='Cookies')
        self._ck.pack(side='left', fill='x', expand=True, padx=(4, 4))
        ctk.CTkButton(rc, text='…', width=30, command=self._pick_ck).pack(side='left', padx=(0, 4))

        self.log = ctk.CTkTextbox(self, font=_FONT, wrap='word', state='disabled')
        self.log.pack(fill='both', expand=True, **P)

        r2 = ctk.CTkFrame(self); r2.pack(fill='x', padx=8, pady=(3, 8))
        ctk.CTkButton(r2, text='Formats', width=70,
                      command=lambda: self._go(self._formats)).pack(side='left', padx=4)
        self.fid = ctk.CTkEntry(r2, placeholder_text='Format ID')
        self.fid.pack(side='left', fill='x', expand=True, padx=4)
        ctk.CTkButton(r2, text='Download', width=80,
                      command=lambda: self._go(self._manual)).pack(side='left', padx=4)

        self._btns = (self.url, self.fid, self.name, self._ck,
                      *r1.winfo_children(), *r2.winfo_children())

    def _pick_ck(self):
        p = filedialog.askopenfilename(
            title='Cookies file', filetypes=[('Text', '*.txt'), ('All', '*.*')])
        if p:
            self._ck.delete(0, 'end'); self._ck.insert(0, p)

    def _ck_args(self) -> list[str]:
        v = self._ck.get().strip()
        if not v: return []
        if v.lower() in _BROWSERS: return ['--cookies-from-browser', v.lower()]
        if os.path.isfile(v):      return ['--cookies', v]
        return []

    def _go(self, fn):
        self._clear(); self._state('disabled')
        threading.Thread(target=lambda: (fn(), self.after(0, lambda: self._state('normal')))
                         if not self._stop.is_set() else None, daemon=True).start()

    def _state(self, s):
        for w in self._btns:
            try: w.configure(state=s)
            except Exception: pass

    @staticmethod
    def _san(t: str) -> str:
        t = t.strip()
        for e in _VEXTS:
            if t.lower().endswith(e): t = t[:-len(e)]; break
        c = _BAD.sub('', t).rstrip()
        return c if c not in ('', '.', '..') else ''

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
            self.log.configure(state='normal'); self.log.insert('end', ''.join(buf))
            n = int(self.log.index('end-1c').split('.')[0])
            if n > _MAXLINES: self.log.delete('1.0', f'{n-_MAXLINES}.0')
            self.log.see('end'); self.log.configure(state='disabled')
        self.after(_POLL, self._drain)

    def _mkdir(self) -> bool:
        try: os.makedirs(self.dl, exist_ok=True); return True
        except OSError: return False

    def _spawn(self, cmd, split_err=False):
        kw = dict(stdout=subprocess.PIPE,
                  stderr=subprocess.PIPE if split_err else subprocess.STDOUT,
                  text=True, encoding='utf-8', errors='replace')
        if _NT: kw['creationflags'] = _NOWIN
        else:   kw['start_new_session'] = True
        with self._lock:
            if self._stop.is_set(): return None
            self._proc = subprocess.Popen(cmd, **kw)
            return self._proc

    def _run(self, cmd) -> bool:
        try:
            p = self._spawn(cmd)
            if not p: return False
            for line in iter(p.stdout.readline, ''):
                if self._stop.is_set(): break
                self._put(line)
            p.stdout.close(); rc = p.wait()
            return rc == 0
        except Exception:
            return False
        finally:
            with self._lock: self._proc = None

    def _probe(self, cmd) -> Optional[str]:
        try:
            p = self._spawn(cmd, split_err=True)
            if not p: return None
            out, _ = p.communicate()
            if p.returncode: return None
            return out.strip()
        except Exception:
            return None
        finally:
            with self._lock: self._proc = None

    def _update(self):
        if self._run(['yt-dlp', '-U']): return
        if not getattr(sys, 'frozen', False):
            self._run([sys.executable, '-m', 'pip', 'install', '-U',
                       '--progress-bar', 'off', 'yt-dlp[default]'])

    def _formats(self):
        u = self.url.get().strip()
        if u:
            self._run(['yt-dlp','--no-playlist','--no-cache-dir',
                       *self._ck_args(), '-F', '--', u])

    def _manual(self):
        u, f = self.url.get().strip(), self.fid.get().strip()
        if not u or not f or not self._mkdir(): return
        n = self._san(self.name.get())
        tmpl = os.path.join(self.dl, f"{n or '%(title)s'}.%(ext)s")
        cmd = ['yt-dlp','--no-playlist','--newline','--no-cache-dir',
               *self._ck_args(), '-f', f, '-o', tmpl]
        if _HAS_FF: cmd += ['--merge-output-format','mkv']
        self._run(cmd + ['--', u])

    def _best(self):
        u = self.url.get().strip()
        if not u or not self._mkdir(): return
        ck = self._ck_args()
        probe = self._probe(['yt-dlp','--print','playlist_title',
                             '--no-warnings','--playlist-items','1',
                             *ck, '--', u])
        if self._stop.is_set(): return
        n = self._san(self.name.get())
        fmt = ['-f','bestvideo+bestaudio/best','--merge-output-format','mkv'] if _HAS_FF else ['-f','best']
        base = ['yt-dlp','--newline','--no-cache-dir', *ck, *fmt]
        if probe is not None and probe.strip() not in ('', 'NA'):
            folder = n or self._san(probe) or f'pl_{uuid.uuid4().hex[:6]}'
            tn = f'{n}_%(autonumber)03d.%(ext)s' if n else '%(playlist_index)03d_%(title)s.%(ext)s'
            self._run(base + ['--yes-playlist','-o',os.path.join(self.dl,folder,tn),'--',u])
        else:
            tn = f'{n}.%(ext)s' if n else '%(title)s.%(ext)s'
            self._run(base + ['--no-playlist','-o',os.path.join(self.dl,tn),'--',u])

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