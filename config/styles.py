STYLESHEET = """
/* BASE */
QMainWindow { background-color: #0B0B0B; }
QWidget { font-family: 'Segoe UI', 'Roboto', sans-serif; color: #e2e8f0; }

/* SIDEBAR */
QFrame#Sidebar { background-color: #101017; border-right: 1px solid #2A2A2A; }
QLabel#LogoText { font-weight: 800; font-size: 18px; letter-spacing: 1px; color: white; }
QLineEdit { background-color: #1e1e24; border: 1px solid #2A2A2A; border-radius: 8px; padding: 8px; color: #94a3b8; font-size: 12px; }
QLineEdit:focus { border: 1px solid #E10600; color: white; }

/* ITEM DE CANAL (Estilo F1) */
QFrame.ChannelItem {
    background-color: transparent;
    border-radius: 6px;
    border-left: 3px solid transparent; /* Borde invisible por defecto */
}
QFrame.ChannelItem:hover { background-color: #1A1A23; }
QFrame.ChannelItem[active="true"] { 
    background-color: #1A1A23; 
    border-left: 3px solid #E10600; /* Borde Rojo al activar */
}

/* TEXTOS DE CANAL */
QLabel.LiveTag { background-color: #E10600; color: white; font-weight: bold; font-size: 9px; padding: 2px 4px; border-radius: 3px; }
QLabel.ChannelTitle { font-weight: bold; font-size: 13px; color: white; }
QLabel.ChannelGroup { font-size: 10px; color: #64748b; font-weight: 600; text-transform: uppercase; }

/* ZONA VIDEO */
QFrame#VideoArea { background-color: black; }

/* CONTROLES (Estilo Overlay) */
QFrame#ControlsBar { background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0,0,0,0), stop:1 rgba(0,0,0, 240)); }
QPushButton.ControlBtn { background: transparent; border: none; color: #cbd5e1; font-weight: bold; }
QPushButton.ControlBtn:hover { color: white; }
QPushButton#PlayBig { background-color: white; color: black; border-radius: 20px; font-weight: bold; }
QPushButton#PlayBig:hover { transform: scale(1.1); background-color: #f1f5f9; }

/* SLIDER ROJO */
QSlider::groove:horizontal { border: none; height: 4px; background: #333333; margin: 2px 0; border-radius: 2px; }
QSlider::sub-page:horizontal { background: #E10600; border-radius: 2px; }
QSlider::handle:horizontal { background: white; width: 10px; height: 10px; margin: -3px 0; border-radius: 5px; }

/* FOOTER */
QFrame#Footer { background-color: #000000; border-top: 1px solid #2A2A2A; }
QLabel.FooterText { font-size: 10px; font-weight: bold; color: #64748b; letter-spacing: 1px; }

/* COMBOBOX PLAYLISTS */
QComboBox {
    background-color: #1e1e24;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    padding: 10px 12px;
    padding-right: 35px;
    color: white;
    font-weight: bold;
    font-size: 13px;
}
QComboBox:hover { 
    border: 1px solid #E10600;
}
QComboBox::drop-down { 
    border: none;
    width: 30px;
    subcontrol-origin: padding;
    subcontrol-position: center right;
}
QComboBox::down-arrow { 
    image: none;
    border-left: 5px solid transparent; 
    border-right: 5px solid transparent; 
    border-top: 6px solid #94a3b8;
    width: 0;
    height: 0;
}
QComboBox:hover::down-arrow {
    border-top-color: #E10600;
}
QComboBox QAbstractItemView {
    background-color: #1e1e24;
    color: white;
    selection-background-color: #E10600;
    selection-color: white;
    border: 1px solid #2A2A2A;
    border-radius: 4px;
    padding: 4px;
    outline: none;
}
QComboBox QAbstractItemView::item {
    padding: 8px;
    border-radius: 4px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #2A2A2A;
}
"""
