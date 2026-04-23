"""
crear_icono_v2.py - Version simplificada sin pywin32
"""
import os, sys, subprocess

HERE    = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")

print()
print("  Creando acceso directo en el Escritorio...")
print()

# Buscar pythonw.exe (abre sin ventana negra)
pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
if not os.path.exists(pythonw):
    pythonw = sys.executable

main_py = os.path.join(HERE, "main.py")
vbs_path = os.path.join(HERE, "DanteStreaming.vbs")
shortcut = os.path.join(DESKTOP, "DanteStreaming.lnk")

# Crear el .vbs limpio
vbs = (
    'Set WshShell = CreateObject("WScript.Shell")\r\n'
    f'WshShell.CurrentDirectory = "{HERE}"\r\n'
    f'WshShell.Run """"""{pythonw}"""" """"{main_py}""""", 0, False\r\n'
    'Set WshShell = Nothing\r\n'
)
with open(vbs_path, "w") as f:
    f.write(vbs)

# Crear .lnk usando PowerShell (no necesita pywin32)
ico_path = os.path.join(HERE, "icon.ico")
ico_line = f'$s.IconLocation = "{ico_path}"' if os.path.exists(ico_path) else ""

ps = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut("{shortcut}")
$s.TargetPath = "{vbs_path}"
$s.WorkingDirectory = "{HERE}"
$s.Description = "DanteStreaming Sistema de Ventas"
{ico_line}
$s.Save()
"""

result = subprocess.run(
    ["powershell", "-Command", ps],
    capture_output=True, text=True
)

if result.returncode == 0 and os.path.exists(shortcut):
    print("  ✅ LISTO — Icono creado en el Escritorio")
    print()
    print("  Busca 'DanteStreaming' en tu Escritorio")
    print("  Doble clic = abre la app sin ventana negra")
else:
    print("  Error PowerShell:", result.stderr)
    # Plan B: crear .bat en el escritorio
    bat = os.path.join(DESKTOP, "DanteStreaming.bat")
    with open(bat, "w") as f:
        f.write(f'@echo off\ncd /d "{HERE}"\nstart "" "{pythonw}" "{main_py}"\n')
    print(f"  ✅ Lanzador creado: {bat}")
    print("  Doble clic en DanteStreaming.bat del Escritorio")

print()
input("  Presiona Enter para cerrar...")
