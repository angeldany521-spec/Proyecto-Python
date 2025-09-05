import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import time
import shutil
import os
import threading


"""
Este script organiza archivos en una carpeta destino basada en su tipo.
Permite seleccionar una carpeta origen y destino, y ofrece opciones de simulación
(dry-run) y recursividad.
"""


"""
funciones principales:
- scan_files: escanea los archivos en la carpeta origen (y subcarpetas si es recursivo)
esto para obtener una lista de archivos a organizar.
"""

def scan_files(origen, recursive):
    archivos = []
    origen = Path(origen)
    if recursive:
        for root, dirs, files in os.walk(origen):
            for file in files:
                archivos.append(Path(root) / file)
    else:
        archivos = [p for p in origen.iterdir() if p.is_file()]
    return archivos

"""
- organizar_archivos: mueve los archivos a las carpetas correspondientes en la carpeta destino
según las reglas definidas. Si dry_run es True, solo simula la acción sin mover archivos.
Adicionalmente, actualiza una barra de progreso y un label de estado en la GUI.
"""

def organizar_archivos(lista_archivos
                       , carpeta_destino, dry_run=False):
    
    total = len(lista_archivos)
    if total == 0:
        root.after(0, lambda: status_label.config(text="Nada que organizar"))
        return
    max_total_time = 5.0
    delay = max_total_time / total if total > 0 else 0
    delay = min(delay, 0.3)

    def procesar_archivo(i):
        if i > total:
            progress_var.set(100)
            status_label.config(text="¡Organización finalizada!")
            return
        archivo_path = lista_archivos[i-1]
        archivo = os.path.basename(archivo_path)
        destino = os.path.join(carpeta_destino, archivo)
        os.makedirs(carpeta_destino, exist_ok=True)
        if not dry_run:
            try:
                # Si el archivo ya existe en destino, renombrar para evitar sobrescribir
                destino_final = destino
                count = 1
                while os.path.exists(destino_final):
                    nombre, ext = os.path.splitext(archivo)
                    destino_final = os.path.join(carpeta_destino, f"{nombre}_{count}{ext}")
                    count += 1
                shutil.move(str(archivo_path), destino_final)
            except Exception as e:
                print(f"Error moviendo {archivo_path}: {e}")
        else:
            print(f"[SIMULADO] {archivo} → {destino}")
        progreso = int(i * 100 / total)
        progress_var.set(progreso)
        status_label.config(text=f"Procesando: {archivo} ({i}/{total})")
        if i < total:
            root.after(int(delay * 1000), lambda: procesar_archivo(i+1))
        else:
            root.after(0, lambda: status_label.config(text="¡Organización finalizada!"))
            progress_var.set(100)

    root.after(0, lambda: procesar_archivo(1))

"""
seleccionar_origen: abre un diálogo para seleccionar la carpeta origen
seleccionar_destino: abre un diálogo para seleccionar la carpeta destino
"""

def seleccionar_origen():
    path = filedialog.askdirectory()
    if path:
        origen_var.set(path)

def seleccionar_destino():
    path = filedialog.askdirectory()
    if path:
        destino_var.set(path)

"""
previsualizar: escanea y muestra los archivos encontrados en la lista de la GUI
iniciar_organizacion: inicia el proceso de organización de archivos al hacer clic en el botón
"Organizar Archivos que aparece en la GUI".
"""

def previsualizar():
    if not origen_var.get():
        messagebox.showwarning("Error", "Selecciona la carpeta origen")
        return
    archivos = scan_files(origen_var.get(), recursive_var.get())
    lista_archivos.delete(0, tk.END)
    for f in archivos:
        lista_archivos.insert(tk.END, f.name)
    messagebox.showinfo("Previsualización", f"Se encontraron {len(archivos)} archivos.")

def iniciar_organizacion():
    if not origen_var.get() or not destino_var.get():
        messagebox.showwarning("Error", "Debes seleccionar carpetas origen y destino")
        return
    archivos = scan_files(origen_var.get(), recursive_var.get())
    if not archivos:
        messagebox.showinfo("Info", "No se encontraron archivos para organizar")
        return
    progress_var.set(0)
    status_label.config(text="Iniciando organización...")
    root.update()


    def run_organizacion():
        organizar_archivos(archivos, destino_var.get(), dry_run_var.get())
        # Mostrar mensaje al finalizar desde el hilo principal
        root.after(int(min(5000, len(archivos)*350)), lambda: messagebox.showinfo("Listo", "¡Organización finalizada!"))

    threading.Thread(target=run_organizacion, daemon=True).start()






    
# --- GUI ---
root = tk.Tk()
root.title("Organizador de Archivos")
root.geometry("500x600")

origen_var = tk.StringVar()
destino_var = tk.StringVar()
dry_run_var = tk.BooleanVar(value=True)
recursive_var = tk.BooleanVar(value=True)
progress_var = tk.IntVar(value=0)

# Carpeta origen
tk.Label(root, text="Carpeta Origen:").pack(pady=5)
tk.Entry(root, textvariable=origen_var, width=50).pack()
tk.Button(root, text="Seleccionar", command=seleccionar_origen).pack(pady=2)

# Carpeta destino
tk.Label(root, text="Carpeta Destino:").pack(pady=5)
tk.Entry(root, textvariable=destino_var, width=50).pack()
tk.Button(root, text="Seleccionar", command=seleccionar_destino).pack(pady=2)

# Opciones
tk.Checkbutton(root, text="Simulación (Dry-run)", variable=dry_run_var).pack()
tk.Checkbutton(root, text="Incluir subcarpetas", variable=recursive_var).pack()

# Previsualización de archivos
tk.Label(root, text="Archivos encontrados:").pack(pady=5)
lista_archivos = tk.Listbox(root, width=60, height=10)
lista_archivos.pack()
tk.Button(root, text="Previsualizar archivos", command=previsualizar, bg="lightblue").pack(pady=5)

# Barra de progreso y status
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=5)
status_label = tk.Label(root, text="Esperando acción...")
status_label.pack()

# Botón de iniciar
tk.Button(root, text="Organizar Archivos", command=iniciar_organizacion, bg="lightgreen").pack(pady=15)

root.mainloop()
# --- Corrección de la lógica de organización de archivos ---

