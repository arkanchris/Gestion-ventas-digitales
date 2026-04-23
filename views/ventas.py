import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from widgets import (COLORS, card, title_label, primary_btn,
                     secondary_btn, entry_field, section_header, DateEntryWidget)
from tirilla import generar_tirilla


class VentasView(ctk.CTkFrame):
    def __init__(self, parent, db, app):
        super().__init__(parent, fg_color=COLORS["bg_dark"], corner_radius=0)
        self.db = db
        self.app = app
        self.editing_id = None
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=COLORS["bg_dark"], corner_radius=0,
            scrollbar_button_color=COLORS["border"])
        scroll.pack(fill="both", expand=True)

        # ── Header ── (sin banner vacío)
        hdr = ctk.CTkFrame(scroll, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(24, 4))

        left_hdr = ctk.CTkFrame(hdr, fg_color="transparent")
        left_hdr.pack(side="left", fill="y")
        title_label(left_hdr, "💰  Nueva Venta", size=22).pack(side="left")

        # Indicador de modo edición
        self.mode_label = ctk.CTkLabel(
            hdr, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["accent4"])
        self.mode_label.pack(side="left", padx=16)

        # ── SECCIÓN: Datos del cliente ──
        section_header(scroll, "📋  Datos del Cliente")
        c_frame = card(scroll)
        c_frame.pack(fill="x", padx=24, pady=4)

        # Fila 1: Cliente + Perfil
        r1 = ctk.CTkFrame(c_frame, fg_color="transparent")
        r1.pack(fill="x", padx=16, pady=8)
        r1.grid_columnconfigure(1, weight=1)
        r1.grid_columnconfigure(3, weight=1)
        _lbl(r1, "Cliente *", 0)
        self.e_cliente = entry_field(r1, placeholder="Nombre del cliente")
        self.e_cliente.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r1, "Teléfono", 2)
        self.e_telefono = entry_field(r1, placeholder="Número de teléfono")
        self.e_telefono.grid(row=0, column=3, sticky="ew", padx=(8, 0))

        # Fila 2: Orden + Perfil
        r2 = ctk.CTkFrame(c_frame, fg_color="transparent")
        r2.pack(fill="x", padx=16, pady=8)
        r2.grid_columnconfigure(1, weight=1)
        r2.grid_columnconfigure(3, weight=1)
        _lbl(r2, "Orden Compra", 0)
        self.e_orden = entry_field(r2, placeholder="# de orden o compra")
        self.e_orden.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r2, "Perfil", 2)
        self.e_perfil = entry_field(r2, placeholder="Ej: Perfil 1")
        self.e_perfil.grid(row=0, column=3, sticky="ew", padx=(8, 0))

        # ── SECCIÓN: Plataforma y Proveedor ──
        section_header(scroll, "📺  Plataforma y Proveedor")
        pf = card(scroll)
        pf.pack(fill="x", padx=24, pady=4)

        r3 = ctk.CTkFrame(pf, fg_color="transparent")
        r3.pack(fill="x", padx=16, pady=8)
        r3.grid_columnconfigure(1, weight=1)
        r3.grid_columnconfigure(3, weight=1)
        _lbl(r3, "Plataforma *", 0)
        plataformas = self.db.get_plataformas(solo_activas=True)
        plat_names = [p["nombre"] for p in plataformas]
        self.plat_map = {p["nombre"]: p["id"] for p in plataformas}
        self.e_plataforma = _combobox(r3, plat_names or ["— Sin plataformas —"])
        self.e_plataforma.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r3, "Proveedor", 2)
        proveedores = self.db.get_proveedores(solo_activos=True)
        prov_names = [p["nombre"] for p in proveedores]
        self.prov_map = {p["nombre"]: p["id"] for p in proveedores}
        self.e_proveedor = _combobox(r3, prov_names or ["— Sin proveedores —"])
        self.e_proveedor.grid(row=0, column=3, sticky="ew", padx=(8, 0))

        # ── SECCIÓN: Datos de acceso ──
        section_header(scroll, "🔐  Datos de Acceso")
        af = card(scroll)
        af.pack(fill="x", padx=24, pady=4)

        r4 = ctk.CTkFrame(af, fg_color="transparent")
        r4.pack(fill="x", padx=16, pady=8)
        r4.grid_columnconfigure(1, weight=2)
        r4.grid_columnconfigure(3, weight=2)
        r4.grid_columnconfigure(5, weight=1)
        _lbl(r4, "Correo/Usuario", 0)
        self.e_correo = entry_field(r4, placeholder="correo@ejemplo.com")
        self.e_correo.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r4, "Contraseña", 2)
        self.e_password = entry_field(r4, placeholder="Contraseña")
        self.e_password.grid(row=0, column=3, sticky="ew", padx=(8, 20))
        _lbl(r4, "PIN", 4)
        self.e_pin = entry_field(r4, placeholder="PIN")
        self.e_pin.grid(row=0, column=5, sticky="ew", padx=(8, 0))

        # ── SECCIÓN: Precio y Fechas ──
        section_header(scroll, "💲  Precio y Fechas")
        ff = card(scroll)
        ff.pack(fill="x", padx=24, pady=4)

        r5 = ctk.CTkFrame(ff, fg_color="transparent")
        r5.pack(fill="x", padx=16, pady=8)
        r5.grid_columnconfigure(1, weight=1)
        r5.grid_columnconfigure(3, weight=1)
        r5.grid_columnconfigure(5, weight=1)
        _lbl(r5, "Precio Venta *", 0)
        self.e_precio = entry_field(r5, placeholder="0.00")
        self.e_precio.grid(row=0, column=1, sticky="ew", padx=(8, 20))
        _lbl(r5, "F. Activación", 2)
        self.e_fecha_act = DateEntryWidget(r5)
        self.e_fecha_act.grid(row=0, column=3, sticky="ew", padx=(8, 20))
        _lbl(r5, "F. Vencimiento", 4)
        self.e_fecha_venc = DateEntryWidget(r5)
        self.e_fecha_venc.grid(row=0, column=5, sticky="ew", padx=(8, 0))

        # Estado pago (interno)
        r6 = ctk.CTkFrame(ff, fg_color="transparent")
        r6.pack(fill="x", padx=16, pady=(0, 10))
        ctk.CTkLabel(r6, text="🔒 Estado de Pago  (solo uso interno)",
                     font=ctk.CTkFont(size=13),
                     text_color=COLORS["text_dim"]).pack(side="left")
        self.estado_pago = ctk.CTkSegmentedButton(
            r6, values=["pagada", "pendiente"],
            selected_color=COLORS["accent"],
            selected_hover_color="#1558b0",
            unselected_color=COLORS["border"],
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text"])
        self.estado_pago.set("pagada")
        self.estado_pago.pack(side="left", padx=14)

        # ── SECCIÓN: Notas ──
        section_header(scroll, "📝  Notas")
        nf = card(scroll)
        nf.pack(fill="x", padx=24, pady=4)
        self.e_notas = ctk.CTkTextbox(
            nf, height=80, fg_color="#0d1828",
            border_color=COLORS["border"], border_width=1,
            font=ctk.CTkFont(size=13), text_color="#ffffff",
            corner_radius=8)
        self.e_notas.pack(fill="x", padx=16, pady=12)

        # ── Botones ──
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=16)
        primary_btn(btn_frame, "💾  Guardar Venta",
                    command=self._guardar).pack(side="left", padx=(0, 8))
        secondary_btn(btn_frame, "✕  Cancelar / Limpiar",
                      command=self._limpiar).pack(side="left")

    # ── helpers ──────────────────────────────────────────────────────────────
    def _get_data(self):
        plat_name = self.e_plataforma.get()
        prov_name = self.e_proveedor.get()
        return {
            "cliente":           self.e_cliente.get().strip(),
            "perfil":            self.e_perfil.get().strip(),
            "telefono":          self.e_telefono.get().strip(),
            "plataforma_id":     self.plat_map.get(plat_name),
            "orden_compra":      self.e_orden.get().strip(),
            "correo_usuario":    self.e_correo.get().strip(),
            "proveedor_id":      self.prov_map.get(prov_name),
            "contrasena":        self.e_password.get().strip(),
            "pin":               self.e_pin.get().strip(),
            "precio_venta":      float(self.e_precio.get() or 0),
            "fecha_activacion":  self.e_fecha_act.get(),
            "fecha_vencimiento": self.e_fecha_venc.get(),
            "notas":             self.e_notas.get("1.0", "end").strip(),
            "estado_pago":       self.estado_pago.get(),
        }

    def _guardar(self):
        data = self._get_data()
        if not data["cliente"]:
            messagebox.showerror("Error", "El nombre del cliente es obligatorio.")
            return
        if not data["plataforma_id"]:
            messagebox.showerror("Error", "Selecciona una plataforma válida.")
            return

        if self.editing_id:
            self.db.update_venta(self.editing_id, data)
            messagebox.showinfo("✅ Actualizado", "Venta actualizada correctamente.")
            self._limpiar()
            # Regresar a clientes para ver la lista actualizada
            self.app.show_view("clientes")
        else:
            vid, factura = self.db.add_venta(data)
            resp = messagebox.askyesno(
                "✅ Venta guardada",
                f"Venta #{factura} registrada exitosamente.\n\n"
                "¿Deseas generar la tirilla digital para enviar al cliente?")
            if resp:
                venta = self.db.get_venta_by_id(vid)
                config = self.db.get_config()
                generar_tirilla(venta, config)
            self._limpiar()

    def _limpiar(self):
        self.editing_id = None
        self.mode_label.configure(text="")
        for e in [self.e_cliente, self.e_perfil, self.e_telefono,
                  self.e_orden, self.e_correo, self.e_password,
                  self.e_pin, self.e_precio]:
            e.delete(0, "end")
        self.e_fecha_act.set("")
        self.e_fecha_venc.set("")
        self.e_notas.delete("1.0", "end")
        self.estado_pago.set("pagada")

    def cargar_venta(self, venta):
        """Carga una venta existente para editar."""
        self.editing_id = venta["id"]
        self.mode_label.configure(
            text=f"✏️  Editando venta #{venta.get('numero_factura','?')} — {venta.get('cliente','')}",
            text_color=COLORS["accent4"])

        def _set(e, v):
            e.delete(0, "end")
            e.insert(0, str(v or ""))

        _set(self.e_cliente,  venta.get("cliente", ""))
        _set(self.e_perfil,   venta.get("perfil", ""))
        _set(self.e_telefono, venta.get("telefono", ""))
        _set(self.e_orden,    venta.get("orden_compra", ""))
        _set(self.e_correo,   venta.get("correo_usuario", ""))
        _set(self.e_password, venta.get("contrasena", ""))
        _set(self.e_pin,      venta.get("pin", ""))
        _set(self.e_precio,   venta.get("precio_venta", ""))
        self.e_fecha_act.set(venta.get("fecha_activacion", ""))
        self.e_fecha_venc.set(venta.get("fecha_vencimiento", ""))
        self.e_notas.delete("1.0", "end")
        self.e_notas.insert("1.0", venta.get("notas", ""))
        self.estado_pago.set(venta.get("estado_pago", "pagada"))

        # Seleccionar plataforma
        plats = self.db.get_plataformas(solo_activas=True)
        for p in plats:
            if p["id"] == venta.get("plataforma_id"):
                self.e_plataforma.set(p["nombre"])
                break
        # Seleccionar proveedor
        provs = self.db.get_proveedores(solo_activos=True)
        for p in provs:
            if p["id"] == venta.get("proveedor_id"):
                self.e_proveedor.set(p["nombre"])
                break


# ── Helpers locales ───────────────────────────────────────────────────────────
def _lbl(parent, text, col):
    ctk.CTkLabel(parent, text=text, anchor="w", width=110,
                 font=ctk.CTkFont(size=13),
                 text_color=COLORS["text_dim"]).grid(row=0, column=col, sticky="w")


def _combobox(parent, values):
    return ctk.CTkComboBox(
        parent, values=values, height=38, corner_radius=8,
        fg_color="#0d1828", border_color=COLORS["border"],
        button_color=COLORS["accent"],
        font=ctk.CTkFont(size=13), text_color="#ffffff")
