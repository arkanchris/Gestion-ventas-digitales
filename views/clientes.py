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
        self.db  = db
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

        # ── Filtros ──
        fbar = card(self)
        fbar.pack(fill="x", padx=24, pady=(0, 4))
        inner = ctk.CTkFrame(fbar, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(inner, text="🔍", font=ctk.CTkFont(size=16),
                     text_color=COLORS["text_dim"]).pack(side="left", padx=(0, 4))
        self.search_var = tk.StringVar()
        entry_field(inner, placeholder="Buscar nombre, teléfono o correo...",
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

        # ══════════════════════════════════════════════════════
        #  BARRA DE ACCIONES — arriba de la tabla
        # ══════════════════════════════════════════════════════
        act_card = card(self)
        act_card.pack(fill="x", padx=24, pady=(0, 4))
        act = ctk.CTkFrame(act_card, fg_color="transparent")
        act.pack(fill="x", padx=14, pady=8)

        # Selección
        ctk.CTkLabel(act, text="Selecciona:",
                     font=ctk.CTkFont(size=11), text_color="#3d5470"
                     ).pack(side="left", padx=(0, 6))

        secondary_btn(act, "☑  Todas",
                      command=self._select_all,
                      height=32, width=90).pack(side="left", padx=(0, 4))

        secondary_btn(act, "☐  Ninguna",
                      command=self._deselect_all,
                      height=32, width=90).pack(side="left", padx=(0, 14))

        # Separador
        ctk.CTkFrame(act, width=1, height=28,
                     fg_color=COLORS["border"]).pack(side="left", padx=(0, 14))

        # Acciones individuales
        primary_btn(act, "✏️  Editar",
                    command=self._editar,
                    height=34, width=110).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            act, text="🧾  Generar Tirilla",
            command=self._tirilla,
            height=34, corner_radius=8, width=140,
            fg_color="#0e6027", hover_color="#0b4d1f",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
        ).pack(side="left", padx=(0, 14))

        # Separador
        ctk.CTkFrame(act, width=1, height=28,
                     fg_color=COLORS["border"]).pack(side="left", padx=(0, 14))

        # Eliminar (individual o múltiple)
        self.btn_eliminar = danger_btn(
            act, "🗑  Eliminar seleccionados",
            command=self._eliminar_seleccionados,
            height=34)
        self.btn_eliminar.pack(side="left")

        # Label de seleccionados
        self.sel_label = ctk.CTkLabel(act, text="",
                                       font=ctk.CTkFont(size=11, weight="bold"),
                                       text_color=COLORS["accent2"])
        self.sel_label.pack(side="right", padx=8)

        # ══════════════════════════════════════════════════════
        #  TABLA con columna de checkbox
        # ══════════════════════════════════════════════════════
        cols = ("sel", "factura", "cliente", "perfil", "telefono",
                "plataforma", "vence", "dias", "estado", "precio")
        anchors = {c: "center" for c in cols}
        anchors["cliente"] = "w"
        anchors["perfil"]  = "center"

        table_frame, self.tree = build_treeview(
            self, cols, heights=17, col_anchors=anchors)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        col_cfg = {
            "sel":        ("☐",          34),
            "factura":    ("#",           55),
            "cliente":    ("Cliente",    145),
            "perfil":     ("Perfil",      85),
            "telefono":   ("Teléfono",   108),
            "plataforma": ("Plataforma", 125),
            "vence":      ("Vence",       95),
            "dias":       ("Días",        62),
            "estado":     ("Estado",     105),
            "precio":     ("Precio",      85),
        }
        for c, (h, w) in col_cfg.items():
            self.tree.heading(c, text=h, anchor="center")
            self.tree.column(c, width=w, minwidth=30)

        # Click en la fila alterna el checkbox
        self.tree.bind("<ButtonRelease-1>", self._on_click)
        self.tree.bind("<Double-1>",        self._on_double_click)

        # Diccionario de IDs seleccionados: {iid: True/False}
        self._checked = {}

    # ═══════════════════════════════════════════════════════════
    #  CARGA DE DATOS
    # ═══════════════════════════════════════════════════════════
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

        # Preservar selección previa
        prev = set(iid for iid, v in self._checked.items() if v)

        self._checked.clear()
        self.tree.delete(*self.tree.get_children())

        for v in ventas:
            iid  = str(v["id"])
            days = days_remaining(v.get("fecha_vencimiento", ""))
            badge, _ = days_badge(days)
            estado_txt = "✅ Pagada" if v["estado_pago"] == "pagada" else "⏳ Pendiente"

            # Restaurar selección si estaba marcada
            checked = iid in prev
            self._checked[iid] = checked
            chk_icon = "☑" if checked else "☐"

            self.tree.insert("", "end", iid=iid, values=(
                chk_icon,
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

            # Color de fila si está seleccionada
            if checked:
                self.tree.item(iid, tags=("checked",))
            else:
                self.tree.item(iid, tags=())

        # Colores para filas seleccionadas
        self.tree.tag_configure("checked", background="#1e3a5f", foreground="#f0f6ff")
        self._update_sel_label()

    # ═══════════════════════════════════════════════════════════
    #  MANEJO DE CLICS — toggle checkbox
    # ═══════════════════════════════════════════════════════════
    def _on_click(self, event):
        """Clic en cualquier celda → toggle el checkbox de esa fila."""
        row = self.tree.identify_row(event.y)
        if not row:
            return
        # Toggle
        current = self._checked.get(row, False)
        self._checked[row] = not current

        # Actualizar icono en columna sel
        vals = list(self.tree.item(row, "values"))
        vals[0] = "☑" if self._checked[row] else "☐"
        self.tree.item(row, values=vals)

        # Color de fila
        if self._checked[row]:
            self.tree.item(row, tags=("checked",))
        else:
            self.tree.item(row, tags=())

        self._update_sel_label()

    def _on_double_click(self, event):
        """Doble clic → editar directamente."""
        row = self.tree.identify_row(event.y)
        if row:
            self._editar_id(int(row))

    def _update_sel_label(self):
        n = sum(1 for v in self._checked.values() if v)
        if n == 0:
            self.sel_label.configure(text="")
            self.btn_eliminar.configure(text="🗑  Eliminar seleccionados")
        elif n == 1:
            self.sel_label.configure(text="1 seleccionado")
            self.btn_eliminar.configure(text="🗑  Eliminar 1")
        else:
            self.sel_label.configure(text=f"{n} seleccionados")
            self.btn_eliminar.configure(text=f"🗑  Eliminar {n}")

    # ═══════════════════════════════════════════════════════════
    #  SELECCIONAR TODO / NINGUNO
    # ═══════════════════════════════════════════════════════════
    def _select_all(self):
        for iid in self.tree.get_children():
            self._checked[iid] = True
            vals = list(self.tree.item(iid, "values"))
            vals[0] = "☑"
            self.tree.item(iid, values=vals, tags=("checked",))
        self._update_sel_label()

    def _deselect_all(self):
        for iid in self.tree.get_children():
            self._checked[iid] = False
            vals = list(self.tree.item(iid, "values"))
            vals[0] = "☐"
            self.tree.item(iid, values=vals, tags=())
        self._update_sel_label()

    # ═══════════════════════════════════════════════════════════
    #  ACCIONES
    # ═══════════════════════════════════════════════════════════
    def _get_selected_ids(self):
        return [int(iid) for iid, v in self._checked.items() if v]

    def _editar(self):
        ids = self._get_selected_ids()
        if not ids:
            messagebox.showwarning("Sin selección",
                                   "Haz clic en una fila para seleccionarla.")
            return
        if len(ids) > 1:
            messagebox.showinfo("Editar",
                                "Para editar, selecciona solo una venta a la vez.")
            return
        self._editar_id(ids[0])

    def _editar_id(self, vid):
        venta = self.db.get_venta_by_id(vid)
        if not venta:
            return
        self.app.show_view("ventas")
        for w in self.app.content_frame.winfo_children():
            if hasattr(w, "cargar_venta"):
                w.cargar_venta(venta)
                break

    def _eliminar_seleccionados(self):
        ids = self._get_selected_ids()
        if not ids:
            messagebox.showwarning("Sin selección",
                                   "Haz clic en una o varias filas para seleccionarlas,\n"
                                   "luego presiona Eliminar.")
            return

        n = len(ids)
        if n == 1:
            # Obtener nombre del cliente para el mensaje
            venta = self.db.get_venta_by_id(ids[0])
            nombre = venta["cliente"] if venta else "esta venta"
            confirmar = messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Eliminar la venta de '{nombre}'?\n\n"
                "Esta acción no se puede deshacer.")
        else:
            # Listar los clientes seleccionados
            nombres = []
            for vid in ids[:8]:
                v = self.db.get_venta_by_id(vid)
                if v:
                    nombres.append(f"  • #{v.get('numero_factura','?')} — {v['cliente']}")
            lista = "\n".join(nombres)
            if n > 8:
                lista += f"\n  ... y {n - 8} más"

            confirmar = messagebox.askyesno(
                "⚠️  Confirmar eliminación múltiple",
                f"¿Eliminar {n} ventas?\n\n"
                f"{lista}\n\n"
                "Esta acción NO se puede deshacer.")

        if not confirmar:
            return

        eliminadas = 0
        for vid in ids:
            self.db.delete_venta(vid)
            eliminadas += 1

        messagebox.showinfo("✅ Eliminadas",
                            f"Se eliminaron {eliminadas} venta(s) correctamente.")
        self._checked.clear()
        self._load()

    def _tirilla(self):
        ids = self._get_selected_ids()
        if not ids:
            messagebox.showwarning("Sin selección",
                                   "Haz clic en una fila para seleccionarla.")
            return
        if len(ids) > 1:
            messagebox.showinfo("Tirilla",
                                "Para generar la tirilla, selecciona solo una venta.")
            return
        venta  = self.db.get_venta_by_id(ids[0])
        if not venta:
            return
        config = self.db.get_config()
        generar_tirilla(venta, config)