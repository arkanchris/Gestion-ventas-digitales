import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import shutil
import os
from widgets import (COLORS, card, title_label, primary_btn, secondary_btn, entry_field, section_header)


class ConfiguracionView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db = db
        self.app = app
        self._build()
        self._load()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0,
                                         scrollbar_button_color=COLORS["border"])
        scroll.pack(fill="both", expand=True)

        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(24, 8))
        title_label(hdr, "⚙️  Configuración del Negocio", size=22).pack(side="left")

        # Business info
        section_header(scroll, "🏢  Información del Negocio")
        biz = card(scroll)
        biz.pack(fill="x", padx=24, pady=4)

        ctk.CTkLabel(biz, text="Nombre del negocio",
                     anchor="w", text_color=COLORS["text_dim"],
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=16, pady=(12, 2))
        self.e_bname = entry_field(biz, placeholder="Ej: Mi Negocio de Streaming")
        self.e_bname.pack(fill="x", padx=16, pady=(0, 12))

        primary_btn(biz, "💾  Guardar nombre", command=self._save_bname).pack(anchor="w", padx=16, pady=(0, 12))

        # Logo
        section_header(scroll, "🖼️  Logo del Negocio")
        logo_card = card(scroll)
        logo_card.pack(fill="x", padx=24, pady=4)

        logo_inner = ctk.CTkFrame(logo_card, fg_color="transparent")
        logo_inner.pack(fill="x", padx=16, pady=12)

        self.logo_path_label = ctk.CTkLabel(logo_inner, text="Sin logo configurado",
                                             text_color=COLORS["text_dim"],
                                             font=ctk.CTkFont(size=13))
        self.logo_path_label.pack(side="left", padx=(0, 12))

        primary_btn(logo_inner, "📂  Seleccionar logo",
                    command=self._select_logo).pack(side="left", padx=(0, 8))
        secondary_btn(logo_inner, "🗑  Quitar logo",
                      command=self._remove_logo).pack(side="left")

        ctk.CTkLabel(logo_card, text="Formatos: PNG, JPG. Recomendado: 400×120 px o similar.",
                     text_color=COLORS["text_dim"],
                     font=ctk.CTkFont(size=11)).pack(anchor="w", padx=16, pady=(0, 12))

        # Factura
        section_header(scroll, "🧾  Numeración de Facturas")
        fac_card = card(scroll)
        fac_card.pack(fill="x", padx=24, pady=4)

        fac_inner = ctk.CTkFrame(fac_card, fg_color="transparent")
        fac_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(fac_inner, text="Próximo número de factura:",
                     text_color=COLORS["text_dim"], font=ctk.CTkFont(size=13)).pack(side="left", padx=(0,8))
        self.e_factura = entry_field(fac_inner, placeholder="1", width=100)
        self.e_factura.pack(side="left", padx=(0, 12))
        primary_btn(fac_inner, "💾  Guardar", command=self._save_factura).pack(side="left")

        # Acerca de
        section_header(scroll, "ℹ️  Acerca de")
        about = card(scroll)
        about.pack(fill="x", padx=24, pady=(4, 20))

        info_text = (
            "StreamControl — Sistema de Ventas de Plataformas de Streaming\n"
            "Versión 1.0.0  •  Desarrollado con Python + CustomTkinter + SQLite\n"
            "Base de datos local: streamcontrol.db"
        )
        ctk.CTkLabel(about, text=info_text,
                     text_color=COLORS["text_dim"], font=ctk.CTkFont(size=12),
                     justify="left").pack(anchor="w", padx=16, pady=16)

    def _load(self):
        config = self.db.get_config()
        self.e_bname.delete(0, "end")
        self.e_bname.insert(0, config.get("business_name", "StreamControl"))

        logo = config.get("logo_path", "")
        if logo and os.path.exists(logo):
            self.logo_path_label.configure(text=f"✅  {os.path.basename(logo)}", text_color=COLORS["accent3"])
        else:
            self.logo_path_label.configure(text="Sin logo configurado", text_color=COLORS["text_dim"])

        self.e_factura.delete(0, "end")
        self.e_factura.insert(0, config.get("factura_consecutivo", "1"))

    def _save_bname(self):
        name = self.e_bname.get().strip()
        if not name:
            messagebox.showerror("Error", "El nombre no puede estar vacío.")
            return
        self.db.set_config("business_name", name)
        self.app.refresh_sidebar_name()
        messagebox.showinfo("✅", "Nombre del negocio guardado.")

    def _select_logo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar logo",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos", "*.*")]
        )
        if path:
            # Copy to app folder
            dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo" + os.path.splitext(path)[1])
            shutil.copy2(path, dest)
            self.db.set_config("logo_path", dest)
            self.logo_path_label.configure(text=f"✅  {os.path.basename(dest)}", text_color=COLORS["accent3"])
            messagebox.showinfo("✅", "Logo configurado correctamente.")

    def _remove_logo(self):
        self.db.set_config("logo_path", "")
        self.logo_path_label.configure(text="Sin logo configurado", text_color=COLORS["text_dim"])

    def _save_factura(self):
        try:
            n = int(self.e_factura.get())
            self.db.set_config("factura_consecutivo", str(n))
            messagebox.showinfo("✅", f"Numeración actualizada. Próxima factura: #{n}")
        except ValueError:
            messagebox.showerror("Error", "Ingresa un número válido.")
