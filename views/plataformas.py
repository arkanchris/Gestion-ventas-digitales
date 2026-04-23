import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import shutil, os
from widgets import (COLORS, card, title_label, primary_btn,
                     danger_btn, secondary_btn, entry_field, build_treeview)


class PlataformasView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db = db
        self.app = app
        self.editing_id = None
        self.imagen_path = ""
        self._build()
        self._load()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(24, 8))
        title_label(hdr, "📺  Gestión de Plataformas", size=22).pack(side="left")

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=24, pady=4)
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=3)
        main.grid_rowconfigure(0, weight=1)

        # ── Left: Form ──
        form_scroll = ctk.CTkScrollableFrame(main, fg_color=COLORS["bg_card"],
                                              corner_radius=12,
                                              scrollbar_button_color=COLORS["border"])
        form_scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(form_scroll,
                     text="➕  Nueva / Editar Plataforma",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#ffffff").pack(anchor="w", padx=16, pady=(14, 8))

        def lbl(text):
            ctk.CTkLabel(form_scroll, text=text, anchor="w",
                         font=ctk.CTkFont(size=13),
                         text_color=COLORS["text_dim"]).pack(
                             anchor="w", padx=16, pady=(8, 2))

        lbl("Nombre de la plataforma *")
        self.e_nombre = entry_field(form_scroll, placeholder="Ej: Netflix, Disney+")
        self.e_nombre.pack(fill="x", padx=16, pady=(0, 6))

        lbl("Costo de compra  🔒  (interno)")
        self.e_costo = entry_field(form_scroll, placeholder="0.00")
        self.e_costo.pack(fill="x", padx=16, pady=(0, 6))

        lbl("Precio de venta al cliente")
        self.e_precio = entry_field(form_scroll, placeholder="0.00")
        self.e_precio.pack(fill="x", padx=16, pady=(0, 6))

        # ── Image section ──
        ctk.CTkFrame(form_scroll, height=1,
                     fg_color=COLORS["border"]).pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(form_scroll, text="🖼️  Icono / Logo de la Plataforma",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["accent2"]).pack(anchor="w", padx=16, pady=(0, 6))
        ctk.CTkLabel(form_scroll,
                     text="Recomendado: imagen cuadrada PNG 200×200px o similar",
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).pack(anchor="w", padx=16)

        # Image preview box
        self.img_preview_frame = ctk.CTkFrame(form_scroll, fg_color="#0d1828",
                                               corner_radius=10, width=100, height=100)
        self.img_preview_frame.pack(padx=16, pady=10, anchor="w")
        self.img_preview_frame.pack_propagate(False)

        self.img_preview_label = ctk.CTkLabel(
            self.img_preview_frame, text="Sin\nicono",
            font=ctk.CTkFont(size=11), text_color=COLORS["text_dim"])
        self.img_preview_label.place(relx=0.5, rely=0.5, anchor="center")

        img_btn_row = ctk.CTkFrame(form_scroll, fg_color="transparent")
        img_btn_row.pack(fill="x", padx=16, pady=(0, 8))
        primary_btn(img_btn_row, "📂  Seleccionar imagen",
                    command=self._select_imagen,
                    height=34).pack(side="left", padx=(0, 8))
        secondary_btn(img_btn_row, "✕  Quitar",
                      command=self._quitar_imagen,
                      height=34, width=80).pack(side="left")

        self.img_name_label = ctk.CTkLabel(form_scroll, text="",
                                            font=ctk.CTkFont(size=11),
                                            text_color=COLORS["accent3"])
        self.img_name_label.pack(anchor="w", padx=16)

        ctk.CTkFrame(form_scroll, height=1,
                     fg_color=COLORS["border"]).pack(fill="x", padx=16, pady=12)

        self.activa_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(form_scroll, text="Plataforma activa",
                        variable=self.activa_var,
                        checkbox_width=20, checkbox_height=20,
                        fg_color=COLORS["accent"],
                        font=ctk.CTkFont(size=13),
                        text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=4)

        btn_row = ctk.CTkFrame(form_scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(12, 16))
        primary_btn(btn_row, "💾  Guardar",
                    command=self._guardar).pack(side="left", padx=(0, 8))
        secondary_btn(btn_row, "🗑  Limpiar",
                      command=self._limpiar).pack(side="left")

        # ── Right: Table ──
        right = ctk.CTkFrame(main, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="📋  Lista de Plataformas",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#ffffff").grid(row=0, column=0,
                                                sticky="w", pady=(14, 6))

        cols = ("id", "icono", "nombre", "costo", "precio", "ganancia", "activa")
        anchors_p = {"id":"center","icono":"center","nombre":"w","costo":"center","precio":"center","ganancia":"center","activa":"center"}
        table_frame, self.tree = build_treeview(right, cols, heights=16, col_anchors=anchors_p)
        table_frame.grid(row=1, column=0, sticky="nsew")

        col_cfg = {
            "id":       ("#",          50),
            "icono":    ("🖼",          40),
            "nombre":   ("Plataforma", 150),
            "costo":    ("🔒 Costo",   100),
            "precio":   ("Precio",     110),
            "ganancia": ("Ganancia",   100),
            "activa":   ("Estado",     80),
        }
        for c, (h, w) in col_cfg.items():
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)

        act = ctk.CTkFrame(right, fg_color="transparent")
        act.grid(row=2, column=0, sticky="ew", pady=8)
        primary_btn(act, "✏️  Cargar para editar",
                    command=self._cargar_edicion).pack(side="left", padx=(0, 8))
        danger_btn(act, "🗑  Eliminar",
                   command=self._eliminar).pack(side="left")

        self.tree.bind("<Double-1>", lambda e: self._cargar_edicion())

    def _select_imagen(self):
        path = filedialog.askopenfilename(
            title="Seleccionar imagen de la plataforma",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                       ("Todos", "*.*")]
        )
        if not path:
            return
        # Copy to icons folder inside project
        icons_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "icons")
        os.makedirs(icons_dir, exist_ok=True)
        ext = os.path.splitext(path)[1]
        nombre_safe = self.e_nombre.get().strip().replace(" ", "_") or "plataforma"
        dest = os.path.join(icons_dir, f"{nombre_safe}{ext}")
        shutil.copy2(path, dest)
        self.imagen_path = dest
        self._show_preview(dest)
        self.img_name_label.configure(text=f"✅  {os.path.basename(dest)}")

    def _quitar_imagen(self):
        self.imagen_path = ""
        self.img_preview_label.configure(text="Sin\nicono", image=None)
        try:
            self.img_preview_label.configure(image="")
        except:
            pass
        self.img_name_label.configure(text="")

    def _show_preview(self, path):
        if not path or not os.path.exists(path):
            return
        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((90, 90), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(90, 90))
            self.img_preview_label.configure(image=ctk_img, text="")
            self.img_preview_label._image = ctk_img  # keep reference
        except Exception as e:
            self.img_preview_label.configure(text="Error\ncargando")

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for p in self.db.get_plataformas():
            ganancia = p["precio_venta"] - p["costo_compra"]
            estado = "✅ Activa" if p["activa"] else "❌ Inactiva"
            icono = "🖼️" if p.get("imagen_path") and os.path.exists(
                p.get("imagen_path", "")) else "—"
            self.tree.insert("", "end", iid=str(p["id"]), values=(
                p["id"],
                icono,
                p["nombre"],
                f"${p['costo_compra']:,.0f}",
                f"${p['precio_venta']:,.0f}",
                f"${ganancia:,.0f}",
                estado,
            ))

    def _guardar(self):
        nombre = self.e_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return
        try:
            costo = float(self.e_costo.get() or 0)
            precio = float(self.e_precio.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "Los precios deben ser números.")
            return

        if self.editing_id:
            self.db.update_plataforma(
                self.editing_id, nombre, costo, precio,
                int(self.activa_var.get()), self.imagen_path)
            messagebox.showinfo("✅", "Plataforma actualizada correctamente.")
        else:
            self.db.add_plataforma(nombre, costo, precio, self.imagen_path)
            messagebox.showinfo("✅", "Plataforma creada correctamente.")
        self._limpiar()
        self._load()

    def _cargar_edicion(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una plataforma.")
            return
        pid = int(sel[0])
        for p in self.db.get_plataformas():
            if p["id"] == pid:
                self.editing_id = pid
                self.e_nombre.delete(0, "end")
                self.e_nombre.insert(0, p["nombre"])
                self.e_costo.delete(0, "end")
                self.e_costo.insert(0, str(p["costo_compra"]))
                self.e_precio.delete(0, "end")
                self.e_precio.insert(0, str(p["precio_venta"]))
                self.activa_var.set(bool(p["activa"]))
                self.imagen_path = p.get("imagen_path", "")
                if self.imagen_path and os.path.exists(self.imagen_path):
                    self._show_preview(self.imagen_path)
                    self.img_name_label.configure(
                        text=f"✅  {os.path.basename(self.imagen_path)}")
                else:
                    self._quitar_imagen()
                break

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una plataforma.")
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar esta plataforma?"):
            self.db.delete_plataforma(int(sel[0]))
            self._load()

    def _limpiar(self):
        self.editing_id = None
        self.imagen_path = ""
        self.e_nombre.delete(0, "end")
        self.e_costo.delete(0, "end")
        self.e_precio.delete(0, "end")
        self.activa_var.set(True)
        self._quitar_imagen()
