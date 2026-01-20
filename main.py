import sys
from PyQt6.QtWidgets import QApplication

from config.vlc_setup import setup_vlc
from ui.main_window import F1TVApp

def main():
    # 1. Configurar VLC DLLs
    setup_vlc()
    
    # 2. Iniciar App
    app = QApplication(sys.argv)
    window = F1TVApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
