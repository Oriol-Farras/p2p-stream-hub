import os
import sys
import time
import subprocess
import requests
import winreg  # Solo para Windows

class AceStreamHandler:
    BASE_URL = "http://127.0.0.1:6878"

    @staticmethod
    def get_engine_path():
        """Intenta encontrar el ejecutable de AceStream en el registro de Windows."""
        try:
            # Buscamos en el registro de Windows la ruta de instalación
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\AceStream")
            install_dir, _ = winreg.QueryValueEx(key, "InstallDir")
            return os.path.join(install_dir, "engine", "ace_engine.exe")
        except Exception:
            # Ruta por defecto común
            return os.path.join(os.getenv('APPDATA'), 'AceStream', 'engine', 'ace_engine.exe')

    @classmethod
    def is_engine_running(cls):
        """Verifica si el motor responde al ping de la API."""
        try:
            # El endpoint /webui/api/service?method=get_version es muy rápido
            url = f"{cls.BASE_URL}/webui/api/service?method=get_version"
            response = requests.get(url, timeout=1)
            return response.status_code == 200
        except requests.ConnectionError:
            return False

    @classmethod
    def start_engine(cls):
        """Arranca el motor si no está corriendo."""
        if cls.is_engine_running():
            return True

        path = cls.get_engine_path()
        if os.path.exists(path):
            print(f"Iniciando AceStream desde: {path}")
            # subprocess.Popen inicia el programa en segundo plano sin bloquear Python
            # Añadimos --client-console para intentar evitar el cierre por inactividad
            subprocess.Popen([path, "--client-console"])
            return True
        else:
            print("No se encontró AceStream instalado.")
            return False

    @classmethod
    def convert_link(cls, stream_url):
        """
        Convierte 'acestream://ID' a 'http://127.0.0.1:6878/ace/getstream?id=ID'.
        Si ya es http, la devuelve tal cual.
        """
        if not stream_url:
            return ""

        # Si ya es un enlace normal (m3u8, mp4), lo devolvemos
        if stream_url.startswith("http"):
            return stream_url

        # Si es acestream
        if stream_url.startswith("acestream://"):
            content_id = stream_url.replace("acestream://", "")
        else:
            # Asumimos que es solo el ID si no tiene prefijo
            content_id = stream_url

        # Asegurar que el motor esté corriendo antes de devolver el link
        if not cls.is_engine_running():
            cls.start_engine()

        # Construir la URL mágica para VLC
        return f"{cls.BASE_URL}/ace/getstream?id={content_id}"
