import sys
import os
import re
import vlc

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QSlider, QFrame, QLabel, QLineEdit, 
                             QScrollArea, QSizePolicy, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QCursor, QIcon

from config.styles import STYLESHEET
from ui.widgets.channel_card import ChannelWidget
from utils.acestream_handler import AceStreamHandler



class MiniPlayerWindow(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.setWindowTitle("Mini Player")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.resize(480, 270)
        # Ventana siempre visible y sin marco (opcional, aquí con marco para poder moverla fácil)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: black;")

    def closeEvent(self, event):
        # Al cerrar la ventana, devolvemos el video a la app principal
        self.parent_app.stop_mini_mode()
        event.accept()

class F1TVApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IPTV HUB - Stream Player")
        self.resize(1280, 800)
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setStyleSheet(STYLESHEET)
        
        # VLC Instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        
        self.channel_widgets = []
        self.mini_window = None # Referencia al mini player
        
        self.init_ui()
        
        # Timer para Slider
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_progress)
        self.is_paused_by_slider = False
        
        # Cargar Listas M3U (Ahora busca todas las disponibles)
        QTimer.singleShot(100, self.load_playlists_list)
        
        # Pre-calentar motor AceStream al inicio (sin bloquear)
        AceStreamHandler.start_engine()
        
        # Timer para esperar al motor
        self.wait_timer = QTimer(self)
        self.wait_timer.setInterval(1000) # Checar cada 1s
        self.wait_timer.timeout.connect(self.check_engine_ready)
        self.wait_attempts = 0
        self.pending_play_args = None

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === SIDEBAR IZQUIERDA ===
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(300)
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(20, 20, 20, 20)
        side_layout.setSpacing(15)

        # Header Sidebar
        header_box = QHBoxLayout()
        icon_f1 = QLabel("TV") 
        icon_f1.setStyleSheet("background-color: #E10600; color: white; padding: 2px 6px; font-weight: 900; border-radius: 4px;")
        lbl_logo = QLabel("STREAM HUB")
        lbl_logo.setObjectName("LogoText")
        header_box.addWidget(icon_f1)
        header_box.addWidget(lbl_logo)
        header_box.addStretch()
        side_layout.addLayout(header_box)

        # Playlist Selector
        self.playlist_combo = QComboBox()
        self.playlist_combo.setPlaceholderText("Select Playlist")
        self.playlist_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.playlist_combo.currentIndexChanged.connect(self.on_playlist_changed)
        side_layout.addWidget(self.playlist_combo)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search channel...")
        self.search_input.textChanged.connect(self.filter_channels)
        side_layout.addWidget(self.search_input)

        # Lista Scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.scroll_content)
        side_layout.addWidget(scroll)
        
        # Botón Settings
        btn_settings = QPushButton("App Settings")
        btn_settings.setStyleSheet("background: #1e1e24; color: #94a3b8; padding: 10px; border-radius: 6px; font-weight: bold; border: 1px solid #2A2A2A;")
        side_layout.addWidget(btn_settings)

        main_layout.addWidget(self.sidebar)

        # === ZONA DERECHA (VIDEO + OVERLAY) ===
        right_area = QWidget()
        self.right_layout = QVBoxLayout(right_area) # Hacer self para poder reinsertar el video
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        # 1. Header Overlay
        self.header_vid = QFrame()
        self.header_vid.setStyleSheet("background-color: #000;")
        self.header_vid.setFixedHeight(50)
        head_layout = QHBoxLayout(self.header_vid)
        
        lbl_dot = QLabel("● LIVE")
        lbl_dot.setStyleSheet("color: #E10600; font-weight: 900; margin-right: 10px;")
        self.lbl_now_playing = QLabel("SELECT A CHANNEL")
        self.lbl_now_playing.setStyleSheet("color: white; font-style: italic; font-weight: 800; font-size: 14px;")
        
        head_layout.addWidget(lbl_dot)
        head_layout.addWidget(self.lbl_now_playing)
        head_layout.addStretch()
        
        # 2. Video Frame
        self.video_frame = QFrame()
        self.video_frame.setObjectName("VideoArea")
        self.video_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # 3. Controles
        self.controls = QFrame()
        self.controls.setObjectName("ControlsBar")
        self.controls.setFixedHeight(80)
        ctrl_layout = QHBoxLayout(self.controls)
        ctrl_layout.setContentsMargins(20, 10, 20, 10)
        
        self.btn_play = QPushButton(" ▶ ")
        self.btn_play.setObjectName("PlayBig")
        self.btn_play.setFixedSize(40, 40)
        self.btn_play.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_play.clicked.connect(self.toggle_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.slider.setMaximum(1000)
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.sliderPressed.connect(self.slider_pressed)
        self.slider.sliderReleased.connect(self.slider_released)

        btn_vol = QPushButton("VOL")
        btn_vol.setProperty("class", "ControlBtn")

        # Botón Mini Player
        self.btn_mini = QPushButton(" ❐ ") 
        self.btn_mini.setFixedSize(40, 40)
        self.btn_mini.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_mini.setStyleSheet("color: white; font-size: 16px; background: transparent; border: none;")
        self.btn_mini.setToolTip("Mini Player (Siempre visible)")
        self.btn_mini.clicked.connect(self.toggle_mini_player)

        # Botón Pantalla Completa
        self.btn_fullscreen = QPushButton(" ⛶ ")
        self.btn_fullscreen.setFixedSize(40, 40)
        self.btn_fullscreen.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_fullscreen.setStyleSheet("color: white; font-size: 18px; background: transparent; border: none;")
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)

        ctrl_layout.addWidget(self.btn_play)
        ctrl_layout.addWidget(self.slider)
        ctrl_layout.addWidget(btn_vol)
        ctrl_layout.addWidget(self.btn_mini)
        ctrl_layout.addWidget(self.btn_fullscreen)

        # 4. Footer
        self.footer = QFrame()
        self.footer.setObjectName("Footer")
        self.footer.setFixedHeight(30)
        foot_layout = QHBoxLayout(self.footer)
        foot_layout.setContentsMargins(20, 0, 20, 0)
        
        self.lbl_stats = QLabel("READY")
        self.lbl_stats.setProperty("class", "FooterText")
        lbl_ver = QLabel("v5.0.0 PRO")
        lbl_ver.setProperty("class", "FooterText")
        
        foot_layout.addWidget(self.lbl_stats)
        foot_layout.addStretch()
        foot_layout.addWidget(lbl_ver)

        self.right_layout.addWidget(self.header_vid)
        self.right_layout.addWidget(self.video_frame)
        self.right_layout.addWidget(self.controls)
        self.right_layout.addWidget(self.footer)

        main_layout.addWidget(right_area)

    # --- LÓGICA DE NEGOCIO ---

    def toggle_mini_player(self):
        if self.mini_window is None:
            self.start_mini_mode()
        else:
            self.stop_mini_mode()

    def start_mini_mode(self):
        # Crear ventana mini
        self.mini_window = MiniPlayerWindow(self)
        
        # Mover video_frame a la ventana mini
        # Al añadirlo al nuevo layout, se reparenta automáticamente
        self.mini_window.layout.addWidget(self.video_frame) 
        self.mini_window.show()
        
        # Actualizar HWND de VLC porque la ventana nativa ha cambiado (o su padre)
        if sys.platform == "win32":
            # A veces requiere stop/play para pillar el nuevo HWND correctamente
             pass # Probamos sin stop primero, suele funcionar al ser el mismo widget ID
             self.player.set_hwnd(self.video_frame.winId())
        
        self.btn_mini.setStyleSheet("color: #E10600; font-size: 16px; background: transparent; border: none;") # Rojo activo

    def stop_mini_mode(self):
        if self.mini_window:
            # Recuperar video_frame
            # Insertar de nuevo en el layout principal (Posición 1, después del header)
            self.right_layout.insertWidget(1, self.video_frame)
            
            self.mini_window.hide()
            self.mini_window = None
            
            # Restaurar HWND
            if sys.platform == "win32":
                 self.player.set_hwnd(self.video_frame.winId())
            
            self.btn_mini.setStyleSheet("color: white; font-size: 16px; background: transparent; border: none;")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            # Salir de fullscreen y restaurar UI
            self.showNormal()
            self.sidebar.show()
            self.header_vid.show()
            self.controls.show()
            self.footer.show()
            self.btn_fullscreen.setText(" ⛶ ")
        else:
            # Entrar a fullscreen y ocultar UI
            self.sidebar.hide()
            self.header_vid.hide()
            self.controls.hide()
            self.footer.hide()
            self.showFullScreen()
            self.btn_fullscreen.setText(" ✖ ")

    def keyPressEvent(self, event):
        """Permitir salir de pantalla completa con ESC"""
        if event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.toggle_fullscreen()
        super().keyPressEvent(event)

    # --- NUEVAS FUNCIONALIDADES MULTI-LISTA ---

    def load_playlists_list(self):
        """Busca archivos .m3u y .m3u8 en la carpeta 'playlists' y llena el Combo."""
        self.playlist_combo.blockSignals(True)
        self.playlist_combo.clear()
        
        playlist_dir = "playlists"
        if not os.path.exists(playlist_dir):
            os.makedirs(playlist_dir)

        found_lists = []
        try:
             files = os.listdir(playlist_dir)
             for f in files:
                 if f.lower().endswith(('.m3u', '.m3u8')):
                     found_lists.append(f)
        except Exception as e:
            print(f"Error buscando listas: {e}")

        if not found_lists:
             self.playlist_combo.addItem("No playlists found")
             self.playlist_combo.setEnabled(False)
        else:
            found_lists.sort()
            
            # Añadir items: Texto limpio (sin ext) -> Data (filename real)
            default_index = 0
            for i, f in enumerate(found_lists):
                name_clean = os.path.splitext(f)[0] # Remover extensión
                self.playlist_combo.addItem(name_clean, f)
                
                if f == "Canales.m3u":
                    default_index = i
            
            self.playlist_combo.setCurrentIndex(default_index)
            self.playlist_combo.setEnabled(True)
            
            # Cargar explicito la primera vez
            self.load_playlist(found_lists[default_index])

        self.playlist_combo.blockSignals(False)

    def on_playlist_changed(self, index):
        if index < 0: return
        # Obtener el filename real desde la data, no el texto mostrado
        filename = self.playlist_combo.itemData(index)
        if filename:
            print(f"Cambiando a lista: {filename}")
            self.load_playlist(filename)

    def load_playlist(self, filename):
        full_path = os.path.join("playlists", filename)
        if not os.path.exists(full_path):
            print(f"No se encontró {full_path}")
            return

        with open(full_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        current_title = ""
        current_logo = ""
        current_group = ""

        # Limpiar UI anterior
        for i in reversed(range(self.scroll_layout.count())): 
            w = self.scroll_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        self.channel_widgets = []

        for line in lines:
            line = line.strip()
            if not line: continue

            if line.startswith("#EXTINF"):
                if ',' in line: 
                    current_title = line.split(',')[-1].strip()
                    # LIMPIEZA: Eliminar códigos tras doble espacio
                    current_title = re.sub(r'\s{2,}.*$', '', current_title)
                else: 
                    current_title = "Sin Nombre"
                
                logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                current_logo = logo_match.group(1) if logo_match else ""
                
                group_match = re.search(r'group-title="([^"]*)"', line)
                current_group = group_match.group(1) if group_match else ""

            elif not line.startswith("#"):
                self.add_channel(current_title, current_logo, line, current_group)
                current_title = ""

    def add_channel(self, title, logo, url, group):
        widget = ChannelWidget(title, logo, url, group, self.play_channel)
        self.scroll_layout.addWidget(widget)
        self.channel_widgets.append(widget)

    def play_channel(self, url, title, widget_ref):
        # 1. Detener reproducción anterior explícitamente para liberar buffer
        if self.player.is_playing():
            self.player.stop()

        # Actualizar UI Selección
        for w in self.channel_widgets: w.set_active(False)
        widget_ref.set_active(True)
        self.lbl_now_playing.setText(title.upper())
        self.lbl_now_playing.setStyleSheet("color: white; font-style: italic; font-weight: 800; font-size: 14px;")

        # Verificar si es AceStream
        is_acestream = "acestream://" in url or (len(url) == 40 and not url.startswith("http"))
        
        if is_acestream:
            # Si el motor NO está corriendo, iniciamos modo espera
            if not AceStreamHandler.is_engine_running():
                print("Motor AceStream no detectado. Iniciando espera...")
                self.lbl_now_playing.setText("STARTING ACESTREAM ENGINE... PLEASE WAIT")
                self.lbl_now_playing.setStyleSheet("color: #ffa500; font-weight: 900; font-size: 14px;")
                
                # Asegurar que se lance el proceso
                AceStreamHandler.start_engine()
                
                # Configurar timer de reintento
                self.pending_play_args = (url, title, widget_ref)
                self.wait_attempts = 0
                self.wait_timer.start()
                return
        
        # Si no es acestream o ya corre, reproducir directo
        self.execute_play(url)

    def check_engine_ready(self):
        """Revisa periódicamente si el motor ya arrancó."""
        self.wait_attempts += 1
        if AceStreamHandler.is_engine_running():
            print("Motor detectado. Reproduciendo...")
            self.wait_timer.stop()
            if self.pending_play_args:
                url, _, _ = self.pending_play_args
                self.execute_play(url)
        elif self.wait_attempts > 20: # 20 segundos timeout
            print("Timeout esperando motor AceStream.")
            self.wait_timer.stop()
            self.lbl_now_playing.setText("ERROR: ACESTREAM ENGINE TIMEOUT")
            self.lbl_now_playing.setStyleSheet("color: red; font-weight: 900; font-size: 14px;")

    def execute_play(self, url):
        # Convertir enlace si es AceStream
        final_url = AceStreamHandler.convert_link(url)
        print(f"Reproduciendo: {final_url}")
        
        # VLC Player
        media = self.instance.media_new(final_url)
        # Añadir opciones para estabilidad y buffer agresivo (5 segundos)
        media.add_option(":network-caching=5000")
        media.add_option(":live-caching=5000")
        media.add_option(":sout-mux-caching=5000")
        media.add_option(":clock-jitter=0")
        media.add_option(":clock-synchro=0")
        # Intentar reconexión automática
        media.add_option(":http-reconnect=true")
        
        self.player.set_media(media)
        
        if sys.platform == "win32":
            self.player.set_hwnd(self.video_frame.winId())
        elif sys.platform.startswith("linux"):
            self.player.set_xwindow(self.video_frame.winId())
            
        self.player.play()
        self.btn_play.setText("II")
        self.timer.start()

    def filter_channels(self, text):
        text = text.lower()
        for w in self.channel_widgets:
            if text in w.title.lower():
                w.show()
            else:
                w.hide()

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.btn_play.setText(" ▶ ")
        else:
            self.player.play()
            self.btn_play.setText("II")

    def update_progress(self):
        # == ACTUALIZACIÓN DE ESTADÍSTICAS EN TIEMPO REAL ==
        try:
            state_obj = self.player.get_state()
            # Convertir enum a string (ej: State.Playing -> PLAYING)
            state_str = str(state_obj).split('.')[-1].upper()
            
            # Obtener métricas
            fps = self.player.get_fps()
            w, h = self.player.video_get_size(0)
            
            # Formatear texto
            stats_text = f"STATUS: {state_str}"
            if w > 0 and h > 0:
                stats_text += f"  |  RES: {w}x{h}"
            if fps > 0:
                stats_text += f"  |  FPS: {fps:.2f}"
            
            # Mostrar también buffering si está cargando
            if state_obj == vlc.State.Buffering:
                 stats_text += " (BUFFERING...)"
                 
            self.lbl_stats.setText(stats_text)
            
            # Colorear según estado con tonos más integrados
            if state_obj == vlc.State.Playing:
                # Usar blanco/gris claro para que parezca nativo, no un aviso
                self.lbl_stats.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 10px;")
            elif state_obj == vlc.State.Error:
                # Rojo suave (Tailwind red-500)
                self.lbl_stats.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 10px;")
            elif state_obj == vlc.State.Buffering:
                 # Ambar suave
                 self.lbl_stats.setStyleSheet("color: #fbbf24; font-weight: 600; font-size: 10px;")
            else:
                self.lbl_stats.setStyleSheet("color: #64748b; font-size: 10px;") # Slate-500 para idle
                
        except Exception:
            pass

        # == LOGICA BARRA DE PROGRESO (SLIDER) ==
        if self.player.is_playing() and not self.is_paused_by_slider:
            if self.player.get_length() > 0:
                pos = self.player.get_position()
                self.slider.setValue(int(pos * 1000))
            else:
                self.slider.setValue(0)

    def set_position(self, pos):
        if self.player.get_length() > 0:
            self.player.set_position(pos / 1000.0)

    def slider_pressed(self): self.is_paused_by_slider = True
    def slider_released(self): self.is_paused_by_slider = False
