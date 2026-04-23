"""
instalar_acceso_directo.py
==========================
Ejecuta este script UNA SOLA VEZ para:
  1. Instalar PyInstaller (si no está instalado)
  2. Crear StreamControl.exe en la carpeta del proyecto
  3. Crear un acceso directo en el Escritorio

Uso:
    python instalar_acceso_directo.py
"""

import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def paso(n, msg):
    print(f"\n{'='*55}")
    print(f"  PASO {n}: {msg}")
    print(f"{'='*55}")


def run(cmd):
    print(f"  > {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


# ── PASO 1: instalar PyInstaller ──────────────────────────────
paso(1, "Instalando PyInstaller...")
ok = run("pip install pyinstaller --quiet")
if not ok:
    print("  ⚠  Advertencia: PyInstaller ya estaba instalado o hubo un problema menor.")

# ── PASO 2: compilar el ejecutable ───────────────────────────
paso(2, "Compilando el ejecutable (esto puede tardar 1-3 minutos)...")

# Check if there's an icon
icon_arg = ""
for candidate in ["icon.ico", "icon.png", os.path.join("icons", "app.ico")]:
    if os.path.exists(os.path.join(HERE, candidate)):
        icon_arg = f'--icon="{os.path.join(HERE, candidate)}"'
        break

cmd_build = (
    f'pyinstaller --onefile --windowed --name "StreamControl" '
    f'--add-data "views;views" '
    f'{icon_arg} '
    f'--hidden-import customtkinter '
    f'--hidden-import PIL '
    f'--hidden-import PIL._imagingtk '
    f'--collect-all customtkinter '
    f'"main.py"'
)

os.chdir(HERE)
ok = run(cmd_build)

if not ok:
    print("\n  ❌ Error al compilar. Intentando método alternativo...")
    cmd_build2 = (
        'pyinstaller --onedir --windowed --name "StreamControl" '
        '--hidden-import customtkinter '
        '--collect-all customtkinter '
        '"main.py"'
    )
    ok = run(cmd_build2)

# ── PASO 3: Acceso directo en el Escritorio ──────────────────
paso(3, "Creando acceso directo en el Escritorio...")

desktop = os.path.join(os.path.expanduser("~"), "Desktop")

# Try with pywin32 (optional)
try:
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut_path = os.path.join(desktop, "StreamControl.lnk")
    shortcut = shell.CreateShortCut(shortcut_path)

    # Prefer .exe if it was built
    exe_path = os.path.join(HERE, "dist", "StreamControl.exe")
    if not os.path.exists(exe_path):
        exe_path = os.path.join(HERE, "dist", "StreamControl", "StreamControl.exe")

    if os.path.exists(exe_path):
        shortcut.Targetpath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.Description = "StreamControl — Sistema de Ventas"
    else:
        # Fallback: point to INICIAR.bat
        shortcut.Targetpath = os.path.join(HERE, "INICIAR.bat")
        shortcut.WorkingDirectory = HERE
        shortcut.Description = "StreamControl — Sistema de Ventas"

    shortcut.save()
    print(f"  ✅ Acceso directo creado en: {shortcut_path}")

except ImportError:
    # pywin32 not available — create .bat shortcut on desktop
    bat_path = os.path.join(desktop, "StreamControl.bat")

    exe_path = os.path.join(HERE, "dist", "StreamControl.exe")
    if not os.path.exists(exe_path):
        exe_path = os.path.join(HERE, "dist", "StreamControl", "StreamControl.exe")

    if os.path.exists(exe_path):
        content = f'@echo off\nstart "" "{exe_path}"\n'
    else:
        content = (
            f'@echo off\n'
            f'cd /d "{HERE}"\n'
            f'python main.py\n'
        )

    with open(bat_path, "w") as f:
        f.write(content)
    print(f"  ✅ Lanzador creado en el Escritorio: {bat_path}")
    print("  💡 Para que tenga icono bonito, instala pywin32:")
    print("     pip install pywin32")

# ── PASO 4: Crear lanzador BAT de respaldo ───────────────────
paso(4, "Creando lanzador de respaldo (INICIAR.bat)...")

bat_content = (
    "@echo off\n"
    "title StreamControl\n"
    f'cd /d "{HERE}"\n'
    "\n"
    ":: Intentar ejecutar el .exe compilado primero\n"
    f'if exist "{os.path.join(HERE, "dist", "StreamControl.exe")}" (\n'
    f'    start "" "{os.path.join(HERE, "dist", "StreamControl.exe")}"\n'
    "    exit\n"
    ")\n"
    "\n"
    ":: Si no hay exe, usar Python directamente\n"
    "python main.py\n"
    "\n"
    "if errorlevel 1 (\n"
    "    echo.\n"
    "    echo ERROR. Asegurate de tener Python instalado.\n"
    "    pause\n"
    ")\n"
)

with open(os.path.join(HERE, "INICIAR.bat"), "w") as f:
    f.write(bat_content)
print("  ✅ INICIAR.bat actualizado.")

# ── Resumen ──────────────────────────────────────────────────
print("\n")
print("╔══════════════════════════════════════════════════════╗")
print("║          ✅  INSTALACIÓN COMPLETADA                  ║")
print("╠══════════════════════════════════════════════════════╣")
print("║  Ahora puedes abrir StreamControl de 3 formas:       ║")
print("║                                                      ║")
print("║  1. 🖥️  Icono en el Escritorio (acceso directo)      ║")
print("║  2. 📄  Doble clic en INICIAR.bat                    ║")
print("║  3. 💻  CMD: python main.py                          ║")
print("╚══════════════════════════════════════════════════════╝")
print()
input("  Presiona Enter para cerrar...")
