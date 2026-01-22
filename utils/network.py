from concurrent.futures import ThreadPoolExecutor
import requests
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, Qt
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

class LogoWatcher(QObject):
    """Vigila la descarga (Future) usando un Timer en lugar de bloquear un QThread"""
    finished = pyqtSignal(object)
    
    def __init__(self, future, parent=None):
        super().__init__(parent)
        self.future = future
        self.timer = QTimer(self)
        self.timer.setInterval(200) # Chequear cada 200ms
        self.timer.timeout.connect(self.check_status)
        self.timer.start()
    
    def check_status(self):
        if self.future.done():
            self.timer.stop()
            try:
                result = self.future.result()
                if result: 
                    self.finished.emit(result)
            except Exception:
                pass
            # Auto-eliminarse tras completar si no tiene padre o para limpiar
            if not self.parent():
                self.deleteLater()
