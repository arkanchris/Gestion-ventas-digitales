import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from widgets import (COLORS, card, title_label, primary_btn, secondary_btn,
                     entry_field, section_header, DateEntryWidget)
from tirilla import generar_tirilla, generar_tirilla_multiple


class VentasView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db             = db
        self.app            = app
        self.editing_id     = None          # ID venta en edición (modo simple)
        self.modo_multiple  = tk.BooleanVar(value=False)
        self.items_multiple = []            # Lista de plataformas en pedido múltiple
        self.editing_item   = None          # Índice del item que se está editando
        self._build()

    # ═══════════════════════════════════════════════════════════
    #  CONSTRUCCIÓN PRINCIPAL
    # ═══════════════════════════════════════════════════════════
    def _build(self):
        self.scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_dark"], corner_radius=0,
            scrollbar_button_color=COLORS["border"])
        self.scroll.pack(fill="both", expand=True)
        self._build_form()

    def _build_form(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        s = self.scroll

        # ── Header ──
        hdr = ctk.CTkFrame(s, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        title_label(hdr, "💰  Nueva Venta", size=22).pack(side="left")
        self.mode_label = ctk.CTkLabel(hdr, text="",
                                        font=ctk.CTkFont(size=12),
                                        text_color=COLORS["accent4"])
        self.mode_label.pack(side="left", padx=14)

        # ── Selector de modo ──
        modo_card = ctk.CTkFrame(s, fg_color="#0e2040", corner_radius=12,
                                  border_width=1, border_color="#1d6fd8")
        modo_card.pack(fill="x", padx=24, pady=(0, 8))
        mi = ctk.CTkFrame(modo_card, fg_color="transparent")
        mi.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(mi, text="Tipo de venta:",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["accent2"]).pack(side="left", padx=(0, 14))
        multi = self.modo_multiple.get()
        ctk.CTkButton(mi, text="📄  Venta Simple",
                      command=lambda: self._set_modo(False),
                      height=34, corner_radius=8, width=180,
                      fg_color=COLORS["accent"] if not multi else COLORS["border"],
                      hover_color="#1558b0",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      text_color="white").pack(side="left", padx=(0, 8))
        ctk.CTkButton(mi, text="📦  Venta Múltiple",
                      command=lambda: self._set_modo(True),
                      height=34, corner_radius=8, width=200,
                      fg_color=COLORS["accent"] if multi else COLORS["border"],
                      hover_color="#1558b0",
                      font=ctk.CTkFont(size=12, weight="bold"),
                      text_color="white").pack(side="left")

        # ── Datos del cliente ──
        section_header(s, "📋  Datos del Cliente")
        cf = card(s); cf.pack(fill="x", padx=24, pady=4)

        r1 = _row(cf); _lbl(r1, "Cliente *", 0)
        self.e_cliente = entry_field(r1, placeholder="Nombre del cliente")
        self.e_cliente.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r1, "Teléfono", 2)
        self.e_telefono = entry_field(r1, placeholder="Número de teléfono")
        self.e_telefono.grid(row=0, column=3, sticky="ew", padx=(8, 0))

        r2 = _row(cf); _lbl(r2, "Orden Compra", 0)
        self.e_orden = entry_field(r2, placeholder="# de orden o compra")
        self.e_orden.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r2, "Distribuidor", 2)
        proveedores      = self.db.get_proveedores(solo_activos=True)
        prov_names       = ["— Sin distribuidor —"] + [p["nombre"] for p in proveedores]
        self.prov_map    = {p["nombre"]: p["id"] for p in proveedores}
        self.e_proveedor = _combo(r2, prov_names)
        self.e_proveedor.grid(row=0, column=3, sticky="ew", padx=(8, 0))

        # ── Área según modo ──
        if self.modo_multiple.get():
            self._build_multiple_area(s)
        else:
            self._build_single_area(s)

    # ═══════════════════════════════════════════════════════════
    #  MODO SIMPLE
    # ═══════════════════════════════════════════════════════════
    def _build_single_area(self, s):
        section_header(s, "📺  Plataforma")
        pf = card(s); pf.pack(fill="x", padx=24, pady=4)
        r3 = _row(pf); _lbl(r3, "Plataforma *", 0)
        plataformas      = self.db.get_plataformas(solo_activas=True)
        self.plat_map    = {p["nombre"]: p["id"] for p in plataformas}
        self.plat_precio = {p["nombre"]: p["precio_venta"] for p in plataformas}
        self.e_plataforma = _combo(r3, [p["nombre"] for p in plataformas] or ["—"])
        self.e_plataforma.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        # Auto-fill price when platform changes
        self.e_plataforma.configure(command=self._on_plataforma_change)

        section_header(s, "🔐  Datos de Acceso")
        af = card(s); af.pack(fill="x", padx=24, pady=4)
        r4 = ctk.CTkFrame(af, fg_color="transparent"); r4.pack(fill="x", padx=16, pady=8)
        for c in (1, 3, 5): r4.grid_columnconfigure(c, weight=1)
        _lbl(r4, "Correo/Usuario", 0)
        self.e_correo = entry_field(r4, placeholder="correo@ejemplo.com")
        self.e_correo.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r4, "Contraseña", 2)
        self.e_password = entry_field(r4, placeholder="Contraseña")
        self.e_password.grid(row=0, column=3, sticky="ew", padx=(8, 20))
        _lbl(r4, "PIN", 4)
        self.e_pin = entry_field(r4, placeholder="PIN")
        self.e_pin.grid(row=0, column=5, sticky="ew", padx=(8, 0))
        r4b = _row(af, cols=2); _lbl(r4b, "Perfil", 0)
        self.e_perfil = entry_field(r4b, placeholder="Ej: Perfil 1")
        self.e_perfil.grid(row=0, column=1, sticky="ew", padx=(8, 0))

        section_header(s, "💲  Precio y Fechas")
        ff = card(s); ff.pack(fill="x", padx=24, pady=4)
        r5 = ctk.CTkFrame(ff, fg_color="transparent"); r5.pack(fill="x", padx=16, pady=8)
        for c in (1, 3, 5): r5.grid_columnconfigure(c, weight=1)
        _lbl(r5, "Precio Venta *", 0)
        self.e_precio = entry_field(r5, placeholder="0.00")
        self.e_precio.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r5, "F. Activación", 2)
        self.e_fecha_act = DateEntryWidget(r5)
        self.e_fecha_act.grid(row=0, column=3, sticky="ew", padx=(8, 20))
        _lbl(r5, "F. Vencimiento", 4)
        self.e_fecha_venc = DateEntryWidget(r5)
        self.e_fecha_venc.grid(row=0, column=5, sticky="ew", padx=(8, 0))

        # ── Fecha de activación = HOY por defecto ──
        from datetime import date
        self.e_fecha_act.set(date.today().strftime("%Y-%m-%d"))

        # ── Si hay plataforma preseleccionada, cargar precio ──
        if plataformas and not self.editing_id:
            first = plataformas[0]["nombre"]
            precio_def = self.plat_precio.get(first, 0)
            if precio_def:
                self.e_precio.delete(0, "end")
                self.e_precio.insert(0, str(int(precio_def)))

        r6 = ctk.CTkFrame(ff, fg_color="transparent"); r6.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkLabel(r6, text="🔒 Estado de Pago (interno)",
                     font=ctk.CTkFont(size=13), text_color=COLORS["text_dim"]).pack(side="left")
        self.estado_pago = ctk.CTkSegmentedButton(
            r6, values=["pagada", "pendiente"],
            selected_color=COLORS["accent"], selected_hover_color="#1558b0",
            unselected_color=COLORS["border"],
            font=ctk.CTkFont(size=13), text_color=COLORS["text"])
        self.estado_pago.set("pagada"); self.estado_pago.pack(side="left", padx=14)

        section_header(s, "📝  Notas")
        nf = card(s); nf.pack(fill="x", padx=24, pady=4)
        self.e_notas = ctk.CTkTextbox(nf, height=70, fg_color="#0d1828",
                                       border_color=COLORS["border"], border_width=1,
                                       font=ctk.CTkFont(size=13), text_color="#ffffff",
                                       corner_radius=8)
        self.e_notas.pack(fill="x", padx=16, pady=10)

        bf = ctk.CTkFrame(s, fg_color="transparent"); bf.pack(fill="x", padx=24, pady=14)
        primary_btn(bf, "💾  Guardar Venta", command=self._guardar_simple).pack(side="left", padx=(0, 8))
        secondary_btn(bf, "✕  Cancelar", command=self._limpiar).pack(side="left")

    def _on_plataforma_change(self, nombre):
        """Auto-fill price when platform is selected (simple mode)."""
        if hasattr(self, 'plat_precio') and hasattr(self, 'e_precio'):
            precio = self.plat_precio.get(nombre, 0)
            if precio:
                self.e_precio.delete(0, "end")
                self.e_precio.insert(0, str(int(precio)))

    def _on_m_plataforma_change(self, nombre):
        """Auto-fill price when platform is selected (multiple mode)."""
        if hasattr(self, 'plat_precio_m') and hasattr(self, 'm_precio'):
            precio = self.plat_precio_m.get(nombre, 0)
            if precio:
                self.m_precio.delete(0, "end")
                self.m_precio.insert(0, str(int(precio)))

    # ═══════════════════════════════════════════════════════════
    #  MODO MÚLTIPLE
    # ═══════════════════════════════════════════════════════════
    def _build_multiple_area(self, s):
        # Título dinámico según si estamos editando un item
        if self.editing_item is not None:
            sec_title = f"✏️  Editando Plataforma #{self.editing_item + 1} del Pedido"
        else:
            sec_title = "📺  Agregar Plataforma al Pedido"
        section_header(s, sec_title)

        pf = card(s); pf.pack(fill="x", padx=24, pady=4)

        r3 = _row(pf); _lbl(r3, "Plataforma *", 0)
        plataformas   = self.db.get_plataformas(solo_activas=True)
        self.plat_map = {p["nombre"]: p["id"] for p in plataformas}
        self.plat_precio_m = {p["nombre"]: p["precio_venta"] for p in plataformas}
        self.m_plataforma = _combo(r3, [p["nombre"] for p in plataformas] or ["—"])
        self.m_plataforma.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        # Auto-fill price on platform change
        self.m_plataforma.configure(command=self._on_m_plataforma_change)
        _lbl(r3, "Perfil", 2)
        self.m_perfil = entry_field(r3, placeholder="Ej: Perfil 2")
        self.m_perfil.grid(row=0, column=3, sticky="ew", padx=(8, 0))

        r4 = ctk.CTkFrame(pf, fg_color="transparent"); r4.pack(fill="x", padx=16, pady=8)
        for c in (1, 3, 5): r4.grid_columnconfigure(c, weight=1)
        _lbl(r4, "Correo/Usuario", 0)
        self.m_correo = entry_field(r4, placeholder="correo@ejemplo.com")
        self.m_correo.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r4, "Contraseña", 2)
        self.m_password = entry_field(r4, placeholder="Contraseña")
        self.m_password.grid(row=0, column=3, sticky="ew", padx=(8, 20))
        _lbl(r4, "PIN", 4)
        self.m_pin = entry_field(r4, placeholder="PIN")
        self.m_pin.grid(row=0, column=5, sticky="ew", padx=(8, 0))

        r5 = ctk.CTkFrame(pf, fg_color="transparent"); r5.pack(fill="x", padx=16, pady=8)
        for c in (1, 3, 5): r5.grid_columnconfigure(c, weight=1)
        _lbl(r5, "Precio *", 0)
        self.m_precio = entry_field(r5, placeholder="0.00")
        self.m_precio.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r5, "F. Activación", 2)
        self.m_fecha_act = DateEntryWidget(r5)
        self.m_fecha_act.grid(row=0, column=3, sticky="ew", padx=(8, 20))
        _lbl(r5, "F. Vencimiento", 4)
        self.m_fecha_venc = DateEntryWidget(r5)
        self.m_fecha_venc.grid(row=0, column=5, sticky="ew", padx=(8, 0))

        r5b = ctk.CTkFrame(pf, fg_color="transparent"); r5b.pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkLabel(r5b, text="🔒 Estado:", font=ctk.CTkFont(size=13),
                     text_color=COLORS["text_dim"]).pack(side="left")
        self.m_estado = ctk.CTkSegmentedButton(
            r5b, values=["pagada", "pendiente"],
            selected_color=COLORS["accent"], selected_hover_color="#1558b0",
            unselected_color=COLORS["border"],
            font=ctk.CTkFont(size=13), text_color=COLORS["text"])
        self.m_estado.set("pagada"); self.m_estado.pack(side="left", padx=10)
        ctk.CTkLabel(r5b, text="Notas:", font=ctk.CTkFont(size=13),
                     text_color=COLORS["text_dim"]).pack(side="left", padx=(20, 6))
        self.m_notas = entry_field(r5b, placeholder="Opcional")
        self.m_notas.pack(side="left", fill="x", expand=True)

        # ── Fecha activación = HOY por defecto (si no hay item en edición) ──
        if self.editing_item is None:
            from datetime import date
            self.m_fecha_act.set(date.today().strftime("%Y-%m-%d"))
            # Precio por defecto de la primera plataforma
            if plataformas:
                first = plataformas[0]["nombre"]
                precio_def = self.plat_precio_m.get(first, 0)
                if precio_def:
                    self.m_precio.delete(0, "end")
                    self.m_precio.insert(0, str(int(precio_def)))

        # Si hay item en edición, pre-cargar sus datos
        if self.editing_item is not None:
            item = self.items_multiple[self.editing_item]
            self.m_plataforma.set(item.get("plat_nombre", ""))
            _set_entry(self.m_perfil,    item.get("perfil", ""))
            _set_entry(self.m_correo,    item.get("correo_usuario", ""))
            _set_entry(self.m_password,  item.get("contrasena", ""))
            _set_entry(self.m_pin,       item.get("pin", ""))
            _set_entry(self.m_precio,    str(item.get("precio_venta", "")))
            self.m_fecha_act.set(item.get("fecha_activacion", ""))
            self.m_fecha_venc.set(item.get("fecha_vencimiento", ""))
            self.m_estado.set(item.get("estado_pago", "pagada"))
            _set_entry(self.m_notas,     item.get("notas", ""))

        # Botón agregar / guardar edición
        add_frame = ctk.CTkFrame(pf, fg_color="transparent")
        add_frame.pack(fill="x", padx=16, pady=(0, 12))

        if self.editing_item is not None:
            ctk.CTkButton(
                add_frame,
                text="💾  Guardar cambios en esta plataforma",
                command=self._guardar_edicion_item,
                height=38, corner_radius=8,
                fg_color="#0e6027", hover_color="#0b4d1f",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="white"
            ).pack(side="left", padx=(0, 8))
            secondary_btn(add_frame, "✕  Cancelar edición",
                          command=self._cancelar_edicion_item,
                          height=38).pack(side="left")
        else:
            ctk.CTkButton(
                add_frame,
                text="➕  Agregar esta plataforma al pedido",
                command=self._agregar_item,
                height=38, corner_radius=8,
                fg_color="#065f46", hover_color="#044a35",
                font=ctk.CTkFont(size=13, weight="bold"), text_color="white"
            ).pack(side="left")
            ctk.CTkLabel(add_frame,
                         text="← Rellena y haz clic para agregar. Repite por cada plataforma.",
                         font=ctk.CTkFont(size=11), text_color="#3d5470"
                         ).pack(side="left", padx=12)

        # ── Lista de plataformas ──
        section_header(s, "🛒  Plataformas en este Pedido")
        self.items_frame = card(s)
        self.items_frame.pack(fill="x", padx=24, pady=4)
        self._refresh_items_list()

        # Notas generales
        section_header(s, "📝  Notas Generales del Pedido")
        nf = card(s); nf.pack(fill="x", padx=24, pady=4)
        self.e_notas_gral = ctk.CTkTextbox(
            nf, height=60, fg_color="#0d1828",
            border_color=COLORS["border"], border_width=1,
            font=ctk.CTkFont(size=13), text_color="#ffffff", corner_radius=8)
        self.e_notas_gral.pack(fill="x", padx=16, pady=10)

        # Botones finales
        bf = ctk.CTkFrame(s, fg_color="transparent"); bf.pack(fill="x", padx=24, pady=14)
        ctk.CTkButton(
            bf, text="💾  GUARDAR PEDIDO COMPLETO Y GENERAR TIRILLA",
            command=self._guardar_multiple,
            height=44, corner_radius=10,
            fg_color="#1d4ed8", hover_color="#1558b0",
            font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
        ).pack(side="left", padx=(0, 10))
        secondary_btn(bf, "✕  Cancelar todo", command=self._limpiar).pack(side="left")

    # ═══════════════════════════════════════════════════════════
    #  LISTA DE ITEMS — bien centrada y alineada
    # ═══════════════════════════════════════════════════════════
    def _refresh_items_list(self):
        for w in self.items_frame.winfo_children():
            w.destroy()

        if not self.items_multiple:
            ctk.CTkLabel(self.items_frame,
                         text="Aún no agregaste ninguna plataforma. "
                              "Rellena el formulario arriba y haz clic en '➕ Agregar'.",
                         font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"]
                         ).pack(padx=16, pady=16)
            return

        # ── Encabezado de tabla ──────────────────────────────
        COL_W = [30, 140, 170, 110, 60, 80, 85, 95, 60, 60]
        HEADERS = ["#", "Plataforma", "Correo", "Contraseña", "PIN",
                   "Perfil", "Precio", "Vence", "✏️", "🗑"]

        hdr = ctk.CTkFrame(self.items_frame, fg_color=COLORS["bg_sidebar"], corner_radius=8)
        hdr.pack(fill="x", padx=10, pady=(8, 2))
        for col, (txt, w) in enumerate(zip(HEADERS, COL_W)):
            ctk.CTkLabel(hdr, text=txt, width=w, anchor="center",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=COLORS["text_dim"]).grid(
                             row=0, column=col, padx=3, pady=6, sticky="ew")
            hdr.grid_columnconfigure(col, minsize=w)

        # ── Filas ────────────────────────────────────────────
        total = 0
        for i, item in enumerate(self.items_multiple):
            bg  = "#0d1828" if i % 2 == 0 else "#111c30"
            row = ctk.CTkFrame(self.items_frame, fg_color=bg, corner_radius=6)
            row.pack(fill="x", padx=10, pady=1)
            total += item.get("precio_venta", 0)

            # Resaltar si está siendo editado
            if self.editing_item == i:
                row.configure(fg_color="#0e2040",
                              border_color=COLORS["accent"], border_width=1)

            vals = [
                str(i + 1),
                item.get("plat_nombre", "")[:16],
                item.get("correo_usuario", "")[:20],
                item.get("contrasena", "")[:14],
                item.get("pin", "")[:8],
                item.get("perfil", "")[:8],
                f"${item.get('precio_venta', 0):,.0f}",
                item.get("fecha_vencimiento", "—"),
            ]
            for col, (txt, w) in enumerate(zip(vals, COL_W)):
                ctk.CTkLabel(row, text=txt, width=w, anchor="center",
                             font=ctk.CTkFont(size=12), text_color=COLORS["text"]
                             ).grid(row=0, column=col, padx=3, pady=7, sticky="ew")
                row.grid_columnconfigure(col, minsize=w)

            # Botón editar
            idx = i
            ctk.CTkButton(
                row, text="✏️", width=COL_W[8], height=28,
                corner_radius=6,
                fg_color=COLORS["accent"], hover_color="#1558b0",
                font=ctk.CTkFont(size=11),
                command=lambda ix=idx: self._editar_item(ix)
            ).grid(row=0, column=8, padx=3, pady=4)

            # Botón eliminar
            ctk.CTkButton(
                row, text="✕", width=COL_W[9], height=28,
                corner_radius=6,
                fg_color=COLORS["red"], hover_color="#cc2233",
                font=ctk.CTkFont(size=11),
                command=lambda ix=idx: self._quitar_item(ix)
            ).grid(row=0, column=9, padx=(3, 6), pady=4)

        # ── Fila de total ─────────────────────────────────────
        tf = ctk.CTkFrame(self.items_frame, fg_color="#0e2040", corner_radius=8)
        tf.pack(fill="x", padx=10, pady=(4, 10))
        ctk.CTkLabel(tf, text=f"  {len(self.items_multiple)} plataforma(s) en el pedido",
                     font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"]
                     ).pack(side="left", padx=12, pady=8)
        ctk.CTkLabel(tf, text=f"TOTAL:  ${total:,.0f}",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent3"]
                     ).pack(side="right", padx=16, pady=8)

    # ═══════════════════════════════════════════════════════════
    #  LÓGICA DE ITEMS
    # ═══════════════════════════════════════════════════════════
    def _agregar_item(self):
        cliente = self.e_cliente.get().strip()
        if not cliente:
            messagebox.showerror("Error", "Primero escribe el nombre del cliente.")
            return
        plat_nombre = self.m_plataforma.get()
        plat_id     = self.plat_map.get(plat_nombre)
        if not plat_id:
            messagebox.showerror("Error", "Selecciona una plataforma válida.")
            return
        try:
            precio = float(self.m_precio.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número.")
            return
        if precio <= 0:
            messagebox.showerror("Error", "El precio debe ser mayor a 0.")
            return

        self.items_multiple.append({
            "plataforma_id":     plat_id,
            "plat_nombre":       plat_nombre,
            "correo_usuario":    self.m_correo.get().strip(),
            "contrasena":        self.m_password.get().strip(),
            "pin":               self.m_pin.get().strip(),
            "perfil":            self.m_perfil.get().strip(),
            "precio_venta":      precio,
            "fecha_activacion":  self.m_fecha_act.get(),
            "fecha_vencimiento": self.m_fecha_venc.get(),
            "estado_pago":       self.m_estado.get(),
            "notas":             self.m_notas.get().strip(),
        })

        # Limpiar campos para el siguiente
        for e in [self.m_correo, self.m_password, self.m_pin,
                  self.m_perfil, self.m_precio, self.m_notas]:
            e.delete(0, "end")
        self.m_fecha_act.set(""); self.m_fecha_venc.set("")
        self.m_estado.set("pagada")
        self._refresh_items_list()

    def _editar_item(self, idx):
        """Carga el item en el formulario para editarlo."""
        self.editing_item = idx
        self._build_form()          # rebuild recarga el form con editing_item != None

    def _guardar_edicion_item(self):
        """Aplica los cambios al item que se estaba editando."""
        plat_nombre = self.m_plataforma.get()
        plat_id     = self.plat_map.get(plat_nombre)
        if not plat_id:
            messagebox.showerror("Error", "Selecciona una plataforma válida.")
            return
        try:
            precio = float(self.m_precio.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número.")
            return

        self.items_multiple[self.editing_item] = {
            "plataforma_id":     plat_id,
            "plat_nombre":       plat_nombre,
            "correo_usuario":    self.m_correo.get().strip(),
            "contrasena":        self.m_password.get().strip(),
            "pin":               self.m_pin.get().strip(),
            "perfil":            self.m_perfil.get().strip(),
            "precio_venta":      precio,
            "fecha_activacion":  self.m_fecha_act.get(),
            "fecha_vencimiento": self.m_fecha_venc.get(),
            "estado_pago":       self.m_estado.get(),
            "notas":             self.m_notas.get().strip(),
        }
        self.editing_item = None
        self._build_form()

    def _cancelar_edicion_item(self):
        self.editing_item = None
        self._build_form()

    def _quitar_item(self, idx):
        if self.editing_item == idx:
            self.editing_item = None
        if 0 <= idx < len(self.items_multiple):
            del self.items_multiple[idx]
        self._refresh_items_list()

    # ═══════════════════════════════════════════════════════════
    #  GUARDAR VENTAS
    # ═══════════════════════════════════════════════════════════
    def _guardar_simple(self):
        data = self._get_single_data()
        if not data: return
        if self.editing_id:
            self.db.update_venta(self.editing_id, data)
            messagebox.showinfo("✅", "Venta actualizada correctamente.")
            self._limpiar(); self.app.show_view("clientes")
        else:
            vid, factura = self.db.add_venta(data)
            resp = messagebox.askyesno("✅ Venta guardada",
                f"Venta #{factura} registrada.\n\n¿Generar la tirilla digital?")
            if resp:
                venta  = self.db.get_venta_by_id(vid)
                config = self.db.get_config()
                generar_tirilla(venta, config)
            self._limpiar()

    def _guardar_multiple(self):
        cliente  = self.e_cliente.get().strip()
        telefono = self.e_telefono.get().strip()
        orden    = self.e_orden.get().strip()
        prov_n   = self.e_proveedor.get()
        prov_id  = self.prov_map.get(prov_n)          # None si "— Sin distribuidor —"
        notas_g  = self.e_notas_gral.get("1.0", "end").strip()

        if not cliente:
            messagebox.showerror("Error", "El nombre del cliente es obligatorio."); return
        if not self.items_multiple:
            messagebox.showerror("Error",
                "No has agregado ninguna plataforma.\n"
                "Rellena el formulario y haz clic en '➕ Agregar'."); return

        vids = []
        config = self.db.get_config()
        for item in self.items_multiple:
            data = {
                "cliente":           cliente,
                "perfil":            item.get("perfil", ""),
                "telefono":          telefono,
                "plataforma_id":     item["plataforma_id"],
                "orden_compra":      orden,
                "correo_usuario":    item.get("correo_usuario", ""),
                "proveedor_id":      prov_id,
                "contrasena":        item.get("contrasena", ""),
                "pin":               item.get("pin", ""),
                "precio_venta":      item.get("precio_venta", 0),
                "fecha_activacion":  item.get("fecha_activacion", ""),
                "fecha_vencimiento": item.get("fecha_vencimiento", ""),
                "notas":             item.get("notas", "") or notas_g,
                "estado_pago":       item.get("estado_pago", "pagada"),
            }
            vid, _ = self.db.add_venta(data)
            vids.append(vid)

        total = sum(i.get("precio_venta", 0) for i in self.items_multiple)
        resp  = messagebox.askyesno(
            "✅ Pedido guardado",
            f"Se registraron {len(vids)} plataformas.\nTotal: ${total:,.0f}\n\n"
            "¿Generar la tirilla múltiple para el cliente?")

        if resp:
            ventas_g = [self.db.get_venta_by_id(v) for v in vids]
            # prov_id = None → sin distribuidor → muestra precios
            # prov_id = algo → con distribuidor → oculta precios
            generar_tirilla_multiple(
                ventas=ventas_g,
                cliente=cliente,
                telefono=telefono,
                config=config,
                notas_generales=notas_g,
                tiene_distribuidor=prov_id is not None,
                orden_compra=orden,
            )
        self._limpiar()

    # ═══════════════════════════════════════════════════════════
    #  HELPERS
    # ═══════════════════════════════════════════════════════════
    def _set_modo(self, multiple):
        self.modo_multiple.set(multiple)
        if not multiple:
            self.items_multiple.clear()
            self.editing_item = None
        self._build_form()

    def _get_single_data(self):
        plat_n  = self.e_plataforma.get()
        plat_id = self.plat_map.get(plat_n)
        if not self.e_cliente.get().strip():
            messagebox.showerror("Error", "El nombre del cliente es obligatorio."); return None
        if not plat_id:
            messagebox.showerror("Error", "Selecciona una plataforma válida."); return None
        try:
            precio = float(self.e_precio.get() or 0)
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número."); return None
        prov_n  = self.e_proveedor.get()
        prov_id = self.prov_map.get(prov_n)
        return {
            "cliente":           self.e_cliente.get().strip(),
            "perfil":            self.e_perfil.get().strip(),
            "telefono":          self.e_telefono.get().strip(),
            "plataforma_id":     plat_id,
            "orden_compra":      self.e_orden.get().strip(),
            "correo_usuario":    self.e_correo.get().strip(),
            "proveedor_id":      prov_id,
            "contrasena":        self.e_password.get().strip(),
            "pin":               self.e_pin.get().strip(),
            "precio_venta":      precio,
            "fecha_activacion":  self.e_fecha_act.get(),
            "fecha_vencimiento": self.e_fecha_venc.get(),
            "notas":             self.e_notas.get("1.0", "end").strip(),
            "estado_pago":       self.estado_pago.get(),
        }

    def _limpiar(self):
        self.editing_id   = None
        self.editing_item = None
        self.items_multiple.clear()
        self.modo_multiple.set(False)
        self._build_form()

    def cargar_venta(self, venta):
        self.modo_multiple.set(False)
        self.editing_id = venta["id"]
        self._build_form()
        self.mode_label.configure(
            text=f"✏️  Editando #{venta.get('numero_factura','?')} — {venta.get('cliente','')}",
            text_color=COLORS["accent4"])

        def _s(e, v): e.delete(0, "end"); e.insert(0, str(v or ""))
        _s(self.e_cliente,  venta.get("cliente", ""))
        _s(self.e_telefono, venta.get("telefono", ""))
        _s(self.e_orden,    venta.get("orden_compra", ""))

        plats = self.db.get_plataformas(solo_activas=True)
        for p in plats:
            if p["id"] == venta.get("plataforma_id"):
                self.e_plataforma.set(p["nombre"]); break
        provs = self.db.get_proveedores(solo_activos=True)
        for p in provs:
            if p["id"] == venta.get("proveedor_id"):
                self.e_proveedor.set(p["nombre"]); break

        _s(self.e_correo,   venta.get("correo_usuario", ""))
        _s(self.e_password, venta.get("contrasena", ""))
        _s(self.e_pin,      venta.get("pin", ""))
        _s(self.e_perfil,   venta.get("perfil", ""))
        _s(self.e_precio,   venta.get("precio_venta", ""))
        self.e_fecha_act.set(venta.get("fecha_activacion", ""))
        self.e_fecha_venc.set(venta.get("fecha_vencimiento", ""))
        self.e_notas.delete("1.0", "end")
        self.e_notas.insert("1.0", venta.get("notas", ""))
        self.estado_pago.set(venta.get("estado_pago", "pagada"))


# ── UI helpers ────────────────────────────────────────────────
def _row(parent, cols=4):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.pack(fill="x", padx=16, pady=8)
    for c in range(1, cols * 2, 2):
        f.grid_columnconfigure(c, weight=1)
    return f

def _lbl(parent, text, col):
    ctk.CTkLabel(parent, text=text, anchor="w", width=115,
                 font=ctk.CTkFont(size=13),
                 text_color=COLORS["text_dim"]).grid(row=0, column=col, sticky="w")

def _combo(parent, values):
    return ctk.CTkComboBox(
        parent, values=values, height=38, corner_radius=8,
        fg_color="#0d1828", border_color=COLORS["border"],
        button_color=COLORS["accent"],
        font=ctk.CTkFont(size=13), text_color="#ffffff")

def _set_entry(entry, value):
    entry.delete(0, "end")
    entry.insert(0, str(value or ""))
