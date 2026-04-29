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


def _fmt_date(d):
    if not d: return "—"
    try: return datetime.strptime(d, "%Y-%m-%d").strftime("%d/%m/%Y")
    except: return d


# ═══════════════════════════════════════════════════════════════
#  RECURSOS COMPARTIDOS
# ═══════════════════════════════════════════════════════════════
_LIBS = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
"""

_BASE_CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{background:#dde3ea;font-family:'Segoe UI',Arial,sans-serif;
     display:flex;flex-direction:column;align-items:center;
     padding:24px 16px 60px;min-height:100vh}
.action-bar{display:flex;gap:8px;margin-bottom:10px}
.save-note{text-align:center;font-size:11px;color:#6b7280;margin-bottom:14px}
.btn{padding:12px 16px;border:none;border-radius:10px;font-size:13px;
     font-weight:700;cursor:pointer;font-family:inherit;
     transition:opacity .15s;display:flex;align-items:center;gap:6px}
.btn:hover{opacity:.87}
.btn-pdf{background:#1d4ed8;color:white;flex:1}
.btn-png{background:#065f46;color:white;flex:1}
.btn-close{background:#374151;color:white;width:42px;justify-content:center}
.sp{display:none;width:15px;height:15px;border:2px solid rgba(255,255,255,.3);
    border-top-color:white;border-radius:50%;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.biz-header{background:#0b1d3a;padding:22px 20px 18px;text-align:center;border-bottom:2px dashed #1e3256}
.biz-logo-wrap{display:flex;justify-content:center;margin-bottom:6px}
.biz-logo{max-height:110px;max-width:260px;object-fit:contain;border-radius:8px}
.biz-name-text{font-size:20px;font-weight:800;color:#fff;letter-spacing:1px}
.factura-badge{display:inline-block;background:rgba(29,111,216,.3);color:#93c5fd;
    border:1px solid rgba(56,189,248,.45);border-radius:20px;padding:3px 14px;
    font-size:11px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-top:6px}
.emision{font-size:10px;color:#3d5470;margin-top:4px}
.section-title{font-size:10px;font-weight:700;text-transform:uppercase;
    letter-spacing:1.5px;color:#1d6fd8;padding:10px 18px 3px}
table.dt{width:100%;border-collapse:collapse}
table.dt td{padding:7px 18px;font-size:12.5px;vertical-align:top}
table.dt .lbl{color:#6b7280;font-weight:500;width:42%;white-space:nowrap}
table.dt .val{color:#111827;font-weight:600;word-break:break-all}
table.dt tr:nth-child(even) td{background:#f8faff}
.dashed{border-top:1px dashed #d1d5db;margin:3px 0}
.dates-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;padding:6px 14px 10px}
.date-card{background:#f0f7ff;border:1px solid #bfdbfe;border-radius:8px;padding:8px 10px;text-align:center}
.date-lbl{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#6b8abf;margin-bottom:3px}
.date-val{font-size:13px;font-weight:700;color:#0b1d3a}
.nota-box{background:#fffbeb;border:1px dashed #fde68a;border-radius:6px;
    margin:3px 14px 8px;padding:8px 12px;font-size:12px;color:#92400e;line-height:1.5}
.receipt-footer{background:#0b1d3a;padding:12px 18px;text-align:center;border-top:2px dashed #1e3256}
.footer-biz{font-size:14px;font-weight:700;color:#fff;margin-bottom:2px}
.footer-sub{font-size:11px;color:#3d5470}
.cut-edge{height:14px;background:#dde3ea;position:relative;overflow:hidden}
.cut-edge::before{content:'';position:absolute;top:-10px;left:-8px;right:-8px;height:22px;
    background:radial-gradient(circle at 9px 0,#dde3ea 9px,transparent 9px);background-size:18px 100%}
@media print{
  @page{size:80mm auto;margin:0}
  body{background:white;padding:0;display:block}
  .action-bar,.save-note{display:none!important}
  .cut-edge{display:none}
  .receipt{width:100%;box-shadow:none}}
"""

_SAVE_JS = """
async function guardarPDF(btn,fileName,elId){
  const sp=btn.querySelector('.sp'),txt=btn.querySelector('.btn-text');
  txt.textContent='Generando...';sp.style.display='block';btn.disabled=true;
  document.getElementById('actionBar').style.display='none';
  document.querySelector('.save-note').style.display='none';
  await new Promise(r=>setTimeout(r,80));
  try{
    const el=document.getElementById(elId);
    const h=el.offsetHeight;
    await html2pdf().set({
      margin:0,filename:fileName+'.pdf',
      image:{type:'jpeg',quality:.98},
      html2canvas:{scale:3,useCORS:true,backgroundColor:'#ffffff'},
      jsPDF:{unit:'px',format:[360,h+20],orientation:'portrait',hotfixes:['px_scaling']},
      pagebreak:{mode:'avoid-all'}
    }).from(el).save();
  }catch(e){window.print();}
  finally{
    document.getElementById('actionBar').style.display='flex';
    document.querySelector('.save-note').style.display='block';
    txt.textContent='💾 Guardar PDF';sp.style.display='none';btn.disabled=false;
  }
}
async function guardarPNG(btn,fileName,elId){
  const sp=btn.querySelector('.sp'),txt=btn.querySelector('.btn-text');
  txt.textContent='Generando...';sp.style.display='block';btn.disabled=true;
  document.getElementById('actionBar').style.display='none';
  document.querySelector('.save-note').style.display='none';
  await new Promise(r=>setTimeout(r,80));
  try{
    const canvas=await html2canvas(document.getElementById(elId),
      {scale:3,useCORS:true,backgroundColor:'#ffffff'});
    const a=document.createElement('a');
    a.download=fileName+'.png';a.href=canvas.toDataURL('image/png');a.click();
  }catch(e){alert('Usa Guardar PDF como alternativa.');}
  finally{
    document.getElementById('actionBar').style.display='flex';
    document.querySelector('.save-note').style.display='block';
    txt.textContent='🖼️ Guardar PNG';sp.style.display='none';btn.disabled=false;
  }
}
"""


def _action_bar(file_name, el_id):
    return f"""
<div class="action-bar" id="actionBar">
  <button class="btn btn-pdf" onclick="guardarPDF(this,'{file_name}','{el_id}')">
    <span class="btn-text">💾 Guardar PDF</span><div class="sp"></div></button>
  <button class="btn btn-png" onclick="guardarPNG(this,'{file_name}','{el_id}')">
    <span class="btn-text">🖼️ Guardar PNG</span><div class="sp"></div></button>
  <button class="btn btn-close" onclick="window.close()">✕</button>
</div>
<div class="save-note">Solo digital — elige cómo guardar para enviar al cliente</div>"""


def _logo_html(logo_path, business_name):
    uri = _img_to_b64(logo_path)
    if uri:
        return f'<div class="biz-logo-wrap"><img src="{uri}" class="biz-logo" alt="{business_name}"></div>'
    return f'<div class="biz-name-text">{business_name}</div>'


def _open_html(html, prefix):
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False,
        encoding="utf-8", prefix=prefix)
    tmp.write(html); tmp.close()
    webbrowser.open(f"file:///{tmp.name.replace(os.sep, '/')}")
    return tmp.name


def _safe(text):
    return "".join(c for c in str(text or "") if c.isalnum() or c in " _-"
                   ).strip().replace(" ", "_")


# ═══════════════════════════════════════════════════════════════
#  TIRILLA SIMPLE — una plataforma
# ═══════════════════════════════════════════════════════════════
def generar_tirilla(venta, config):
    """
    Genera tirilla para una sola plataforma.
    Muestra precio si NO hay distribuidor asignado.
    Oculta precio si tiene distribuidor asignado.
    """
    business_name = config.get("business_name", "StreamControl")
    logo_path     = config.get("logo_path", "")
    num_factura   = venta.get("numero_factura", "0")
    fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")

    # ¿Tiene distribuidor? → ocultar precio
    tiene_dist    = bool(venta.get("proveedor_id") or venta.get("proveedor_nombre"))

    logo_h = _logo_html(logo_path, business_name)

    plat_uri  = _img_to_b64(venta.get("plataforma_imagen", ""))
    plat_logo = (f'<img src="{plat_uri}" class="plat-icon" alt="">'
                 if plat_uri else '<span class="plat-emoji">📺</span>')

    def v(k): return str(venta.get(k, "") or "").strip() or None
    def row(label, value):
        val = value if isinstance(value, str) else v(value)
        if not val: return ""
        return f'<tr><td class="lbl">{label}</td><td class="val">{val}</td></tr>'

    sep   = '<tr><td colspan="2"><div class="dashed"></div></td></tr>'
    notas = v("notas")
    notas_h = (f'<div class="section-title">📝 Notas</div>'
               f'<div class="nota-box">{notas}</div>') if notas else ""

    # Precio: solo si NO hay distribuidor
    precio_row = "" if tiene_dist else row("Precio", f"${venta.get('precio_venta',0):,.0f}")

    file_name = f"Factura_{num_factura}_{_safe(venta.get('cliente','cliente'))}"

    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>Factura #{num_factura}</title>{_LIBS}
<style>{_BASE_CSS}
.receipt{{width:360px;background:#fff;overflow:hidden;box-shadow:0 6px 28px rgba(0,0,0,.18)}}
.receipt::before{{content:'';display:block;height:5px;
  background:linear-gradient(90deg,#1d6fd8,#38bdf8,#22c55e,#38bdf8,#1d6fd8)}}
.plat-block{{background:linear-gradient(135deg,#eff6ff,#e0f2fe);
  border-bottom:1px dashed #bfdbfe;padding:12px 18px;display:flex;align-items:center;gap:12px}}
.plat-icon{{width:50px;height:50px;object-fit:contain;border-radius:10px;flex-shrink:0;
  background:white;padding:3px;box-shadow:0 2px 6px rgba(0,0,0,.1)}}
.plat-emoji{{font-size:36px;flex-shrink:0;line-height:1}}
.plat-label{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#6b8abf;margin-bottom:2px}}
.plat-name{{font-size:16px;font-weight:800;color:#0b1d3a;line-height:1.2}}
.body{{padding:2px 0 6px}}
.action-bar{{width:360px}}.cut-edge{{width:360px}}
</style></head><body>
{_action_bar(file_name, "receipt")}
<div class="receipt" id="receipt">
  <div class="biz-header">{logo_h}
    <div class="factura-badge">Factura #{num_factura}</div>
    <div class="emision">Emitida el {fecha_emision}</div></div>
  <div class="plat-block">{plat_logo}
    <div><div class="plat-label">Plataforma</div>
    <div class="plat-name">{venta.get('plataforma_nombre','—')}</div></div></div>
  <div class="body">
    <div class="section-title">👤 Cliente</div>
    <table class="dt">
      {row("Cliente", v("cliente"))}
      {row("Orden de compra", v("orden_compra"))}
      {precio_row}
    </table>{sep}
    <div class="section-title">🔐 Datos de Acceso</div>
    <table class="dt">
      {row("Correo / Usuario", v("correo_usuario"))}
      {row("Contraseña", v("contrasena"))}
      {row("Perfil", v("perfil"))}
      {row("PIN", v("pin"))}
      
    </table>{sep}
    <div class="section-title">📅 Vigencia</div>
    <div class="dates-row">
      <div class="date-card"><div class="date-lbl">Activación</div>
        <div class="date-val">{_fmt_date(v("fecha_activacion"))}</div></div>
      <div class="date-card"><div class="date-lbl">Vencimiento</div>
        <div class="date-val">{_fmt_date(v("fecha_vencimiento"))}</div></div>
    </div>{notas_h}</div>
  <div class="receipt-footer">
    <div class="footer-biz">{business_name}</div>
    <div class="footer-sub">¡Gracias por tu compra! 💙</div></div>
</div>
<div class="cut-edge"></div>
<script>{_SAVE_JS}</script></body></html>"""

    return _open_html(html, f"tirilla_{num_factura}_")


# ═══════════════════════════════════════════════════════════════
#  TIRILLA MÚLTIPLE — varias plataformas, un cliente
# ═══════════════════════════════════════════════════════════════
def generar_tirilla_multiple(ventas, cliente, telefono, config,
                              notas_generales="", tiene_distribuidor=False,
                              orden_compra=""):
    """
    Genera tirilla para pedido con varias plataformas.
    tiene_distribuidor=True  → NO muestra precios ni total.
    tiene_distribuidor=False → SÍ muestra precio por plataforma y total.
    """
    if not ventas:
        return

    business_name = config.get("business_name", "StreamControl")
    logo_path     = config.get("logo_path", "")
    fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")
    logo_h        = _logo_html(logo_path, business_name)
    num_pedido    = ventas[0].get("numero_factura", "0")
    total         = sum(v.get("precio_venta", 0) for v in ventas)

    # Bloque de cada plataforma
    bloques = ""
    for i, venta in enumerate(ventas, 1):
        plat_uri  = _img_to_b64(venta.get("plataforma_imagen", ""))
        plat_logo = (f'<img src="{plat_uri}" class="plat-icon" alt="">'
                     if plat_uri else '<span class="plat-emoji">📺</span>')

        notas = str(venta.get("notas", "") or "").strip()
        notas_h = (f'<div class="nota-box" style="margin:3px 14px 6px">{notas}</div>'
                   if notas else "")

        def v(k): return str(venta.get(k, "") or "").strip() or None
        def row(label, value):
            val = value if isinstance(value, str) else v(value)
            if not val: return ""
            return f'<tr><td class="lbl">{label}</td><td class="val">{val}</td></tr>'

        # Precio por plataforma: solo si NO hay distribuidor
        if not tiene_distribuidor:
            precio_plat = f'<div class="plat-precio">Precio: <strong>${venta.get("precio_venta",0):,.0f}</strong></div>'
        else:
            precio_plat = ""

        bloques += f"""
        <div class="plat-section">
          <div class="plat-num">Plataforma {i} de {len(ventas)}</div>
          <div class="plat-block">
            {plat_logo}
            <div>
              <div class="plat-label">Plataforma</div>
              <div class="plat-name">{venta.get('plataforma_nombre','—')}</div>
              <div class="plat-factura">Factura #{venta.get('numero_factura','—')}</div>
            </div>
          </div>
          <div class="body">
            <div class="section-title">🔐 Datos de Acceso</div>
            <table class="dt">
              {row("Correo / Usuario", v("correo_usuario"))}
              {row("Contraseña",       v("contrasena"))}
              {row("Perfil",           v("perfil"))}
              {row("PIN",              v("pin"))}
              
            </table>
            <div class="section-title" style="padding-top:6px">📅 Vigencia</div>
            <div class="dates-row">
              <div class="date-card">
                <div class="date-lbl">Activación</div>
                <div class="date-val">{_fmt_date(v("fecha_activacion"))}</div>
              </div>
              <div class="date-card">
                <div class="date-lbl">Vencimiento</div>
                <div class="date-val">{_fmt_date(v("fecha_vencimiento"))}</div>
              </div>
            </div>
            {notas_h}
          </div>
          {precio_plat}
        </div>
        {'<div class="sep-plat"></div>' if i < len(ventas) else ''}"""

    notas_g_h = (f'<div class="section-title">📝 Notas</div>'
                 f'<div class="nota-box">{notas_generales}</div>'
                 if notas_generales else "")

    # Total: solo si NO hay distribuidor
    if not tiene_distribuidor:
        total_band = f"""
        <div class="total-band">
          <div>
            <div class="total-label">TOTAL DEL PEDIDO</div>
            <div class="total-qty">{len(ventas)} plataforma(s)</div>
          </div>
          <div class="total-amount">${total:,.0f}</div>
        </div>"""
    else:
        total_band = f"""
        <div class="total-band" style="justify-content:center">
          <div class="total-label">{len(ventas)} plataforma(s) — Pedido #{num_pedido}</div>
        </div>"""

    file_name = f"Pedido_{num_pedido}_{_safe(cliente)}"

    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>Pedido #{num_pedido} — {cliente}</title>{_LIBS}
<style>{_BASE_CSS}
.receipt{{width:360px;background:#fff;overflow:hidden;box-shadow:0 6px 28px rgba(0,0,0,.18)}}
.receipt::before{{content:'';display:block;height:5px;
  background:linear-gradient(90deg,#1d6fd8,#38bdf8,#22c55e,#f59e0b,#1d6fd8)}}
.cliente-block{{background:#f0f7ff;border-bottom:1px dashed #bfdbfe;padding:12px 18px}}
.cli-label{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#6b8abf;margin-bottom:3px}}
.cli-name{{font-size:17px;font-weight:800;color:#0b1d3a}}
.cli-orden{{font-size:12px;color:#1d6fd8;margin-top:3px;font-weight:600}}
.plat-section{{}}
.plat-num{{font-size:9px;font-weight:700;text-transform:uppercase;
  letter-spacing:1px;color:#f59e0b;padding:8px 18px 2px;background:#fffbeb}}
.plat-block{{background:linear-gradient(135deg,#eff6ff,#e0f2fe);
  border-bottom:1px dashed #bfdbfe;padding:10px 18px;display:flex;align-items:center;gap:12px}}
.plat-icon{{width:44px;height:44px;object-fit:contain;border-radius:8px;
  flex-shrink:0;background:white;padding:2px;box-shadow:0 2px 6px rgba(0,0,0,.1)}}
.plat-emoji{{font-size:32px;flex-shrink:0;line-height:1}}
.plat-label{{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:1px;color:#6b8abf;margin-bottom:1px}}
.plat-name{{font-size:15px;font-weight:800;color:#0b1d3a;line-height:1.2}}
.plat-factura{{font-size:10px;color:#6b8abf;margin-top:2px}}
.body{{padding:2px 0 4px}}
.plat-precio{{text-align:right;padding:4px 18px 8px;font-size:13px;color:#1d6fd8}}
.sep-plat{{border-top:3px dashed #dbeafe;margin:0}}
.total-band{{background:#0b1d3a;padding:14px 20px;
  display:flex;justify-content:space-between;align-items:center}}
.total-label{{font-size:12px;font-weight:700;color:#93c5fd}}
.total-qty{{font-size:11px;color:#4b6280;margin-top:2px}}
.total-amount{{font-size:22px;font-weight:800;color:#ffffff}}
.action-bar{{width:360px}}.cut-edge{{width:360px}}
</style></head><body>
{_action_bar(file_name, "receipt")}
<div class="receipt" id="receipt">
  <div class="biz-header">{logo_h}
    <div class="factura-badge">Pedido #{num_pedido}</div>
    <div class="emision">Emitido el {fecha_emision}</div></div>
  <div class="cliente-block">
    <div class="cli-label">👤 Cliente</div>
    <div class="cli-name">{cliente}</div>
    {'<div class="cli-orden">Orden de compra: <strong>' + str(orden_compra) + '</strong></div>' if orden_compra else ''}
  </div>
  {bloques}
  {notas_g_h}
  {total_band}
  <div class="receipt-footer">
    <div class="footer-biz">{business_name}</div>
    <div class="footer-sub">¡Gracias por tu compra! 💙</div></div>
</div>
<div class="cut-edge"></div>
<script>{_SAVE_JS}</script></body></html>"""

    return _open_html(html, f"pedido_{num_pedido}_")
