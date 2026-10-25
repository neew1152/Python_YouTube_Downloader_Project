from __future__ import annotations
import os, sys, uuid, signal, subprocess, threading, queue, re
from typing import Optional
from tkinter import filedialog
import customtkinter as ctk

_POLL, _MAXLINES = (50, 4000)
_ACC, _ACCH = ('#1f538d', '#14375e')
_NOWIN = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
_NT = os.name == 'nt'
_BAD = re.compile(r'[^\w \-_.]')
_PROBE_TIMEOUT = 120
_REENABLE = object()


class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._proc: Optional[subprocess.Popen] = None
        self._q: queue.Queue = queue.Queue()
        self._quitting = False
        self._gen = 0
        self.title('Python Media Downloader 5.5')
        self.geometry(
            f'{self.winfo_screenwidth() // 2}x{self.winfo_screenheight() // 2}'
        )
        self.protocol('WM_DELETE_WINDOW', self._quit)
        base = (
            os.path.dirname(sys.executable)
            if getattr(sys, 'frozen', False)
            else os.path.dirname(os.path.abspath(__file__))
        )
        self.dl = os.path.join(base, 'Downloads')
        self._ui()
        self.after(_POLL, self._drain)

    def _ui(self):
        P = dict(padx=8, pady=3)
        self.url = ctk.CTkEntry(self, placeholder_text='URL')
        self.url.pack(fill='x', padx=8, pady=(8, 3))

        r1 = ctk.CTkFrame(self)
        r1.pack(fill='x', **P)
        ctk.CTkButton(
            r1,
            text='Update',
            width=70,
            fg_color='transparent',
            border_width=1,
            text_color=('gray10', '#DCE4EE'),
            command=lambda: self._go(self._update),
        ).pack(side='left', padx=4)
        ctk.CTkButton(
            r1,
            text='Download Best',
            fg_color=_ACC,
            hover_color=_ACCH,
            command=lambda: self._go(self._best),
        ).pack(side='left', fill='x', expand=True, padx=4)

        self.name = ctk.CTkEntry(self, placeholder_text='Output name (optional)')
        self.name.pack(fill='x', **P)

        self.log = ctk.CTkTextbox(self, wrap='word', state='disabled')
        self.log.pack(fill='both', expand=True, **P)

        r2 = ctk.CTkFrame(self)
        r2.pack(fill='x', **P)
        ctk.CTkButton(
            r2, text='Formats', width=70, command=lambda: self._go(self._formats)
        ).pack(side='left', padx=4)
        self.fid = ctk.CTkEntry(r2, placeholder_text='Format ID')
        self.fid.pack(side='left', fill='x', expand=True, padx=4)
        ctk.CTkButton(
            r2,
            text='Download',
            width=80,
            command=lambda: self._go(self._manual),
        ).pack(side='left', padx=4)

        rc = ctk.CTkFrame(self)
        rc.pack(fill='x', padx=8, pady=(3, 8))
        self._ck = ctk.CTkEntry(rc, placeholder_text='Cookies')
        self._ck.pack(side='left', fill='x', expand=True, padx=(4, 4))
        self._ck_btn = ctk.CTkButton(
            rc, text='…', width=30, command=self._pick_ck
        )
        self._ck_btn.pack(side='left', padx=(0, 4))

        self._btns = (
            self.url,
            self.name,
            self._ck,
            self._ck_btn,
            *r1.winfo_children(),
            *r2.winfo_children(),
        )

    def _pick_ck(self):
        p = filedialog.askopenfilename(
            title='Cookies file',
            filetypes=[('Text / JSON', '*.txt *.json'), ('All files', '*.*')],
        )
        if p:
            self._ck.delete(0, 'end')
            self._ck.insert(0, p)

    @staticmethod
    def _ck_args(v: str) -> list[str]:
        v = v.strip()
        if not v:
            return []
        if os.path.isfile(v):
            return ['--cookies', v]
        return ['--cookies-from-browser', v]

    @staticmethod
    def _san(t: str) -> str:
        t = t.strip()
        root, ext = os.path.splitext(t)
        if ext:
            t = root
        c = _BAD.sub('', t).rstrip()
        if not c or c.lstrip('.') == '':
            return ''
        return c

    def _go(self, fn):
        self._stop.clear()
        self._clear()
        self._state('disabled')
        self._gen += 1
        gen = self._gen
        snap = dict(
            url=self.url.get().strip(),
            fid=self.fid.get().strip(),
            name=self.name.get().strip(),
            ck=self._ck.get().strip(),
        )

        def _wrapper():
            try:
                if not self._stop.is_set():
                    fn(snap)
            finally:
                self._q.put((_REENABLE, gen))

        threading.Thread(target=_wrapper, daemon=True).start()

    def _state(self, s):
        for w in self._btns:
            try:
                w.configure(state=s)
            except Exception:
                pass

    def _put(self, t: str):
        if not self._stop.is_set():
            self._q.put(t)

    def _clear(self):
        try:
            while True:
                self._q.get_nowait()
        except queue.Empty:
            pass
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.configure(state='disabled')

    def _drain(self):
        if self._quitting:
            return
        buf: list = []
        try:
            while True:
                buf.append(self._q.get_nowait())
        except queue.Empty:
            pass
        if buf:
            text_parts: list[str] = []
            for item in buf:
                if isinstance(item, tuple) and item[0] is _REENABLE:
                    if item[1] == self._gen:
                        self._state('normal')
                else:
                    text_parts.append(item)
            if text_parts:
                self.log.configure(state='normal')
                self.log.insert('end', ''.join(text_parts))
                n = int(self.log.index('end-1c').split('.')[0])
                if n > _MAXLINES:
                    self.log.delete('1.0', f'{n - _MAXLINES}.0')
                self.log.see('end')
                self.log.configure(state='disabled')
        try:
            self.after(_POLL, self._drain)
        except Exception:
            pass

    def _mkdir(self) -> bool:
        try:
            os.makedirs(self.dl, exist_ok=True)
            return True
        except OSError:
            return False

    def _spawn(self, cmd, *, split_err=False):
        kw: dict = dict(
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE if split_err else subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        if _NT:
            kw['creationflags'] = _NOWIN
        else:
            kw['start_new_session'] = True
        with self._lock:
            if self._stop.is_set():
                return None
            self._proc = subprocess.Popen(cmd, **kw)
            return self._proc

    def _run(self, cmd) -> bool:
        try:
            p = self._spawn(cmd)
            if not p:
                return False
            for line in iter(p.stdout.readline, ''):
                if self._stop.is_set():
                    break
                self._put(line)
            p.stdout.close()
            try:
                rc = p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._kill_proc(p, wait=True)
                rc = -1
            return rc == 0
        except Exception:
            return False
        finally:
            with self._lock:
                self._proc = None

    def _probe(self, cmd) -> Optional[str]:
        try:
            p = self._spawn(cmd, split_err=True)
            if not p:
                return None
            try:
                out, _ = p.communicate(timeout=_PROBE_TIMEOUT)
            except subprocess.TimeoutExpired:
                self._kill_proc(p, wait=True)
                return None
            if p.returncode:
                return None
            return out.strip()
        except Exception:
            return None
        finally:
            with self._lock:
                self._proc = None

    @staticmethod
    def _kill_proc(p, *, wait=True):
        try:
            if _NT:
                subprocess.call(
                    ['taskkill', '/F', '/T', '/PID', str(p.pid)],
                    creationflags=_NOWIN,
                )
            else:
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except OSError:
                    p.kill()
            if wait:
                p.wait(timeout=5)
        except Exception:
            pass

    def _update(self, snap: dict):
        if self._run(['yt-dlp', '-U']):
            return
        if not getattr(sys, 'frozen', False):
            self._run(
                [
                    sys.executable,
                    '-m',
                    'pip',
                    'install',
                    '-U',
                    '--progress-bar',
                    'off',
                    'yt-dlp[default]',
                ]
            )

    def _formats(self, snap: dict):
        u = snap['url']
        if not u:
            return
        self._run(
            [
                'yt-dlp',
                '--no-playlist',
                '--no-cache-dir',
                *self._ck_args(snap['ck']),
                '-F',
                '--',
                u,
            ]
        )

    def _manual(self, snap: dict):
        u, f = (snap['url'], snap['fid'])
        if not u or not f:
            return
        if not self._mkdir():
            return
        n = self._san(snap['name'])
        tmpl = os.path.join(self.dl, f"{n or '%(title)s'}.%(ext)s")
        cmd = [
            'yt-dlp',
            '--no-playlist',
            '--newline',
            '--no-cache-dir',
            *self._ck_args(snap['ck']),
            '-f',
            f,
            '-o',
            tmpl,
            '--merge-output-format',
            'mkv',
            '--',
            u,
        ]
        self._run(cmd)

    def _best(self, snap: dict):
        u = snap['url']
        if not u:
            return
        if not self._mkdir():
            return
        ck = self._ck_args(snap['ck'])
        probe = self._probe(
            [
                'yt-dlp',
                '--print',
                'playlist_title',
                '--no-warnings',
                '--playlist-items',
                '1',
                '--skip-download',
                *ck,
                '--',
                u,
            ]
        )
        if self._stop.is_set():
            return
        n = self._san(snap['name'])
        fmt = ['-f', 'bestvideo+bestaudio/best', '--merge-output-format', 'mkv']
        base = ['yt-dlp', '--newline', '--no-cache-dir', *ck, *fmt]
        if probe is not None and probe.strip() not in ('', 'NA'):
            folder = n or self._san(probe) or f'pl_{uuid.uuid4().hex[:6]}'
            tn = (
                f'{n}_%(autonumber)03d.%(ext)s'
                if n
                else '%(playlist_index)03d_%(title)s.%(ext)s'
            )
            self._run(
                base
                + [
                    '--yes-playlist',
                    '-o',
                    os.path.join(self.dl, folder, tn),
                    '--',
                    u,
                ]
            )
        else:
            tn = f'{n}.%(ext)s' if n else '%(title)s.%(ext)s'
            self._run(
                base + ['--no-playlist', '-o', os.path.join(self.dl, tn), '--', u]
            )

    def _quit(self):
        self._quitting = True
        self._stop.set()
        self.withdraw()
        with self._lock:
            p = self._proc
        if p and p.poll() is None:
            self._kill_proc(p, wait=True)
        self.destroy()
        sys.exit(0)


if __name__ == '__main__':
    App().mainloop()