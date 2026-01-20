# Stream Hub - IPTV & AceStream Player

A modern, high-performance IPTV player built with Python, PySide6, and VLC. Designed to seamlessly handle both standard HTTP streams and AceStream (P2P) content with a premium, responsive user interface.

## Features

- 📺 **Modern UI**: sleek, dark-themed interface with glassmorphism effects.
- 🚀 **AceStream Integration**: Native support for `acestream://` links with auto-engine startup and management.
- ⚡ **Instant Playback**: Optimized buffering and network caching for smooth channel switching.
- 📋 **M3U Support**: Easy playlist management via `Canales.m3u`.
- 🔍 **Search & Filter**: Real-time channel filtering.
- 🖥️ **Cross-Platform**: Built on Python, compatible with Windows (and easily adaptable to Linux).

## Requirements

- **Python 3.10+**
- **VLC Media Player** (Must be installed on the system, specifically the correct bit-version matching your Python installation).
- **AceStream Engine** (For P2P livestreams).

### Python Dependencies

```bash
pip install PySide6 python-vlc requests
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stream-hub.git
   cd stream-hub
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: You may need to generate a requirements.txt first)*

3. Add your channels:
   Create a `Canales.m3u` file in the root directory with your stream links.

## Usage

Run the application handles:

```bash
python main.py
```

*Note: The application expects `libvlc.dll` to be accessible. If you run into issues, ensure VLC is installed in the default directory or update `config/vlc_setup.py`.*

## License

Distributed under the MIT License. See `LICENSE` for more information.
