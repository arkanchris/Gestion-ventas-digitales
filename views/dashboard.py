import customtkinter as ctk
from widgets import (COLORS, card, title_label, dim_label, stat_card,
                     pill_badge, days_badge, days_remaining)
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
        title_label(hdr, f"Dashboard — {bname}", size=22).pack(side="left")
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
            ("💰", "Ventas hoy",    res_dia["cantidad"],              COLORS["accent4"]),
            ("📈", "Ingresos hoy",  f"${res_dia['total']:,.0f}",      COLORS["accent3"]),
            ("📅", "Ventas mes",    res_mes["cantidad"],              COLORS["accent2"]),
            ("⚠️",  "Deudas pend.", len(deudas),
             COLORS["red"] if deudas else COLORS["text_dim"]),
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
        #  IZQUIERDA — Ventas Recientes (tarjetas con
        #  insignias de color, no tabla nativa)
        # ═══════════════════════════════════════════════
        left = card(cols_frame)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        ctk.CTkLabel(left, text="Ventas recientes",
                     font=ctk.CTkFont(family="Bahnschrift", size=14, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=18, pady=(16, 4))

        # Encabezado + filas en UNA SOLA cuadrícula (grid) compartida:
        # así el ancho de cada columna se define en un único lugar y es
        # IMPOSIBLE que el encabezado y los datos queden desalineados.
        COLS = [
            ("CLIENTE",    120, "w"),
            ("PLATAFORMA", 120, "w"),
            ("VENCE",       78, "w"),
            ("DÍAS",        56, ""),
            ("ESTADO",      76, ""),
            ("PRECIO",      78, "e"),
        ]

        table = ctk.CTkFrame(left, fg_color="transparent")
        table.pack(fill="both", expand=True, padx=18, pady=(4, 14))
        for c, (_, w, _a) in enumerate(COLS):
            table.grid_columnconfigure(c, minsize=w, weight=0)

        for c, (txt, w, anchor) in enumerate(COLS):
            ctk.CTkLabel(table, text=txt, anchor=anchor or "center",
                         font=ctk.CTkFont(family="Bahnschrift", size=10, weight="bold"),
                         text_color=COLORS["text_dim"]
                         ).grid(row=0, column=c, sticky=anchor, padx=(0, 6), pady=(0, 8))

        ventas = self.db.get_ventas()[:12]
        row_i = 1

        for v in ventas:
            days   = days_remaining(v.get("fecha_vencimiento", ""))
            d_txt, d_color = days_badge(days)
            pagada = v["estado_pago"] == "pagada"
            e_txt   = "Pagada" if pagada else "Pendiente"
            e_color = COLORS["accent3"] if pagada else COLORS["accent4"]

            ctk.CTkLabel(table, text=v["cliente"][:16], anchor="w",
                         font=ctk.CTkFont(family="Segoe UI", size=12),
                         text_color=COLORS["text"]
                         ).grid(row=row_i, column=0, sticky="w", padx=(0, 6), pady=7)
            ctk.CTkLabel(table, text=(v.get("plataforma_nombre") or "—")[:15], anchor="w",
                         font=ctk.CTkFont(family="Segoe UI", size=12),
                         text_color=COLORS["text_dim"]
                         ).grid(row=row_i, column=1, sticky="w", padx=(0, 6))
            ctk.CTkLabel(table, text=v.get("fecha_vencimiento", "—"), anchor="w",
                         font=ctk.CTkFont(family="Consolas", size=11),
                         text_color=COLORS["text_dim"]
                         ).grid(row=row_i, column=2, sticky="w", padx=(0, 6))

            pill_badge(table, d_txt, d_color).grid(row=row_i, column=3, pady=3)
            pill_badge(table, e_txt, e_color).grid(row=row_i, column=4, pady=3)

            ctk.CTkLabel(table, text=f"${v['precio_venta']:,.0f}", anchor="e",
                         font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                         text_color=COLORS["text"]
                         ).grid(row=row_i, column=5, sticky="e", padx=(6, 0))

            row_i += 1
            ctk.CTkFrame(table, height=1, fg_color=COLORS["border"]).grid(
                row=row_i, column=0, columnspan=6, sticky="ew", pady=(7, 7))
            row_i += 1

        if not ventas:
            ctk.CTkLabel(rows_wrap, text="No hay ventas registradas aún",
                         text_color=COLORS["text_dim"],
                         font=ctk.CTkFont(size=12)).pack(pady=30)

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
        ctk.CTkLabel(top_p, text="Top plataformas (mes)",
                     font=ctk.CTkFont(family="Bahnschrift", size=13, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 8))

        por_plat  = res_mes.get("por_plataforma", [])
        total_mes = res_mes["cantidad"] or 1
        acc       = [COLORS["accent"], COLORS["accent2"], COLORS["accent3"], COLORS["accent4"]]

        for i, p in enumerate(por_plat[:5]):
            color = acc[i % len(acc)]
            pct   = p["cantidad"] / total_mes
            row   = ctk.CTkFrame(top_p, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=4)
            ctk.CTkLabel(row, text=p["nombre"][:16],
                         font=ctk.CTkFont(family="Segoe UI", size=12),
                         text_color=COLORS["text"],
                         width=112, anchor="w").pack(side="left")
            bar = ctk.CTkProgressBar(row, height=10, corner_radius=5,
                                     fg_color=COLORS["border"],
                                     progress_color=color)
            bar.set(pct)
            bar.pack(side="left", fill="x", expand=True, padx=(6, 8))
            ctk.CTkLabel(row, text=str(p["cantidad"]),
                         font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                         text_color=color,
                         width=22).pack(side="right")

        if not por_plat:
            ctk.CTkLabel(top_p, text="Sin datos aún",
                         text_color=COLORS["text_dim"],
                         font=ctk.CTkFont(size=12)).pack(pady=14)

        # Próximos a vencer
        alert_card = card(right)
        alert_card.grid(row=1, column=0, sticky="nsew")
        ctk.CTkLabel(alert_card, text="Próximos a vencer",
                     font=ctk.CTkFont(family="Bahnschrift", size=13, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(14, 8))

        all_v    = self.db.get_ventas()
        proximos = sorted(
            [v for v in all_v
             if days_remaining(v.get("fecha_vencimiento", "")) is not None
             and 0 <= days_remaining(v["fecha_vencimiento"]) <= 10],
            key=lambda x: days_remaining(x["fecha_vencimiento"])
        )[:8]

        for v in proximos:
            days = days_remaining(v["fecha_vencimiento"])
            d_txt, d_color = days_badge(days)
            r = ctk.CTkFrame(alert_card, fg_color=COLORS["bg_sidebar"], corner_radius=8)
            r.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(r, text=v["cliente"][:18],
                         font=ctk.CTkFont(family="Segoe UI", size=12),
                         text_color=COLORS["text"]).pack(side="left", padx=10, pady=8)
            pill_badge(r, d_txt, d_color).pack(side="right", padx=8, pady=6)

        if not proximos:
            ctk.CTkLabel(alert_card, text="✅ Sin vencimientos próximos",
                         text_color=COLORS["accent3"],
                         font=ctk.CTkFont(size=12)).pack(pady=14)