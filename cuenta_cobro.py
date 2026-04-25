import os
import webbrowser
import tempfile
import base64
from datetime import datetime


def _img_to_b64(path):
    if not path or not os.path.exists(path):
        return None
    ext  = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext or "png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/{mime};base64,{b64}"


def generar_cuenta_cobro(distribuidor_nombre, deudas, config,
                          fecha_desde="", fecha_hasta=""):
    """
    Genera una Cuenta de Cobro profesional para un distribuidor.
    Lista todas las plataformas pendientes de pago con su detalle
    y el total a cobrar. Se puede guardar como PDF.
    """
    business_name = config.get("business_name", "StreamControl")
    logo_path     = config.get("logo_path", "")
    fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Número de cuenta de cobro (timestamp simple)
    num_cc = datetime.now().strftime("%Y%m%d%H%M")

    # Logo
    logo_uri = _img_to_b64(logo_path)
    if logo_uri:
        logo_html = (f'<img src="{logo_uri}" class="logo-img" alt="{business_name}">')
    else:
        logo_html = f'<span class="logo-text">{business_name}</span>'

    # Rango de fechas para mostrar en el encabezado
    rango_str = ""
    if fecha_desde and fecha_hasta:
        rango_str = f"Período: {_fmt(fecha_desde)} al {_fmt(fecha_hasta)}"
    elif fecha_desde:
        rango_str = f"Desde: {_fmt(fecha_desde)}"
    elif fecha_hasta:
        rango_str = f"Hasta: {_fmt(fecha_hasta)}"
    else:
        rango_str = "Todas las deudas pendientes"

    # Total
    total = sum(d["precio_venta"] for d in deudas)

    # Filas de la tabla
    filas_html = ""
    for i, d in enumerate(deudas, 1):
        plat   = d.get("plataforma_nombre", "—")
        cliente = d.get("cliente", "—")
        perfil  = d.get("perfil", "—")
        f_act   = _fmt(d.get("fecha_activacion", ""))
        f_venc  = _fmt(d.get("fecha_vencimiento", ""))
        precio  = d.get("precio_venta", 0)
        factura = d.get("numero_factura", "—")
        bg      = "#f8faff" if i % 2 == 0 else "#ffffff"

        filas_html += f"""
        <tr style="background:{bg}">
          <td class="tc">{i}</td>
          <td class="tc">#{factura}</td>
          <td class="tl"><strong>{plat}</strong></td>
          <td class="tl">{cliente}</td>
          <td class="tc">{perfil}</td>
          <td class="tc">{f_act}</td>
          <td class="tc">{f_venc}</td>
          <td class="tr"><strong>${precio:,.0f}</strong></td>
        </tr>"""

    # Nombre seguro para el archivo
    dist_safe = "".join(
        c for c in distribuidor_nombre if c.isalnum() or c in " _-"
    ).strip().replace(" ", "_")
    file_name = f"CuentaCobro_{dist_safe}_{datetime.now().strftime('%Y%m%d')}"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Cuenta de Cobro — {distribuidor_nombre}</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>

<style>
/* ══ Reset ══ */
*{{margin:0;padding:0;box-sizing:border-box}}
body{{
  background:#e8ecf0;
  font-family:'Segoe UI',Arial,sans-serif;
  padding:30px 20px 60px;
  display:flex;flex-direction:column;align-items:center;
  min-height:100vh;
}}

/* ══ Barra acciones ══ */
.action-bar{{
  width:760px;display:flex;gap:10px;margin-bottom:14px;
}}
.btn{{
  padding:11px 22px;border:none;border-radius:9px;
  font-size:13px;font-weight:700;cursor:pointer;
  font-family:inherit;transition:opacity .15s;
  display:flex;align-items:center;gap:6px;
}}
.btn:hover{{opacity:.87}}
.btn-pdf{{background:#1d4ed8;color:white;flex:1}}
.btn-close{{background:#475569;color:white}}

/* spinner */
.sp{{display:none;width:15px;height:15px;border:2px solid rgba(255,255,255,.3);
    border-top-color:white;border-radius:50%;animation:spin .7s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}

/* ══ Documento ══ */
.doc{{
  width:760px;background:white;
  box-shadow:0 6px 28px rgba(0,0,0,.14);
  border-radius:4px;overflow:hidden;
}}
/* Banda superior */
.doc::before{{
  content:'';display:block;height:6px;
  background:linear-gradient(90deg,#1d6fd8,#38bdf8,#1d6fd8);
}}

/* ══ Cabecera ══ */
.header{{
  background:#0b1d3a;
  padding:28px 36px 22px;
  display:flex;justify-content:space-between;align-items:center;
}}
.header-left{{}}
.logo-img{{max-height:70px;max-width:200px;object-fit:contain;border-radius:6px}}
.logo-text{{font-size:22px;font-weight:800;color:white;letter-spacing:1px}}
.header-right{{text-align:right}}
.doc-title{{
  font-size:22px;font-weight:800;color:white;
  letter-spacing:.5px;margin-bottom:4px;
}}
.doc-num{{
  display:inline-block;
  background:rgba(29,111,216,.35);color:#93c5fd;
  border:1px solid rgba(56,189,248,.4);
  border-radius:16px;padding:3px 14px;
  font-size:11px;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;
}}

/* ══ Info bloque ══ */
.info-band{{
  background:#f0f6ff;
  border-bottom:2px solid #dbeafe;
  padding:18px 36px;
  display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;
}}
.info-item{{}}
.info-label{{font-size:10px;font-weight:700;text-transform:uppercase;
            letter-spacing:1px;color:#6b8abf;margin-bottom:3px}}
.info-value{{font-size:14px;font-weight:700;color:#0b1d3a}}
.info-value.big{{font-size:16px;color:#1d4ed8}}

/* ══ Tabla ══ */
.body{{padding:24px 36px 28px}}
.section-label{{
  font-size:11px;font-weight:700;text-transform:uppercase;
  letter-spacing:1.5px;color:#1d6fd8;margin-bottom:10px;
}}

table.main{{width:100%;border-collapse:collapse;font-size:13px}}
table.main thead tr{{background:#0b1d3a}}
table.main thead th{{
  color:#93c5fd;font-weight:700;padding:10px 12px;
  font-size:11px;text-transform:uppercase;letter-spacing:.8px;
}}
table.main tbody tr{{border-bottom:1px solid #e5e7eb}}
table.main tbody tr:hover{{background:#eff6ff!important}}
table.main td{{padding:10px 12px;font-size:13px;color:#1e293b}}
.tc{{text-align:center}}
.tl{{text-align:left}}
.tr{{text-align:right}}

/* ══ Total ══ */
.total-band{{
  background:#0b1d3a;
  margin:0 36px 28px;
  border-radius:10px;
  padding:16px 24px;
  display:flex;justify-content:space-between;align-items:center;
}}
.total-label{{font-size:14px;font-weight:700;color:#93c5fd}}
.total-amount{{font-size:26px;font-weight:800;color:#ffffff}}
.total-count{{font-size:12px;color:#4b6280;margin-top:2px}}

/* ══ Footer ══ */
.footer{{
  background:#f8faff;
  border-top:2px dashed #dbeafe;
  padding:16px 36px;
  display:flex;justify-content:space-between;align-items:center;
}}
.footer-biz{{font-size:14px;font-weight:700;color:#0b1d3a}}
.footer-note{{font-size:11px;color:#6b7280;text-align:right;line-height:1.6}}

/* ══ PRINT ══ */
@media print{{
  @page{{size:A4;margin:10mm}}
  body{{background:white;padding:0;display:block}}
  .action-bar{{display:none!important}}
  .doc{{width:100%;box-shadow:none;border-radius:0}}
}}
</style>
</head>
<body>

<!-- Barra acciones -->
<div class="action-bar" id="actionBar">
  <button class="btn btn-pdf" onclick="guardarPDF(this)">
    <span class="btn-text">💾 Guardar / Imprimir como PDF</span>
    <div class="sp" id="spPDF"></div>
  </button>
  <button class="btn btn-close" onclick="window.close()">✕ Cerrar</button>
</div>

<!-- Documento -->
<div class="doc" id="doc">

  <!-- Cabecera -->
  <div class="header">
    <div class="header-left">{logo_html}</div>
    <div class="header-right">
      <div class="doc-title">Cuenta de Cobro</div>
      <div class="doc-num">CC-{num_cc}</div>
    </div>
  </div>

  <!-- Info -->
  <div class="info-band">
    <div class="info-item">
      <div class="info-label">Cobrar a (Distribuidor)</div>
      <div class="info-value big">{distribuidor_nombre}</div>
    </div>
    <div class="info-item">
      <div class="info-label">Período</div>
      <div class="info-value">{rango_str}</div>
    </div>
    <div class="info-item">
      <div class="info-label">Fecha de emisión</div>
      <div class="info-value">{fecha_emision}</div>
    </div>
  </div>

  <!-- Tabla -->
  <div class="body">
    <div class="section-label">📋 Detalle de cuentas pendientes</div>
    <table class="main">
      <thead>
        <tr>
          <th class="tc">#</th>
          <th class="tc">Factura</th>
          <th class="tl">Plataforma</th>
          <th class="tl">Cliente</th>
          <th class="tc">Perfil</th>
          <th class="tc">F. Activación</th>
          <th class="tc">F. Vencimiento</th>
          <th class="tr">Saldo</th>
        </tr>
      </thead>
      <tbody>
        {filas_html}
      </tbody>
    </table>
  </div>

  <!-- Total -->
  <div class="total-band">
    <div>
      <div class="total-label">TOTAL A COBRAR</div>
      <div class="total-count">{len(deudas)} cuenta(s) pendiente(s)</div>
    </div>
    <div class="total-amount">${total:,.0f}</div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <div class="footer-biz">{business_name}</div>
    <div class="footer-note">
      Este documento es una cuenta de cobro interna.<br>
      Los valores son confidenciales.
    </div>
  </div>

</div>

<script>
const FILE_NAME = "{file_name}";

async function guardarPDF(btn) {{
  const sp  = document.getElementById('spPDF');
  const txt = btn.querySelector('.btn-text');
  txt.textContent = 'Generando PDF...';
  sp.style.display = 'block';
  btn.disabled = true;

  document.getElementById('actionBar').style.display = 'none';
  await new Promise(r => setTimeout(r, 80));

  try {{
    const el  = document.getElementById('doc');
    const opt = {{
      margin:      [8, 8, 8, 8],
      filename:    FILE_NAME + '.pdf',
      image:       {{ type: 'jpeg', quality: 0.97 }},
      html2canvas: {{ scale: 2, useCORS: true, backgroundColor: '#ffffff' }},
      jsPDF:       {{ unit: 'mm', format: 'a4', orientation: 'portrait' }},
      pagebreak:   {{ mode: ['avoid-all', 'css'] }},
    }};
    await html2pdf().set(opt).from(el).save();
  }} catch(e) {{
    // Fallback: abrir diálogo de impresión
    window.print();
  }} finally {{
    document.getElementById('actionBar').style.display = 'flex';
    txt.textContent = '💾 Guardar / Imprimir como PDF';
    sp.style.display = 'none';
    btn.disabled = false;
  }}
}}
</script>
</body>
</html>"""

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False,
        encoding="utf-8",
        prefix=f"cuenta_cobro_{dist_safe}_"
    )
    tmp.write(html)
    tmp.close()
    webbrowser.open(f"file:///{tmp.name.replace(os.sep, '/')}")
    return tmp.name


def _fmt(d):
    """Format YYYY-MM-DD to DD/MM/YYYY."""
    if not d:
        return "—"
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return d
