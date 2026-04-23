import os
import webbrowser
import tempfile
import base64
from datetime import datetime


def _img_to_base64(path):
    if not path or not os.path.exists(path):
        return None
    ext  = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext or "png"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/{mime};base64,{b64}"


def generar_tirilla(venta, config):
    """
    Genera tirilla digital.
    - PDF: usa html2pdf.js → guarda archivo .pdf directo en el PC (sin diálogo de impresora).
    - PNG: usa html2canvas → guarda imagen .png directo en el PC.
    - La tirilla mantiene su formato estrecho y bonito en ambos casos.
    Orden: Correo → Contraseña → Perfil → PIN
    """
    business_name = config.get("business_name", "StreamControl")
    logo_path     = config.get("logo_path", "")
    num_factura   = venta.get("numero_factura", "0")
    fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── Imágenes ──
    logo_uri = _img_to_base64(logo_path)
    if logo_uri:
        header_logo_html = (
            f'<div class="biz-logo-wrap">'
            f'<img src="{logo_uri}" class="biz-logo" alt="{business_name}">'
            f'</div>')
    else:
        header_logo_html = f'<div class="biz-name-text">{business_name}</div>'

    plat_uri = _img_to_base64(venta.get("plataforma_imagen", ""))
    if plat_uri:
        plat_logo_html = f'<img src="{plat_uri}" class="plat-icon" alt="">'
    else:
        plat_logo_html = '<span class="plat-emoji">📺</span>'

    # ── Helpers ──
    def val(key):
        v = venta.get(key, "")
        return str(v).strip() if v and str(v).strip() else None

    def row(label, value):
        v = value if isinstance(value, str) else val(value)
        if not v:
            return ""
        return (f'<tr>'
                f'<td class="lbl">{label}</td>'
                f'<td class="val">{v}</td>'
                f'</tr>')

    def fmt_date(d):
        if not d:
            return None
        try:
            return datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
        except:
            return d

    notas   = val("notas")
    notas_h = (f'<div class="section-title">📝 Notas</div>'
               f'<div class="nota-box">{notas}</div>') if notas else ""

    sep = '<tr><td colspan="2"><div class="dashed"></div></td></tr>'

    # Nombre de archivo seguro
    cliente_safe = "".join(
        c for c in (venta.get("cliente") or "cliente") if c.isalnum() or c in " _-"
    ).strip().replace(" ", "_")
    file_name = f"Factura_{num_factura}_{cliente_safe}_{business_name.replace(' ','_')}"

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Factura #{num_factura} — {business_name}</title>

<!-- html2pdf: genera PDF real sin diálogo de impresora -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
<!-- html2canvas: para guardar PNG -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

<style>
/* ══════════════════════════════════
   BASE
══════════════════════════════════ */
*{{margin:0;padding:0;box-sizing:border-box}}
body{{
  background:#dde3ea;
  font-family:'Segoe UI',Arial,sans-serif;
  display:flex;
  flex-direction:column;
  align-items:center;
  padding:24px 16px 60px;
  min-height:100vh;
}}

/* ══════════════════════════════════
   BARRA DE ACCIONES
══════════════════════════════════ */
.action-bar{{
  width:360px;
  display:flex;
  gap:8px;
  margin-bottom:10px;
}}
.save-note{{
  width:360px;
  text-align:center;
  font-size:11px;
  color:#6b7280;
  margin-bottom:14px;
}}
.btn{{
  flex:1;
  padding:12px 6px;
  border:none;
  border-radius:10px;
  font-size:13px;
  font-weight:700;
  cursor:pointer;
  font-family:inherit;
  transition:opacity .15s, transform .1s;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:6px;
}}
.btn:hover{{opacity:.88; transform:translateY(-1px)}}
.btn:active{{transform:translateY(0)}}
.btn-pdf {{ background:#1d4ed8; color:white }}
.btn-png {{ background:#065f46; color:white }}
.btn-close{{
  flex:0 0 auto; width:42px; padding:12px 0;
  background:#374151; color:white; font-size:16px;
}}

/* spinner */
.spinner{{
  display:none;
  width:18px;height:18px;
  border:3px solid rgba(255,255,255,.3);
  border-top-color:white;
  border-radius:50%;
  animation:spin .7s linear infinite;
}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}

/* ══════════════════════════════════
   TIRILLA
══════════════════════════════════ */
.receipt{{
  width:360px;
  background:#fff;
  overflow:hidden;
  box-shadow:0 6px 28px rgba(0,0,0,.18);
}}
/* Banda de color superior */
.receipt::before{{
  content:'';display:block;height:5px;
  background:linear-gradient(90deg,#1d6fd8,#38bdf8,#22c55e,#38bdf8,#1d6fd8);
}}

/* Cabecera negocio */
.biz-header{{
  background:#0b1d3a;
  padding:18px 20px 14px;
  text-align:center;
  border-bottom:2px dashed #1e3256;
}}
.biz-logo-wrap{{display:flex;justify-content:center;margin-bottom:6px}}
.biz-logo{{max-height:66px;max-width:200px;object-fit:contain;border-radius:6px}}
.biz-name-text{{font-size:20px;font-weight:800;color:#fff;letter-spacing:1px;margin-bottom:4px}}
.factura-badge{{
  display:inline-block;
  background:rgba(29,111,216,.3);color:#93c5fd;
  border:1px solid rgba(56,189,248,.45);
  border-radius:20px;padding:3px 14px;
  font-size:11px;font-weight:700;letter-spacing:1.5px;
  text-transform:uppercase;margin-top:6px;
}}
.emision{{font-size:10px;color:#3d5470;margin-top:4px}}

/* Bloque plataforma */
.plat-block{{
  background:linear-gradient(135deg,#eff6ff,#e0f2fe);
  border-bottom:1px dashed #bfdbfe;
  padding:12px 18px;
  display:flex;align-items:center;gap:12px;
}}
.plat-icon{{
  width:50px;height:50px;object-fit:contain;
  border-radius:10px;flex-shrink:0;
  background:white;padding:3px;
  box-shadow:0 2px 6px rgba(0,0,0,.1);
}}
.plat-emoji{{font-size:36px;flex-shrink:0;line-height:1}}
.plat-label{{font-size:9px;font-weight:700;text-transform:uppercase;
             letter-spacing:1px;color:#6b8abf;margin-bottom:2px}}
.plat-name{{font-size:16px;font-weight:800;color:#0b1d3a;line-height:1.2}}

/* Cuerpo */
.body{{padding:2px 0 6px}}
.section-title{{
  font-size:10px;font-weight:700;text-transform:uppercase;
  letter-spacing:1.5px;color:#1d6fd8;
  padding:10px 18px 3px;
}}
table.dt{{width:100%;border-collapse:collapse}}
table.dt td{{padding:7px 18px;font-size:12.5px;vertical-align:top}}
table.dt .lbl{{color:#6b7280;font-weight:500;width:42%;white-space:nowrap}}
table.dt .val{{color:#111827;font-weight:600;word-break:break-all}}
table.dt tr:nth-child(even) td{{background:#f8faff}}
.dashed{{border-top:1px dashed #d1d5db;margin:3px 0}}

/* Fechas */
.dates-row{{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:6px 14px 10px}}
.date-card{{
  background:#f0f7ff;border:1px solid #bfdbfe;
  border-radius:8px;padding:8px 10px;text-align:center;
}}
.date-lbl{{font-size:9px;font-weight:700;text-transform:uppercase;
           letter-spacing:1px;color:#6b8abf;margin-bottom:3px}}
.date-val{{font-size:13px;font-weight:700;color:#0b1d3a}}

/* Notas */
.nota-box{{
  background:#fffbeb;border:1px dashed #fde68a;
  border-radius:6px;margin:3px 14px 8px;
  padding:8px 12px;font-size:12px;color:#92400e;line-height:1.5;
}}

/* Footer */
.receipt-footer{{
  background:#0b1d3a;
  padding:12px 18px;text-align:center;
  border-top:2px dashed #1e3256;
}}
.footer-biz{{font-size:14px;font-weight:700;color:#fff;margin-bottom:2px}}
.footer-sub{{font-size:11px;color:#3d5470}}

/* Borde de corte */
.cut-edge{{
  width:360px;height:14px;background:#dde3ea;
  position:relative;overflow:hidden;
}}
.cut-edge::before{{
  content:'';position:absolute;top:-10px;left:-8px;right:-8px;height:22px;
  background:radial-gradient(circle at 9px 0,#dde3ea 9px,transparent 9px);
  background-size:18px 100%;
}}
</style>
</head>
<body>

<!-- Barra de acciones -->
<div class="action-bar" id="actionBar">
  <button class="btn btn-pdf" onclick="guardarPDF(this)">
    <span class="btn-text">💾 Guardar PDF</span>
    <div class="spinner" id="spnPDF"></div>
  </button>
  <button class="btn btn-png" onclick="guardarPNG(this)">
    <span class="btn-text">🖼️ Guardar PNG</span>
    <div class="spinner" id="spnPNG"></div>
  </button>
  <button class="btn btn-close" onclick="window.close()">✕</button>
</div>
<div class="save-note" id="saveNote">
  Solo digital — elige cómo guardar para enviar al cliente
</div>

<!-- ══ TIRILLA ══ -->
<div class="receipt" id="receipt">

  <div class="biz-header">
    {header_logo_html}
    <div class="factura-badge">Factura #{num_factura}</div>
    <div class="emision">Emitida el {fecha_emision}</div>
  </div>

  <div class="plat-block">
    {plat_logo_html}
    <div>
      <div class="plat-label">Plataforma</div>
      <div class="plat-name">{venta.get('plataforma_nombre','—')}</div>
    </div>
  </div>

  <div class="body">

    <div class="section-title">👤 Cliente</div>
    <table class="dt">
      {row("Cliente",         val("cliente"))}
      {row("Orden de compra", val("orden_compra"))}
    </table>
    {sep}

    <div class="section-title">🔐 Datos de Acceso</div>
    <table class="dt">
      {row("Correo / Usuario", val("correo_usuario"))}
      {row("Contraseña",       val("contrasena"))}
      {row("Perfil",           val("perfil"))}
      {row("PIN",              val("pin"))}
    </table>
    {sep}

    <div class="section-title">📅 Vigencia</div>
    <div class="dates-row">
      <div class="date-card">
        <div class="date-lbl">Activación</div>
        <div class="date-val">{fmt_date(val("fecha_activacion")) or "—"}</div>
      </div>
      <div class="date-card">
        <div class="date-lbl">Vencimiento</div>
        <div class="date-val">{fmt_date(val("fecha_vencimiento")) or "—"}</div>
      </div>
    </div>

    {notas_h}

  </div>

  <div class="receipt-footer">
    <div class="footer-biz">{business_name}</div>
    <div class="footer-sub">¡Gracias por tu compra! 💙</div>
  </div>

</div>
<div class="cut-edge" id="cutEdge"></div>

<script>
const FILE_NAME = "{file_name}";

/* ══════════════════════════════════════
   GUARDAR PDF  (html2pdf — sin diálogo
   de impresora, descarga directa .pdf)
══════════════════════════════════════ */
async function guardarPDF(btn) {{
  const spn  = document.getElementById('spnPDF');
  const txt  = btn.querySelector('.btn-text');
  txt.textContent = 'Generando...';
  spn.style.display = 'block';
  btn.disabled = true;

  // Ocultar elementos de UI antes de capturar
  _hideUI(true);
  await _sleep(80);

  try {{
    const element = document.getElementById('receipt');
    const opt = {{
      margin:      0,
      filename:    FILE_NAME + '.pdf',
      image:       {{ type: 'jpeg', quality: 0.98 }},
      html2canvas: {{
        scale: 3,
        useCORS: true,
        backgroundColor: '#ffffff',
        logging: false,
      }},
      jsPDF: {{
        unit:        'px',
        format:      [360, element.offsetHeight + 20],
        orientation: 'portrait',
        hotfixes:    ['px_scaling'],
      }},
      pagebreak: {{ mode: 'avoid-all' }},
    }};
    await html2pdf().set(opt).from(element).save();
  }} catch(e) {{
    alert('Error al generar PDF: ' + e.message);
  }} finally {{
    _hideUI(false);
    txt.textContent = '💾 Guardar PDF';
    spn.style.display = 'none';
    btn.disabled = false;
  }}
}}

/* ══════════════════════════════════════
   GUARDAR PNG  (html2canvas — descarga
   directa .png, sin diálogos)
══════════════════════════════════════ */
async function guardarPNG(btn) {{
  const spn = document.getElementById('spnPNG');
  const txt = btn.querySelector('.btn-text');
  txt.textContent = 'Generando...';
  spn.style.display = 'block';
  btn.disabled = true;

  _hideUI(true);
  await _sleep(80);

  try {{
    const element = document.getElementById('receipt');
    const canvas  = await html2canvas(element, {{
      scale: 3, useCORS: true,
      backgroundColor: '#ffffff', logging: false,
    }});
    const link      = document.createElement('a');
    link.download   = FILE_NAME + '.png';
    link.href       = canvas.toDataURL('image/png');
    link.click();
  }} catch(e) {{
    alert('Error al generar PNG: ' + e.message);
  }} finally {{
    _hideUI(false);
    txt.textContent = '🖼️ Guardar PNG';
    spn.style.display = 'none';
    btn.disabled = false;
  }}
}}

/* Helpers */
function _hideUI(hide) {{
  const bar  = document.getElementById('actionBar');
  const note = document.getElementById('saveNote');
  const cut  = document.getElementById('cutEdge');
  const d    = hide ? 'none' : '';
  if(bar)  bar.style.display  = d;
  if(note) note.style.display = d;
  if(cut)  cut.style.display  = d;
}}

function _sleep(ms) {{
  return new Promise(r => setTimeout(r, ms));
}}
</script>
</body>
</html>"""

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False,
        encoding="utf-8",
        prefix=f"tirilla_{num_factura}_"
    )
    tmp.write(html)
    tmp.close()
    webbrowser.open(f"file:///{tmp.name.replace(os.sep, '/')}")
    return tmp.name
