import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from datetime import datetime

COLORS = {
    "bg_dark":   "#0b1120",
    "bg_card":   "#111c30",
    "bg_sidebar":"#091020",
    "accent":    "#1d6fd8",
    "accent2":   "#38bdf8",
    "accent3":   "#22c55e",
    "accent4":   "#f59e0b",
    "text":      "#f0f6ff",
    "text_dim":  "#8aabda",
    "border":    "#1e3256",
    "red":       "#ef4444",
    "green":     "#22c55e",
    "yellow":    "#f59e0b",
}


def card(parent, **kwargs):
    defaults = dict(fg_color=COLORS["bg_card"], corner_radius=12)
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def title_label(parent, text, size=20, **kwargs):
    defaults = dict(
        text=text,
        font=ctk.CTkFont(family="Segoe UI", size=size, weight="bold"),
        text_color="#ffffff",
    )
    defaults.update(kwargs)
    return ctk.CTkLabel(parent, **defaults)


def dim_label(parent, text, size=12, **kwargs):
    defaults = dict(
        text=text,
        font=ctk.CTkFont(family="Segoe UI", size=size),
        text_color=COLORS["text_dim"],
    )
    defaults.update(kwargs)
    return ctk.CTkLabel(parent, **defaults)


def primary_btn(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text, command=command, height=38, corner_radius=8,
        fg_color=COLORS["accent"], hover_color="#1558b0",
        font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        text_color="white",
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def danger_btn(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text, command=command, height=38, corner_radius=8,
        fg_color=COLORS["red"], hover_color="#cc3344",
        font=ctk.CTkFont(family="Segoe UI", size=13),
        text_color="white",
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def success_btn(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text, command=command, height=38, corner_radius=8,
        fg_color=COLORS["green"], hover_color="#18a84a",
        font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        text_color="#0f1117",
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def secondary_btn(parent, text, command=None, **kwargs):
    defaults = dict(
        text=text, command=command, height=38, corner_radius=8,
        fg_color=COLORS["border"], hover_color="#2a4a7a",
        font=ctk.CTkFont(family="Segoe UI", size=13),
        text_color=COLORS["text"],
    )
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def entry_field(parent, placeholder="", show=None, **kwargs):
    defaults = dict(
        placeholder_text=placeholder, height=38, corner_radius=8,
        fg_color="#0d1828", border_color=COLORS["border"], border_width=1,
        text_color="#ffffff", placeholder_text_color=COLORS["text_dim"],
        font=ctk.CTkFont(family="Segoe UI", size=13),
    )
    if show:
        defaults["show"] = show
    defaults.update(kwargs)
    return ctk.CTkEntry(parent, **defaults)


def section_header(parent, text, pady=(20, 8)):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.pack(fill="x", padx=20, pady=pady)
    ctk.CTkLabel(f, text=text,
                 font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                 text_color=COLORS["accent2"]).pack(side="left")
    ctk.CTkFrame(f, height=1, fg_color=COLORS["border"]).pack(
        side="left", fill="x", expand=True, padx=(10, 0))
    return f


def stat_card(parent, icon, title, value, color=None, **kwargs):
    c = card(parent, **kwargs)
    color = color or COLORS["accent"]
    ctk.CTkLabel(c, text=icon, font=ctk.CTkFont(size=28)).pack(pady=(16, 4))
    ctk.CTkLabel(c, text=str(value),
                 font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
                 text_color=color).pack()
    ctk.CTkLabel(c, text=title,
                 font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                 text_color="#c8dcf5").pack(pady=(2, 16))
    return c


def build_treeview(parent, columns, heights=None, col_anchors=None):
    """
    col_anchors: dict { col_name: "center"/"w"/"e" }
    Default: all columns centered except the first (left-aligned).
    """
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Stream.Treeview",
                    background="#111c30",
                    foreground="#f0f6ff",
                    fieldbackground="#111c30",
                    rowheight=40,
                    font=("Segoe UI", 11),
                    borderwidth=0)
    style.configure("Stream.Treeview.Heading",
                    background="#091020",
                    foreground="#8aabda",
                    font=("Segoe UI", 11, "bold"),
                    borderwidth=0,
                    relief="flat")
    style.map("Stream.Treeview",
              background=[("selected", "#1d6fd8")],
              foreground=[("selected", "white")])

    frame = ctk.CTkFrame(parent, fg_color="#111c30", corner_radius=12)
    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        style="Stream.Treeview",
                        height=heights or 14)

    # Apply anchors: default center for all columns
    for i, col in enumerate(columns):
        anchor = "center"
        if col_anchors and col in col_anchors:
            anchor = col_anchors[col]
        tree.column(col, anchor=anchor)
        tree.heading(col, anchor="center")

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)
    return frame, tree


def days_remaining(fecha_venc_str):
    if not fecha_venc_str:
        return None
    try:
        from datetime import date
        fv  = datetime.strptime(fecha_venc_str, "%Y-%m-%d").date()
        hoy = date.today()
        return (fv - hoy).days
    except:
        return None


def days_badge(days):
    if days is None:
        return ("—", COLORS["text_dim"])
    if days < 0:
        return ("Vencido", COLORS["red"])
    if days == 0:
        return ("Hoy ⚠️", COLORS["red"])
    if days <= 5:
        return (f"{days}d ⚠️", COLORS["yellow"])
    if days <= 15:
        return (f"{days}d", COLORS["yellow"])
    return (f"{days}d", COLORS["green"])


class DatePicker(ctk.CTkToplevel):
    def __init__(self, parent, initial_date=None, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.title("Seleccionar fecha")
        self.geometry("320x300")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.grab_set()
        now = initial_date or datetime.now()
        self.year  = tk.IntVar(value=now.year)
        self.month = tk.IntVar(value=now.month)
        self._build()

    def _build(self):
        top = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0)
        top.pack(fill="x")
        ctk.CTkButton(top, text="◀", width=36, height=32,
                      fg_color="transparent", text_color=COLORS["text"],
                      command=self._prev_month).pack(side="left", padx=6, pady=6)
        self.header = ctk.CTkLabel(top, text="",
                                   font=ctk.CTkFont(size=13, weight="bold"),
                                   text_color=COLORS["text"])
        self.header.pack(side="left", expand=True)
        ctk.CTkButton(top, text="▶", width=36, height=32,
                      fg_color="transparent", text_color=COLORS["text"],
                      command=self._next_month).pack(side="right", padx=6, pady=6)
        self.cal_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.cal_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._draw_calendar()

    def _draw_calendar(self):
        import calendar
        for w in self.cal_frame.winfo_children():
            w.destroy()
        MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
                 "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
        self.header.configure(text=f"{MESES[self.month.get()-1]} {self.year.get()}")
        for i, d in enumerate(["Lu","Ma","Mi","Ju","Vi","Sa","Do"]):
            ctk.CTkLabel(self.cal_frame, text=d, width=36,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=COLORS["text_dim"]).grid(row=0, column=i, padx=2, pady=2)
        cal = calendar.monthcalendar(self.year.get(), self.month.get())
        for ri, week in enumerate(cal):
            for ci, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(self.cal_frame, text="", width=36
                                 ).grid(row=ri+1, column=ci)
                else:
                    ctk.CTkButton(
                        self.cal_frame, text=str(day), width=34, height=30,
                        corner_radius=6, fg_color="transparent",
                        hover_color=COLORS["accent"], text_color=COLORS["text"],
                        font=ctk.CTkFont(size=12),
                        command=lambda d=day: self._select(d)
                    ).grid(row=ri+1, column=ci, padx=1, pady=1)

    def _prev_month(self):
        m, y = self.month.get(), self.year.get()
        self.month.set(12 if m == 1 else m-1)
        if m == 1:
            self.year.set(y-1)
        self._draw_calendar()

    def _next_month(self):
        m, y = self.month.get(), self.year.get()
        self.month.set(1 if m == 12 else m+1)
        if m == 12:
            self.year.set(y+1)
        self._draw_calendar()

    def _select(self, day):
        date_str = f"{self.year.get():04d}-{self.month.get():02d}-{day:02d}"
        if self.callback:
            self.callback(date_str)
        self.destroy()


class DateEntryWidget(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent")
        self.var = tk.StringVar()
        self.entry = entry_field(self, placeholder="AAAA-MM-DD", **kwargs)
        self.entry.configure(textvariable=self.var)
        self.entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(self, text="📅", width=38, height=38,
                      corner_radius=8, fg_color=COLORS["border"],
                      hover_color=COLORS["accent"],
                      command=self._open_picker).pack(side="left", padx=(4, 0))

    def _open_picker(self):
        try:
            d = datetime.strptime(self.var.get(), "%Y-%m-%d")
        except:
            d = None
        DatePicker(self, initial_date=d, callback=lambda v: self.var.set(v))

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)
