import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
import tempfile
import threading
import winreg
import subprocess
import math

# ══════════════════════════════════════════════
#  FARBEN
# ══════════════════════════════════════════════
C_BG          = "#0d0d1a"
C_SIDEBAR     = "#12122a"
C_CARD        = "#1a1a35"
C_CARD_BORDER = "#2a2a50"
C_ACCENT1     = "#38bdf8"
C_ACCENT2     = "#8b5cf6"
C_ACCENT3     = "#06d6a0"
C_RED         = "#f43f5e"
C_TEXT        = "#e2e8f0"
C_TEXT_SOFT   = "#7c8db5"
C_TEXT_DIM    = "#3d4a6b"

FONT_NAV  = ("Segoe UI", 10, "bold")
FONT_HEAD = ("Segoe UI", 18, "bold")
FONT_SUB  = ("Segoe UI", 9)
FONT_CARD = ("Segoe UI", 10, "bold")
FONT_BODY = ("Segoe UI", 9)
FONT_BTN  = ("Segoe UI", 10, "bold")
FONT_LOG  = ("Consolas", 9)


def fmt_size(b):
    if b < 1024:       return f"{b} B"
    elif b < 1024**2:  return f"{b/1024:.1f} KB"
    elif b < 1024**3:  return f"{b/1024**2:.1f} MB"
    else:              return f"{b/1024**3:.2f} GB"


def dir_size(path):
    total = 0
    try:
        for root, _, files in os.walk(path):
            for f in files:
                try: total += os.path.getsize(os.path.join(root, f))
                except: pass
    except: pass
    return total


# ══════════════════════════════════════════════
#  ANIMIERTER HINTERGRUND
# ══════════════════════════════════════════════
class AnimatedBg(tk.Canvas):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=C_BG, highlightthickness=0, bd=0, **kw)
        self._t = 0
        self._orbs = [
            {"rx": 0.15, "ry": 0.25, "r": 180, "col": (56, 189, 248),  "sp": 0.7},
            {"rx": 0.82, "ry": 0.65, "r": 220, "col": (139, 92, 246),  "sp": 0.5},
            {"rx": 0.50, "ry": 0.88, "r": 130, "col": (6, 214, 160),   "sp": 0.9},
            {"rx": 0.88, "ry": 0.12, "r": 110, "col": (244, 63, 94),   "sp": 0.6},
        ]
        self.after(200, self._tick)

    def _blend(self, r, g, b, a):
        br, bg_, bb = 13, 13, 26
        return "#{:02x}{:02x}{:02x}".format(
            int(br + (r  - br) * a),
            int(bg_ + (g - bg_) * a),
            int(bb + (b  - bb) * a))

    def _tick(self):
        try:
            self.delete("orb")
            w = self.winfo_width()
            h = self.winfo_height()
            if w < 2 or h < 2:
                self.after(100, self._tick)
                return
            t = self._t
            for o in self._orbs:
                cx = o["rx"] * w
                cy = o["ry"] * h + math.sin(t * o["sp"] * 0.05) * 22
                R  = o["r"] + math.sin(t * o["sp"] * 0.04) * 18
                for i in range(10, 0, -1):
                    f = i / 10
                    self.create_oval(cx - R*f, cy - R*f,
                                     cx + R*f, cy + R*f,
                                     fill=self._blend(*o["col"], 0.07*f),
                                     outline="", tags="orb")
            self._t += 1
            self.after(40, self._tick)
        except tk.TclError:
            pass


# ══════════════════════════════════════════════
#  HAUPT-APP
# ══════════════════════════════════════════════
class MultiTool(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("⚡ Luca's MultiTool")
        self.geometry("860x600")
        self.minsize(820, 560)
        self.configure(bg=C_BG)
        self._active_key = ""
        self._build_layout()
        self._show_tab("cleaner")
        self.bind("<Configure>", self._on_resize)

    def _build_layout(self):
        self.sidebar = tk.Frame(self, bg=C_SIDEBAR, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Frame(self, bg=C_CARD_BORDER, width=1).pack(side="left", fill="y")

        self.bg_canvas = AnimatedBg(self)
        self.bg_canvas.pack(side="left", fill="both", expand=True)

        self.main = tk.Frame(self.bg_canvas, bg=C_BG)
        self.main.place(x=0, y=0, relwidth=1, relheight=1)
        self._build_sidebar()

    def _build_sidebar(self):
        logo = tk.Frame(self.sidebar, bg=C_SIDEBAR)
        logo.pack(fill="x", padx=18, pady=(22, 6))
        tk.Label(logo, text="⚡ MultiTool",
                 font=("Segoe UI", 15, "bold"),
                 fg=C_ACCENT2, bg=C_SIDEBAR, anchor="w").pack(fill="x")
        tk.Label(logo, text="by Luca  •  v1.0",
                 font=("Segoe UI", 8), fg=C_TEXT_DIM,
                 bg=C_SIDEBAR, anchor="w").pack(fill="x")
        tk.Frame(self.sidebar, bg=C_CARD_BORDER,
                 height=1).pack(fill="x", padx=14, pady=12)

        self.nav_btns = {}
        tabs = [("cleaner","🧹","Cleaner"),
                ("browser","🌐","Browser"),
                ("startup","🚀","Autostart"),
                ("disk",   "💾","Festplatte"),
                ("tools",  "🔧","Tools")]

        for key, icon, label in tabs:
            row   = tk.Frame(self.sidebar, bg=C_SIDEBAR, cursor="hand2")
            row.pack(fill="x", padx=8, pady=2)
            inner = tk.Frame(row, bg=C_SIDEBAR)
            inner.pack(fill="x", padx=4)
            ilbl  = tk.Label(inner, text=icon, font=("Segoe UI", 12),
                             bg=C_SIDEBAR, fg=C_TEXT_SOFT, width=2, anchor="w")
            ilbl.pack(side="left", padx=(8, 4), pady=8)
            tlbl  = tk.Label(inner, text=label, font=FONT_NAV,
                             bg=C_SIDEBAR, fg=C_TEXT_SOFT, anchor="w")
            tlbl.pack(side="left", pady=8)
            bar   = tk.Frame(row, bg=C_SIDEBAR, width=3)
            bar.pack(side="right", fill="y")
            self.nav_btns[key] = {"row": row, "inner": inner,
                                  "icon": ilbl, "text": tlbl, "bar": bar}
            all_w = [row, inner, ilbl, tlbl]
            for w in all_w:
                w.bind("<Button-1>", lambda e, k=key: self._show_tab(k))
                w.bind("<Enter>",    lambda e, k=key: self._nav_hover(k, True))
                w.bind("<Leave>",    lambda e, k=key: self._nav_hover(k, False))

        tk.Label(self.sidebar, text="Windows only",
                 font=("Segoe UI", 8), fg=C_TEXT_DIM,
                 bg=C_SIDEBAR).pack(side="bottom", pady=10)

    def _nav_hover(self, key, on):
        if key == self._active_key: return
        bg = "#1e1e40" if on else C_SIDEBAR
        nb = self.nav_btns[key]
        for w in [nb["row"], nb["inner"], nb["icon"], nb["text"]]:
            w.config(bg=bg)

    def _nav_style(self, active):
        self._active_key = active
        for key, nb in self.nav_btns.items():
            if key == active:
                for w in [nb["row"], nb["inner"], nb["icon"], nb["text"]]:
                    w.config(bg="#1e1040")
                nb["text"].config(fg=C_ACCENT2)
                nb["icon"].config(fg=C_ACCENT1)
                nb["bar"].config(bg=C_ACCENT2)
            else:
                for w in [nb["row"], nb["inner"], nb["icon"], nb["text"]]:
                    w.config(bg=C_SIDEBAR)
                nb["text"].config(fg=C_TEXT_SOFT)
                nb["icon"].config(fg=C_TEXT_SOFT)
                nb["bar"].config(bg=C_SIDEBAR)

    def _show_tab(self, key):
        for w in self.main.winfo_children():
            w.destroy()
        self._nav_style(key)
        {"cleaner": self._tab_cleaner,
         "browser": self._tab_browser,
         "startup": self._tab_startup,
         "disk":    self._tab_disk,
         "tools":   self._tab_tools}[key]()

    def _on_resize(self, e):
        pass

    # ── Shared Helpers ───────────────────────────
    def _header(self, icon, title, sub):
        f = tk.Frame(self.main, bg=C_BG)
        f.pack(fill="x", padx=26, pady=(20, 0))
        tk.Label(f, text=f"{icon}  {title}", font=FONT_HEAD,
                 fg=C_ACCENT2, bg=C_BG, anchor="w").pack(fill="x")
        tk.Label(f, text=sub, font=FONT_SUB,
                 fg=C_TEXT_SOFT, bg=C_BG, anchor="w").pack(fill="x", pady=(2, 0))
        tk.Frame(self.main, bg=C_CARD_BORDER,
                 height=1).pack(fill="x", padx=26, pady=10)

    def _card(self, parent, title="", pady=(0, 10)):
        outer = tk.Frame(parent, bg=C_CARD,
                         highlightthickness=1,
                         highlightbackground=C_CARD_BORDER)
        outer.pack(fill="x", padx=26, pady=pady)
        if title:
            tk.Label(outer, text=title, font=FONT_CARD,
                     fg=C_ACCENT1, bg=C_CARD,
                     anchor="w").pack(fill="x", padx=14, pady=(10, 4))
        return outer

    def _btn(self, parent, text, cmd, color=C_ACCENT2, width=16):
        b = tk.Button(parent, text=text, font=FONT_BTN,
                      fg=C_BG, bg=color,
                      activebackground=C_ACCENT1,
                      activeforeground=C_BG,
                      relief="flat", bd=0,
                      cursor="hand2", width=width,
                      command=cmd)
        b.bind("<Enter>", lambda e: b.config(bg=C_ACCENT1))
        b.bind("<Leave>", lambda e: b.config(bg=color))
        return b

    def _progress(self, parent):
        s = ttk.Style()
        s.theme_use("clam")
        uid = f"PB{id(parent)}.Horizontal.TProgressbar"
        s.configure(uid, troughcolor=C_CARD_BORDER,
                    background=C_ACCENT2,
                    bordercolor=C_CARD_BORDER,
                    lightcolor=C_ACCENT1,
                    darkcolor=C_ACCENT2, thickness=8)
        return ttk.Progressbar(parent, style=uid,
                               mode="determinate", maximum=100)

    def _logbox(self, parent, h=7):
        f = tk.Frame(parent, bg=C_CARD,
                     highlightthickness=1,
                     highlightbackground=C_CARD_BORDER)
        f.pack(fill="both", expand=True, padx=26, pady=(0, 14))
        log = tk.Text(f, font=FONT_LOG, fg=C_TEXT,
                      bg="#0a0a18", insertbackground=C_ACCENT1,
                      relief="flat", bd=0,
                      state="disabled", wrap="word", height=h)
        sb = ttk.Scrollbar(f, command=log.yview)
        log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        log.pack(fill="both", expand=True, padx=6, pady=6)
        log.tag_configure("ok",   foreground=C_ACCENT3)
        log.tag_configure("warn", foreground="#fbbf24")
        log.tag_configure("err",  foreground=C_RED)
        log.tag_configure("dim",  foreground=C_TEXT_DIM)
        log.tag_configure("head", foreground=C_ACCENT1,
                          font=("Consolas", 9, "bold"))
        return log

    def _log(self, log, msg, tag=""):
        def _do():
            log.config(state="normal")
            log.insert("end", msg + "\n", tag)
            log.see("end")
            log.config(state="disabled")
        self.after(0, _do)

    def _chk(self, parent, text, var):
        return tk.Checkbutton(
            parent, text=text, variable=var,
            font=FONT_BODY, fg=C_TEXT, bg=C_CARD,
            activebackground=C_CARD,
            activeforeground=C_ACCENT1,
            selectcolor=C_BG, cursor="hand2")

    # ══════════════════════════════════════════
    #  CLEANER
    # ══════════════════════════════════════════
    def _tab_cleaner(self):
        self._header("🧹", "System Cleaner",
                     "Temporäre Dateien, Cache und Papierkorb bereinigen")
        self.cv = {}
        items = [("temp",      "Windows Temp  (C:\\Windows\\Temp)"),
                 ("user_temp", "Benutzer Temp-Ordner"),
                 ("prefetch",  "Prefetch-Cache"),
                 ("recycle",   "Papierkorb"),
                 ("thumb",     "Thumbnail-Cache")]
        card = self._card(self.main, "Was soll bereinigt werden?")
        inner = tk.Frame(card, bg=C_CARD)
        inner.pack(fill="x", padx=10, pady=(0, 10))
        for k, lbl in items:
            v = tk.BooleanVar(value=True)
            self.cv[k] = v
            self._chk(inner, lbl, v).pack(anchor="w", pady=2, padx=4)

        bf = tk.Frame(self.main, bg=C_BG)
        bf.pack(fill="x", padx=26, pady=(0, 8))
        self._btn(bf, "🔍  Analysieren", self._scan_clean, C_ACCENT1, 14).pack(
            side="left", padx=(0, 8), ipady=8)
        self._btn(bf, "🗑  Bereinigen", self._run_clean, C_ACCENT2, 14).pack(
            side="left", ipady=8)
        self.cstat = tk.Label(bf, text="", font=FONT_BODY,
                              fg=C_TEXT_SOFT, bg=C_BG)
        self.cstat.pack(side="left", padx=12)

        pb = self._progress(self.main)
        pb.pack(fill="x", padx=26, pady=(0, 6))
        self.cpb = pb

        self.clog = self._logbox(self.main, 7)
        self._log(self.clog, "  Bereit. Klicke Analysieren zum Starten.", "dim")

    def _clean_paths(self):
        paths, v = [], self.cv
        if v["temp"].get():      paths.append(r"C:\Windows\Temp")
        if v["user_temp"].get(): paths.append(tempfile.gettempdir())
        if v["prefetch"].get():  paths.append(r"C:\Windows\Prefetch")
        if v["recycle"].get():
            for d in "CDEFGH":
                p = f"{d}:\\$Recycle.Bin"
                if os.path.exists(p): paths.append(p)
        if v["thumb"].get():
            paths.append(os.path.expandvars(
                r"%LOCALAPPDATA%\Microsoft\Windows\Explorer"))
        return paths

    def _scan_clean(self):
        self.cstat.config(text="Scanne ...")
        def _do():
            total = sum(
                dir_size(p) if os.path.isdir(p)
                else (os.path.getsize(p) if os.path.isfile(p) else 0)
                for p in self._clean_paths())
            msg = f"Gefunden: ca. {fmt_size(total)}"
            self.after(0, lambda: self.cstat.config(text=msg))
            self._log(self.clog, f"  Scan fertig - {fmt_size(total)} gefunden.", "ok")
        threading.Thread(target=_do, daemon=True).start()

    def _run_clean(self):
        if not messagebox.askyesno("Bereinigen?", "Jetzt bereinigen?"):
            return
        self.cpb["value"] = 0
        def _do():
            paths = self._clean_paths()
            freed = errors = 0
            for i, path in enumerate(paths):
                self.cpb["value"] = int(i / max(len(paths), 1) * 100)
                if not os.path.exists(path): continue
                self._log(self.clog, f"  {path}", "head")
                try:
                    for e in os.scandir(path):
                        try:
                            if e.is_file(follow_symlinks=False):
                                sz = e.stat().st_size
                                os.remove(e.path); freed += sz
                                self._log(self.clog, f"     ok {e.name}", "ok")
                            elif e.is_dir(follow_symlinks=False):
                                sz = dir_size(e.path)
                                shutil.rmtree(e.path, ignore_errors=True)
                                freed += sz
                                self._log(self.clog, f"     {e.name}/", "ok")
                        except PermissionError: errors += 1
                        except: errors += 1
                except Exception as ex:
                    self._log(self.clog, f"  Fehler: {ex}", "warn")
                    errors += 1
            self.cpb["value"] = 100
            msg = (f"  Fertig - {fmt_size(freed)} freigegeben"
                   + (f"  ({errors} uebersprungen)" if errors else ""))
            self._log(self.clog, "  " + "-"*42, "dim")
            self._log(self.clog, msg, "ok")
            self.after(0, lambda: self.cstat.config(text=msg.strip()))
        threading.Thread(target=_do, daemon=True).start()

    # ══════════════════════════════════════════
    #  BROWSER
    # ══════════════════════════════════════════
    def _tab_browser(self):
        self._header("🌐", "Browser Cleaner",
                     "Cache, Cookies und Verlauf bereinigen")
        self.bv = {}
        card1 = self._card(self.main, "Browser auswaehlen")
        i1 = tk.Frame(card1, bg=C_CARD)
        i1.pack(fill="x", padx=10, pady=(0, 10))
        for k, l in [("chrome", "Google Chrome"),
                     ("edge",   "Microsoft Edge"),
                     ("firefox","Mozilla Firefox")]:
            v = tk.BooleanVar(value=True); self.bv[k] = v
            self._chk(i1, l, v).pack(anchor="w", pady=2, padx=4)

        card2 = self._card(self.main, "Was loeschen?", (0, 10))
        i2 = tk.Frame(card2, bg=C_CARD)
        i2.pack(fill="x", padx=10, pady=(0, 10))
        for k, l in [("cache","Cache"),("cookies","Cookies"),("history","Verlauf")]:
            v = tk.BooleanVar(value=True); self.bv[k] = v
            self._chk(i2, l, v).pack(anchor="w", pady=2, padx=4)

        bf = tk.Frame(self.main, bg=C_BG)
        bf.pack(fill="x", padx=26, pady=(0, 8))
        self._btn(bf, "Loeschen", self._run_browser, C_ACCENT2, 22).pack(
            side="left", ipady=8)
        self.bstat = tk.Label(bf, text="", font=FONT_BODY, fg=C_TEXT_SOFT, bg=C_BG)
        self.bstat.pack(side="left", padx=12)
        self.blog = self._logbox(self.main, 8)

    def _browser_paths(self):
        local = os.environ.get("LOCALAPPDATA", "")
        roam  = os.environ.get("APPDATA", "")
        v = self.bv; paths = []
        if v["chrome"].get():
            base = os.path.join(local, "Google", "Chrome", "User Data", "Default")
            if v["cache"].get():
                paths += [os.path.join(base, "Cache"),
                          os.path.join(base, "Code Cache")]
            if v["cookies"].get(): paths.append(os.path.join(base, "Cookies"))
            if v["history"].get(): paths.append(os.path.join(base, "History"))
        if v["edge"].get():
            base = os.path.join(local, "Microsoft", "Edge", "User Data", "Default")
            if v["cache"].get():   paths.append(os.path.join(base, "Cache"))
            if v["cookies"].get(): paths.append(os.path.join(base, "Cookies"))
            if v["history"].get(): paths.append(os.path.join(base, "History"))
        if v["firefox"].get():
            ff = os.path.join(roam, "Mozilla", "Firefox", "Profiles")
            if os.path.exists(ff):
                for p in os.listdir(ff):
                    pp = os.path.join(ff, p)
                    if v["cache"].get():   paths.append(os.path.join(pp, "cache2"))
                    if v["cookies"].get(): paths.append(os.path.join(pp, "cookies.sqlite"))
                    if v["history"].get(): paths.append(os.path.join(pp, "places.sqlite"))
        return paths

    def _run_browser(self):
        def _do():
            freed = errors = 0
            for p in self._browser_paths():
                if not os.path.exists(p): continue
                self._log(self.blog, f"  {os.path.basename(p)}", "head")
                try:
                    if os.path.isfile(p):
                        freed += os.path.getsize(p); os.remove(p)
                    elif os.path.isdir(p):
                        freed += dir_size(p)
                        shutil.rmtree(p, ignore_errors=True)
                    self._log(self.blog, "     geloescht", "ok")
                except PermissionError:
                    self._log(self.blog, "     Browser offen? Bitte schliessen.", "warn")
                    errors += 1
                except: errors += 1
            msg = (f"  {fmt_size(freed)} freigegeben"
                   + (f"  ({errors} Fehler)" if errors else ""))
            self._log(self.blog, "  " + "-"*42, "dim")
            self._log(self.blog, msg, "ok")
            self.after(0, lambda: self.bstat.config(text=msg.strip()))
        threading.Thread(target=_do, daemon=True).start()

    # ══════════════════════════════════════════
    #  AUTOSTART
    # ══════════════════════════════════════════
    def _tab_startup(self):
        self._header("🚀", "Autostart Manager",
                     "Programme beim Windows-Start verwalten")
        bf = tk.Frame(self.main, bg=C_BG)
        bf.pack(fill="x", padx=26, pady=(0, 10))
        self._btn(bf, "Aktualisieren", self._load_startup, C_ACCENT1, 14).pack(
            side="left", ipady=6)

        s = ttk.Style(); s.theme_use("clam")
        s.configure("D.Treeview",
                    background="#0a0a18", fieldbackground="#0a0a18",
                    foreground=C_TEXT, rowheight=28, font=FONT_BODY)
        s.configure("D.Treeview.Heading",
                    background=C_CARD, foreground=C_ACCENT1,
                    font=("Segoe UI", 9, "bold"))
        s.map("D.Treeview",
              background=[("selected", C_ACCENT2)],
              foreground=[("selected", "white")])

        tf = tk.Frame(self.main, bg=C_CARD,
                      highlightthickness=1, highlightbackground=C_CARD_BORDER)
        tf.pack(fill="both", expand=True, padx=26, pady=(0, 16))
        cols = ("Name", "Pfad", "Quelle")
        self.tree = ttk.Treeview(tf, columns=cols, show="headings",
                                 style="D.Treeview")
        for col, w in zip(cols, [160, 310, 90]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w)
        sb = ttk.Scrollbar(tf, command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self._load_startup()

    def _load_startup(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        for hive, path, src in [
            (winreg.HKEY_CURRENT_USER,
             r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM")]:
            try:
                key = winreg.OpenKey(hive, path); i = 0
                while True:
                    try:
                        n, v, _ = winreg.EnumValue(key, i)
                        self.tree.insert("", "end", values=(n, v, src)); i += 1
                    except OSError: break
            except: pass
        sf = os.path.expandvars(
            r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
        if os.path.exists(sf):
            for f in os.listdir(sf):
                self.tree.insert("", "end", values=(f, sf, "Ordner"))

    # ══════════════════════════════════════════
    #  DISK
    # ══════════════════════════════════════════
    def _tab_disk(self):
        self._header("💾", "Festplatten-Info",
                     "Speicherplatz und Laufwerke im Ueberblick")
        self._btn(self.main, "Aktualisieren", self._load_disk, C_ACCENT1, 14).pack(
            anchor="w", padx=26, pady=(0, 10), ipady=6)
        self.dframe = tk.Frame(self.main, bg=C_BG)
        self.dframe.pack(fill="both", expand=True, padx=26)
        self._load_disk()

    def _load_disk(self):
        for w in self.dframe.winfo_children(): w.destroy()
        for letter in "CDEFGHIJ":
            p = f"{letter}:\\"
            if not os.path.exists(p): continue
            try:
                total, used, free = shutil.disk_usage(p)
            except: continue
            pct   = used / total if total > 0 else 0
            color = C_RED if pct > .85 else C_ACCENT2 if pct > .6 else C_ACCENT3

            card = tk.Frame(self.dframe, bg=C_CARD,
                            highlightthickness=1,
                            highlightbackground=C_CARD_BORDER)
            card.pack(fill="x", pady=6)
            top = tk.Frame(card, bg=C_CARD)
            top.pack(fill="x", padx=14, pady=(12, 4))
            tk.Label(top, text=f"Laufwerk {letter}:",
                     font=("Segoe UI", 11, "bold"),
                     fg=C_ACCENT1, bg=C_CARD).pack(side="left")
            tk.Label(top,
                     text=f"{fmt_size(used)} / {fmt_size(total)}  -  {fmt_size(free)} frei",
                     font=FONT_BODY, fg=C_TEXT_SOFT, bg=C_CARD).pack(side="right")

            track = tk.Frame(card, bg=C_CARD_BORDER, height=10)
            track.pack(fill="x", padx=14, pady=(0, 4))
            track.pack_propagate(False)
            fill_bar = tk.Frame(track, bg=color, height=10)
            fill_bar.place(x=0, y=0, relwidth=0, height=10)
            tk.Label(card, text=f"{int(pct*100)}%",
                     font=("Segoe UI", 8, "bold"),
                     fg=color, bg=C_CARD).pack(anchor="e", padx=14, pady=(0, 8))
            self._anim_bar(fill_bar, pct)

    def _anim_bar(self, bar, target, step=0):
        steps = 30
        frac  = (step / steps) ** 0.5 * target if step < steps else target
        bar.place_configure(relwidth=frac)
        if step < steps:
            self.after(int(step * 16),
                       lambda: self._anim_bar(bar, target, step + 1))

    # ══════════════════════════════════════════
    #  TOOLS
    # ══════════════════════════════════════════
    def _tab_tools(self):
        self._header("🔧", "System-Tools",
                     "Nuetzliche Windows-Werkzeuge schnell oeffnen")
        tools = [
            ("🖥", "Task-Manager",          "taskmgr"),
            ("⚙", "Systemkonfig.",          "msconfig"),
            ("📋","Ereignisanzeige",         "eventvwr"),
            ("💻","Systeminfos",             "msinfo32"),
            ("🧹","Datentraegerberein.",     "cleanmgr"),
            ("🔍","Ressourcenmonitor",       "resmon"),
            ("📦","Programme & Features",   "appwiz.cpl"),
            ("⚙", "Dienste",               "services.msc"),
            ("🖱","Geraete-Manager",         "devmgmt.msc"),
            ("🌐","Netzwerk-Reset",
             "cmd /c netsh winsock reset && pause"),
        ]
        grid = tk.Frame(self.main, bg=C_BG)
        grid.pack(fill="both", expand=True, padx=26, pady=(0, 16))

        for i, (icon, label, cmd) in enumerate(tools):
            row, col = divmod(i, 2)

            def run(c=cmd):
                try: subprocess.Popen(c, shell=True)
                except Exception as ex:
                    messagebox.showerror("Fehler", str(ex))

            cell = tk.Frame(grid, bg=C_CARD,
                            highlightthickness=1,
                            highlightbackground=C_CARD_BORDER,
                            cursor="hand2")
            cell.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            inner = tk.Frame(cell, bg=C_CARD)
            inner.pack(expand=True, fill="both", padx=14, pady=12)
            ilbl = tk.Label(inner, text=icon, font=("Segoe UI", 18),
                            bg=C_CARD, fg=C_ACCENT1)
            ilbl.pack()
            tlbl = tk.Label(inner, text=label, font=("Segoe UI", 9, "bold"),
                            bg=C_CARD, fg=C_TEXT)
            tlbl.pack()

            def bind(c, i_, ls, r=run):
                def on_enter(e):
                    c.config(bg="#1e1040", highlightbackground=C_ACCENT2)
                    i_.config(bg="#1e1040")
                    for l in ls: l.config(bg="#1e1040")
                def on_leave(e):
                    c.config(bg=C_CARD, highlightbackground=C_CARD_BORDER)
                    i_.config(bg=C_CARD)
                    for l in ls: l.config(bg=C_CARD)
                for w in [c, i_] + ls:
                    w.bind("<Enter>", on_enter)
                    w.bind("<Leave>", on_leave)
                    w.bind("<Button-1>", lambda e, rr=r: rr())
            bind(cell, inner, [ilbl, tlbl])

        for c in range(2):
            grid.columnconfigure(c, weight=1)


if __name__ == "__main__":
    app = MultiTool()
    app.mainloop()