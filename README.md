## Prerequisites

### System dependencies (Linux / WSL)
```bash
sudo apt install libgl1 libxkbcommon-x11-0 libdbus-1-3 libegl1 \
  libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
  libxcb-render-util0 libxcb-xinerama0 libxcb-xfixes0 \
  libxcb-cursor0 libxcb-cursor-dev libxcb-shape0 libwayland-dev \
  fonts-dejavu fonts-liberation fontconfig x11-apps

sudo fc-cache -fv
```

### WSL environment variables
Add these to your `~/.bashrc`:
```bash
export DISPLAY=:0
export QT_LOGGING_RULES="*.debug=false;qt.qpa.*=false"
```

Then reload:
```bash
source ~/.bashrc
```

### If the window doesn't appear
Restart WSL from PowerShell (as Administrator):
```powershell
wsl --shutdown
wsl
```

## Installation
```bash
pip install -r requirements.txt
```