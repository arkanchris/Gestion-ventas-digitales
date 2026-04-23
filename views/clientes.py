import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from widgets import (COLORS, card, title_label, primary_btn,
                     danger_btn, secondary_btn, entry_field, build_treeview,
                     days_remaining, days_badge)
from tirilla import generar_tirilla


class ClientesView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db = db
        self.app = app
        self._build()
        self._load()

    def _build(self):
        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(24, 8))
        title_label(hdr, "👥  Clientes y Ventas", size=22).pack(side="left")
        primary_btn(hdr, "+ Nueva Venta",
                    command=lambda: self.app.show_view("ventas")).pack(side="right")

        # ── Barra de filtros ──
        fbar = card(self)
        fbar.pack(fill="x", padx=24, pady=(0, 4))
        inner = ctk.CTkFrame(fbar, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(inner, text="🔍", font=ctk.CTkFont(size=16),
                     text_color=COLORS["text_dim"]).pack(side="left", padx=(0, 4))
        self.search_var = tk.StringVar()
        entry_field(inner,
                    placeholder="Buscar nombre, teléfono o correo...",
                    width=240, textvariable=self.search_var
                    ).pack(side="left", padx=(0, 10))
        self.search_var.trace("w", lambda *a: self._load())

        ctk.CTkLabel(inner, text="Plataforma:", text_color=COLORS["text_dim"],
                     font=ctk.CTkFont(size=13)).pack(side="left", padx=(0, 4))
        plataformas = self.db.get_plataformas(solo_activas=True)
        self.plat_filter_map = {"Todas": None}
        self.plat_filter_map.update({p["nombre"]: p["id"] for p in plataformas})
        self.plat_filter = ctk.CTkComboBox(
            inner, values=list(self.plat_filter_map.keys()),
            width=150, height=34, corner_radius=8,
            fg_color="#0d1828", border_color=COLORS["border"],
            button_color=COLORS["accent"],
            font=ctk.CTkFont(size=13), text_color=COLORS["text"],
            command=lambda e: self._load())
        self.plat_filter.set("Todas")
        self.plat_filter.pack(side="left", padx=(0, 10))

        ctk.CTkLabel(inner, text="Estado:", text_color=COLORS["text_dim"],
                     font=ctk.CTkFont(size=13)).pack(side="left", padx=(0, 4))
        self.estado_filter = ctk.CTkComboBox(
            inner, values=["Todos", "pagada", "pendiente"],
            width=120, height=34, corner_radius=8,
            fg_color="#0d1828", border_color=COLORS["border"],
            button_color=COLORS["accent"],
            font=ctk.CTkFont(size=13), text_color=COLORS["text"],
            command=lambda e: self._load())
        self.estado_filter.set("Todos")
        self.estado_filter.pack(side="left")

        self.count_label = ctk.CTkLabel(inner, text="",
                                         text_color=COLORS["text_dim"],
                                         font=ctk.CTkFont(size=12))
        self.count_label.pack(side="right", padx=8)

        # ══════════════════════════════════════════════════
        #  BARRA DE ACCIONES — SIEMPRE VISIBLE, ANTES DE
        #  LA TABLA (no al final, así no hay que hacer scroll)
        # ══════════════════════════════════════════════════
        act_card = card(self)
        act_card.pack(fill="x", padx=24, pady=(0, 4))
        act = ctk.CTkFrame(act_card, fg_color="transparent")
        act.pack(fill="x", padx=14, pady=8)

        ctk.CTkLabel(act, text="Selecciona una fila:",
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_dim"]).pack(side="left", padx=(0, 10))

        # ── Editar ──
        primary_btn(
            act, "✏️  Editar",
            command=self._editar,
            height=36, width=110
        ).pack(side="left", padx=(0, 6))

        # ── Eliminar ──
        danger_btn(
            act, "🗑  Eliminar",
            command=self._eliminar,
            height=36, width=110
        ).pack(side="left", padx=(0, 14))

        # Separador
        ctk.CTkFrame(act, width=1, height=28,
                     fg_color=COLORS["border"]).pack(side="left", padx=(0, 14))

        # ── Generar Tirilla ──
        ctk.CTkButton(
            act,
            text="🧾  Generar / Re-enviar Tirilla",
            command=self._tirilla,
            height=36, corner_radius=8,
            fg_color="#0e6027", hover_color="#0b4d1f",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="white",
        ).pack(side="left")

        # Tip lado derecho
        ctk.CTkLabel(act,
                     text="Doble clic en la fila = editar rápido",
                     font=ctk.CTkFont(size=11),
                     text_color="#3d5470").pack(side="right")

        # ── Tabla ──
        cols = ("factura", "cliente", "perfil", "telefono",
                "plataforma", "vence", "dias", "estado", "precio")
        anchors = {
            "factura":    "center",
            "cliente":    "w",
            "perfil":     "center",
            "telefono":   "center",
            "plataforma": "center",
            "vence":      "center",
            "dias":       "center",
            "estado":     "center",
            "precio":     "center",
        }
        table_frame, self.tree = build_treeview(
            self, cols, heights=18, col_anchors=anchors)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        col_cfg = {
            "factura":    ("#",          58),
            "cliente":    ("Cliente",    145),
            "perfil":     ("Perfil",     88),
            "telefono":   ("Teléfono",   108),
            "plataforma": ("Plataforma", 128),
            "vence":      ("Vence",       98),
            "dias":       ("Días",        65),
            "estado":     ("Estado",     108),
            "precio":     ("Precio",      88),
        }
        for c, (h, w) in col_cfg.items():
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w, minwidth=40)

        self.tree.bind("<Double-1>", lambda e: self._editar())

    # ── Carga de datos ──────────────────────────────────────
    def _load(self):
        filtros = {}
        q = self.search_var.get().strip()
        if q:
            filtros["busqueda"] = q
        plat = self.plat_filter.get()
        if plat != "Todas":
            filtros["plataforma_id"] = self.plat_filter_map.get(plat)
        estado = self.estado_filter.get()
        if estado != "Todos":
            filtros["estado_pago"] = estado

        ventas = self.db.get_ventas(filtros)
        self.count_label.configure(text=f"{len(ventas)} registros")

        self.tree.delete(*self.tree.get_children())
        for v in ventas:
            days = days_remaining(v.get("fecha_vencimiento", ""))
            badge, _ = days_badge(days)
            estado_txt = "✅ Pagada" if v["estado_pago"] == "pagada" else "⏳ Pendiente"
            self.tree.insert("", "end", iid=str(v["id"]), values=(
                f"#{v.get('numero_factura', '—')}",
                v["cliente"],
                v.get("perfil", ""),
                v.get("telefono", ""),
                v.get("plataforma_nombre", "—"),
                v.get("fecha_vencimiento", "—"),
                badge,
                estado_txt,
                f"${v['precio_venta']:,.0f}",
            ))

    # ── Helpers ─────────────────────────────────────────────
    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(
                "Sin selección",
                "Haz clic sobre una fila de la tabla para seleccionarla,\n"
                "luego elige la acción que deseas realizar.")
            return None
        return int(sel[0])

    def _editar(self):
        vid = self._selected_id()
        if not vid:
            return
        venta = self.db.get_venta_by_id(vid)
        if not venta:
            return
        self.app.show_view("ventas")
        for w in self.app.content_frame.winfo_children():
            if hasattr(w, "cargar_venta"):
                w.cargar_venta(venta)
                break

    def _eliminar(self):
        vid = self._selected_id()
        if not vid:
            return
        sel    = self.tree.selection()
        nombre = self.tree.item(sel[0])["values"][1] if sel else "esta venta"
        if messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Eliminar la venta de '{nombre}'?\n\n"
                "Esta acción no se puede deshacer."):
            self.db.delete_venta(vid)
            self._load()
            messagebox.showinfo("✅", "Venta eliminada correctamente.")

    def _tirilla(self):
        vid = self._selected_id()
        if not vid:
            return
        venta = self.db.get_venta_by_id(vid)
        if not venta:
            return
        config = self.db.get_config()
        generar_tirilla(venta, config)
