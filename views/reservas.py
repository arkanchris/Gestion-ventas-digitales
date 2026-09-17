import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from widgets import (COLORS, card, title_label, primary_btn, secondary_btn,
                     danger_btn, entry_field, DateEntryWidget, days_remaining)
from datetime import date


# ══════════════════════════════════════════════════════════════
#  VISTA PRINCIPAL
# ══════════════════════════════════════════════════════════════
class ReservasView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db           = db
        self.app          = app
        self.selected_cid = None
        self._editing_perfil_id = None
        self._cuenta_ref        = None
        self._build()
        self._load_cuentas()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        title_label(hdr, "📒  Libro de Cuentas", size=22).pack(side="left")
        primary_btn(hdr, "➕  Nueva Cuenta",
                    command=self._abrir_form_nueva).pack(side="right")

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.pack(fill="both", expand=True, padx=24, pady=(4, 16))
        self.main.grid_columnconfigure(0, weight=1, minsize=210)
        self.main.grid_columnconfigure(1, weight=3)
        self.main.grid_rowconfigure(0, weight=1)

        self._build_left()

        self.right_panel = ctk.CTkFrame(
            self.main, fg_color=COLORS["bg_card"], corner_radius=12)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self._show_empty_detail()

    # ─── Panel izquierdo ──────────────────────────────────────
    def _build_left(self):
        left = ctk.CTkFrame(self.main, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        sc = ctk.CTkFrame(left, fg_color=COLORS["bg_card"], corner_radius=12)
        sc.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        sf = ctk.CTkFrame(sc, fg_color="transparent")
        sf.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(sf, text="🔍", font=ctk.CTkFont(size=15),
                     text_color=COLORS["text_dim"]).pack(side="left", padx=(0, 6))
        self.search_var = tk.StringVar()
        entry_field(sf, placeholder="Buscar cuenta...",
                    textvariable=self.search_var, width=150
                    ).pack(side="left", padx=(0, 8))
        self.search_var.trace("w", lambda *a: self._load_cuentas())

        plataformas    = self.db.get_plataformas(solo_activas=True)
        self.fplat_map = {"Todas": None}
        self.fplat_map.update({p["nombre"]: p["id"] for p in plataformas})
        self.f_plat = ctk.CTkComboBox(
            sf, values=list(self.fplat_map.keys()),
            width=120, height=32, corner_radius=8,
            fg_color="#0a1620", border_color=COLORS["border"],
            button_color=COLORS["accent"],
            font=ctk.CTkFont(size=12), text_color=COLORS["text"],
            command=lambda e: self._load_cuentas())
        self.f_plat.set("Todas")
        self.f_plat.pack(side="left")

        self.cnt_lbl = ctk.CTkLabel(sf, text="",
                                     font=ctk.CTkFont(size=11),
                                     text_color=COLORS["text_dim"])
        self.cnt_lbl.pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(
            left, fg_color=COLORS["bg_card"], corner_radius=12,
            scrollbar_button_color=COLORS["border"])
        self.list_frame.grid(row=1, column=0, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)
        self._cuenta_cards = {}

    # ─── Lista de cuentas ─────────────────────────────────────
    def _load_cuentas(self, *_):
        q       = self.search_var.get().strip()
        plat_id = self.fplat_map.get(self.f_plat.get())
        cuentas = self.db.get_cuentas_maestras(busqueda=q, plataforma_id=plat_id)
        self.cnt_lbl.configure(text=f"{len(cuentas)} cuentas")

        for w in self.list_frame.winfo_children():
            w.destroy()
        self._cuenta_cards.clear()

        if not cuentas:
            ctk.CTkLabel(self.list_frame,
                         text="No hay cuentas registradas.\nHaz clic en '➕ Nueva Cuenta'.",
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["text_dim"],
                         justify="center").pack(pady=40)
            return

        for c in cuentas:
            self._make_list_card(c)

        if self.selected_cid:
            self._highlight_card(self.selected_cid)

    def _make_list_card(self, c):
        cid   = c["id"]
        total = c.get("total_perfiles", 0)
        usado = c.get("perfiles_usados", 0)
        dias  = days_remaining(c.get("fecha_caducidad",""))

        if dias is None:   ind_color = COLORS["border"]
        elif dias < 0:     ind_color = COLORS["red"]
        elif dias <= 10:   ind_color = COLORS["yellow"]
        else:              ind_color = COLORS["accent3"]

        frame = ctk.CTkFrame(self.list_frame, fg_color="#0a1620",
                              corner_radius=10, border_width=2,
                              border_color=COLORS["border"])
        frame.pack(fill="x", padx=8, pady=4)
        frame.grid_columnconfigure(1, weight=1)

        bar = ctk.CTkFrame(frame, fg_color=ind_color, corner_radius=6, width=5)
        bar.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(8,10), pady=8)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=1, sticky="ew", pady=(8,2))
        ctk.CTkLabel(top, text=c.get("plataforma_nombre","—"),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#ffffff").pack(side="left")

        if dias is not None:
            badge_txt   = "Vencida" if dias < 0 else f"{dias}d"
            ctk.CTkLabel(top, text=badge_txt,
                         font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=ind_color).pack(side="right", padx=8)

        bot = ctk.CTkFrame(frame, fg_color="transparent")
        bot.grid(row=1, column=1, sticky="ew", pady=(0,8))
        ctk.CTkLabel(bot, text=c.get("correo_usuario","—"),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).pack(side="left")
        ctk.CTkLabel(bot, text=f"👥 {usado}/{total}",
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).pack(side="right", padx=8)

        for w in [frame, bar, top, bot] + list(top.winfo_children()) + list(bot.winfo_children()):
            try: w.bind("<Button-1>", lambda e, cid=cid: self._select_cuenta(cid))
            except: pass

        self._cuenta_cards[cid] = frame

    def _select_cuenta(self, cid):
        self.selected_cid = cid
        self._highlight_card(cid)
        cuenta = self.db.get_cuenta_maestra_by_id(cid)
        if cuenta:
            self._show_detail(cuenta)

    def _highlight_card(self, cid):
        for c_id, frame in self._cuenta_cards.items():
            try:
                if c_id == cid:
                    frame.configure(border_color=COLORS["accent"], fg_color="#123044")
                else:
                    frame.configure(border_color=COLORS["border"], fg_color="#0a1620")
            except: pass

    # ─── Panel derecho: DETALLE ───────────────────────────────
    def _show_empty_detail(self):
        for w in self.right_panel.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.right_panel,
                     text="👆  Selecciona una cuenta\npara ver todos sus detalles",
                     font=ctk.CTkFont(size=14),
                     text_color=COLORS["text_dim"],
                     justify="center").place(relx=0.5, rely=0.5, anchor="center")

    def _show_detail(self, cuenta):
        for w in self.right_panel.winfo_children():
            w.destroy()

        cid   = cuenta["id"]
        total = cuenta.get("total_perfiles", 0)
        usado = cuenta.get("perfiles_usados", 0)
        dias  = days_remaining(cuenta.get("fecha_caducidad",""))
        plat  = cuenta.get("plataforma_nombre","—")

        if dias is None:   dias_color, dias_txt = COLORS["text_dim"], "Sin fecha"
        elif dias < 0:     dias_color, dias_txt = COLORS["red"],     f"Vencida hace {abs(dias)} días"
        elif dias == 0:    dias_color, dias_txt = COLORS["red"],     "Vence HOY"
        elif dias <= 10:   dias_color, dias_txt = COLORS["yellow"],  f"{dias} días restantes ⚠️"
        else:              dias_color, dias_txt = COLORS["accent3"], f"{dias} días restantes"

        scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent",
                                         scrollbar_button_color=COLORS["border"])
        scroll.pack(fill="both", expand=True)

        # ── Encabezado cuenta ──
        hdr = ctk.CTkFrame(scroll, fg_color="#0a141a", corner_radius=12)
        hdr.pack(fill="x", padx=14, pady=(14, 8))

        h1 = ctk.CTkFrame(hdr, fg_color="transparent")
        h1.pack(fill="x", padx=14, pady=(12, 6))
        ctk.CTkLabel(h1, text=f"📺  {plat}",
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color="#ffffff").pack(side="left")

        dias_badge = ctk.CTkFrame(h1, fg_color=dias_color, corner_radius=8)
        dias_badge.pack(side="right")
        ctk.CTkLabel(dias_badge, text=dias_txt,
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="#ffffff" if dias_color != COLORS["yellow"] else "#000000"
                     ).pack(padx=10, pady=4)

        # Grid de datos — SIN PIN en cuenta principal
        data_frame = ctk.CTkFrame(hdr, fg_color="transparent")
        data_frame.pack(fill="x", padx=14, pady=(0, 4))
        data_frame.grid_columnconfigure(0, weight=1)
        data_frame.grid_columnconfigure(1, weight=1)

        campos = [
            ("📧 Correo / Usuario",      cuenta.get("correo_usuario","—")),
            ("🔑 Contraseña",            cuenta.get("contrasena","—") or "—"),
            ("📋 Orden de compra",       cuenta.get("orden_compra","—") or "—"),
            ("👥 Perfiles disponibles",  f"{usado} usados / {total} totales"),
            ("📅 Fecha de compra",       cuenta.get("fecha_creacion","—") or "—"),
            ("⏳ Fecha de vencimiento",  cuenta.get("fecha_caducidad","—") or "—"),
        ]

        for i, (lbl, val) in enumerate(campos):
            col = i % 2
            row = i // 2
            box = ctk.CTkFrame(data_frame, fg_color="#0a1620", corner_radius=8)
            box.grid(row=row, column=col, sticky="ew", padx=4, pady=4)
            ctk.CTkLabel(box, text=lbl, font=ctk.CTkFont(size=10),
                         text_color=COLORS["text_dim"], anchor="w"
                         ).pack(anchor="w", padx=10, pady=(6,1))
            ctk.CTkLabel(box, text=val, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#ffffff", anchor="w", wraplength=200
                         ).pack(anchor="w", padx=10, pady=(0,6))

        # Notas
        notas = cuenta.get("notas","").strip()
        if notas:
            n_box = ctk.CTkFrame(hdr, fg_color="#142a28", corner_radius=8)
            n_box.pack(fill="x", padx=14, pady=(0, 12))
            ctk.CTkLabel(n_box, text="📝 Notas",
                         font=ctk.CTkFont(size=10),
                         text_color=COLORS["accent3"]).pack(anchor="w", padx=10, pady=(6,2))
            ctk.CTkLabel(n_box, text=notas,
                         font=ctk.CTkFont(size=12), text_color="#b9f3e8",
                         anchor="w", justify="left", wraplength=380
                         ).pack(anchor="w", padx=10, pady=(0,8))

        # Botones cuenta
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(0, 8))
        primary_btn(btn_row, "✏️  Editar cuenta",
                    command=lambda: self._abrir_form_editar(cuenta),
                    height=34).pack(side="left", padx=(0, 8))
        danger_btn(btn_row, "🗑  Eliminar cuenta",
                   command=lambda: self._eliminar_cuenta(cid),
                   height=34).pack(side="left")

        # ── Sección perfiles ──
        ctk.CTkFrame(scroll, fg_color=COLORS["border"], height=1
                     ).pack(fill="x", padx=14, pady=8)

        ph = ctk.CTkFrame(scroll, fg_color="transparent")
        ph.pack(fill="x", padx=14, pady=(0,6))
        ctk.CTkLabel(ph, text="👥  Perfiles asignados",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#ffffff").pack(side="left")
        pct_color = COLORS["accent3"] if usado < total else COLORS["accent2"]
        ctk.CTkLabel(ph, text=f"{usado}/{total}",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=pct_color).pack(side="right")

        if total > 0:
            prog = ctk.CTkProgressBar(scroll, height=8, corner_radius=4,
                                       fg_color=COLORS["border"],
                                       progress_color=pct_color)
            prog.set(min(usado / total, 1.0))
            prog.pack(fill="x", padx=14, pady=(0,10))

               # ── Formulario agregar / editar perfil ──
        self._editing_perfil_id = None
        self._cuenta_ref        = cuenta

        add_card = ctk.CTkFrame(scroll, fg_color="#0a1620", corner_radius=10)
        add_card.pack(fill="x", padx=14, pady=(0, 10))

        add_top = ctk.CTkFrame(add_card, fg_color="transparent")
        add_top.pack(fill="x", padx=12, pady=(10, 6))
        self._add_lbl = ctk.CTkLabel(add_top, text="➕  Agregar perfil",
                                      font=ctk.CTkFont(size=12, weight="bold"),
                                      text_color=COLORS["accent2"])
        self._add_lbl.pack(side="left")

        form = ctk.CTkFrame(add_card, fg_color="transparent")
        form.pack(fill="x", padx=12, pady=(0, 10))
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        # Fila 1: # Perfil | PIN (mitad y mitad, se adaptan al ancho)
        ctk.CTkLabel(form, text="# Perfil:", font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(form, text="PIN:", font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).grid(row=0, column=1, sticky="w", padx=(10, 0))

        self._e_num = entry_field(form, placeholder="1")
        self._e_num.grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=(2, 10))
        self._e_pin = entry_field(form, placeholder="PIN")
        self._e_pin.grid(row=1, column=1, sticky="ew", padx=(6, 0), pady=(2, 10))

        # Fila 2: Cliente (ancho completo)
        ctk.CTkLabel(form, text="Asignado a:", font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).grid(row=2, column=0, columnspan=2, sticky="w")
        self._e_cli = entry_field(form, placeholder="Nombre del cliente")
        self._e_cli.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(2, 10))

        # Fila 3: F. Inicio | F. Fin (mitad y mitad)
        ctk.CTkLabel(form, text="F. Inicio:", font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).grid(row=4, column=0, sticky="w")
        ctk.CTkLabel(form, text="F. Fin:", font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).grid(row=4, column=1, sticky="w", padx=(10, 0))

        self._e_fi = DateEntryWidget(form)
        self._e_fi.grid(row=5, column=0, sticky="ew", padx=(0, 6), pady=(2, 12))
        self._e_fi.set(date.today().strftime("%Y-%m-%d"))

        self._e_ff = DateEntryWidget(form)
        self._e_ff.grid(row=5, column=1, sticky="ew", padx=(6, 0), pady=(2, 12))

        # Fila 4: Notas (ancho completo)
        ctk.CTkLabel(form, text="Notas (opcional):", font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).grid(row=6, column=0, columnspan=2, sticky="w")
        self._e_notas_perfil = ctk.CTkTextbox(
            form, height=50, fg_color="#0a1620",
            border_color=COLORS["border"], border_width=1,
            font=ctk.CTkFont(size=12), text_color="#ffffff", corner_radius=8)
        self._e_notas_perfil.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(2, 12))

        # Fila 5: botones, siempre visibles en su propia fila
        btnrow = ctk.CTkFrame(form, fg_color="transparent")
        btnrow.grid(row=8, column=0, columnspan=2, sticky="w")

        self._btn_add_p = ctk.CTkButton(
            btnrow, text="➕  Agregar",
            command=self._guardar_perfil,
            height=32, corner_radius=8, width=110,
            fg_color=COLORS["accent"], hover_color="#0b8482",
            font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
        self._btn_add_p.pack(side="left", padx=(0, 6))

        self._btn_cancel_p = ctk.CTkButton(
            btnrow, text="✕",
            command=self._cancelar_perfil,
            height=32, corner_radius=8, width=36,
            fg_color="#193040", hover_color=COLORS["border"],
            font=ctk.CTkFont(size=12), text_color="#2c4a5c", state="disabled")
        self._btn_cancel_p.pack(side="left")

        # Tarjetas de perfiles
        self._perfiles_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self._perfiles_container.pack(fill="x", padx=14, pady=(0, 14))
        self._render_perfiles(cid)

        # ─── Render perfiles como tarjetas ────────────────────────
    def _render_perfiles(self, cid):
        for w in self._perfiles_container.winfo_children():
            w.destroy()

        perfiles = self.db.get_perfiles_cuenta(cid)
        total    = self._cuenta_ref.get("total_perfiles", 0)
        self.db.update_perfiles_usados(cid, len(perfiles))

        if not perfiles:
            ctk.CTkLabel(self._perfiles_container,
                         text="No hay perfiles asignados. Usa el formulario de arriba.",
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["text_dim"]).pack(pady=12)
            return

        for i, p in enumerate(perfiles):
            pid  = p["id"]
            dias = days_remaining(p.get("fecha_fin",""))
            bg   = "#0e1a22" if i % 2 == 0 else "#0a1620"

            if dias is None:   d_color, d_txt = COLORS["text_dim"], "Sin fecha"
            elif dias < 0:     d_color, d_txt = COLORS["red"],    f"Vencido hace {abs(dias)}d"
            elif dias <= 5:    d_color, d_txt = COLORS["red"],    f"{dias}d restantes ⚠"
            elif dias <= 15:   d_color, d_txt = COLORS["yellow"], f"{dias}d restantes"
            else:              d_color, d_txt = COLORS["accent3"],f"{dias}d restantes"

            pcard = ctk.CTkFrame(self._perfiles_container, fg_color=bg, corner_radius=8)
            pcard.pack(fill="x", pady=3)

                        # Fila superior: # perfil + cliente (izq, expande) y botones (der, fijos)
            top_row = ctk.CTkFrame(pcard, fg_color="transparent")
            top_row.pack(fill="x", padx=10, pady=(10, 2))

            btns = ctk.CTkFrame(top_row, fg_color="transparent")
            btns.pack(side="right")
            ctk.CTkButton(
                btns, text="🗑  Eliminar", command=lambda pid=pid: self._eliminar_perfil(pid),
                height=30, corner_radius=6,
                fg_color=COLORS["red"], hover_color="#c7425a",
                font=ctk.CTkFont(size=11, weight="bold"), text_color="white"
            ).pack(side="right", padx=(6, 0))
            ctk.CTkButton(
                btns, text="✏️  Editar", command=lambda p=p: self._editar_perfil_inline(p),
                height=30, corner_radius=6,
                fg_color=COLORS["accent"], hover_color="#0b8482",
                font=ctk.CTkFont(size=11, weight="bold"), text_color="white"
            ).pack(side="right")

            info = ctk.CTkFrame(top_row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info,
                         text=f"#{p.get('numero_perfil','?')}   {p.get('cliente_asignado','—')}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color="#ffffff", anchor="w").pack(anchor="w")

            # Fila inferior: PIN, fechas y días restantes
            bot_row = ctk.CTkFrame(pcard, fg_color="transparent")
            bot_row.pack(fill="x", padx=10, pady=(0, 4))

            pin_txt    = p.get("pin_perfil") or "—"
            f_ini      = p.get("fecha_inicio") or "—"
            f_fin      = p.get("fecha_fin") or "—"
            detail_txt = f"🔢 {pin_txt}    📅 {f_ini}  →  ⏳ {f_fin}"

            ctk.CTkLabel(bot_row, text=detail_txt,
                         font=ctk.CTkFont(size=11),
                         text_color=COLORS["text_dim"],
                         anchor="w", justify="left", wraplength=340
                         ).pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(bot_row, text=d_txt,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=d_color).pack(side="right")

            # Nota del perfil (si existe)
            nota_p = (p.get("notas") or "").strip()
            if nota_p:
                ctk.CTkLabel(pcard, text=f"📝 {nota_p}",
                             font=ctk.CTkFont(size=11),
                             text_color=COLORS["accent3"],
                             anchor="w", justify="left", wraplength=340
                             ).pack(anchor="w", padx=10, pady=(0, 10))

    # ─── CRUD perfiles ────────────────────────────────────────
    def _guardar_perfil(self):
        num = self._e_num.get().strip()
        cli = self._e_cli.get().strip()
        if not num:
            messagebox.showerror("Error", "El número de perfil es obligatorio."); return
        if not cli:
            messagebox.showerror("Error", "El nombre del cliente es obligatorio."); return

        data = {
            "cuenta_maestra_id": self._cuenta_ref["id"],
            "numero_perfil":     num,
            "nombre_perfil":     "",
            "cliente_asignado":  cli,
            "pin_perfil":        self._e_pin.get().strip(),
            "fecha_inicio":      self._e_fi.get(),
            "fecha_fin":         self._e_ff.get(),
            "telefono_cliente":  "",
            "notas":             self._e_notas_perfil.get("1.0", "end").strip(),
        }
        if self._editing_perfil_id:
            self.db.update_perfil_cuenta(self._editing_perfil_id, data)
        else:
            self.db.add_perfil_cuenta(data)

        self._cancelar_perfil()
        self._render_perfiles(self._cuenta_ref["id"])
        self._load_cuentas()

    def _editar_perfil_inline(self, p):
        self._editing_perfil_id = p["id"]
        self._add_lbl.configure(text="✏️  Editando perfil")
        self._btn_add_p.configure(text="💾  Guardar", fg_color="#4c3fa8",
                                   hover_color="#3c3186")
        self._btn_cancel_p.configure(state="normal", fg_color=COLORS["border"],
                                      text_color=COLORS["text"])
        self._e_num.delete(0,"end"); self._e_num.insert(0, str(p.get("numero_perfil","")))
        self._e_cli.delete(0,"end"); self._e_cli.insert(0, str(p.get("cliente_asignado","")))
        self._e_pin.delete(0,"end"); self._e_pin.insert(0, str(p.get("pin_perfil","") or ""))
        self._e_fi.set(p.get("fecha_inicio",""))
        self._e_ff.set(p.get("fecha_fin",""))
        self._e_notas_perfil.delete("1.0", "end")
        self._e_notas_perfil.insert("1.0", p.get("notas","") or "")

    def _cancelar_perfil(self):
        self._editing_perfil_id = None
        self._add_lbl.configure(text="➕  Agregar perfil")
        self._btn_add_p.configure(text="➕  Agregar", fg_color=COLORS["accent"],
                                   hover_color="#0b8482")
        self._btn_cancel_p.configure(state="disabled", fg_color="#193040",
                                      text_color="#2c4a5c")
        for e in [self._e_num, self._e_cli, self._e_pin]:
            e.delete(0,"end")
        self._e_fi.set(date.today().strftime("%Y-%m-%d"))
        self._e_ff.set("")
        self._e_notas_perfil.delete("1.0", "end")

    def _eliminar_perfil(self, pid):
        if messagebox.askyesno("Confirmar", "¿Eliminar este perfil?"):
            self.db.delete_perfil_cuenta(pid)
            self._render_perfiles(self._cuenta_ref["id"])
            self._load_cuentas()

    # ─── Cuenta CRUD ──────────────────────────────────────────
    def _abrir_form_nueva(self):
        CuentaFormWindow(self, self.db, cuenta=None,
                         on_save=self._on_cuenta_guardada)

    def _abrir_form_editar(self, cuenta):
        CuentaFormWindow(self, self.db, cuenta=cuenta,
                         on_save=self._on_cuenta_guardada)

    def _on_cuenta_guardada(self, cid):
        self._load_cuentas()
        self.selected_cid = cid
        cuenta = self.db.get_cuenta_maestra_by_id(cid)
        if cuenta:
            self._show_detail(cuenta)
            self._highlight_card(cid)

    def _eliminar_cuenta(self, cid):
        if messagebox.askyesno("Confirmar",
                               "¿Eliminar esta cuenta y todos sus perfiles?\n\n"
                               "Esta acción no se puede deshacer."):
            self.db.delete_cuenta_maestra(cid)
            self.selected_cid = None
            self._load_cuentas()
            self._show_empty_detail()


# ══════════════════════════════════════════════════════════════
#  FORMULARIO MODAL NUEVA / EDITAR CUENTA  (sin campo PIN)
# ══════════════════════════════════════════════════════════════
class CuentaFormWindow(ctk.CTkToplevel):
    def __init__(self, parent, db, cuenta=None, on_save=None):
        super().__init__(parent)
        self.db      = db
        self.cuenta  = cuenta
        self.on_save = on_save
        self.editing = cuenta is not None

        self.title("Editar Cuenta" if self.editing else "Nueva Cuenta")
        self.geometry("500x560")
        self.resizable(False, True)
        self.configure(fg_color=COLORS["bg_dark"])
        self.grab_set()

        self._build()
        if self.editing:
            self._prefill()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_dark"],
                                         corner_radius=0,
                                         scrollbar_button_color=COLORS["border"])
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll,
                     text="✏️  Editar Cuenta" if self.editing else "➕  Nueva Cuenta",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="#ffffff").pack(anchor="w", padx=20, pady=(16,12))

        def lbl(txt):
            ctk.CTkLabel(scroll, text=txt, anchor="w",
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["text_dim"]
                         ).pack(anchor="w", padx=20, pady=(8,2))

        lbl("Plataforma *")
        plataformas   = self.db.get_plataformas(solo_activas=True)
        plat_names    = [p["nombre"] for p in plataformas]
        self.plat_map = {p["nombre"]: p["id"] for p in plataformas}
        self.e_plat   = ctk.CTkComboBox(
            scroll, values=plat_names or ["— Crea plataformas primero —"],
            height=36, corner_radius=8,
            fg_color="#0a1620", border_color=COLORS["border"],
            button_color=COLORS["accent"],
            font=ctk.CTkFont(size=13), text_color="#ffffff")
        self.e_plat.pack(fill="x", padx=20, pady=(0,4))

        lbl("Correo / Usuario *")
        self.e_correo = entry_field(scroll, placeholder="correo@ejemplo.com")
        self.e_correo.pack(fill="x", padx=20, pady=(0,4))

        lbl("Contraseña")
        self.e_pass = entry_field(scroll, placeholder="Contraseña de la cuenta")
        self.e_pass.pack(fill="x", padx=20, pady=(0,4))

        lbl("Orden de compra")
        self.e_orden = entry_field(scroll, placeholder="# orden del proveedor")
        self.e_orden.pack(fill="x", padx=20, pady=(0,4))

        ctk.CTkFrame(scroll, height=1,
                     fg_color=COLORS["border"]).pack(fill="x", padx=20, pady=12)
        ctk.CTkLabel(scroll, text="¿Cuántos perfiles tiene esta cuenta?",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["accent2"]).pack(anchor="w", padx=20)
        ctk.CTkLabel(scroll, text="Ej: Netflix = 5, Disney = 7",
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).pack(anchor="w", padx=20, pady=(2,4))
        self.e_perfiles = entry_field(scroll, placeholder="Ej: 5")
        self.e_perfiles.pack(fill="x", padx=20, pady=(0,4))
        ctk.CTkFrame(scroll, height=1,
                     fg_color=COLORS["border"]).pack(fill="x", padx=20, pady=12)

        lbl("Fecha de compra")
        self.e_f_ini = DateEntryWidget(scroll)
        self.e_f_ini.pack(fill="x", padx=20, pady=(0,4))
        if not self.editing:
            self.e_f_ini.set(date.today().strftime("%Y-%m-%d"))

        lbl("Fecha de vencimiento")
        self.e_f_fin = DateEntryWidget(scroll)
        self.e_f_fin.pack(fill="x", padx=20, pady=(0,4))

        lbl("Notas (opcional)")
        self.e_notas = ctk.CTkTextbox(scroll, height=65, fg_color="#0a1620",
                                       border_color=COLORS["border"], border_width=1,
                                       font=ctk.CTkFont(size=12), text_color="#ffffff",
                                       corner_radius=8)
        self.e_notas.pack(fill="x", padx=20, pady=(0,8))

        bf = ctk.CTkFrame(scroll, fg_color="transparent")
        bf.pack(fill="x", padx=20, pady=(4,20))
        primary_btn(bf, "💾  Guardar",
                    command=self._guardar).pack(side="left", padx=(0,8))
        secondary_btn(bf, "✕  Cancelar",
                      command=self.destroy).pack(side="left")

    def _prefill(self):
        c     = self.cuenta
        plats = self.db.get_plataformas(solo_activas=True)
        for p in plats:
            if p["id"] == c.get("plataforma_id"):
                self.e_plat.set(p["nombre"]); break
        def _s(e, v): e.delete(0,"end"); e.insert(0, str(v or ""))
        _s(self.e_correo,   c.get("correo_usuario",""))
        _s(self.e_pass,     c.get("contrasena",""))
        _s(self.e_orden,    c.get("orden_compra",""))
        _s(self.e_perfiles, c.get("total_perfiles",""))
        self.e_f_ini.set(c.get("fecha_creacion",""))
        self.e_f_fin.set(c.get("fecha_caducidad",""))
        self.e_notas.delete("1.0","end")
        self.e_notas.insert("1.0", c.get("notas",""))

    def _guardar(self):
        plat_n  = self.e_plat.get()
        plat_id = self.plat_map.get(plat_n)
        if not plat_id:
            messagebox.showerror("Error", "Selecciona una plataforma válida."); return
        correo = self.e_correo.get().strip()
        if not correo:
            messagebox.showerror("Error", "El correo/usuario es obligatorio."); return
        try:    total_p = int(self.e_perfiles.get() or 0)
        except: total_p = 0

        data = {
            "plataforma_id":   plat_id,
            "correo_usuario":  correo,
            "contrasena":      self.e_pass.get().strip(),
            "pin":             "",          # PIN ya no va en cuenta
            "orden_compra":    self.e_orden.get().strip(),
            "total_perfiles":  total_p,
            "fecha_creacion":  self.e_f_ini.get(),
            "fecha_caducidad": self.e_f_fin.get(),
            "proveedor_id":    None,
            "notas":           self.e_notas.get("1.0","end").strip(),
        }

        if self.editing:
            self.db.update_cuenta_maestra(self.cuenta["id"], data)
            cid = self.cuenta["id"]
        else:
            self.db.add_cuenta_maestra(data)
            cuentas = self.db.get_cuentas_maestras(busqueda=correo)
            cid = cuentas[0]["id"] if cuentas else None

        self.destroy()
        if self.on_save and cid:
            self.on_save(cid)