import tkinter as tk
from tkinter import messagebox, filedialog
import yt_dlp
import os
from threading import Thread

class DownloaderApp:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Descargador de YouTube")
        self.ventana.geometry("500x450")

        # Etiqueta y campo para URL
        self.label_url = tk.Label(ventana, text="Ingresa la URL de YouTube:")
        self.label_url.pack(pady=5)
        self.entry_url = tk.Entry(ventana, width=60)
        self.entry_url.pack(pady=5)

        # Selección de carpeta
        self.label_ruta = tk.Label(ventana, text="Ruta de guardado: No seleccionada")
        self.label_ruta.pack(pady=5)
        self.boton_ruta = tk.Button(ventana, text="Elegir carpeta", command=self.elegir_ruta)
        self.boton_ruta.pack(pady=5)
        self.ruta_guardado = os.getcwd()  # Ruta por defecto

        # Opción de lista de reproducción
        self.lista_var = tk.BooleanVar()
        self.check_lista = tk.Checkbutton(ventana, text="Descargar lista completa", variable=self.lista_var)
        self.check_lista.pack(pady=5)

        # Selección de tipo (video o audio)
        self.label_tipo = tk.Label(ventana, text="Tipo de descarga:")
        self.label_tipo.pack(pady=5)
        self.tipo_var = tk.StringVar(value="video")
        self.opciones_tipo = tk.OptionMenu(ventana, self.tipo_var, "video", "audio", command=self.actualizar_calidad)
        self.opciones_tipo.pack(pady=5)

        # Selección de calidad/formato
        self.label_calidad = tk.Label(ventana, text="Calidad/Formato:")
        self.label_calidad.pack(pady=5)
        self.calidad_var = tk.StringVar(value="720p")
        self.opciones_calidad = tk.OptionMenu(ventana, self.calidad_var, "144p", "360p", "480p", "720p", "1080p", "1440p", "2160p")
        self.opciones_calidad.pack(pady=5)

        # Selección de formato de audio (inicialmente oculto)
        self.label_formato_audio = tk.Label(ventana, text="Formato de audio:")
        self.formato_audio_var = tk.StringVar(value="mp3")
        self.opciones_formato_audio = tk.OptionMenu(ventana, self.formato_audio_var, "mp3", "aac", "m4a", "wav")
        self.actualizar_calidad("video")  # Inicializar visibilidad

        # Barra de progreso
        self.label_progreso = tk.Label(ventana, text="Progreso: 0%")
        self.label_progreso.pack(pady=5)

        # Botón de descarga
        self.boton_descargar = tk.Button(ventana, text="Descargar", command=self.iniciar_descarga)
        self.boton_descargar.pack(pady=20)

    def elegir_ruta(self):
        ruta = filedialog.askdirectory()
        if ruta:
            self.ruta_guardado = ruta
            self.label_ruta.config(text=f"Ruta de guardado: {ruta}")

    def actualizar_calidad(self, tipo):
        # Mostrar u ocultar opciones según tipo (video o audio)
        if tipo == "video":
            self.label_calidad.pack(pady=5)
            self.opciones_calidad.pack(pady=5)
            self.label_formato_audio.pack_forget()
            self.opciones_formato_audio.pack_forget()
        else:  # audio
            self.label_calidad.pack_forget()
            self.opciones_calidad.pack_forget()
            self.label_formato_audio.pack(pady=5)
            self.opciones_formato_audio.pack(pady=5)

    def actualizar_progreso(self, d):
        if d['status'] == 'downloading':
            porcentaje = d.get('_percent_str', '0%').replace('%', '')
            self.label_progreso.config(text=f"Progreso: {porcentaje}%")
        elif d['status'] == 'finished':
            self.label_progreso.config(text="Progreso: 100% - ¡Descarga completada!")

    def descargar_video(self):
        url = self.entry_url.get()
        if not url:
            messagebox.showerror("Error", "Por favor, ingresa una URL.")
            return

        tipo = self.tipo_var.get()
        ydl_opts = {
            'outtmpl': os.path.join(self.ruta_guardado, '%(title)s.%(ext)s'),
            'progress_hooks': [self.actualizar_progreso],
        }

        if tipo == "video":
            calidad = self.calidad_var.get()
            # Mapear calidad a formato de yt-dlp
            formatos = {
                "144p": "bestvideo[height<=144]+bestaudio/best[height<=144]",
                "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
                "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
                "720p": "bestvideo[height<=720]+bestaudio/best[height<=720]",
                "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
                "1440p": "bestvideo[height<=1440]+bestaudio/best[height<=1440]",
                "2160p": "bestvideo[height<=2160]+bestaudio/best[height<=2160]"
            }
            ydl_opts['format'] = formatos.get(calidad, "bestvideo+bestaudio/best")
        else:  # audio
            formato_audio = self.formato_audio_var.get()
            ydl_opts['format'] = 'bestaudio'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': formato_audio,
                'preferredquality': '192',  # Calidad de audio en kbps
            }]

        # Si no se marca "Descargar lista completa", forzamos descarga de un solo video
        if not self.lista_var.get():
            ydl_opts['playlist_items'] = '1'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            messagebox.showinfo("Éxito", "¡Descarga finalizada!")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo descargar: {str(e)}")
        finally:
            self.label_progreso.config(text="Progreso: 0%")

    def iniciar_descarga(self):
        thread = Thread(target=self.descargar_video)
        thread.start()

# Crear ventana y ejecutar
ventana = tk.Tk()
app = DownloaderApp(ventana)
ventana.mainloop()