import os
import shutil
import logging
import hashlib
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk

def configurar_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    log_handler = logging.StreamHandler(LogRedirector())
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(log_handler)

class LogRedirector:
    def write(self, text):
        gui_log_area.insert(tk.END, text)
        gui_log_area.see(tk.END)
    
    def flush(self):
        pass

def calcular_hash(arquivo):
    hash_sha256 = hashlib.sha256()
    try:
        with open(arquivo, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logging.error(f"Erro ao calcular hash do arquivo {arquivo}: {str(e)}")
        return None

def copiar_arquivos(pasta_origem, pasta_destino, total_files, extensao):
    copied, identical, errors = 0, 0, 0
    with ThreadPoolExecutor() as executor:
        for diretorio, subpastas, arquivos in os.walk(pasta_origem):
            for arquivo in arquivos:
                if arquivo.endswith(extensao):
                    caminho_origem = os.path.join(diretorio, arquivo)
                    caminho_destino = os.path.join(pasta_destino, arquivo)
                    caminho_destino = rename_if_exists(caminho_destino)
                    try:
                        shutil.copy(caminho_origem, caminho_destino)
                        logging.info(f"Arquivo {arquivo} copiado para {caminho_destino}.")
                        copied += 1
                    except Exception as e:
                        logging.error(f"Erro ao copiar o arquivo {arquivo}: {str(e)}")
                        errors += 1
                    progress_var.set((copied + identical + errors) / total_files * 100)
                    root.update_idletasks()
    update_statistics(copied, identical, errors)

def rename_if_exists(caminho_destino):
    base, ext = os.path.splitext(caminho_destino)
    counter = 1
    while os.path.exists(caminho_destino):
        caminho_destino = f"{base}_{counter}{ext}"
        counter += 1
    return caminho_destino

def update_statistics(copied, identical, errors):
    stats_label.config(text=f"Copied: {copied}, Identical: {identical}, Errors: {errors}")

def select_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_label.config(text=f"Selected Directory: {directory}")
        count_files(directory, file_extension_entry.get())

def count_files(path, extensao):
    count = 0
    for base, dirs, files in os.walk(path):
        count += sum(1 for _ in files if _.endswith(extensao))
    total_files.set(count)

def start_copy():
    if directory_label['text'] != "Selected Directory: " and file_extension_entry.get():
        source_path = directory_label['text'].split(": ")[1]
        extension = file_extension_entry.get()
        destination = os.path.join(source_path, f"arquivos {extension}")
        if not os.path.exists(destination):
            os.makedirs(destination)
        total = total_files.get()
        copiar_arquivos(source_path, destination, total, extension)
    else:
        messagebox.showerror("Error", "Please select a directory and specify a file extension.")

# Setup GUI
root = tk.Tk()
root.title("File Copier")

total_files = tk.DoubleVar()
progress_var = tk.DoubleVar()

directory_label = tk.Label(root, text="Selected Directory: ")
directory_label.pack()

select_button = tk.Button(root, text="Select Directory", command=select_directory)
select_button.pack()

file_extension_entry = tk.Entry(root)
file_extension_entry.pack()

start_button = tk.Button(root, text="Start Copying", command=start_copy)
start_button.pack()

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode='determinate', variable=progress_var)
progress_bar.pack()

gui_log_area = scrolledtext.ScrolledText(root, width=80, height=20)
gui_log_area.pack()

stats_label = tk.Label(root, text="Copied: 0, Identical: 0, Errors: 0")
stats_label.pack()

configurar_logging()

root.mainloop()
