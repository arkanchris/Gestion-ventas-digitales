import customtkinter as ctk
import tkinter as tk
from widgets import (COLORS, card, title_label, dim_label, stat_card, build_treeview)
from datetime import datetime


class ReportesView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db = db
        self.app = app
        self.periodo_var = tk.StringVar(value="mes")
        self._build()
        self._load()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0,
                                         scrollbar_button_color=COLORS["border"])
        scroll.pack(fill="both", expand=True)

        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(24, 8))
        title_label(hdr, "📊  Reportes y Estadísticas", size=22).pack(side="left")

        # Period selector
        period_card = card(scroll)
        period_card.pack(fill="x", padx=24, pady=4)
        pf = ctk.CTkFrame(period_card, fg_color="transparent")
        pf.pack(padx=16, pady=12)

        ctk.CTkLabel(pf, text="Ver reporte por:",
                     font=ctk.CTkFont(size=13), text_color=COLORS["text_dim"]).pack(side="left", padx=(0,12))

        periods = [("📅 Hoy", "dia"), ("📆 Semana", "semana"), ("🗓 Mes", "mes"), ("📈 Año", "anio")]
        for label, val in periods:
            ctk.CTkRadioButton(pf, text=label, variable=self.periodo_var, value=val,
                               fg_color=COLORS["accent"],
                               font=ctk.CTkFont(size=13), text_color=COLORS["text"],
                               command=self._load).pack(side="left", padx=8)

        # Stats row
        self.stats_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=24, pady=8)

        # Platform breakdown table
        tbl_card = card(scroll)
        tbl_card.pack(fill="x", padx=24, pady=4)
        ctk.CTkLabel(tbl_card, text="📺  Ventas por Plataforma",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(12, 6))

        self.plat_frame = ctk.CTkFrame(tbl_card, fg_color="transparent")
        self.plat_frame.pack(fill="x", padx=16, pady=(0, 12))

        # All time totals
        totals_card = card(scroll)
        totals_card.pack(fill="x", padx=24, pady=(4, 16))
        ctk.CTkLabel(totals_card, text="📈  Todas las Plataformas (historial total)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(12, 6))

        cols = ("plataforma", "cantidad", "ingresos", "ganancia")
        anchors_r = {"plataforma":"w","cantidad":"center","ingresos":"center","ganancia":"center"}
        tf, self.all_tree = build_treeview(totals_card, cols, heights=8, col_anchors=anchors_r)
        tf.pack(fill="x", padx=16, pady=(0, 12))
        for c, (h, w) in {
            "plataforma": ("Plataforma", 180),
            "cantidad":   ("Ventas",     90),
            "ingresos":   ("Ingresos",   120),
            "ganancia":   ("🔒 Ganancia",120),
        }.items():
            self.all_tree.heading(c, text=h)
            self.all_tree.column(c, width=w)

    def _load(self):
        periodo = self.periodo_var.get()
        res = self.db.get_resumen_ventas(periodo)

        # Clear stats
        for w in self.stats_frame.winfo_children():
            w.destroy()
        for i in range(4):
            self.stats_frame.grid_columnconfigure(i, weight=1)

        total_ing = res["total"]
        cantidad  = res["cantidad"]
        # Calculate ganancia from plataforma breakdown
        total_gan = sum(p.get("ganancia", 0) or 0 for p in res["por_plataforma"])

        periodo_labels = {"dia": "hoy", "semana": "esta semana", "mes": "este mes", "anio": "este año"}
        plabel = periodo_labels.get(periodo, "")

        cards_data = [
            ("🛒", f"Ventas {plabel}",    cantidad,              COLORS["accent"]),
            ("💰", "Ingresos totales",    f"${total_ing:,.0f}",  COLORS["accent3"]),
            ("💹", "Ganancia estimada",   f"${total_gan:,.0f}",  COLORS["accent2"]),
            ("📦", "Plataformas distintas", len(res["por_plataforma"]), COLORS["accent4"]),
        ]
        for i, (icon, ttl, val, color) in enumerate(cards_data):
            sc = stat_card(self.stats_frame, icon, ttl, val, color)
            sc.grid(row=0, column=i, padx=6, pady=4, sticky="ew")

        # Platform breakdown bars
        for w in self.plat_frame.winfo_children():
            w.destroy()

        total_qty = cantidad or 1
        accent_list = [COLORS["accent"], COLORS["accent2"], COLORS["accent3"], COLORS["accent4"]]

        if res["por_plataforma"]:
            for i, p in enumerate(res["por_plataforma"]):
                color = accent_list[i % len(accent_list)]
                pct = p["cantidad"] / total_qty
                row = ctk.CTkFrame(self.plat_frame, fg_color="transparent")
                row.pack(fill="x", pady=4)
                row.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(row, text=p["nombre"][:20], width=150,
                             font=ctk.CTkFont(size=13), text_color=COLORS["text"],
                             anchor="w").grid(row=0, column=0, sticky="w")

                bar = ctk.CTkProgressBar(row, height=18, corner_radius=8,
                                         fg_color=COLORS["border"], progress_color=color)
                bar.set(pct)
                bar.grid(row=0, column=1, sticky="ew", padx=12)

                ganancia = p.get("ganancia") or 0
                info = f"{p['cantidad']} ventas  •  ${p.get('total',0):,.0f}  •  🔒 ${ganancia:,.0f}"
                ctk.CTkLabel(row, text=info, width=280,
                             font=ctk.CTkFont(size=12), text_color=color,
                             anchor="e").grid(row=0, column=2, sticky="e")
        else:
            ctk.CTkLabel(self.plat_frame, text="Sin datos para este período",
                         text_color=COLORS["text_dim"], font=ctk.CTkFont(size=13)).pack(pady=16)

        # All time table
        self.all_tree.delete(*self.all_tree.get_children())
        res_all = self.db.get_resumen_ventas("todo")
        for p in res_all["por_plataforma"]:
            ganancia = p.get("ganancia") or 0
            self.all_tree.insert("", "end", values=(
                p["nombre"],
                p["cantidad"],
                f"${p.get('total',0):,.0f}",
                f"${ganancia:,.0f}",
            ))
