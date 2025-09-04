import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import shutil
import os

"""
Este script organiza archivos en una carpeta destino basada en su tipo.
Permite seleccionar una carpeta origen y destino, y ofrece opciones de simulación
(dry-run) y recursividad.
"""
# Reglas simples: extensión → carpeta
RULES = {
    "jpg": "Fotos",
    "jpeg": "Fotos",
    "png": "Fotos",
    "gif": "Fotos",
    "pdf": "Documentos",
    "docx": "Documentos",
    "txt": "Textos",
    "mp3": "Música",
    "wav": "Música",
    "mp4": "Videos",
    "mkv": "Videos",
    "zip": "Comprimidos",
    "rar": "Comprimidos",
}

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

def organizar_archivos(carpeta_origen, carpeta_destino, dry_run=False):
    extensiones = {
        "Documentos": [".pdf", ".docx", ".txt"],
        "Fotos": [".jpg", ".jpeg", ".png"],
        "Videos": [".mp4", ".avi"],
        "Música": [".mp3", ".wav"],
        "Comprimidos": [".zip", ".rar"],
    } 

    for archivo in os.listdir(carpeta_origen):
        ruta_archivo = os.path.join(carpeta_origen, archivo) 

#Ese bloque de abajo (if os.path.isfile(ruta_archivo)) revisa si algo es un archivo, obtiene su 
#extensión y la normaliza en minúscula para que sea 
# más fácil clasificarlo.

        if os.path.isfile(ruta_archivo):
            _, extension = os.path.splitext(archivo) 
            extension = extension.lower() 

            # Buscar a qué categoría pertenece
            carpeta_categoria = "Otros"
            for categoria, lista_ext in extensiones.items():
                if extension in lista_ext:
                    carpeta_categoria = categoria
                    break

            # Crear la carpeta destino si no existe
            destino = os.path.join(carpeta_destino, carpeta_categoria)
            os.makedirs(destino, exist_ok=True)

            # Mover o simular
            if not dry_run:
                shutil.move(ruta_archivo, os.path.join(destino, archivo))
            else:
                print(f"[SIMULADO] {archivo} → {destino}")

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
    organizar_archivos(archivos, destino_var.get(), dry_run_var.get(), progress_var, status_label)
    messagebox.showinfo("Listo", "¡Organización finalizada!")

# --- GUI ---
root = tk.Tk()
root.title("Organizador de Archivos")
root.geometry("500x500")

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
