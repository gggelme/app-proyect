import subprocess
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import webbrowser
from PIL import Image, ImageTk
import sys
import requests
import socket

class IrupecApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Irupec API - Panel de Control")
        self.root.geometry("700x700")
        self.root.resizable(False, False)
        
        # --- Configuración de Colores Pastel ---
        self.color_bg = "#F0F8FF"
        self.color_primary = "#A2D2FF"
        self.color_secondary = "#BDE0FE"
        self.color_accent = "#2196F3"
        self.color_white = "#FFFFFF"
        self.color_text = "#333333"
        
        self.root.configure(bg=self.color_bg)
        
        # Variables de proceso
        self.api_process = None
        self.ngrok_process = None
        self.servicios_corriendo = False
        self.proyecto_root = os.path.dirname(os.path.abspath(__file__))
        self.back_dir = os.path.join(self.proyecto_root, "back")
        
        # CORREGIDO: La ruta correcta de ngrok.exe
        self.ngrok_exe = os.path.join(self.back_dir, "src", "ngrok.exe")
        
        # URL fija de ngrok (puedes cambiarla si es dinámica)
        self.ngrok_url = "https://galen-unfossilised-nonrespectably.ngrok-free.dev"
        
        # Configurar Estilos Modernos
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configuración de frames y etiquetas
        self.style.configure("TFrame", background=self.color_bg)
        self.style.configure("Card.TFrame", background=self.color_white, relief="flat")
        self.style.configure("TLabel", background=self.color_bg, foreground=self.color_text, font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", background=self.color_bg, foreground=self.color_accent, font=("Segoe UI", 18, "bold"))
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_ui()
        self.verificar_configuracion()

    def cargar_logo(self):
        """Carga y redimensiona el logo"""
        logo_path = os.path.join(self.proyecto_root, "icono_irupe.png")
        
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img = img.resize((70, 70), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                return self.logo_img
            except Exception as e:
                print(f"Error cargando logo: {e}")
                return None
        return None

    def setup_ui(self):
        # Contenedor Principal con margen
        main_container = tk.Frame(self.root, bg=self.color_bg)
        main_container.pack(fill="both", expand=True, padx=25, pady=20)

        # --- Header con Logo ---
        header_frame = tk.Frame(main_container, bg=self.color_bg)
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Cargar logo
        logo = self.cargar_logo()
        
        if logo:
            logo_label = tk.Label(header_frame, image=logo, bg=self.color_bg)
            logo_label.pack(pady=(0, 5))
        
        # Título principal
        tk.Label(header_frame, text="Academia Irupe", 
                 font=("Segoe UI", 22, "bold"), fg=self.color_accent, bg=self.color_bg).pack()
        
        # Subtítulo
        tk.Label(header_frame, text="PANEL DE CONTROL DE SERVICIOS", 
                 font=("Segoe UI", 9, "bold"), fg="#888888", bg=self.color_bg).pack()

        # --- Card de Estado ---
        card_estado = tk.Frame(main_container, bg=self.color_white, bd=0, highlightthickness=1, highlightbackground=self.color_secondary)
        card_estado.pack(fill="x", pady=5)
        
        inner_estado = tk.Frame(card_estado, bg=self.color_white, padx=15, pady=15)
        inner_estado.pack(fill="x")

        self.lbl_postgres = tk.Label(inner_estado, text="🐘 PostgreSQL: Verificando...", font=("Segoe UI", 10, "bold"), bg=self.color_white, fg="#555555")
        self.lbl_postgres.grid(row=0, column=0, sticky="w", pady=3)
        
        self.lbl_api = tk.Label(inner_estado, text="🔴 API: Detenida", font=("Segoe UI", 10, "bold"), bg=self.color_white, fg="#555555")
        self.lbl_api.grid(row=1, column=0, sticky="w", pady=3)
        
        self.lbl_ngrok = tk.Label(inner_estado, text="🔴 Ngrok: Detenido", font=("Segoe UI", 10, "bold"), bg=self.color_white, fg="#555555")
        self.lbl_ngrok.grid(row=2, column=0, sticky="w", pady=3)
        
        self.lbl_url = tk.Label(inner_estado, text="🌐 URL: No disponible", font=("Segoe UI", 9), fg="#999999", bg=self.color_white)
        self.lbl_url.grid(row=3, column=0, sticky="w", pady=(10, 0))

        # --- Botonera Principal ---
        frame_botones = tk.Frame(main_container, bg=self.color_bg)
        frame_botones.pack(fill="x", pady=20)

        button_config = {"font": ("Segoe UI", 10, "bold"), "relief": "flat", "cursor": "hand2", "pady": 8}

        self.btn_iniciar = tk.Button(frame_botones, text="▶ INICIAR TODO", command=self.iniciar_todo,
                                    bg="#BCF4DE", fg="#2D6A4F", **button_config)
        self.btn_iniciar.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_detener = tk.Button(frame_botones, text="⏹ DETENER TODO", command=self.detener_todo,
                                    bg="#FFD6D6", fg="#A4161A", state="disabled", **button_config)
        self.btn_detener.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_abrir = tk.Button(frame_botones, text="🌐 ABRIR APP", command=self.abrir_app,
                                  bg=self.color_primary, fg=self.color_white, state="disabled", **button_config)
        self.btn_abrir.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # --- Consola / Log ---
        tk.Label(main_container, text="Registro de Actividad", font=("Segoe UI", 9, "bold"), bg=self.color_bg, fg="#777777").pack(anchor="w")
        
        self.log_text = scrolledtext.ScrolledText(main_container, height=10, font=("Consolas", 9), 
                                                bg=self.color_white, fg="#444444", relief="flat", 
                                                highlightthickness=1, highlightbackground=self.color_secondary)
        self.log_text.pack(fill="both", expand=True, pady=(5, 10))

        # --- Botón secundario ---
        self.btn_minimizar = tk.Button(main_container, text="Minimizar a la bandeja", command=self.minimizar_bandeja,
                                       bg=self.color_bg, fg="#888888", font=("Segoe UI", 8), relief="flat", cursor="hand2")
        self.btn_minimizar.pack()

        # Barra de estado inferior
        self.status_bar = tk.Label(self.root, text=" ✅ Sistema listo", bd=0, relief="flat", 
                                  anchor="w", bg=self.color_secondary, fg="#333333", pady=3)
        self.status_bar.pack(side="bottom", fill="x")

    def log(self, mensaje):
        hora = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{hora}] {mensaje}\n")
        self.log_text.see("end")
        self.root.update()

    def minimizar_bandeja(self):
        self.root.iconify()
        self.log("📌 Aplicación minimizada.")
        messagebox.showinfo("Irupec", "Los servicios siguen corriendo en segundo plano.")

    def on_closing(self):
        if self.servicios_corriendo:
            respuesta = messagebox.askyesno("Cerrar Irupec", "¿Querés detener los servicios antes de salir?")
            if respuesta:
                self.detener_todo()
                self.root.destroy()
            else:
                self.root.destroy()
        else:
            self.root.destroy()

    def verificar_postgres(self):
        self.log("🔍 Verificando PostgreSQL...")
        servicios = [
            "postgresql-x64-18", "postgresql-18",
            "postgresql-x64-17", "postgresql-17",
            "postgresql-x64-16", "postgresql-16",
            "postgresql-x64-15", "postgresql-15",
            "postgresql-x64-14", "postgresql-14",
            "postgresql"
        ]
        for servicio in servicios:
            try:
                result = subprocess.run(f'sc query "{servicio}"', shell=True, capture_output=True, text=True)
                if "RUNNING" in result.stdout:
                    self.lbl_postgres.config(text="🐘 PostgreSQL: Corriendo", fg="#2D6A4F")
                    return True
                elif "STOPPED" in result.stdout:
                    subprocess.run(f'net start "{servicio}"', shell=True, capture_output=True)
                    time.sleep(3)
                    self.lbl_postgres.config(text="🐘 PostgreSQL: Corriendo", fg="#2D6A4F")
                    return True
            except: continue
        self.lbl_postgres.config(text="🐘 PostgreSQL: No encontrado", fg="#E67E22")
        return False

    def verificar_configuracion(self):
        if not os.path.exists(self.back_dir):
            messagebox.showerror("Error", f"No se encuentra: {self.back_dir}")
            return False
        
        # Verificar que ngrok.exe existe
        if not os.path.exists(self.ngrok_exe):
            self.log(f"⚠️ Advertencia: No se encuentra ngrok.exe en {self.ngrok_exe}")
            messagebox.showwarning("Advertencia", f"No se encuentra ngrok.exe en:\n{self.ngrok_exe}\n\nVerificá que esté en back/src/ngrok.exe")
        else:
            self.log(f"✅ Ngrok encontrado en: {self.ngrok_exe}")
        
        self.log(f"✅ Configuración OK")
        self.verificar_postgres()
        return True

    def verificar_puerto(self, puerto=8000):
        """Verifica si el puerto está en uso"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', puerto)) == 0

    def iniciar_todo(self):
        self.btn_iniciar.config(state="disabled", bg="#E0E0E0")
        self.status_bar.config(text=" 🟡 Iniciando servicios...", bg="#FFF3CD")
        thread = threading.Thread(target=self._iniciar_servicios)
        thread.daemon = True
        thread.start()

    def _iniciar_servicios(self):
        try:
            # Verificar PostgreSQL
            self.verificar_postgres()
            
            # ========== INICIAR API ==========
            self.log("🚀 Iniciando API...")
            self.root.after(0, lambda: self.lbl_api.config(text="🟡 API: Iniciando...", fg="#E67E22"))
            
            # CORREGIDO: Ruta correcta al main_api.py
            api_script = os.path.join(self.back_dir, "src", "api", "main_api.py")
            
            if not os.path.exists(api_script):
                self.log(f"❌ ERROR: No se encuentra {api_script}")
                self.root.after(0, lambda: self.lbl_api.config(text="🔴 API: Archivo no encontrado", fg="#A4161A"))
                return
            
            # CORREGIDO: Usar el Python del entorno virtual
            venv_python = os.path.join(self.back_dir, ".venv", "Scripts", "python.exe")
            
            if os.path.exists(venv_python):
                python_exe = venv_python
                self.log(f"✅ Usando Python del venv: {venv_python}")
            else:
                python_exe = "python"
                self.log(f"⚠️ Usando Python del sistema: python")
            
            # CORREGIDO: Ejecutar la API con ventana visible para ver errores
            self.api_process = subprocess.Popen(
                f'"{python_exe}" "{api_script}"',
                cwd=self.back_dir,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE  # Mostrar consola para ver errores
            )
            
            # Esperar que la API inicie
            self.log("⏳ Esperando a que la API inicie (10 segundos)...")
            time.sleep(10)
            
            # Verificar si la API responde
            if self.verificar_api():
                self.root.after(0, lambda: self.lbl_api.config(text="🟢 API: Corriendo", fg="#2D6A4F"))
                self.log("✅ API iniciada correctamente en http://localhost:8000")
            else:
                self.log("❌ API no responde en puerto 8000")
                self.log("💡 Verificá que el puerto 8000 no esté ocupado")
                self.root.after(0, lambda: self.lbl_api.config(text="🔴 API: Error - Puerto 8000", fg="#A4161A"))
            
            # ========== INICIAR NGROK ==========
            self.log("🚀 Iniciando ngrok...")
            self.root.after(0, lambda: self.lbl_ngrok.config(text="🟡 Ngrok: Iniciando...", fg="#E67E22"))
            
            # CORREGIDO: Usar ngrok.exe con ruta correcta
            ngrok_path = self.ngrok_exe
            
            # Si ngrok está en back/src, ajustá la ruta
            if not os.path.exists(ngrok_path):
                ngrok_path = os.path.join(self.back_dir, "src", "ngrok.exe")
            
            if os.path.exists(ngrok_path):
                self.log(f"✅ Usando ngrok: {ngrok_path}")
                
                # CORREGIDO: Comando ngrok sin --domain (que genere URL aleatoria)
                ngrok_cmd = f'"{ngrok_path}" http 8000'
                
                self.ngrok_process = subprocess.Popen(
                    ngrok_cmd,
                    cwd=self.proyecto_root,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE  # Mostrar consola para ver estado
                )
                
                # Esperar a que ngrok inicie
                time.sleep(5)
                
                # Obtener la URL generada
                ngrok_url = self.obtener_url_ngrok()
                
                if ngrok_url:
                    self.ngrok_url = ngrok_url
                    self.root.after(0, lambda: self.lbl_ngrok.config(text="🟢 Ngrok: Corriendo", fg="#2D6A4F"))
                    self.root.after(0, lambda: self.lbl_url.config(text=f"🌐 URL: {self.ngrok_url}", fg=self.color_accent))
                    self.log(f"✅ Ngrok iniciado: {self.ngrok_url}")
                else:
                    self.log("⚠️ Ngrok iniciado pero no se pudo obtener la URL")
                    self.root.after(0, lambda: self.lbl_ngrok.config(text="🟡 Ngrok: Iniciado (ver consola)", fg="#E67E22"))
            else:
                self.log(f"❌ No se encuentra ngrok.exe")
                self.log(f"🔍 Buscado en: {ngrok_path}")
                self.root.after(0, lambda: self.lbl_ngrok.config(text="🔴 Ngrok: No encontrado", fg="#A4161A"))
            
            self.servicios_corriendo = True
            self.root.after(0, lambda: self.btn_detener.config(state="normal", bg="#FFD6D6"))
            self.root.after(0, lambda: self.btn_abrir.config(state="normal", bg=self.color_primary))
            self.root.after(0, lambda: self.status_bar.config(text=" ✅ Servicios iniciados", bg="#D4EDDA"))
            
            self.log("✅ Proceso de inicio completado")
            
        except Exception as e:
            self.log(f"❌ ERROR: {e}")
            import traceback
            self.log(traceback.format_exc())
            self.root.after(0, lambda: self.btn_iniciar.config(state="normal", bg="#BCF4DE"))

    def detener_todo(self):
        try:
            self.log("🛑 Deteniendo servicios...")
            
            if self.api_process:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                self.log("✅ API detenida")
            
            if self.ngrok_process:
                self.ngrok_process.terminate()
                self.ngrok_process.wait(timeout=5)
                self.log("✅ Ngrok detenido")
            
            self.servicios_corriendo = False
            self.lbl_api.config(text="🔴 API: Detenida", fg="#555555")
            self.lbl_ngrok.config(text="🔴 Ngrok: Detenido", fg="#555555")
            self.lbl_url.config(text="🌐 URL: No disponible", fg="#999999")
            self.btn_iniciar.config(state="normal", bg="#BCF4DE")
            self.btn_detener.config(state="disabled", bg="#E0E0E0")
            self.btn_abrir.config(state="disabled", bg="#E0E0E0")
            self.status_bar.config(text=" ✅ Servicios detenidos", bg=self.color_secondary)
            
            self.log("✅ Todos los servicios detenidos correctamente")
            
        except Exception as e:
            self.log(f"❌ Error al detener: {e}")

    def abrir_app(self):
        """Abrir la aplicación en el navegador"""
        url = f"{self.ngrok_url}/docs"
        self.log(f"🌐 Abriendo: {url}")
        webbrowser.open(url)


    def verificar_api(self):
        """Verifica si la API está respondiendo"""
        try:
            import requests
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                return True
            else:
                self.log(f"⚠️ API respondió con código: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log("⚠️ API: No se pudo conectar - ¿está corriendo?")
            return False
        except Exception as e:
            self.log(f"⚠️ API: Error al verificar - {e}")
            return False

    def obtener_url_ngrok(self):
        """Obtiene la URL pública de ngrok desde la API local"""
        try:
            time.sleep(2)  # Esperar un poco más
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data["tunnels"]:
                    url = data["tunnels"][0]["public_url"]
                    self.log(f"📡 URL obtenida de ngrok: {url}")
                    return url
            return None
        except Exception as e:
            self.log(f"⚠️ No se pudo obtener URL de ngrok: {e}")
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = IrupecApp(root)
    root.mainloop()