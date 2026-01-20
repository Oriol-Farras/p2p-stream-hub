from concurrent.futures import ThreadPoolExecutor
import requests
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage, QPixmap

# Pool global para limitar descargas concurrentes
LOGO_DOWNLOAD_POOL = ThreadPoolExecutor(max_workers=8)

def download_logo_sync(url):
    """Descarga imagen en segundo plano (se ejecuta en thread pool)"""
    if not url: return None
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            img = QImage()
            img.loadFromData(r.content)
            if not img.isNull():
                pix = QPixmap.fromImage(img)
                # Escalar para el diseño F1 (35x35)
                # Nota: Devolvemos pixmap escalado para optimizar memoria
                return pix.scaled(35, 35, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    except: pass
    return None

class LogoWatcher(QThread):
    """Vigila la descarga (Future) y emite señal en el hilo principal cuando termina"""
    finished = pyqtSignal(object)
    
    def __init__(self, future, parent=None):
        super().__init__(parent)
        self.future = future
    
    def run(self):
        try:
            result = self.future.result()
            if result: 
                self.finished.emit(result)
        except Exception:
            pass
