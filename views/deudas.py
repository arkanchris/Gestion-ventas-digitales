import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from widgets import (COLORS, card, title_label, primary_btn, secondary_btn,
                     build_treeview, days_remaining, days_badge)


class DeudasView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db = db
        self.app = app
        self._build()
        self._load()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(24, 8))
        title_label(hdr, "📋  Sistema de Deudas / Pendientes", size=22).pack(side="left")

        # Summary
        self.summary = card(self)
        self.summary.pack(fill="x", padx=24, pady=4)
        self.sum_label = ctk.CTkLabel(self.summary, text="",
                                       font=ctk.CTkFont(size=14, weight="bold"),
                                       text_color=COLORS["accent2"])
        self.sum_label.pack(padx=16, pady=12)

        # Table
        cols = ("factura", "cliente", "telefono", "plataforma", "proveedor",
                "precio", "vence", "dias", "credito_prov")
        anchors_d = {"factura":"center","cliente":"w","telefono":"center","plataforma":"center","proveedor":"center","precio":"center","vence":"center","dias":"center","credito_prov":"center"}
        tf, self.tree = build_treeview(self, cols, heights=16, col_anchors=anchors_d)
        tf.pack(fill="both", expand=True, padx=24, pady=4)

        col_cfg = {
            "factura":    ("#",           60),
            "cliente":    ("Cliente",     150),
            "telefono":   ("Teléfono",    110),
            "plataforma": ("Plataforma",  110),
            "proveedor":  ("Proveedor",   120),
            "precio":     ("Precio",      90),
            "vence":      ("Vence",       100),
            "dias":       ("Días rest.",  80),
            "credito_prov": ("Créd. Prov.", 90),
        }
        for c, (h, w) in col_cfg.items():
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)

        act = ctk.CTkFrame(self, fg_color="transparent")
        act.pack(fill="x", padx=24, pady=(0, 12))
        primary_btn(act, "✅  Marcar como Pagada", command=self._marcar_pagada,
                    fg_color=COLORS["accent3"], hover_color="#28c96a",
                    text_color="#0f1117").pack(side="left", padx=(0, 8))
        secondary_btn(act, "🔄  Actualizar", command=self._load).pack(side="left")

    def _load(self):
        deudas = self.db.get_deudas()
        self.tree.delete(*self.tree.get_children())

        total = sum(d["precio_venta"] for d in deudas)
        self.sum_label.configure(
            text=f"⚠️  {len(deudas)} ventas pendientes de pago  •  Total: ${total:,.0f}"
        )

        for d in deudas:
            days = days_remaining(d.get("fecha_vencimiento",""))
            badge, _ = days_badge(days)
            # Check if provider has credit
            provs = self.db.get_proveedores()
            prov_credito = "—"
            for p in provs:
                if p["id"] == d.get("proveedor_id"):
                    prov_credito = "💳 Sí" if p["maneja_credito"] else "No"
                    break

            self.tree.insert("", "end", iid=str(d["id"]), values=(
                f"#{d.get('numero_factura','—')}",
                d["cliente"],
                d.get("telefono", ""),
                d.get("plataforma_nombre","—"),
                d.get("proveedor_nombre","—"),
                f"${d['precio_venta']:,.0f}",
                d.get("fecha_vencimiento","—"),
                badge,
                prov_credito,
            ))

    def _marcar_pagada(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una venta.")
            return
        vid = int(sel[0])
        venta = self.db.get_venta_by_id(vid)
        if not venta:
            return
        venta_data = dict(venta)
        venta_data["estado_pago"] = "pagada"
        self.db.update_venta(vid, venta_data)
        messagebox.showinfo("✅", "Venta marcada como pagada.")
        self._load()
