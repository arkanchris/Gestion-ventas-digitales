import customtkinter as ctk
import tkinter as tk
from widgets import (COLORS, card, title_label, dim_label, stat_card,
                     build_treeview, DateEntryWidget, primary_btn, secondary_btn)
from datetime import datetime, date


class ReportesView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db = db
        self.app = app
        self.periodo_var = tk.StringVar(value="mes")
        self._build()
        self._load()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_dark"], corner_radius=0,
            scrollbar_button_color=COLORS["border"])
        scroll.pack(fill="both", expand=True)

        # ── Header ──
        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(24, 8))
        title_label(hdr, "📊  Reportes y Estadísticas", size=22).pack(side="left")

        # ═══════════════════════════════════════════════════════
        #  SELECTORES DE PERÍODO
        # ═══════════════════════════════════════════════════════
        period_card = card(scroll)
        period_card.pack(fill="x", padx=24, pady=4)

        # Fila 1 — botones rápidos
        pf = ctk.CTkFrame(period_card, fg_color="transparent")
        pf.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(pf, text="Ver reporte por:",
                     font=ctk.CTkFont(size=13), text_color=COLORS["text_dim"]
                     ).pack(side="left", padx=(0, 12))

        periods = [
            ("📅 Hoy",    "dia"),
            ("📆 Semana", "semana"),
            ("🗓 Mes",    "mes"),
            ("📈 Año",    "anio"),
        ]
        for label, val in periods:
            ctk.CTkRadioButton(
                pf, text=label, variable=self.periodo_var, value=val,
                fg_color=COLORS["accent"],
                font=ctk.CTkFont(size=13), text_color=COLORS["text"],
                command=self._on_periodo_change
            ).pack(side="left", padx=8)

        # Separador
        ctk.CTkFrame(period_card, height=1,
                     fg_color=COLORS["border"]).pack(fill="x", padx=16)

        # Fila 2 — rango personalizado
        custom_frame = ctk.CTkFrame(period_card, fg_color="transparent")
        custom_frame.pack(fill="x", padx=16, pady=(8, 12))

        # Radio "Personalizado"
        self.radio_custom = ctk.CTkRadioButton(
            custom_frame,
            text="📆  Rango personalizado:",
            variable=self.periodo_var, value="personalizado",
            fg_color=COLORS["accent2"],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["accent2"],
            command=self._on_periodo_change
        )
        self.radio_custom.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(custom_frame, text="Desde:",
                     font=ctk.CTkFont(size=13), text_color=COLORS["text_dim"],
                     width=55, anchor="w").pack(side="left")
        self.fecha_desde = DateEntryWidget(custom_frame, width=120)
        self.fecha_desde.pack(side="left", padx=(0, 14))

        ctk.CTkLabel(custom_frame, text="Hasta:",
                     font=ctk.CTkFont(size=13), text_color=COLORS["text_dim"],
                     width=50, anchor="w").pack(side="left")
        self.fecha_hasta = DateEntryWidget(custom_frame, width=120)
        self.fecha_hasta.pack(side="left", padx=(0, 14))

        # Botones de rango personalizado
        primary_btn(custom_frame, "🔍  Consultar",
                    command=self._load,
                    height=34, width=110).pack(side="left", padx=(0, 8))

        secondary_btn(custom_frame, "✕  Limpiar",
                      command=self._limpiar_fechas,
                      height=34, width=90).pack(side="left", padx=(0, 14))

        # Atajos de fecha
        atajos = [
            ("Ayer",         self._set_ayer),
            ("Últ. 7 días",  self._set_ultima_semana),
            ("Últ. 30 días", self._set_ultimos_30),
            ("Mes anterior", self._set_mes_anterior),
        ]
        for txt, cmd in atajos:
            ctk.CTkButton(
                custom_frame, text=txt,
                command=cmd,
                height=28, width=90, corner_radius=6,
                fg_color=COLORS["border"], hover_color="#2a4a7a",
                font=ctk.CTkFont(size=11), text_color=COLORS["text_dim"]
            ).pack(side="left", padx=2)

        # Label de período activo
        self.periodo_label = ctk.CTkLabel(
            period_card, text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["accent2"])
        self.periodo_label.pack(anchor="e", padx=16, pady=(0, 8))

        # ── Tarjetas stats ──
        self.stats_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=24, pady=8)

        # ── Ventas por Plataforma ──
        tbl_card = card(scroll)
        tbl_card.pack(fill="x", padx=24, pady=4)
        ctk.CTkLabel(tbl_card, text="📺  Ventas por Plataforma",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(12, 6))
        self.plat_frame = ctk.CTkFrame(tbl_card, fg_color="transparent")
        self.plat_frame.pack(fill="x", padx=16, pady=(0, 12))

        # ── Historial total ──
        totals_card = card(scroll)
        totals_card.pack(fill="x", padx=24, pady=(4, 16))
        ctk.CTkLabel(totals_card, text="📈  Todas las Plataformas (historial total)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(12, 6))
        cols = ("plataforma", "cantidad", "ingresos", "ganancia")
        anchors_r = {"plataforma": "w", "cantidad": "center",
                     "ingresos": "center", "ganancia": "center"}
        tf, self.all_tree = build_treeview(totals_card, cols, heights=8, col_anchors=anchors_r)
        tf.pack(fill="x", padx=16, pady=(0, 12))
        for c, (h, w) in {
            "plataforma": ("Plataforma",  200),
            "cantidad":   ("Ventas",       90),
            "ingresos":   ("Ingresos",    130),
            "ganancia":   ("🔒 Ganancia", 130),
        }.items():
            self.all_tree.heading(c, text=h)
            self.all_tree.column(c, width=w)

    # ═══════════════════════════════════════════════════════════
    #  ATAJOS DE FECHA
    # ═══════════════════════════════════════════════════════════
    def _set_fechas(self, desde: date, hasta: date):
        self.fecha_desde.set(desde.strftime("%Y-%m-%d"))
        self.fecha_hasta.set(hasta.strftime("%Y-%m-%d"))
        self.periodo_var.set("personalizado")
        self._load()

    def _set_ayer(self):
        from datetime import timedelta
        ayer = date.today() - timedelta(days=1)
        self._set_fechas(ayer, ayer)

    def _set_ultima_semana(self):
        from datetime import timedelta
        hoy = date.today()
        self._set_fechas(hoy - timedelta(days=6), hoy)

    def _set_ultimos_30(self):
        from datetime import timedelta
        hoy = date.today()
        self._set_fechas(hoy - timedelta(days=29), hoy)

    def _set_mes_anterior(self):
        hoy = date.today()
        # Primer día del mes actual
        primer_este = hoy.replace(day=1)
        # Último día del mes anterior
        ultimo_ant  = primer_este - __import__("datetime").timedelta(days=1)
        # Primer día del mes anterior
        primer_ant  = ultimo_ant.replace(day=1)
        self._set_fechas(primer_ant, ultimo_ant)

    def _limpiar_fechas(self):
        self.fecha_desde.set("")
        self.fecha_hasta.set("")
        self.periodo_var.set("mes")
        self._load()

    def _on_periodo_change(self):
        """Al cambiar radio button, limpiar fechas personalizadas si no es 'personalizado'."""
        if self.periodo_var.get() != "personalizado":
            self.fecha_desde.set("")
            self.fecha_hasta.set("")
        self._load()

    # ═══════════════════════════════════════════════════════════
    #  CARGA DE DATOS
    # ═══════════════════════════════════════════════════════════
    def _load(self):
        periodo  = self.periodo_var.get()
        fd       = self.fecha_desde.get().strip()
        fh       = self.fecha_hasta.get().strip()

        # Si hay fechas personalizadas, usarlas
        if periodo == "personalizado":
            if not fd and not fh:
                self.periodo_label.configure(text="⚠️  Define al menos una fecha")
                return
            res = self.db.get_resumen_ventas("personalizado",
                                              fecha_desde=fd or None,
                                              fecha_hasta=fh or None)
            # Construir etiqueta del período
            if fd and fh:
                plabel = f"del {self._fmt(fd)} al {self._fmt(fh)}"
            elif fd:
                plabel = f"desde {self._fmt(fd)}"
            else:
                plabel = f"hasta {self._fmt(fh)}"
        else:
            res = self.db.get_resumen_ventas(periodo)
            labels = {
                "dia":    "hoy",
                "semana": "esta semana",
                "mes":    "este mes",
                "anio":   "este año",
            }
            plabel = labels.get(periodo, "")

        self.periodo_label.configure(text=f"📅  Mostrando: {plabel}")

        # ── Tarjetas ──
        for w in self.stats_frame.winfo_children():
            w.destroy()
        for i in range(4):
            self.stats_frame.grid_columnconfigure(i, weight=1)

        total_ing = res["total"]
        cantidad  = res["cantidad"]
        total_gan = sum(p.get("ganancia", 0) or 0 for p in res["por_plataforma"])

        cards_data = [
            ("🛒", f"Ventas",             cantidad,              COLORS["accent"]),
            ("💰", "Ingresos totales",    f"${total_ing:,.0f}",  COLORS["accent3"]),
            ("💹", "Ganancia estimada",   f"${total_gan:,.0f}",  COLORS["accent2"]),
            ("📦", "Plataformas distintas", len(res["por_plataforma"]), COLORS["accent4"]),
        ]
        for i, (icon, ttl, val, color) in enumerate(cards_data):
            sc = stat_card(self.stats_frame, icon, ttl, val, color)
            sc.grid(row=0, column=i, padx=6, pady=4, sticky="ew")

        # ── Barras por plataforma ──
        for w in self.plat_frame.winfo_children():
            w.destroy()

        total_qty   = cantidad or 1
        accent_list = [COLORS["accent"], COLORS["accent2"],
                       COLORS["accent3"], COLORS["accent4"]]

        if res["por_plataforma"]:
            for i, p in enumerate(res["por_plataforma"]):
                color = accent_list[i % len(accent_list)]
                pct   = p["cantidad"] / total_qty
                row   = ctk.CTkFrame(self.plat_frame, fg_color="transparent")
                row.pack(fill="x", pady=4)
                row.grid_columnconfigure(1, weight=1)

                ctk.CTkLabel(row, text=p["nombre"][:20], width=160,
                             font=ctk.CTkFont(size=13), text_color=COLORS["text"],
                             anchor="w").grid(row=0, column=0, sticky="w")

                bar = ctk.CTkProgressBar(row, height=18, corner_radius=8,
                                         fg_color=COLORS["border"],
                                         progress_color=color)
                bar.set(pct)
                bar.grid(row=0, column=1, sticky="ew", padx=12)

                ganancia = p.get("ganancia") or 0
                info = (f"{p['cantidad']} ventas  •  "
                        f"${p.get('total', 0):,.0f}  •  "
                        f"🔒 ${ganancia:,.0f}")
                ctk.CTkLabel(row, text=info, width=300,
                             font=ctk.CTkFont(size=12), text_color=color,
                             anchor="e").grid(row=0, column=2, sticky="e")
        else:
            ctk.CTkLabel(self.plat_frame,
                         text="Sin ventas en este período",
                         text_color=COLORS["text_dim"],
                         font=ctk.CTkFont(size=13)).pack(pady=16)

        # ── Historial total ──
        self.all_tree.delete(*self.all_tree.get_children())
        res_all = self.db.get_resumen_ventas("todo")
        for p in res_all["por_plataforma"]:
            ganancia = p.get("ganancia") or 0
            self.all_tree.insert("", "end", values=(
                p["nombre"],
                p["cantidad"],
                f"${p.get('total', 0):,.0f}",
                f"${ganancia:,.0f}",
            ))

    def _fmt(self, fecha_str):
        """YYYY-MM-DD → DD/MM/YYYY"""
        try:
            return datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            return fecha_str
