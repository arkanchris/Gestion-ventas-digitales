import os
import customtkinter as ctk
from PIL import Image
from database import Database
from widgets import COLORS, _tint

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
from views.dashboard import Dashboard
from views.ventas import VentasView
from views.clientes import ClientesView
from views.plataformas import PlataformasView
from views.proveedores import ProveedoresView
from views.reportes import ReportesView
from views.configuracion import ConfiguracionView
from views.deudas import DeudasView
from views.reservas import ReservasView
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class StreamControlApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.db.init_db()

        config        = self.db.get_config()
        business_name = config.get("business_name", "StreamControl") if config else "StreamControl"

        self.title(f"🎬 {business_name} — Sistema de Ventas")
        self.geometry("1280x780")
        self.minsize(1100, 680)

        # Un único origen de verdad para los colores: widgets.py
        self.colors = COLORS

        self.configure(fg_color=self.colors["bg_dark"])
        self._build_ui()
        self.show_view("dashboard")

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──
        self.sidebar = ctk.CTkFrame(
            self, width=222,
            fg_color=self.colors["bg_sidebar"],
            corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(20, weight=1)
        self.sidebar.grid_propagate(False)

        # Logo — imagen real del negocio, grande, en vez del punto + texto
        logo_frame = ctk.CTkFrame(
            self.sidebar, fg_color=self.colors["bg_sidebar"],
            corner_radius=0, height=128)
        logo_frame.grid(row=0, column=0, sticky="ew")
        logo_frame.grid_propagate(False)

        config = self.db.get_config()
        bname  = config.get("business_name", "StreamControl") if config else "StreamControl"

        self.logo_image = None
        try:
            pil_img = Image.open(LOGO_PATH)
            self.logo_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img,
                                            size=(96, 96))
            self.logo_label = ctk.CTkLabel(logo_frame, image=self.logo_image, text="")
        except Exception:
            # Si no se encuentra assets/logo.png, cae de vuelta al texto
            self.logo_label = ctk.CTkLabel(
                logo_frame, text=bname,
                font=ctk.CTkFont(family="Bahnschrift", size=15, weight="bold"),
                text_color=self.colors["text"])
        self.logo_label.place(relx=0.5, rely=0.5, anchor="center")

        # Nav items
        nav_items = [
            ("dashboard",    "🏠",  "Dashboard",         self.colors["accent3"]),
            ("ventas",       "💰",  "Nueva Venta",       self.colors["accent4"]),
            ("clientes",     "👥",  "Clientes",          self.colors["accent2"]),
            ("deudas",       "📋",  "Deudas",            self.colors["red"]),
            ("plataformas",  "📺",  "Plataformas",       self.colors["accent"]),
            ("proveedores",  "🏭",  "Distribuidores",    self.colors["accent4"]),
            ("reportes",     "📊",  "Reportes",          self.colors["accent2"]),
            ("reservas",     "📒",  "Libro de Cuentas",  self.colors["accent3"]),
            ("configuracion","⚙️",  "Configuración",     self.colors["text_dim"]),
        ]

        self.nav_refs = {}
        self._active_key = None

        for i, (key, icon, label, color) in enumerate(nav_items):
            row = ctk.CTkFrame(self.sidebar, fg_color="transparent",
                                corner_radius=10, height=42)
            row.grid(row=i+1, column=0, sticky="ew", padx=12, pady=2)
            row.grid_propagate(False)

            chip = ctk.CTkFrame(row, width=30, height=30, corner_radius=9,
                                 fg_color=_tint(color, 0.22))
            chip.place(x=6, rely=0.5, anchor="w")
            chip.pack_propagate(False)
            icon_lbl = ctk.CTkLabel(chip, text=icon, font=ctk.CTkFont(size=14),
                                     text_color=color)
            icon_lbl.place(relx=0.5, rely=0.5, anchor="center")

            text_lbl = ctk.CTkLabel(row, text=label, anchor="w",
                                     font=ctk.CTkFont(family="Segoe UI", size=13),
                                     text_color=self.colors["text_dim"])
            text_lbl.place(x=48, rely=0.5, anchor="w")

            for w in (row, chip, icon_lbl, text_lbl):
                w.bind("<Button-1>", lambda e, k=key: self.show_view(k))
                w.bind("<Enter>", lambda e, k=key: self._nav_hover(k, True))
                w.bind("<Leave>", lambda e, k=key: self._nav_hover(k, False))

            self.nav_refs[key] = dict(row=row, chip=chip, icon_lbl=icon_lbl,
                                       text_lbl=text_lbl, color=color)

        # Se mantiene por compatibilidad con código que aún use nav_buttons
        self.nav_buttons = self.nav_refs

        ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0 — StreamControl",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#2c4658"
        ).grid(row=21, column=0, pady=10)

        # ── Content area ──
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["bg_dark"],
            corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def _nav_hover(self, key, entering):
        if key == self._active_key:
            return  # el ítem activo no cambia con el hover
        refs = self.nav_refs[key]
        refs["row"].configure(fg_color=self.colors["border"] if entering else "transparent")

    def show_view(self, name):
        self._active_key = name
        for k, refs in self.nav_refs.items():
            active = (k == name)
            if active:
                refs["row"].configure(fg_color=self.colors["accent3"])
                refs["chip"].configure(fg_color="transparent")
                refs["icon_lbl"].configure(text_color="#04110f")
                refs["text_lbl"].configure(text_color="#04110f",
                                            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"))
            else:
                refs["row"].configure(fg_color="transparent")
                refs["chip"].configure(fg_color=_tint(refs["color"], 0.22))
                refs["icon_lbl"].configure(text_color=refs["color"])
                refs["text_lbl"].configure(text_color=self.colors["text_dim"],
                                            font=ctk.CTkFont(family="Segoe UI", size=13, weight="normal"))

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        view_map = {
            "dashboard":    Dashboard,
            "ventas":       VentasView,
            "clientes":     ClientesView,
            "deudas":       DeudasView,
            "plataformas":  PlataformasView,
            "proveedores":  ProveedoresView,
            "reportes":     ReportesView,
            "reservas":     ReservasView,
            "configuracion":ConfiguracionView,
        }

        ViewClass = view_map.get(name)
        if ViewClass:
            view = ViewClass(self.content_frame, self.db, self)
            view.pack(fill="both", expand=True)

    def refresh_sidebar_name(self):
        config = self.db.get_config()
        bname  = config.get("business_name", "StreamControl") if config else "StreamControl"
        if self.logo_image is None:
            # Solo si estamos en modo texto de respaldo (no se encontró el logo)
            self.logo_label.configure(text=bname)
        self.title(f"🎬 {bname} — Sistema de Ventas")


if __name__ == "__main__":
    app = StreamControlApp()
    app.mainloop()