"""
crear_icono_v3.py
-----------------
Crea el acceso directo en el Escritorio usando solo PowerShell.
No necesita pywin32 ni ninguna libreria extra.
"""
import os, sys, subprocess

HERE    = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
PYTHONW = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.exists(PYTHONW):
    PYTHONW = sys.executable

MAIN    = os.path.join(HERE, "main.py")
VBS     = os.path.join(HERE, "DanteStreaming.vbs")
LNK     = os.path.join(DESKTOP, "DanteStreaming.lnk")
ICO     = os.path.join(HERE, "icon.ico")

print()
print("=" * 50)
print("  DanteStreaming - Creador de icono")
print("=" * 50)

# ── 1. Verificar que el .vbs existe ──────────────
if not os.path.exists(VBS):
    print("\n  Creando DanteStreaming.vbs...")
    vbs_content = (
        'Dim objShell\r\n'
        'Dim strFolder\r\n'
        'Set objShell = CreateObject("WScript.Shell")\r\n'
        'strFolder = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\\"))\r\n'
        'objShell.CurrentDirectory = strFolder\r\n'
        'objShell.Run "pythonw.exe """ & strFolder & "main.py""", 0, False\r\n'
        'Set objShell = Nothing\r\n'
    )
    with open(VBS, "w", encoding="ascii") as f:
        f.write(vbs_content)
    print("  OK")

# ── 2. Buscar icon.ico ────────────────────────────
if os.path.exists(ICO):
    ico_line = f'$s.IconLocation = "{ICO}"'
    print(f"\n  Icono encontrado: icon.ico")
else:
    ico_line = ""
    print("\n  Sin icon.ico - se usara icono de Windows por defecto")
    print("  (Para poner tu logo, lee las instrucciones al final)")

# ── 3. Crear el .lnk con PowerShell ──────────────
print("\n  Creando acceso directo...")

ps_script = f"""
$ws = New-Object -ComObject WScript.Shell
$s  = $ws.CreateShortcut("{LNK}")
$s.TargetPath       = "{VBS}"
$s.WorkingDirectory = "{HERE}"
$s.Description      = "DanteStreaming Sistema de Ventas"
{ico_line}
$s.Save()
Write-Output "OK"
"""

result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
    capture_output=True, text=True
)

if "OK" in result.stdout and os.path.exists(LNK):
    print()
    print("=" * 50)
    print("  LISTO - Icono creado en el Escritorio")
    print("=" * 50)
    print()
    print("  Busca 'DanteStreaming' en tu Escritorio")
    print("  Doble clic = abre la app directamente")
    print()
    print("  Para poner TU PROPIO LOGO:")
    print("  1. Consigue tu imagen (PNG o JPG)")
    print("  2. Ve a: https://cloudconvert.com/png-to-ico")
    print("  3. Sube tu imagen y convierte a ICO")
    print("  4. Descarga el archivo y llámalo:  icon.ico")
    print("  5. Pega icon.ico en la carpeta StreamControl")
    print("  6. Vuelve a ejecutar:  python crear_icono_v3.py")
else:
    print("  Error:", result.stderr[:200] if result.stderr else "desconocido")
    print()
    print("  Creando lanzador alternativo en el Escritorio...")
    bat = os.path.join(DESKTOP, "DanteStreaming.bat")
    with open(bat, "w") as f:
        f.write(f'@echo off\ncd /d "{HERE}"\nstart "" "{PYTHONW}" "{MAIN}"\n')
    print(f"  Lanzador creado: DanteStreaming.bat")
    print("  Doble clic en ese archivo del Escritorio para abrir la app")

print()
input("  Presiona Enter para cerrar...")
