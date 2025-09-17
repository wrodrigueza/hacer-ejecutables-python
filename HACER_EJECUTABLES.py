# autobuilder_exe_frozen_safe.py
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess, sys, shlex, importlib.util, shutil
from pathlib import Path

def has_module(mod: str) -> bool:
    try:
        return importlib.util.find_spec(mod) is not None
    except Exception:
        return False

def pick_file():
    r = tk.Tk(); r.withdraw(); r.attributes("-topmost", True); r.update()
    f = filedialog.askopenfilename(title="Selecciona el .py", filetypes=[("Python files","*.py")])
    r.destroy()
    return f

def pick_dir():
    r = tk.Tk(); r.withdraw(); r.attributes("-topmost", True); r.update()
    d = filedialog.askdirectory(title="Selecciona carpeta de salida")
    r.destroy()
    return d

def python_runner():
    """Devuelve el intérprete de Python correcto para ejecutar PyInstaller."""
    if getattr(sys, "frozen", False):
        # Estamos dentro de un .exe congelado → NO usar sys.executable
        for cand in ("py", "python", "python3"):
            p = shutil.which(cand)
            if p:
                return p
        messagebox.showerror("Python no encontrado",
                             "No encontré 'py' ni 'python' en PATH.\nAgrega Python al PATH o indica la ruta manualmente.")
        raise SystemExit(1)
    else:
        # Ejecutando como script .py normal
        return sys.executable

def ensure_pyinstaller(pyrun: str) -> None:
    """Instala PyInstaller con el intérprete elegido si no está disponible."""
    try:
        import PyInstaller  # noqa
        return
    except Exception:
        pass
    # Intentar instalar en el runner
    msg = f"No se encontró PyInstaller con {pyrun}. Instalando..."
    print("[!] " + msg)
    res = subprocess.run([pyrun, "-m", "pip", "install", "--upgrade", "pyinstaller"])
    if res.returncode != 0:
        messagebox.showerror("Error instalando PyInstaller",
                             "Falló la instalación de PyInstaller.\nRevisa tu conexión o permisos.")
        raise SystemExit(1)

def main():
    pyfile = pick_file()
    if not pyfile:
        print("⚠ No seleccionaste archivo.")
        return
    outdir = pick_dir()
    if not outdir:
        print("⚠ No seleccionaste carpeta de salida.")
        return
    Path(outdir).mkdir(parents=True, exist_ok=True)

    pyrun = python_runner()
    ensure_pyinstaller(pyrun)

    # Flags base; quita --noconsole si quieres ver la consola del app empaquetada
    cmd = [pyrun, "-m", "PyInstaller", "--clean", "--onefile", "--noconsole",
           "--distpath", outdir, "--specpath", outdir]

    # Extras seguros (solo si los módulos existen)
    if has_module("PIL"):
        cmd += ["--collect-all", "PIL"]
    if has_module("reportlab"):
        cmd += ["--collect-all", "reportlab"]
    if has_module("win32com"):
        cmd += ["--hidden-import", "win32com.client"]

    cmd.append(pyfile)

    print("\n▶ Ejecutando:", " ".join(shlex.quote(c) for c in cmd))
    ret = subprocess.call(cmd)
    if ret == 0:
        print(f"✅ Ejecutable generado en: {outdir}")
        messagebox.showinfo("OK", f"Ejecutable generado en:\n{outdir}")
    else:
        print("❌ PyInstaller terminó con errores.")
        messagebox.showerror("Error", "PyInstaller terminó con errores. Revisa la terminal/log.")

if __name__ == "__main__":
    main()
