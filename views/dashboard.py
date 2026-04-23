import customtkinter as ctk
from tkinter import ttk
from widgets import COLORS, card, title_label, dim_label, stat_card, days_badge, days_remaining, build_treeview
from datetime import datetime


class Dashboard(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db  = db
        self.app = app
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_dark"], corner_radius=0,
            scrollbar_button_color=COLORS["border"])
        scroll.pack(fill="both", expand=True)

        # ── Header ──
        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(24, 8))
        config = self.db.get_config()
        bname  = config.get("business_name", "StreamControl")
        title_label(hdr, f"🏠  Dashboard — {bname}", size=22).pack(side="left")
        dim_label(hdr, datetime.now().strftime("%A, %d de %B %Y")).pack(side="right", pady=4)

        # ── Tarjetas de estadísticas ──
        sf = ctk.CTkFrame(scroll, fg_color="transparent")
        sf.pack(fill="x", padx=24, pady=(8, 4))
        for i in range(4):
            sf.grid_columnconfigure(i, weight=1)

        res_dia = self.db.get_resumen_ventas("dia")
        res_mes = self.db.get_resumen_ventas("mes")
        deudas  = self.db.get_deudas()

        cards_data = [
            ("💰", "Ventas hoy",    res_dia["cantidad"],              COLORS["accent"]),
            ("📈", "Ingresos hoy",  f"${res_dia['total']:,.0f}",      COLORS["accent3"]),
            ("📅", "Ventas mes",    res_mes["cantidad"],              COLORS["accent2"]),
            ("⚠️",  "Deudas pend.", len(deudas),
             COLORS["yellow"] if deudas else COLORS["text_dim"]),
        ]
        for i, (icon, ttl, val, color) in enumerate(cards_data):
            stat_card(sf, icon, ttl, val, color).grid(
                row=0, column=i, padx=6, pady=4, sticky="ew")

        # ── Layout dos columnas ──
        cols_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cols_frame.pack(fill="both", expand=True, padx=24, pady=8)
        cols_frame.grid_columnconfigure(0, weight=3)
        cols_frame.grid_columnconfigure(1, weight=2)
        cols_frame.grid_rowconfigure(0, weight=1)

        # ═══════════════════════════════════════════════
        #  IZQUIERDA — Ventas Recientes (treeview igual
        #  al de Clientes, bien alineado y centrado)
        # ═══════════════════════════════════════════════
        left = card(cols_frame)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="📋  Ventas Recientes",
                     font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                     text_color="#ffffff").grid(row=0, column=0, sticky="w",
                                                padx=16, pady=(14, 6))

        ventas = self.db.get_ventas()[:15]

        cols_tv  = ("cliente", "plataforma", "vence", "dias", "estado", "precio")
        anchors  = {
            "cliente":    "w",
            "plataforma": "center",
            "vence":      "center",
            "dias":       "center",
            "estado":     "center",
            "precio":     "center",
        }
        tv_frame, tree = build_treeview(left, cols_tv,
                                        heights=min(len(ventas) + 1, 12),
                                        col_anchors=anchors)
        tv_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        col_cfg = {
            "cliente":    ("Cliente",    150),
            "plataforma": ("Plataforma", 140),
            "vence":      ("Vence",       90),
            "dias":       ("Días",        60),
            "estado":     ("Estado",      90),
            "precio":     ("Precio",      80),
        }
        for c, (h, w) in col_cfg.items():
            tree.heading(c, text=h)
            tree.column(c, width=w, minwidth=40)

        for v in ventas:
            days  = days_remaining(v.get("fecha_vencimiento", ""))
            badge, _ = days_badge(days)
            estado_txt = "✅ Pagada" if v["estado_pago"] == "pagada" else "⏳ Pendiente"
            tree.insert("", "end", values=(
                v["cliente"][:22],
                v.get("plataforma_nombre", "—"),
                v.get("fecha_vencimiento", "—"),
                badge,
                estado_txt,
                f"${v['precio_venta']:,.0f}",
            ))

        if not ventas:
            ctk.CTkLabel(left, text="No hay ventas registradas aún",
                         text_color=COLORS["text_dim"],
                         font=ctk.CTkFont(size=12)).grid(row=1, column=0, pady=30)

        # ═══════════════════════════════════════════════
        #  DERECHA — Top plataformas + Próximos a vencer
        # ═══════════════════════════════════════════════
        right = ctk.CTkFrame(cols_frame, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Top plataformas
        top_p = card(right)
        top_p.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkLabel(top_p, text="📺  Top Plataformas (mes)",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#ffffff").pack(anchor="w", padx=14, pady=(12, 6))

        por_plat  = res_mes.get("por_plataforma", [])
        total_mes = res_mes["cantidad"] or 1
        acc       = [COLORS["accent"], COLORS["accent2"], COLORS["accent3"], COLORS["accent4"]]

        for i, p in enumerate(por_plat[:5]):
            color = acc[i % len(acc)]
            pct   = p["cantidad"] / total_mes
            row   = ctk.CTkFrame(top_p, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row, text=p["nombre"][:16],
                         font=ctk.CTkFont(size=12), text_color=COLORS["text"],
                         width=110, anchor="w").pack(side="left")
            bar = ctk.CTkProgressBar(row, height=12, corner_radius=6,
                                     fg_color=COLORS["border"],
                                     progress_color=color)
            bar.set(pct)
            bar.pack(side="left", fill="x", expand=True, padx=(6, 8))
            ctk.CTkLabel(row, text=str(p["cantidad"]),
                         font=ctk.CTkFont(size=12), text_color=color,
                         width=22).pack(side="right")

        if not por_plat:
            ctk.CTkLabel(top_p, text="Sin datos aún",
                         text_color=COLORS["text_dim"],
                         font=ctk.CTkFont(size=12)).pack(pady=14)

        # Próximos a vencer
        alert_card = card(right)
        alert_card.grid(row=1, column=0, sticky="nsew")
        ctk.CTkLabel(alert_card, text="⏰  Próximos a vencer",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#ffffff").pack(anchor="w", padx=14, pady=(12, 6))

        all_v    = self.db.get_ventas()
        proximos = sorted(
            [v for v in all_v
             if days_remaining(v.get("fecha_vencimiento", "")) is not None
             and 0 <= days_remaining(v["fecha_vencimiento"]) <= 10],
            key=lambda x: days_remaining(x["fecha_vencimiento"])
        )[:8]

        for v in proximos:
            days  = days_remaining(v["fecha_vencimiento"])
            badge, bc = days_badge(days)
            r = ctk.CTkFrame(alert_card, fg_color=COLORS["bg_sidebar"], corner_radius=8)
            r.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(r, text=v["cliente"][:18],
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["text"]).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(r, text=badge,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=bc).pack(side="right", padx=10)

        if not proximos:
            ctk.CTkLabel(alert_card, text="✅ Sin vencimientos próximos",
                         text_color=COLORS["accent3"],
                         font=ctk.CTkFont(size=12)).pack(pady=14)
