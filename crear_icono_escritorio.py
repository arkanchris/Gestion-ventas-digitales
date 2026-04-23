"""
crear_icono_escritorio.py
=========================
Ejecuta este script UNA SOLA VEZ desde CMD:

    cd C:\\ruta\\a\\StreamControl
    python crear_icono_escritorio.py

Crea un ícono bonito en tu Escritorio que:
  ✅ Abre la app sin ventana negra del CMD
  ✅ Siempre usa el código más reciente (nunca hay que recompilar)
  ✅ Tiene el ícono personalizado de tu negocio
"""

import os, sys, subprocess, urllib.request, shutil

HERE    = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")

print()
print("╔══════════════════════════════════════════════════╗")
print("║   DanteStreaming — Creador de ícono escritorio   ║")
print("╚══════════════════════════════════════════════════╝")

# ── PASO 1: instalar pywin32 ────────────────────────────────
print("\n[1/4] Verificando pywin32...")
try:
    import win32com.client
    print("      ✅ pywin32 listo.")
except ImportError:
    print("      Instalando pywin32 (solo esta vez)...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pywin32", "--quiet"],
        check=True)
    # post-install script
    scripts = os.path.join(os.path.dirname(sys.executable), "Scripts")
    psc = os.path.join(scripts, "pywin32_postinstall.py")
    if os.path.exists(psc):
        subprocess.run([sys.executable, psc, "-install"], capture_output=True)
    import win32com.client
    print("      ✅ pywin32 instalado.")

# ── PASO 2: crear / buscar ícono ────────────────────────────
print("\n[2/4] Preparando ícono...")

ico_path = os.path.join(HERE, "icon.ico")

# Intentar generar ícono desde el logo del negocio si existe
logo_candidates = [
    os.path.join(HERE, "logo.png"), os.path.join(HERE, "logo.jpg"),
    os.path.join(HERE, "logo.jpeg"),
]
logo_found = next((p for p in logo_candidates if os.path.exists(p)), None)

if os.path.exists(ico_path):
    print(f"      ✅ Usando ícono existente: icon.ico")

elif logo_found:
    print(f"      Convirtiendo logo a .ico...")
    try:
        from PIL import Image
        img = Image.open(logo_found).convert("RGBA")
        sizes = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
        img.save(ico_path, format="ICO", sizes=sizes)
        print(f"      ✅ ícono generado desde {os.path.basename(logo_found)}")
    except Exception as e:
        print(f"      ⚠  No se pudo convertir: {e}")
        ico_path = ""

else:
    # Descargar ícono genérico de streaming bonito desde internet
    print("      Descargando ícono por defecto...")
    try:
        # Ícono de play/streaming libre
        url = "https://www.iconarchive.com/download/i121328/papirus-team/papirus-apps/kodi.ico"
        urllib.request.urlretrieve(url, ico_path)
        print("      ✅ ícono descargado.")
    except:
        print("      ⚠  Sin ícono (se usará el de Python). Puedes agregar")
        print("         un archivo llamado  icon.ico  en la carpeta del proyecto")
        print("         y volver a ejecutar este script.")
        ico_path = ""

# ── PASO 3: copiar el lanzador .vbs ────────────────────────
print("\n[3/4] Instalando lanzador...")

vbs_src = os.path.join(HERE, "DanteStreaming.vbs")

# Crear el .vbs si no existe aún
vbs_content = (
    'Set WshShell = CreateObject("WScript.Shell")\r\n'
    'strPath = WScript.ScriptFullName\r\n'
    'strFolder = Left(strPath, InStrRev(strPath, "\\\\"))\r\n'
    'WshShell.CurrentDirectory = strFolder\r\n'
    'WshShell.Run "pythonw.exe " & Chr(34) & strFolder & "main.py" & Chr(34), 0, False\r\n'
    'Set WshShell = Nothing\r\n'
)
with open(vbs_src, "w", encoding="utf-8") as f:
    f.write(vbs_content)
print("      ✅ DanteStreaming.vbs listo.")

# ── PASO 4: crear acceso directo en Escritorio ─────────────
print("\n[4/4] Creando ícono en el Escritorio...")

shortcut_path = os.path.join(DESKTOP, "DanteStreaming.lnk")

shell    = win32com.client.Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(shortcut_path)
shortcut.TargetPath       = vbs_src
shortcut.WorkingDirectory = HERE
shortcut.Description      = "DanteStreaming — Sistema de Ventas"
if ico_path and os.path.exists(ico_path):
    shortcut.IconLocation = ico_path
shortcut.save()

print(f"      ✅ Ícono creado en el Escritorio.")

# ── Resumen ─────────────────────────────────────────────────
print()
print("╔══════════════════════════════════════════════════════╗")
print("║          ✅  TODO LISTO                              ║")
print("╠══════════════════════════════════════════════════════╣")
print("║                                                      ║")
print("║  Busca  'DanteStreaming'  en tu Escritorio.          ║")
print("║  Doble clic → abre la app, sin ventana negra.        ║")
print("║                                                      ║")
print("║  Cada vez que modifiques el código, el ícono         ║")
print("║  abre la versión más reciente AUTOMÁTICAMENTE.       ║")
print("║  No necesitas recompilar nada nunca más. ✅           ║")
print("║                                                      ║")
print("║  ── Cambiar el ícono ──────────────────────────────  ║")
print("║  1. Pon tu imagen como  icon.ico  en la carpeta      ║")
print("║  2. Vuelve a ejecutar:  python crear_icono...py      ║")
print("╚══════════════════════════════════════════════════════╝")
print()
input("  Presiona Enter para cerrar...")
