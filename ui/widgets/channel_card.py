from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor

# Imports relativos/absolutos según estructura. 
# Asumiendo ejecución desde root.
from utils.network import LOGO_DOWNLOAD_POOL, download_logo_sync, LogoWatcher

class ChannelWidget(QFrame):
    """
    Widget visual para cada canal.
    Muestra Logo, Título, Grupo y etiqueta LIVE.
    """
    def __init__(self, title, logo_url, stream_url, group, callback, parent=None):
        super().__init__(parent)
        self.stream_url = stream_url
        self.callback = callback
        self.title = title # Guardamos titulo para el buscador
        
        self.setProperty("class", "ChannelItem")
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(70) # Altura fija
        
        # Layout Horizontal: [Logo] [Textos]
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(12)

        # 1. IMAGEN DEL LOGO
        self.lbl_logo = QLabel()
        self.lbl_logo.setFixedSize(45, 45)
        self.lbl_logo.setStyleSheet("background-color: #15151E; border-radius: 6px; border: 1px solid #2A2A2A;")
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Cargar imagen asíncrona
        self.load_image_async(logo_url)
        
        # 2. COLUMNA DE TEXTO
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Fila superior: [TAG LIVE] [GRUPO]
        top_row = QHBoxLayout()
        top_row.setSpacing(6)
        
        lbl_live = QLabel("LIVE")
        lbl_live.setProperty("class", "LiveTag")
        
        lbl_group = QLabel(group if group else "GENERAL")
        lbl_group.setProperty("class", "ChannelGroup")
        
        top_row.addWidget(lbl_live)
        top_row.addWidget(lbl_group)
        top_row.addStretch()
        
        # Título
        lbl_title = QLabel(title)
        lbl_title.setProperty("class", "ChannelTitle")
        
        # Elide texto largo
        font_metrics = lbl_title.fontMetrics()
        elided_title = font_metrics.elidedText(title, Qt.TextElideMode.ElideRight, 180)
        lbl_title.setText(elided_title)

        text_layout.addLayout(top_row)
        text_layout.addWidget(lbl_title)
        
        layout.addWidget(self.lbl_logo)
        layout.addLayout(text_layout)

    def load_image_async(self, url):
        # Icono temporal
        self.lbl_logo.setText("TV")
        self.lbl_logo.setStyleSheet("color: #64748b; font-weight: bold; background-color: #15151E; border: 1px solid #2A2A2A; border-radius: 6px;")
        
        if not url: return

        # Enviar tarea al pool
        future = LOGO_DOWNLOAD_POOL.submit(download_logo_sync, url)
        self.logo_watcher = LogoWatcher(future, self) # Parent self para cleanup automático
        self.logo_watcher.finished.connect(self.on_logo_loaded)
        self.logo_watcher.start()

    def on_logo_loaded(self, pixmap):
        if pixmap:
            self.lbl_logo.clear()
            self.lbl_logo.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.callback(self.stream_url, self.title, self)

    def set_active(self, active):
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)
