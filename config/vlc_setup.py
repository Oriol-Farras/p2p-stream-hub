import sys
import os

def setup_vlc():
    """Configura las rutas de DLL para VLC en Windows"""
    if sys.platform == "win32":
        # Se asume que app.py (o main.py) está en la raíz del proyecto
        # y las DLLs podrían estar ahí mismo. Ajustamos según necesidad de búsqueda.
        # Si las DLL están en el root del proyecto:
        dll_path = os.getcwd() 
        if dll_path not in os.environ['PATH']:
             os.environ['PATH'] = dll_path + ";" + os.environ['PATH']
        
        if hasattr(os, 'add_dll_directory'):
            try: 
                os.add_dll_directory(dll_path)
            except: 
                pass
