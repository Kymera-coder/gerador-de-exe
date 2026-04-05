import os
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import subprocess
import shutil
import sys
import hashlib
import uuid
from datetime import datetime, timedelta

# ================= AUTO-INSTALL CUSTOMTKINTER =================
try:
    import customtkinter as ctk
except ImportError:
    print("Instalando CustomTkinter...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
    import customtkinter as ctk

# ================= CONFIGURAÇÃO VISUAL (TEMA COMPACTO) =================
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

# Cores
COLOR_BG = "#1a1a1a"
COLOR_CARD = "#2b2b2b"
COLOR_ACCENT = "#00E676"
COLOR_HOVER = "#00A856"
COLOR_TEXT = "#ffffff"
COLOR_LOG_BG = "#0f0f0f"

APP_NAME = "Compiler Pro Studio"
LIC_FILE = os.path.join(os.getenv("APPDATA"), "gerador_licenca.json")
TRIAL_DAYS = 7  # <--- ALTERADO PARA 7 DIAS

VALID_KEYS = [
    "4K7R9-X2WLP-Q8M1N-Z5BTY-V6C4D",
    "G9Z2X-L5P1R-W7N3M-Q8K4V-T6B9J",
    "B3V8N-M1Q9P-R7W2L-K5X4Z-T6C7Y",
    "W1R9L-K5Z2X-Q8N3M-P7V6B-T4Y1G",
    "P8M1N-Q7W2L-X5Z4K-V6C9B-T3Y2R",
    "X5Z2K-L9W1R-Q8N3M-P7V6B-T4Y1G",
    "M1N8Q-P7W2L-X5Z4K-V6C9B-T3Y2R"
]

# ================= LICENÇA =================
def get_hwid():
    return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()

def load_license():
    if os.path.exists(LIC_FILE):
        with open(LIC_FILE, "r") as f:
            return json.load(f)
    return None

def save_license(data):
    os.makedirs(os.path.dirname(LIC_FILE), exist_ok=True)
    with open(LIC_FILE, "w") as f:
        json.dump(data, f)

def init_license():
    lic = load_license()
    if lic: return lic
    lic = {"hwid": get_hwid(), "start": datetime.now().isoformat(), "activated": False}
    save_license(lic)
    return lic

def trial_days_left(lic):
    if lic["activated"]: return None
    start = datetime.fromisoformat(lic["start"])
    end = start + timedelta(days=TRIAL_DAYS)
    days_left = (end - datetime.now()).days
    return max(0, days_left)

def trial_valid(lic):
    if lic["activated"]: return True
    return trial_days_left(lic) > 0

# ================= APP PRINCIPAL =================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.files = []
        self.added_folders = []
        self.output_dir = ""
        self.exe_icon = None
        self.no_console = tk.BooleanVar()

        self.lic = init_license()
        self.title(APP_NAME)
        
        # === TAMANHO REDUZIDO ===
        self.geometry("780x600")
        self.configure(fg_color=COLOR_BG)

        if not trial_valid(self.lic):
            self.activate_pro(block=True)
        else:
            self.update_title()

        self.build_ui()

    def update_title(self):
        if self.lic["activated"]:
            self.title(f"{APP_NAME} | 💎 PRO ATIVADO")
        else:
            days = trial_days_left(self.lic)
            # AQUI ESTÁ A MUDANÇA NO TÍTULO
            self.title(f"{APP_NAME} | ⏳ FREE - {days} DIAS RESTANTES")

    def build_ui(self):
        # --- HEADER COMPACTO ---
        header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        ctk.CTkLabel(header, text="GERADOR DE EXECUTÁVEIS", font=("Segoe UI", 20, "bold"), text_color=COLOR_TEXT).pack(side="left")
        
        lic_text = "ATIVAR PRO" if not self.lic["activated"] else "PRO ATIVO"
        lic_color = "#E59400" if not self.lic["activated"] else COLOR_ACCENT
        ctk.CTkButton(header, text=lic_text, command=self.activate_pro, 
                      fg_color="transparent", border_width=1, border_color=lic_color, text_color=lic_color, 
                      width=80, height=25).pack(side="right")

        # --- CORPO (GRID) ---
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20)
        
        # COLUNA ESQUERDA
        left_col = ctk.CTkFrame(body, fg_color=COLOR_CARD, corner_radius=10)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Inputs
        ctk.CTkLabel(left_col, text="📂 PROJETO", font=("Segoe UI", 13, "bold"), text_color="#888").pack(anchor="w", padx=15, pady=(10, 5))
        
        self.btn_files = ctk.CTkButton(left_col, text="📄 Selecionar Scripts (.py)", command=self.select_files, 
                                       height=35, fg_color="#3a3a3a", hover_color="#4a4a4a", font=("Segoe UI", 12))
        self.btn_files.pack(fill="x", padx=15, pady=5)

        self.btn_folder = ctk.CTkButton(left_col, text="📁 Adicionar Pasta Extra", command=self.add_project_folder, 
                                        height=35, fg_color="#3a3a3a", hover_color="#4a4a4a", font=("Segoe UI", 12))
        self.btn_folder.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(left_col, text="⚙️ OPÇÕES", font=("Segoe UI", 13, "bold"), text_color="#888").pack(anchor="w", padx=15, pady=(15, 5))

        self.btn_dest = ctk.CTkButton(left_col, text="💾 Destino", command=self.select_dest, height=30, fg_color="#3a3a3a", hover_color="#4a4a4a")
        self.btn_dest.pack(fill="x", padx=15, pady=3)

        self.btn_icon_exe = ctk.CTkButton(left_col, text="📦 Ícone do EXE", command=self.select_exe_icon, height=30, fg_color="#3a3a3a", hover_color="#4a4a4a")
        self.btn_icon_exe.pack(fill="x", padx=15, pady=3)

        self.btn_icon_win = ctk.CTkButton(left_col, text="🖼️ Ícone da Janela", command=self.select_window_icon, height=30, fg_color="#3a3a3a", hover_color="#4a4a4a")
        self.btn_icon_win.pack(fill="x", padx=15, pady=3)

        ctk.CTkSwitch(left_col, text="Modo Janela (Sem Console)", variable=self.no_console, 
                      progress_color=COLOR_ACCENT, button_hover_color=COLOR_HOVER, font=("Segoe UI", 11)).pack(padx=15, pady=15, anchor="w")

        # COLUNA DIREITA
        right_col = ctk.CTkFrame(body, fg_color=COLOR_CARD, corner_radius=10)
        right_col.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(right_col, text="📟 LOG", font=("Segoe UI", 13, "bold"), text_color="#888").pack(anchor="w", padx=15, pady=(10, 5))

        self.log = ctk.CTkTextbox(right_col, fg_color=COLOR_LOG_BG, text_color="#00ff9c", font=("Consolas", 11), corner_radius=6)
        self.log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.progress = ctk.CTkProgressBar(right_col, height=8, progress_color=COLOR_ACCENT)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=10, pady=(0, 15))

        # --- FOOTER ---
        self.btn_build = ctk.CTkButton(self, text="🚀  INICIAR COMPILAÇÃO", command=self.start_build, 
                                       height=50, font=("Segoe UI", 16, "bold"), 
                                       fg_color=COLOR_ACCENT, hover_color=COLOR_HOVER, text_color="black", corner_radius=10)
        self.btn_build.pack(fill="x", padx=20, pady=15)

    # ================= FUNÇÕES =================
    def log_msg(self, txt):
        self.log.insert("end", txt + "\n")
        self.log.see("end")

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Python", "*.py")])
        if files:
            self.files = files
            self.btn_files.configure(text=f"📄 {len(files)} Scripts Selecionados", fg_color=COLOR_ACCENT, text_color="black")
            self.log_msg(f"📌 Arquivos carregados: {len(files)}")

    def add_project_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.added_folders.append(folder)
            self.log_msg(f"📂 Pasta incluída: {os.path.basename(folder)}")

    def select_dest(self):
        d = filedialog.askdirectory()
        if d:
            self.output_dir = d
            self.btn_dest.configure(text=f"💾 .../{os.path.basename(d)}")
            self.log_msg(f"📁 Destino: {d}")

    def select_exe_icon(self):
        f = filedialog.askopenfilename(filetypes=[("Icon", "*.ico")])
        if f:
            self.exe_icon = f
            self.log_msg(f"📦 Ícone EXE definido.")

    def select_window_icon(self):
        f = filedialog.askopenfilename(filetypes=[("Icon", "*.ico")])
        if f:
            try:
                self.wm_iconbitmap(f) 
                self.iconbitmap(f)
                self.log_msg(f"🖼️ Visual da Janela atualizado!")
            except Exception as e:
                self.log_msg(f"⚠️ Erro ao aplicar ícone: {e}")
                messagebox.showwarning("Aviso", "Use um arquivo .ico válido.")

    def activate_pro(self, block=False):
        key = simpledialog.askstring("Licença PRO", "Chave de ativação:")
        if not key:
            if block: self.destroy()
            return
        
        if key in VALID_KEYS:
            self.lic["activated"] = True
            save_license(self.lic)
            self.update_title()
            messagebox.showinfo("Sucesso", "PRO Ativado!")
            self.build_ui() # Atualiza visual (simples)
        else:
            messagebox.showerror("Erro", "Chave inválida.")

    def start_build(self):
        if not self.files or not self.output_dir:
            messagebox.showerror("Erro", "Selecione arquivos e destino.")
            return
        threading.Thread(target=self.run_pyinstaller).start()

    def run_pyinstaller(self):
        if shutil.which("pyinstaller") is None:
            self.log_msg("⚠️ Instalando PyInstaller...")
            subprocess.call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        self.btn_build.configure(state="disabled", text="AGUARDE...")
        self.progress.set(0)
        
        total = len(self.files)
        step = 1.0 / total if total > 0 else 1

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        for i, file_path in enumerate(self.files):
            name = os.path.basename(file_path)
            self.log_msg(f"\n--- COMPILANDO: {name} ---")
            
            cmd = ["pyinstaller", "--onefile", f"--distpath={self.output_dir}"]
            if self.no_console.get(): cmd.append("--noconsole")
            if self.exe_icon: cmd.append(f"--icon={self.exe_icon}")
            
            for folder in self.added_folders:
                fname = os.path.basename(folder)
                cmd.append(f"--add-data={folder};{fname}")
            
            cmd.append(file_path)

            try:
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                    text=True, startupinfo=startupinfo
                )

                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None: break
                    if line:
                        self.log.insert("end", line)
                        self.log.see("end")
                        curr = self.progress.get()
                        if curr < (i + 1) * step:
                            self.progress.set(curr + 0.002)
            except Exception as e:
                self.log_msg(f"❌ ERRO: {e}")

            self.progress.set((i + 1) * step)

        self.log_msg("\n✅ SUCESSO!")
        self.btn_build.configure(state="normal", text="🚀  INICIAR COMPILAÇÃO")
        messagebox.showinfo("Concluído", "Sucesso!")

if __name__ == "__main__":
    app = App()
    app.mainloop()