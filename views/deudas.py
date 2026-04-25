import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from widgets import (COLORS, card, title_label, primary_btn, secondary_btn,
                     danger_btn, entry_field, build_treeview,
                     days_remaining, days_badge, DateEntryWidget)
from cuenta_cobro import generar_cuenta_cobro


class DeudasView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db  = db
        self.app = app
        self._build()
        self._load()

    def _build(self):
        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 6))
        title_label(hdr, "📋  Deudas — Distribuidores", size=22).pack(side="left")

        # ════════════════════════════════════════════════
        #  BOTÓN CUENTA DE COBRO — MUY VISIBLE ARRIBA
        # ════════════════════════════════════════════════
        cobro_card = ctk.CTkFrame(self, fg_color="#0e2040", corner_radius=12,
                                   border_width=1, border_color="#1d6fd8")
        cobro_card.pack(fill="x", padx=24, pady=(0, 6))

        cobro_inner = ctk.CTkFrame(cobro_card, fg_color="transparent")
        cobro_inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(cobro_inner,
                     text="🧾  Cuenta de Cobro:",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["accent2"]).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(cobro_inner,
                     text="Filtra por distribuidor y fechas → luego haz clic en Generar",
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_dim"]).pack(side="left", padx=(0, 20))

        ctk.CTkButton(
            cobro_inner,
            text="📄  Generar Cuenta de Cobro",
            command=self._generar_cuenta_cobro,
            height=36, corner_radius=8,
            fg_color="#1d4ed8", hover_color="#1558b0",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
        ).pack(side="right")

        # ── Resumen ──
        self.summary_card = card(self)
        self.summary_card.pack(fill="x", padx=24, pady=(0, 4))
        self.sum_label = ctk.CTkLabel(
            self.summary_card, text="",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["accent2"])
        self.sum_label.pack(padx=16, pady=8)

        # ── Filtros ──
        fcard = card(self)
        fcard.pack(fill="x", padx=24, pady=(0, 4))

        f1 = ctk.CTkFrame(fcard, fg_color="transparent")
        f1.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(f1, text="Distribuidor:",
                     font=ctk.CTkFont(size=13), text_color=COLORS["text_dim"],
                     width=100, anchor="w").pack(side="left")

        distribuidores = self.db.get_proveedores()
        self.dist_map  = {"Todos": None}
        self.dist_map.update({p["nombre"]: p["id"] for p in distribuidores})

        self.dist_filter = ctk.CTkComboBox(
            f1, values=list(self.dist_map.keys()),
            width=200, height=34, corner_radius=8,
            fg_color="#0d1828", border_color=COLORS["border"],
            button_color=COLORS["accent"],
            font=ctk.CTkFont(size=13), text_color=COLORS["text"],
            command=lambda e: self._load())
        self.dist_filter.set("Todos")
        self.dist_filter.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(f1, text="Plataforma:",
                     font=ctk.CTkFont(size=13), text_color=COLORS["text_dim"],
                     width=80, anchor="w").pack(side="left")

        plataformas  = self.db.get_plataformas()
        self.plat_map = {"Todas": None}
        self.plat_map.update({p["nombre"]: p["id"] for p in plataformas})

        self.plat_filter = ctk.CTkComboBox(
            f1, values=list(self.plat_map.keys()),
            width=180, height=34, corner_radius=8,
            fg_color="#0d1828", border_color=COLORS["border"],
            button_color=COLORS["accent"],
            font=ctk.CTkFont(size=13), text_color=COLORS["text"],
            command=lambda e: self._load())
        self.plat_filter.set("Todas")
        self.plat_filter.pack(side="left", padx=(0, 20))

        self.count_label = ctk.CTkLabel(f1, text="",
                                         font=ctk.CTkFont(size=12),
                                         text_color=COLORS["text_dim"])
        self.count_label.pack(side="right")

        f2 = ctk.CTkFrame(fcard, fg_color="transparent")
        f2.pack(fill="x", padx=14, pady=(4, 10))

        ctk.CTkLabel(f2, text="Desde:",
                     font=ctk.CTkFont(size=13), text_color=COLORS["text_dim"],
                     width=100, anchor="w").pack(side="left")
        self.fecha_desde = DateEntryWidget(f2, width=120)
        self.fecha_desde.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(f2, text="Hasta:",
                     font=ctk.CTkFont(size=13), text_color=COLORS["text_dim"],
                     width=55, anchor="w").pack(side="left")
        self.fecha_hasta = DateEntryWidget(f2, width=120)
        self.fecha_hasta.pack(side="left", padx=(0, 20))

        primary_btn(f2, "🔍  Filtrar",
                    command=self._load, height=34, width=100).pack(side="left", padx=(0, 8))
        secondary_btn(f2, "✕  Limpiar",
                      command=self._limpiar_filtros, height=34, width=100).pack(side="left")

        # ── Tabla ──
        cols = ("factura", "cliente", "telefono", "plataforma", "distribuidor",
                "f_activacion", "f_vence", "dias", "precio")
        anchors = {c: "center" for c in cols}
        anchors["cliente"]      = "w"
        anchors["distribuidor"] = "center"

        tf, self.tree = build_treeview(self, cols, heights=13, col_anchors=anchors)
        tf.pack(fill="both", expand=True, padx=24, pady=(0, 4))

        col_cfg = {
            "factura":      ("#",            55),
            "cliente":      ("Cliente",      128),
            "telefono":     ("Teléfono",     108),
            "plataforma":   ("Plataforma",   118),
            "distribuidor": ("Distribuidor", 130),
            "f_activacion": ("F. Activación", 98),
            "f_vence":      ("F. Vence",      98),
            "dias":         ("Días rest.",    72),
            "precio":       ("Precio",        82),
        }
        for c, (h, w) in col_cfg.items():
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)

        # ── Acciones inferiores ──
        act_card = card(self)
        act_card.pack(fill="x", padx=24, pady=(0, 12))
        act = ctk.CTkFrame(act_card, fg_color="transparent")
        act.pack(fill="x", padx=14, pady=8)

        ctk.CTkButton(
            act, text="✅  Marcar como Pagada",
            command=self._marcar_pagada,
            height=36, corner_radius=8,
            fg_color="#065f46", hover_color="#044a35",
            font=ctk.CTkFont(size=13, weight="bold"), text_color="white"
        ).pack(side="left", padx=(0, 8))

        secondary_btn(act, "🔄  Actualizar",
                      command=self._load, height=36).pack(side="left")

    # ── Datos ────────────────────────────────────────
    def _load(self, *_):
        filtros = {"estado_pago": "pendiente"}

        dist_id = self.dist_map.get(self.dist_filter.get())
        if dist_id:
            filtros["proveedor_id"] = dist_id

        plat_id = self.plat_map.get(self.plat_filter.get())
        if plat_id:
            filtros["plataforma_id"] = plat_id

        fd = self.fecha_desde.get().strip()
        fh = self.fecha_hasta.get().strip()
        if fd: filtros["fecha_desde"] = fd
        if fh: filtros["fecha_hasta"] = fh

        deudas = self.db.get_ventas(filtros)
        total  = sum(d["precio_venta"] for d in deudas)
        self.sum_label.configure(
            text=f"⚠️  {len(deudas)} ventas pendientes  •  Total: ${total:,.0f}")
        self.count_label.configure(text=f"{len(deudas)} registros")

        self.tree.delete(*self.tree.get_children())
        for d in deudas:
            days  = days_remaining(d.get("fecha_vencimiento", ""))
            badge, _ = days_badge(days)
            self.tree.insert("", "end", iid=str(d["id"]), values=(
                f"#{d.get('numero_factura','—')}",
                d["cliente"],
                d.get("telefono", ""),
                d.get("plataforma_nombre", "—"),
                d.get("proveedor_nombre", "—"),
                d.get("fecha_activacion", "—"),
                d.get("fecha_vencimiento", "—"),
                badge,
                f"${d['precio_venta']:,.0f}",
            ))

    def _limpiar_filtros(self):
        self.dist_filter.set("Todos")
        self.plat_filter.set("Todas")
        self.fecha_desde.set("")
        self.fecha_hasta.set("")
        self._load()

    def _marcar_pagada(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una venta de la lista.")
            return
        vid   = int(sel[0])
        venta = self.db.get_venta_by_id(vid)
        if not venta: return
        data = dict(venta)
        data["estado_pago"] = "pagada"
        self.db.update_venta(vid, data)
        messagebox.showinfo("✅", "Venta marcada como pagada.")
        self._load()

    def _generar_cuenta_cobro(self):
        dist_nombre = self.dist_filter.get()
        if dist_nombre == "Todos":
            messagebox.showwarning(
                "Selecciona un Distribuidor",
                "En el filtro 'Distribuidor' selecciona uno específico\n"
                "(ej: Adriana revendedora) y luego haz clic en Generar.")
            return

        dist_id = self.dist_map.get(dist_nombre)
        filtros = {"estado_pago": "pendiente", "proveedor_id": dist_id}

        plat_id = self.plat_map.get(self.plat_filter.get())
        if plat_id: filtros["plataforma_id"] = plat_id

        fd = self.fecha_desde.get().strip()
        fh = self.fecha_hasta.get().strip()
        if fd: filtros["fecha_desde"] = fd
        if fh: filtros["fecha_hasta"] = fh

        deudas = self.db.get_ventas(filtros)
        if not deudas:
            messagebox.showinfo("Sin datos",
                f"No hay deudas pendientes para '{dist_nombre}' con esos filtros.")
            return

        config = self.db.get_config()
        generar_cuenta_cobro(
            distribuidor_nombre=dist_nombre,
            deudas=deudas,
            config=config,
            fecha_desde=fd,
            fecha_hasta=fh,
        )
