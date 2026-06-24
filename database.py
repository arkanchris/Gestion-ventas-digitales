import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streamcontrol.db")

class Database:
    def __init__(self):
        self.path = DB_PATH

    def get_conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_conn()
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS configuracion (
            id INTEGER PRIMARY KEY, clave TEXT UNIQUE, valor TEXT)""")

        c.execute("""CREATE TABLE IF NOT EXISTS plataformas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL, costo_compra REAL DEFAULT 0,
            precio_venta REAL DEFAULT 0, imagen_path TEXT DEFAULT '',
            activa INTEGER DEFAULT 1)""")
        try:
            c.execute("ALTER TABLE plataformas ADD COLUMN imagen_path TEXT DEFAULT ''")
        except: pass

        c.execute("""CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL, telefono TEXT, correo TEXT,
            maneja_credito INTEGER DEFAULT 0, notas TEXT,
            activo INTEGER DEFAULT 1)""")

        c.execute("""CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_factura INTEGER, cliente TEXT NOT NULL, perfil TEXT,
            telefono TEXT, plataforma_id INTEGER, orden_compra TEXT,
            correo_usuario TEXT, proveedor_id INTEGER, contrasena TEXT,
            pin TEXT, precio_venta REAL DEFAULT 0, fecha_activacion TEXT,
            fecha_vencimiento TEXT, notas TEXT,
            estado_pago TEXT DEFAULT 'pagada', fecha_registro TEXT,
            FOREIGN KEY(plataforma_id) REFERENCES plataformas(id),
            FOREIGN KEY(proveedor_id)  REFERENCES proveedores(id))""")

        # ── Libro de Cuentas Maestras ──
        c.execute("""CREATE TABLE IF NOT EXISTS cuentas_maestras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plataforma_id   INTEGER,
            correo_usuario  TEXT NOT NULL,
            contrasena      TEXT,
            pin             TEXT,
            orden_compra    TEXT,
            total_perfiles  INTEGER DEFAULT 0,
            perfiles_usados INTEGER DEFAULT 0,
            fecha_creacion  TEXT,
            fecha_caducidad TEXT,
            proveedor_id    INTEGER,
            notas           TEXT,
            fecha_registro  TEXT,
            FOREIGN KEY(plataforma_id) REFERENCES plataformas(id),
            FOREIGN KEY(proveedor_id)  REFERENCES proveedores(id))""")

        c.execute("""CREATE TABLE IF NOT EXISTS perfiles_cuenta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cuenta_maestra_id INTEGER NOT NULL,
            numero_perfil     TEXT,
            nombre_perfil     TEXT,
            cliente_asignado  TEXT,
            telefono_cliente  TEXT,
            notas             TEXT,
            FOREIGN KEY(cuenta_maestra_id) REFERENCES cuentas_maestras(id))""")

        c.execute("""CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descripcion TEXT, monto REAL DEFAULT 0,
            fecha TEXT, categoria TEXT)""")

        defaults = {
            "business_name":       "StreamControl",
            "factura_consecutivo": "1",
            "logo_path":           "",
        }
        for k, v in defaults.items():
            c.execute(
                "INSERT OR IGNORE INTO configuracion (clave,valor) VALUES (?,?)",
                (k, v))

        conn.commit()
        conn.close()

    # ── CONFIG ───────────────────────────────────────────────
    def get_config(self):
        conn = self.get_conn()
        rows = conn.execute("SELECT clave,valor FROM configuracion").fetchall()
        conn.close()
        return {r["clave"]: r["valor"] for r in rows}

    def set_config(self, clave, valor):
        conn = self.get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO configuracion (clave,valor) VALUES (?,?)",
            (clave, valor))
        conn.commit(); conn.close()

    def next_factura(self):
        cfg = self.get_config()
        n   = int(cfg.get("factura_consecutivo", "1"))
        self.set_config("factura_consecutivo", str(n + 1))
        return n

    # ── PLATAFORMAS ──────────────────────────────────────────
    def get_plataformas(self, solo_activas=False):
        conn = self.get_conn()
        q = ("SELECT * FROM plataformas WHERE activa=1 ORDER BY nombre"
             if solo_activas else
             "SELECT * FROM plataformas ORDER BY nombre")
        rows = conn.execute(q).fetchall(); conn.close()
        return [dict(r) for r in rows]

    def add_plataforma(self, nombre, costo, precio, imagen_path=""):
        conn = self.get_conn()
        conn.execute(
            "INSERT INTO plataformas (nombre,costo_compra,precio_venta,imagen_path) VALUES (?,?,?,?)",
            (nombre, costo, precio, imagen_path))
        conn.commit(); conn.close()

    def update_plataforma(self, pid, nombre, costo, precio, activa, imagen_path=""):
        conn = self.get_conn()
        conn.execute(
            "UPDATE plataformas SET nombre=?,costo_compra=?,precio_venta=?,activa=?,imagen_path=? WHERE id=?",
            (nombre, costo, precio, activa, imagen_path, pid))
        conn.commit(); conn.close()

    def delete_plataforma(self, pid):
        conn = self.get_conn()
        conn.execute("DELETE FROM plataformas WHERE id=?", (pid,))
        conn.commit(); conn.close()

    # ── PROVEEDORES ──────────────────────────────────────────
    def get_proveedores(self, solo_activos=False):
        conn = self.get_conn()
        q = ("SELECT * FROM proveedores WHERE activo=1 ORDER BY nombre"
             if solo_activos else
             "SELECT * FROM proveedores ORDER BY nombre")
        rows = conn.execute(q).fetchall(); conn.close()
        return [dict(r) for r in rows]

    def add_proveedor(self, nombre, telefono, correo, credito, notas):
        conn = self.get_conn()
        conn.execute(
            "INSERT INTO proveedores (nombre,telefono,correo,maneja_credito,notas) VALUES (?,?,?,?,?)",
            (nombre, telefono, correo, credito, notas))
        conn.commit(); conn.close()

    def update_proveedor(self, pid, nombre, telefono, correo, credito, notas, activo):
        conn = self.get_conn()
        conn.execute(
            "UPDATE proveedores SET nombre=?,telefono=?,correo=?,maneja_credito=?,notas=?,activo=? WHERE id=?",
            (nombre, telefono, correo, credito, notas, activo, pid))
        conn.commit(); conn.close()

    def delete_proveedor(self, pid):
        conn = self.get_conn()
        conn.execute("DELETE FROM proveedores WHERE id=?", (pid,))
        conn.commit(); conn.close()

    # ── VENTAS ───────────────────────────────────────────────
    def add_venta(self, data):
        conn    = self.get_conn()
        factura = self.next_factura()
        conn.execute("""INSERT INTO ventas
            (numero_factura,cliente,perfil,telefono,plataforma_id,orden_compra,
             correo_usuario,proveedor_id,contrasena,pin,precio_venta,
             fecha_activacion,fecha_vencimiento,notas,estado_pago,fecha_registro)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (factura, data["cliente"], data["perfil"], data["telefono"],
             data["plataforma_id"], data["orden_compra"], data["correo_usuario"],
             data["proveedor_id"], data["contrasena"], data["pin"],
             data["precio_venta"], data["fecha_activacion"],
             data["fecha_vencimiento"], data["notas"], data["estado_pago"],
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        vid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit(); conn.close()
        return vid, factura

    def get_ventas(self, filtros=None):
        conn  = self.get_conn()
        query = """SELECT v.*,
                          p.nombre      as plataforma_nombre,
                          p.imagen_path as plataforma_imagen,
                          pr.nombre     as proveedor_nombre
                   FROM ventas v
                   LEFT JOIN plataformas p  ON v.plataforma_id = p.id
                   LEFT JOIN proveedores pr ON v.proveedor_id  = pr.id
                   WHERE 1=1"""
        params = []
        if filtros:
            if filtros.get("plataforma_id"):
                query += " AND v.plataforma_id=?"; params.append(filtros["plataforma_id"])
            if filtros.get("proveedor_id"):
                query += " AND v.proveedor_id=?";  params.append(filtros["proveedor_id"])
            if filtros.get("estado_pago"):
                query += " AND v.estado_pago=?";   params.append(filtros["estado_pago"])
            if filtros.get("busqueda"):
                b = f"%{filtros['busqueda']}%"
                query += (" AND (v.cliente LIKE ? OR v.telefono LIKE ?"
                          " OR v.correo_usuario LIKE ?)")
                params.extend([b, b, b])
            if filtros.get("fecha_desde"):
                query += " AND v.fecha_activacion>=?"; params.append(filtros["fecha_desde"])
            if filtros.get("fecha_hasta"):
                query += " AND v.fecha_activacion<=?"; params.append(filtros["fecha_hasta"])
        query += " ORDER BY v.id DESC"
        rows = conn.execute(query, params).fetchall(); conn.close()
        return [dict(r) for r in rows]

    def get_venta_by_id(self, vid):
        conn = self.get_conn()
        row  = conn.execute("""SELECT v.*,
                                      p.nombre      as plataforma_nombre,
                                      p.imagen_path as plataforma_imagen,
                                      pr.nombre     as proveedor_nombre
                               FROM ventas v
                               LEFT JOIN plataformas p  ON v.plataforma_id=p.id
                               LEFT JOIN proveedores pr ON v.proveedor_id=pr.id
                               WHERE v.id=?""", (vid,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def update_venta(self, vid, data):
        conn = self.get_conn()
        conn.execute("""UPDATE ventas SET
            cliente=?,perfil=?,telefono=?,plataforma_id=?,orden_compra=?,
            correo_usuario=?,proveedor_id=?,contrasena=?,pin=?,precio_venta=?,
            fecha_activacion=?,fecha_vencimiento=?,notas=?,estado_pago=?
            WHERE id=?""",
            (data["cliente"], data["perfil"], data["telefono"],
             data["plataforma_id"], data["orden_compra"], data["correo_usuario"],
             data["proveedor_id"], data["contrasena"], data["pin"],
             data["precio_venta"], data["fecha_activacion"],
             data["fecha_vencimiento"], data["notas"], data["estado_pago"], vid))
        conn.commit(); conn.close()

    def delete_venta(self, vid):
        conn = self.get_conn()
        conn.execute("DELETE FROM ventas WHERE id=?", (vid,))
        conn.commit(); conn.close()

    # ── REPORTES ─────────────────────────────────────────────
    def get_resumen_ventas(self, periodo, fecha_desde=None, fecha_hasta=None):
        conn = self.get_conn()
        hoy  = datetime.now().strftime("%Y-%m-%d")

        if fecha_desde and fecha_hasta:
            where = (f"DATE(v.fecha_registro)>='{fecha_desde}'"
                     f" AND DATE(v.fecha_registro)<='{fecha_hasta}'")
        elif fecha_desde:
            where = f"DATE(v.fecha_registro)>='{fecha_desde}'"
        elif fecha_hasta:
            where = f"DATE(v.fecha_registro)<='{fecha_hasta}'"
        elif periodo == "dia":
            where = f"DATE(v.fecha_registro)='{hoy}'"
        elif periodo == "semana":
            where = f"DATE(v.fecha_registro)>=DATE('{hoy}','-7 days')"
        elif periodo == "mes":
            where = (f"strftime('%Y-%m',v.fecha_registro)"
                     f"=strftime('%Y-%m','{hoy}')")
        elif periodo == "anio":
            where = (f"strftime('%Y',v.fecha_registro)"
                     f"=strftime('%Y','{hoy}')")
        else:
            where = "1=1"

        total = conn.execute(
            f"SELECT COALESCE(SUM(precio_venta),0) as total,"
            f" COUNT(*) as cantidad FROM ventas v WHERE {where}"
        ).fetchone()

        por_plat = conn.execute(f"""
            SELECT p.nombre, COUNT(*) as cantidad,
                   SUM(v.precio_venta) as total,
                   SUM(v.precio_venta - p.costo_compra) as ganancia
            FROM ventas v
            JOIN plataformas p ON v.plataforma_id=p.id
            WHERE {where}
            GROUP BY v.plataforma_id ORDER BY cantidad DESC
        """).fetchall()

        conn.close()
        return {
            "total":          total["total"],
            "cantidad":       total["cantidad"],
            "por_plataforma": [dict(r) for r in por_plat],
        }

    def get_deudas(self):
        conn = self.get_conn()
        rows = conn.execute("""
            SELECT v.*,
                   p.nombre      as plataforma_nombre,
                   p.imagen_path as plataforma_imagen,
                   pr.nombre     as proveedor_nombre
            FROM ventas v
            LEFT JOIN plataformas p  ON v.plataforma_id=p.id
            LEFT JOIN proveedores pr ON v.proveedor_id=pr.id
            WHERE v.estado_pago='pendiente'
            ORDER BY v.fecha_vencimiento""").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ── CUENTAS MAESTRAS ─────────────────────────────────────
    def add_cuenta_maestra(self, data):
        conn = self.get_conn()
        conn.execute("""INSERT INTO cuentas_maestras
            (plataforma_id,correo_usuario,contrasena,pin,orden_compra,
             total_perfiles,fecha_creacion,fecha_caducidad,
             proveedor_id,notas,fecha_registro)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (data["plataforma_id"], data["correo_usuario"], data["contrasena"],
             data["pin"], data["orden_compra"], data["total_perfiles"],
             data["fecha_creacion"], data["fecha_caducidad"],
             data["proveedor_id"], data["notas"],
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit(); conn.close()

    def get_cuentas_maestras(self, busqueda=None, plataforma_id=None):
        conn  = self.get_conn()
        query = """SELECT cm.*,
                          p.nombre  as plataforma_nombre,
                          pr.nombre as proveedor_nombre
                   FROM cuentas_maestras cm
                   LEFT JOIN plataformas p  ON cm.plataforma_id=p.id
                   LEFT JOIN proveedores pr ON cm.proveedor_id=pr.id
                   WHERE 1=1"""
        params = []
        if plataforma_id:
            query += " AND cm.plataforma_id=?"; params.append(plataforma_id)
        if busqueda:
            b = f"%{busqueda}%"
            query += (" AND (cm.correo_usuario LIKE ?"
                      " OR cm.orden_compra LIKE ?"
                      " OR p.nombre LIKE ?)")
            params.extend([b, b, b])
        query += " ORDER BY cm.id DESC"
        rows = conn.execute(query, params).fetchall(); conn.close()
        return [dict(r) for r in rows]

    def get_cuenta_maestra_by_id(self, cid):
        conn = self.get_conn()
        row  = conn.execute("""SELECT cm.*,
                                      p.nombre  as plataforma_nombre,
                                      pr.nombre as proveedor_nombre
                               FROM cuentas_maestras cm
                               LEFT JOIN plataformas p  ON cm.plataforma_id=p.id
                               LEFT JOIN proveedores pr ON cm.proveedor_id=pr.id
                               WHERE cm.id=?""", (cid,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def update_cuenta_maestra(self, cid, data):
        conn = self.get_conn()
        conn.execute("""UPDATE cuentas_maestras SET
            plataforma_id=?,correo_usuario=?,contrasena=?,pin=?,orden_compra=?,
            total_perfiles=?,fecha_creacion=?,fecha_caducidad=?,
            proveedor_id=?,notas=?
            WHERE id=?""",
            (data["plataforma_id"], data["correo_usuario"], data["contrasena"],
             data["pin"], data["orden_compra"], data["total_perfiles"],
             data["fecha_creacion"], data["fecha_caducidad"],
             data["proveedor_id"], data["notas"], cid))
        conn.commit(); conn.close()

    def update_perfiles_usados(self, cid, n):
        conn = self.get_conn()
        conn.execute(
            "UPDATE cuentas_maestras SET perfiles_usados=? WHERE id=?", (n, cid))
        conn.commit(); conn.close()

    def delete_cuenta_maestra(self, cid):
        conn = self.get_conn()
        conn.execute("DELETE FROM perfiles_cuenta WHERE cuenta_maestra_id=?", (cid,))
        conn.execute("DELETE FROM cuentas_maestras WHERE id=?", (cid,))
        conn.commit(); conn.close()

    # ── PERFILES DE CUENTA ───────────────────────────────────
    def add_perfil_cuenta(self, data):
        conn = self.get_conn()
        conn.execute("""INSERT INTO perfiles_cuenta
            (cuenta_maestra_id,numero_perfil,nombre_perfil,
             cliente_asignado,telefono_cliente,notas)
            VALUES (?,?,?,?,?,?)""",
            (data["cuenta_maestra_id"], data["numero_perfil"],
             data["nombre_perfil"], data["cliente_asignado"],
             data["telefono_cliente"], data["notas"]))
        conn.commit(); conn.close()

    def get_perfiles_cuenta(self, cuenta_maestra_id):
        conn = self.get_conn()
        rows = conn.execute(
            "SELECT * FROM perfiles_cuenta"
            " WHERE cuenta_maestra_id=? ORDER BY numero_perfil",
            (cuenta_maestra_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_perfil_cuenta(self, pid, data):
        conn = self.get_conn()
        conn.execute("""UPDATE perfiles_cuenta SET
            numero_perfil=?,nombre_perfil=?,cliente_asignado=?,
            telefono_cliente=?,notas=? WHERE id=?""",
            (data["numero_perfil"], data["nombre_perfil"],
             data["cliente_asignado"], data["telefono_cliente"],
             data["notas"], pid))
        conn.commit(); conn.close()

    def delete_perfil_cuenta(self, pid):
        conn = self.get_conn()
        conn.execute("DELETE FROM perfiles_cuenta WHERE id=?", (pid,))
        conn.commit(); conn.close()
