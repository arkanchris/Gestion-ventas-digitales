import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from widgets import (COLORS, card, title_label, primary_btn,
                     danger_btn, secondary_btn, entry_field, build_treeview)


class ProveedoresView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db = db
        self.app = app
        self.editing_id = None
        self._build()
        self._load()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(24, 8))
        title_label(hdr, "🏭  Gestión de Distribuidores", size=22).pack(side="left")

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=24, pady=4)
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=3)
        main.grid_rowconfigure(0, weight=1)

        # ── Form ──
        form = card(main)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(form, text="➕  Nuevo / Editar Distribuidor",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 8))

        def lbl(text):
            ctk.CTkLabel(form, text=text, anchor="w",
                         font=ctk.CTkFont(size=13),
                         text_color=COLORS["text_dim"]).pack(anchor="w", padx=16, pady=(8, 2))

        lbl("Nombre del distribuidor *")
        self.e_nombre = entry_field(form, placeholder="Nombre")
        self.e_nombre.pack(fill="x", padx=16, pady=(0, 4))

        lbl("Teléfono")
        self.e_tel = entry_field(form, placeholder="Teléfono de contacto")
        self.e_tel.pack(fill="x", padx=16, pady=(0, 4))

        lbl("Correo electrónico")
        self.e_correo = entry_field(form, placeholder="correo@proveedor.com")
        self.e_correo.pack(fill="x", padx=16, pady=(0, 4))

        lbl("Notas")
        self.e_notas = ctk.CTkTextbox(form, height=70, fg_color="#12151f",
                                       border_color=COLORS["border"], border_width=1,
                                       font=ctk.CTkFont(size=13), text_color=COLORS["text"],
                                       corner_radius=8)
        self.e_notas.pack(fill="x", padx=16, pady=(0, 8))

        self.credito_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(form, text="💳  Maneja crédito",
                        variable=self.credito_var,
                        checkbox_width=20, checkbox_height=20,
                        fg_color=COLORS["accent4"],
                        font=ctk.CTkFont(size=13), text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=4)

        self.activo_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(form, text="✅  Proveedor activo",
                        variable=self.activo_var,
                        checkbox_width=20, checkbox_height=20,
                        fg_color=COLORS["accent"],
                        font=ctk.CTkFont(size=13), text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=4)

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(12, 16))
        primary_btn(btn_row, "💾  Guardar", command=self._guardar).pack(side="left", padx=(0, 8))
        secondary_btn(btn_row, "🗑  Limpiar", command=self._limpiar).pack(side="left")

        # ── Table ──
        right = ctk.CTkFrame(main, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="📋  Lista de Distribuidores",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text"]).grid(row=0, column=0, sticky="w", pady=(14, 6))

        cols = ("id", "nombre", "telefono", "correo", "credito", "estado")
        anchors_v = {"id":"center","nombre":"w","telefono":"center","correo":"w","credito":"center","estado":"center"}
        table_frame, self.tree = build_treeview(right, cols, heights=14, col_anchors=anchors_v)
        table_frame.grid(row=1, column=0, sticky="nsew")

        col_cfg = {
            "id":       ("#",        50),
            "nombre":   ("Nombre",   160),
            "telefono": ("Teléfono", 110),
            "correo":   ("Correo",   160),
            "credito":  ("Crédito",  80),
            "estado":   ("Estado",   80),
        }
        for c, (h, w) in col_cfg.items():
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)

        act = ctk.CTkFrame(right, fg_color="transparent")
        act.grid(row=2, column=0, sticky="ew", pady=8)
        primary_btn(act, "✏️  Editar", command=self._cargar_edicion).pack(side="left", padx=(0, 8))
        danger_btn(act, "🗑  Eliminar", command=self._eliminar).pack(side="left")
        self.tree.bind("<Double-1>", lambda e: self._cargar_edicion())

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for p in self.db.get_proveedores():
            self.tree.insert("", "end", iid=str(p["id"]), values=(
                p["id"], p["nombre"],
                p.get("telefono", ""),
                p.get("correo", ""),
                "💳 Sí" if p["maneja_credito"] else "No",
                "✅ Activo" if p["activo"] else "❌ Inactivo",
            ))

    def _guardar(self):
        nombre = self.e_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "El nombre es obligatorio.")
            return
        tel = self.e_tel.get().strip()
        correo = self.e_correo.get().strip()
        notas = self.e_notas.get("1.0", "end").strip()
        credito = int(self.credito_var.get())
        activo = int(self.activo_var.get())

        if self.editing_id:
            self.db.update_proveedor(self.editing_id, nombre, tel, correo, credito, notas, activo)
            messagebox.showinfo("✅", "Distribuidor actualizado.")
        else:
            self.db.add_proveedor(nombre, tel, correo, credito, notas)
            messagebox.showinfo("✅", "Distribuidor creado.")
        self._limpiar()
        self._load()

    def _cargar_edicion(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un distribuidor.")
            return
        pid = int(sel[0])
        for p in self.db.get_proveedores():
            if p["id"] == pid:
                self.editing_id = pid
                self.e_nombre.delete(0, "end"); self.e_nombre.insert(0, p["nombre"])
                self.e_tel.delete(0, "end");    self.e_tel.insert(0, p.get("telefono",""))
                self.e_correo.delete(0, "end"); self.e_correo.insert(0, p.get("correo",""))
                self.e_notas.delete("1.0","end"); self.e_notas.insert("1.0", p.get("notas",""))
                self.credito_var.set(bool(p["maneja_credito"]))
                self.activo_var.set(bool(p["activo"]))
                break

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un distribuidor.")
            return
        if messagebox.askyesno("Confirmar", "¿Eliminar este distribuidor?"):
            self.db.delete_proveedor(int(sel[0]))
            self._load()

    def _limpiar(self):
        self.editing_id = None
        for e in [self.e_nombre, self.e_tel, self.e_correo]:
            e.delete(0, "end")
        self.e_notas.delete("1.0", "end")
        self.credito_var.set(False)
        self.activo_var.set(True)
