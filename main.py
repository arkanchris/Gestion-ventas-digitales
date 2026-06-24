import customtkinter as ctk
from database import Database
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

        self.colors = {
            "bg_dark":    "#0b1120",
            "bg_card":    "#111c30",
            "bg_sidebar": "#091020",
            "accent":     "#1d6fd8",
            "accent2":    "#38bdf8",
            "accent3":    "#22c55e",
            "text":       "#f0f6ff",
            "text_dim":   "#6b8abf",
            "border":     "#1e3256",
        }

        self.configure(fg_color=self.colors["bg_dark"])
        self._build_ui()
        self.show_view("dashboard")

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──
        self.sidebar = ctk.CTkFrame(
            self, width=220,
            fg_color=self.colors["bg_sidebar"],
            corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(20, weight=1)
        self.sidebar.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(
            self.sidebar, fg_color="#0d0f1a",
            corner_radius=0, height=80)
        logo_frame.grid(row=0, column=0, sticky="ew")
        logo_frame.grid_columnconfigure(0, weight=1)
        logo_frame.grid_propagate(False)

        config = self.db.get_config()
        bname  = config.get("business_name", "StreamControl") if config else "StreamControl"
        self.logo_label = ctk.CTkLabel(
            logo_frame,
            text=f"🎬 {bname}",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=self.colors["accent"])
        self.logo_label.place(relx=0.5, rely=0.5, anchor="center")

        # Nav items
        nav_items = [
            ("dashboard",    "🏠",  "Dashboard"),
            ("ventas",       "💰",  "Nueva Venta"),
            ("clientes",     "👥",  "Clientes"),
            ("deudas",       "📋",  "Deudas"),
            ("plataformas",  "📺",  "Plataformas"),
            ("proveedores",  "🏭",  "Distribuidores"),
            ("reportes",     "📊",  "Reportes"),
            ("reservas",     "📒",  "Libro de Cuentas"),
            ("configuracion","⚙️",  "Configuración"),
        ]

        self.nav_buttons = {}
        for i, (key, icon, label) in enumerate(nav_items):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}  {label}",
                anchor="w", height=44, corner_radius=8,
                fg_color="transparent",
                hover_color=self.colors["border"],
                text_color=self.colors["text_dim"],
                font=ctk.CTkFont(family="Segoe UI", size=13),
                command=lambda k=key: self.show_view(k))
            btn.grid(row=i+1, column=0, sticky="ew", padx=12, pady=2)
            self.nav_buttons[key] = btn

        ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0 — StreamControl",
            font=ctk.CTkFont(size=10),
            text_color="#3a3d5a"
        ).grid(row=21, column=0, pady=10)

        # ── Content area ──
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=self.colors["bg_dark"],
            corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def show_view(self, name):
        for k, btn in self.nav_buttons.items():
            btn.configure(
                fg_color="#0e2040" if k == name else "transparent",
                text_color=self.colors["text"] if k == name else self.colors["text_dim"])

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
        self.logo_label.configure(text=f"🎬 {bname}")
        self.title(f"🎬 {bname} — Sistema de Ventas")


if __name__ == "__main__":
    app = StreamControlApp()
    app.mainloop()
