import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from widgets import (COLORS, card, title_label, primary_btn, secondary_btn,
                     danger_btn, entry_field, build_treeview, DateEntryWidget)
from datetime import date


class ReservasView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db         = db
        self.app        = app
        self.editing_id = None
        self._build()
        self._load_cuentas()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        title_label(hdr, "📒  Libro de Cuentas", size=22).pack(side="left")

        ctk.CTkLabel(
            self,
            text="  Registra tus cuentas compradas y asigna cada perfil a un cliente. "
                 "Útil para consultas de soporte técnico.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"]
        ).pack(anchor="w", padx=24, pady=(0, 8))

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=24, pady=4)
        main.grid_columnconfigure(0, weight=2)
        main.grid_columnconfigure(1, weight=3)
        main.grid_rowconfigure(0, weight=1)

        self._build_form(main)
        self._build_right(main)

    # ═══════════════════════════════════════════════════════════
    #  FORMULARIO IZQUIERDO
    # ═══════════════════════════════════════════════════════════
    def _build_form(self, parent):
        scroll = ctk.CTkScrollableFrame(
            parent, fg_color=COLORS["bg_card"], corner_radius=12,
            scrollbar_button_color=COLORS["border"])
        scroll.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.form_title_lbl = ctk.CTkLabel(
            scroll, text="➕  Nueva Cuenta",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff")
        self.form_title_lbl.pack(anchor="w", padx=16, pady=(14, 6))

        def lbl(txt):
            ctk.CTkLabel(scroll, text=txt, anchor="w",
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["text_dim"]
                         ).pack(anchor="w", padx=16, pady=(8, 2))

        lbl("Plataforma *")
        plataformas   = self.db.get_plataformas(solo_activas=True)
        plat_names    = [p["nombre"] for p in plataformas]
        self.plat_map = {p["nombre"]: p["id"] for p in plataformas}
        self.e_plat   = ctk.CTkComboBox(
            scroll, values=plat_names or ["— Crea plataformas primero —"],
            height=36, corner_radius=8,
            fg_color="#0d1828", border_color=COLORS["border"],
            button_color=COLORS["accent"],
            font=ctk.CTkFont(size=13), text_color="#ffffff")
        self.e_plat.pack(fill="x", padx=16, pady=(0, 4))

        lbl("Correo / Usuario *")
        self.e_correo = entry_field(scroll, placeholder="correo@ejemplo.com")
        self.e_correo.pack(fill="x", padx=16, pady=(0, 4))

        lbl("Contraseña")
        self.e_password = entry_field(scroll, placeholder="Contraseña")
        self.e_password.pack(fill="x", padx=16, pady=(0, 4))

        lbl("PIN (si aplica)")
        self.e_pin = entry_field(scroll, placeholder="PIN")
        self.e_pin.pack(fill="x", padx=16, pady=(0, 4))

        lbl("Orden de compra")
        self.e_orden = entry_field(scroll, placeholder="# orden del proveedor")
        self.e_orden.pack(fill="x", padx=16, pady=(0, 4))

        ctk.CTkFrame(scroll, height=1,
                     fg_color=COLORS["border"]).pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(scroll,
                     text="¿Cuántos perfiles tiene esta cuenta?",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["accent2"]).pack(anchor="w", padx=16)
        ctk.CTkLabel(scroll, text="Ej: Netflix = 5, Disney = 7",
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_dim"]).pack(anchor="w", padx=16, pady=(2, 4))
        self.e_perfiles = entry_field(scroll, placeholder="Ej: 5")
        self.e_perfiles.pack(fill="x", padx=16, pady=(0, 4))
        ctk.CTkFrame(scroll, height=1,
                     fg_color=COLORS["border"]).pack(fill="x", padx=16, pady=10)

        lbl("Fecha de compra / inicio")
        self.e_fecha_ini = DateEntryWidget(scroll)
        self.e_fecha_ini.pack(fill="x", padx=16, pady=(0, 4))
        self.e_fecha_ini.set(date.today().strftime("%Y-%m-%d"))

        lbl("Fecha de vencimiento")
        self.e_fecha_fin = DateEntryWidget(scroll)
        self.e_fecha_fin.pack(fill="x", padx=16, pady=(0, 4))

        lbl("Notas")
        self.e_notas = ctk.CTkTextbox(
            scroll, height=55, fg_color="#0d1828",
            border_color=COLORS["border"], border_width=1,
            font=ctk.CTkFont(size=12), text_color="#ffffff", corner_radius=8)
        self.e_notas.pack(fill="x", padx=16, pady=(0, 8))

        bf = ctk.CTkFrame(scroll, fg_color="transparent")
        bf.pack(fill="x", padx=16, pady=(0, 16))
        primary_btn(bf, "💾  Guardar Cuenta",
                    command=self._guardar_cuenta).pack(side="left", padx=(0, 8))
        secondary_btn(bf, "✕  Limpiar",
                      command=self._limpiar_form).pack(side="left")

    # ═══════════════════════════════════════════════════════════
    #  DERECHA
    # ═══════════════════════════════════════════════════════════
    def _build_right(self, parent):
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        sc = card(right)
        sc.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        sf = ctk.CTkFrame(sc, fg_color="transparent")
        sf.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(sf, text="🔍", font=ctk.CTkFont(size=15),
                     text_color=COLORS["text_dim"]).pack(side="left", padx=(0, 4))
        self.search_var = tk.StringVar()
        entry_field(sf, placeholder="Buscar por correo, orden o plataforma...",
                    textvariable=self.search_var, width=230
                    ).pack(side="left", padx=(0, 10))
        self.search_var.trace("w", lambda *a: self._load_cuentas())

        ctk.CTkLabel(sf, text="Plataforma:", text_color=COLORS["text_dim"],
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 4))
        plataformas    = self.db.get_plataformas(solo_activas=True)
        self.fplat_map = {"Todas": None}
        self.fplat_map.update({p["nombre"]: p["id"] for p in plataformas})
        self.f_plat = ctk.CTkComboBox(
            sf, values=list(self.fplat_map.keys()),
            width=130, height=32, corner_radius=8,
            fg_color="#0d1828", border_color=COLORS["border"],
            button_color=COLORS["accent"],
            font=ctk.CTkFont(size=12), text_color=COLORS["text"],
            command=lambda e: self._load_cuentas())
        self.f_plat.set("Todas")
        self.f_plat.pack(side="left")

        self.cnt_lbl = ctk.CTkLabel(sf, text="",
                                     font=ctk.CTkFont(size=11),
                                     text_color=COLORS["text_dim"])
        self.cnt_lbl.pack(side="right")

        ac = card(right)
        ac.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        af = ctk.CTkFrame(ac, fg_color="transparent")
        af.pack(fill="x", padx=12, pady=8)

        ctk.CTkLabel(af, text="Selecciona una cuenta:",
                     font=ctk.CTkFont(size=11),
                     text_color="#3d5470").pack(side="left", padx=(0, 8))

        primary_btn(af, "✏️  Editar",
                    command=self._editar_cuenta,
                    height=32, width=90).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            af, text="👥  Ver / Asignar Perfiles",
            command=self._ver_perfiles,
            height=32, corner_radius=8, width=170,
            fg_color="#1d4ed8", hover_color="#1558b0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=(0, 6))

        danger_btn(af, "🗑  Eliminar",
                   command=self._eliminar_cuenta,
                   height=32, width=90).pack(side="left")

        ctk.CTkLabel(af, text="← Doble clic = ver perfiles",
                     font=ctk.CTkFont(size=10),
                     text_color="#3d5470").pack(side="right")

        cols = ("plataforma", "correo", "orden", "perfiles", "f_inicio", "f_vence", "notas")
        anchors = {
            "plataforma": "w", "correo": "w", "orden": "center",
            "perfiles": "center", "f_inicio": "center",
            "f_vence": "center", "notas": "w"
        }
        tf, self.tree = build_treeview(right, cols, heights=14, col_anchors=anchors)
        tf.grid(row=2, column=0, sticky="nsew")

        col_cfg = {
            "plataforma": ("Plataforma",       125),
            "correo":     ("Correo / Usuario",  175),
            "orden":      ("Orden",              95),
            "perfiles":   ("Perfiles",           70),
            "f_inicio":   ("F. Inicio",          95),
            "f_vence":    ("F. Vence",           95),
            "notas":      ("Notas",             120),
        }
        for c, (h, w) in col_cfg.items():
            self.tree.heading(c, text=h)
            self.tree.column(c, width=w)

        self.tree.bind("<Double-1>", lambda e: self._ver_perfiles())

    # ═══════════════════════════════════════════════════════════
    #  CARGA
    # ═══════════════════════════════════════════════════════════
    def _load_cuentas(self, *_):
        q       = self.search_var.get().strip()
        plat_id = self.fplat_map.get(self.f_plat.get())
        cuentas = self.db.get_cuentas_maestras(busqueda=q, plataforma_id=plat_id)
        self.cnt_lbl.configure(text=f"{len(cuentas)} cuentas")
        self.tree.delete(*self.tree.get_children())
        for c in cuentas:
            usados = c.get("perfiles_usados", 0)
            total  = c.get("total_perfiles", 0)
            self.tree.insert("", "end", iid=str(c["id"]), values=(
                c.get("plataforma_nombre", "—"),
                c.get("correo_usuario", "—"),
                c.get("orden_compra", "—") or "—",
                f"{usados}/{total}" if total else "—",
                c.get("fecha_creacion", "—") or "—",
                c.get("fecha_caducidad", "—") or "—",
                c.get("notas", "") or "",
            ))

    def _guardar_cuenta(self):
        plat_n  = self.e_plat.get()
        plat_id = self.plat_map.get(plat_n)
        if not plat_id:
            messagebox.showerror("Error", "Selecciona una plataforma válida.")
            return
        correo = self.e_correo.get().strip()
        if not correo:
            messagebox.showerror("Error", "El correo/usuario es obligatorio.")
            return
        try:
            total_p = int(self.e_perfiles.get() or 0)
        except ValueError:
            total_p = 0

        data = {
            "plataforma_id":   plat_id,
            "correo_usuario":  correo,
            "contrasena":      self.e_password.get().strip(),
            "pin":             self.e_pin.get().strip(),
            "orden_compra":    self.e_orden.get().strip(),
            "total_perfiles":  total_p,
            "fecha_creacion":  self.e_fecha_ini.get(),
            "fecha_caducidad": self.e_fecha_fin.get(),
            "proveedor_id":    None,
            "notas":           self.e_notas.get("1.0", "end").strip(),
        }

        if self.editing_id:
            self.db.update_cuenta_maestra(self.editing_id, data)
            messagebox.showinfo("✅", "Cuenta actualizada.")
            self._limpiar_form()
            self._load_cuentas()
        else:
            self.db.add_cuenta_maestra(data)
            self._limpiar_form()
            self._load_cuentas()
            cuentas = self.db.get_cuentas_maestras(busqueda=correo)
            if cuentas and messagebox.askyesno(
                    "✅ Cuenta guardada",
                    f"Cuenta de {plat_n} guardada.\n\n"
                    "¿Deseas asignar los perfiles ahora?"):
                cid = cuentas[0]["id"]
                self.tree.selection_set(str(cid))
                self._ver_perfiles()

    def _limpiar_form(self):
        self.editing_id = None
        self.form_title_lbl.configure(text="➕  Nueva Cuenta")
        for e in [self.e_correo, self.e_password, self.e_pin,
                  self.e_orden, self.e_perfiles]:
            e.delete(0, "end")
        self.e_fecha_ini.set(date.today().strftime("%Y-%m-%d"))
        self.e_fecha_fin.set("")
        self.e_notas.delete("1.0", "end")

    def _editar_cuenta(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una cuenta.")
            return
        cuenta = self.db.get_cuenta_maestra_by_id(int(sel[0]))
        if not cuenta: return
        self.editing_id = cuenta["id"]
        self.form_title_lbl.configure(text="✏️  Editando Cuenta")
        plats = self.db.get_plataformas(solo_activas=True)
        for p in plats:
            if p["id"] == cuenta.get("plataforma_id"):
                self.e_plat.set(p["nombre"]); break
        def _s(e, v): e.delete(0,"end"); e.insert(0, str(v or ""))
        _s(self.e_correo,   cuenta.get("correo_usuario",""))
        _s(self.e_password, cuenta.get("contrasena",""))
        _s(self.e_pin,      cuenta.get("pin",""))
        _s(self.e_orden,    cuenta.get("orden_compra",""))
        _s(self.e_perfiles, cuenta.get("total_perfiles",""))
        self.e_fecha_ini.set(cuenta.get("fecha_creacion",""))
        self.e_fecha_fin.set(cuenta.get("fecha_caducidad",""))
        self.e_notas.delete("1.0","end")
        self.e_notas.insert("1.0", cuenta.get("notas",""))

    def _eliminar_cuenta(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una cuenta.")
            return
        cuenta = self.db.get_cuenta_maestra_by_id(int(sel[0]))
        correo = cuenta.get("correo_usuario","") if cuenta else "esta cuenta"
        if messagebox.askyesno("Confirmar",
                               f"¿Eliminar '{correo}' y todos sus perfiles?\n\n"
                               "Esta acción no se puede deshacer."):
            self.db.delete_cuenta_maestra(int(sel[0]))
            self._load_cuentas()

    def _ver_perfiles(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona una cuenta primero.")
            return
        cuenta = self.db.get_cuenta_maestra_by_id(int(sel[0]))
        if not cuenta: return
        PerfilesWindow(self, self.db, cuenta)
        self._load_cuentas()


# ═══════════════════════════════════════════════════════════════
#  VENTANA DE PERFILES — layout fijo, sin scroll externo
# ═══════════════════════════════════════════════════════════════
class PerfilesWindow(ctk.CTkToplevel):
    def __init__(self, parent, db, cuenta):
        super().__init__(parent)
        self.db             = db
        self.cuenta         = cuenta
        self.cid            = cuenta["id"]
        self.editing_perfil = None

        plat = cuenta.get("plataforma_nombre", "Cuenta")
        self.title(f"Perfiles — {plat}")
        self.geometry("820x560")
        self.minsize(700, 480)
        self.configure(fg_color=COLORS["bg_dark"])
        self.grab_set()
        self.resizable(True, True)

        self._build()
        self._load()

    def _build(self):
        # ════════════════════════════════════════════
        #  ZONA FIJA SUPERIOR (info + formulario)
        # ════════════════════════════════════════════
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=16, pady=(14, 0))

        # ── Info de la cuenta ──
        info = ctk.CTkFrame(top_frame, fg_color="#0e2040", corner_radius=10)
        info.pack(fill="x", pady=(0, 8))

        title_row = ctk.CTkFrame(info, fg_color="transparent")
        title_row.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(
            title_row,
            text=f"📺  {self.cuenta.get('plataforma_nombre','—')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        fi = self.cuenta.get("fecha_creacion", "—")  or "—"
        ff = self.cuenta.get("fecha_caducidad", "—") or "—"
        ctk.CTkLabel(
            title_row,
            text=f"📅 Inicio: {fi}   |   ⏳ Vence: {ff}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["accent2"]
        ).pack(side="right")

        datos_row = ctk.CTkFrame(info, fg_color="transparent")
        datos_row.pack(fill="x", padx=14, pady=(0, 12))

        datos = [
            ("📧 Correo",     self.cuenta.get("correo_usuario","—")),
            ("🔑 Contraseña", self.cuenta.get("contrasena","—") or "—"),
            ("🔢 PIN",        self.cuenta.get("pin","—") or "—"),
            ("📋 Orden",      self.cuenta.get("orden_compra","—") or "—"),
            ("👥 Perfiles",   str(self.cuenta.get("total_perfiles","—"))),
        ]
        for lbl_txt, val in datos:
            col = ctk.CTkFrame(datos_row, fg_color="#091020", corner_radius=8)
            col.pack(side="left", padx=4)
            ctk.CTkLabel(col, text=lbl_txt,
                         font=ctk.CTkFont(size=10),
                         text_color=COLORS["text_dim"]).pack(padx=10, pady=(6, 1))
            ctk.CTkLabel(col, text=val,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#ffffff").pack(padx=10, pady=(0, 6))

        # ── Formulario de perfil ──
        form_card = ctk.CTkFrame(top_frame, fg_color=COLORS["bg_card"],
                                  corner_radius=10)
        form_card.pack(fill="x", pady=(0, 8))

        self.form_lbl = ctk.CTkLabel(
            form_card, text="➕  Agregar Perfil",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["accent2"])
        self.form_lbl.pack(anchor="w", padx=14, pady=(10, 6))

        ff_row = ctk.CTkFrame(form_card, fg_color="transparent")
        ff_row.pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkLabel(ff_row, text="# Perfil:",
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_dim"],
                     width=65).pack(side="left")
        self.e_num = entry_field(ff_row, placeholder="Ej: 1", width=65)
        self.e_num.pack(side="left", padx=(4, 16))

        ctk.CTkLabel(ff_row, text="Asignado a:",
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_dim"],
                     width=80).pack(side="left")
        self.e_cliente = entry_field(
            ff_row, placeholder="Nombre del cliente", width=220)
        self.e_cliente.pack(side="left", padx=(4, 16))

        self.btn_guardar = ctk.CTkButton(
            ff_row, text="➕  Agregar",
            command=self._guardar_perfil,
            height=34, corner_radius=8, width=110,
            fg_color=COLORS["accent"], hover_color="#1558b0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white")
        self.btn_guardar.pack(side="left", padx=(0, 6))

        self.btn_cancel = ctk.CTkButton(
            ff_row, text="✕  Cancelar",
            command=self._cancelar_edicion,
            height=34, corner_radius=8, width=100,
            fg_color="#1e3256", hover_color=COLORS["border"],
            font=ctk.CTkFont(size=12),
            text_color="#3d5470",
            state="disabled")
        self.btn_cancel.pack(side="left")

        # ════════════════════════════════════════════
        #  BARRA INFERIOR FIJA — se empaqueta PRIMERO
        #  para que siempre quede visible
        # ════════════════════════════════════════════
        bottom = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                               corner_radius=0, height=52)
        bottom.pack(fill="x", padx=0, pady=0, side="bottom")
        bottom.pack_propagate(False)

        inner = ctk.CTkFrame(bottom, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(inner, text="Selecciona un perfil:",
                     font=ctk.CTkFont(size=11),
                     text_color="#3d5470").pack(side="left", padx=(0, 10))

        primary_btn(inner, "✏️  Editar perfil",
                    command=self._editar_perfil,
                    height=34, width=130).pack(side="left", padx=(0, 8))

        danger_btn(inner, "🗑  Eliminar perfil",
                   command=self._eliminar_perfil,
                   height=34, width=130).pack(side="left")

        self.perfiles_lbl = ctk.CTkLabel(
            inner, text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["accent3"])
        self.perfiles_lbl.pack(side="right", padx=8)

        ctk.CTkLabel(inner,
                     text="← Doble clic en una fila para editarla",
                     font=ctk.CTkFont(size=10),
                     text_color="#3d5470").pack(side="right", padx=(0, 16))

        # ════════════════════════════════════════════
        #  TABLA — se empaqueta DESPUÉS para ocupar
        #  el espacio restante entre form y barra
        # ════════════════════════════════════════════
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 4))
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        cols    = ("num", "cliente")
        anchors = {"num": "center", "cliente": "w"}
        tf, self.ptree = build_treeview(
            table_frame, cols, heights=12, col_anchors=anchors)
        tf.grid(row=0, column=0, sticky="nsew")

        self.ptree.heading("num",     text="# Perfil")
        self.ptree.heading("cliente", text="Asignado a")
        self.ptree.column("num",     width=120)
        self.ptree.column("cliente", width=500)

        self.ptree.bind("<Double-1>", lambda e: self._editar_perfil())

    # ── Carga ─────────────────────────────────────────────────
    def _load(self):
        perfiles = self.db.get_perfiles_cuenta(self.cid)
        self.ptree.delete(*self.ptree.get_children())
        for p in perfiles:
            self.ptree.insert("", "end", iid=str(p["id"]), values=(
                p.get("numero_perfil", "—"),
                p.get("cliente_asignado", "—"),
            ))
        total  = self.cuenta.get("total_perfiles", 0)
        usados = len(perfiles)
        self.db.update_perfiles_usados(self.cid, usados)
        color = COLORS["accent3"] if usados < total else COLORS["accent2"]
        self.perfiles_lbl.configure(
            text=f"  {usados} de {total} perfiles asignados",
            text_color=color)

    # ── Guardar perfil ────────────────────────────────────────
    def _guardar_perfil(self):
        num     = self.e_num.get().strip()
        cliente = self.e_cliente.get().strip()
        if not num:
            messagebox.showerror("Error", "El número de perfil es obligatorio.")
            return
        if not cliente:
            messagebox.showerror("Error", "Indica a quién está asignado.")
            return

        data = {
            "cuenta_maestra_id": self.cid,
            "numero_perfil":     num,
            "nombre_perfil":     "",
            "cliente_asignado":  cliente,
            "telefono_cliente":  "",
            "notas":             "",
        }
        if self.editing_perfil:
            self.db.update_perfil_cuenta(self.editing_perfil, data)
        else:
            self.db.add_perfil_cuenta(data)

        self._cancelar_edicion()
        self._load()

    # ── Editar perfil ─────────────────────────────────────────
    def _editar_perfil(self):
        sel = self.ptree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un perfil de la lista.")
            return
        pid   = int(sel[0])
        perfs = self.db.get_perfiles_cuenta(self.cid)
        for p in perfs:
            if p["id"] == pid:
                self.editing_perfil = pid
                self.form_lbl.configure(text="✏️  Editando Perfil")
                self.btn_guardar.configure(
                    text="💾  Guardar cambios",
                    fg_color="#065f46", hover_color="#044a35")
                self.btn_cancel.configure(
                    state="normal",
                    fg_color=COLORS["border"],
                    text_color=COLORS["text"])
                self.e_num.delete(0, "end")
                self.e_num.insert(0, str(p.get("numero_perfil", "")))
                self.e_cliente.delete(0, "end")
                self.e_cliente.insert(0, str(p.get("cliente_asignado", "")))
                break

    # ── Cancelar edición ──────────────────────────────────────
    def _cancelar_edicion(self):
        self.editing_perfil = None
        self.form_lbl.configure(text="➕  Agregar Perfil")
        self.btn_guardar.configure(
            text="➕  Agregar",
            fg_color=COLORS["accent"], hover_color="#1558b0")
        self.btn_cancel.configure(
            state="disabled",
            fg_color="#1e3256", text_color="#3d5470")
        self.e_num.delete(0, "end")
        self.e_cliente.delete(0, "end")

    # ── Eliminar perfil ───────────────────────────────────────
    def _eliminar_perfil(self):
        sel = self.ptree.selection()
        if not sel:
            messagebox.showwarning("Selección", "Selecciona un perfil.")
            return
        pid   = int(sel[0])
        perfs = self.db.get_perfiles_cuenta(self.cid)
        nombre = ""
        for p in perfs:
            if p["id"] == pid:
                nombre = (f"Perfil #{p.get('numero_perfil','?')}"
                          f" — {p.get('cliente_asignado','')}")
                break
        if messagebox.askyesno(
                "Confirmar",
                f"¿Eliminar '{nombre}'?\n\nEsta acción no se puede deshacer."):
            self.db.delete_perfil_cuenta(pid)
            self._cancelar_edicion()
            self._load()
