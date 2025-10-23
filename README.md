# Waybar-Configurator-GUI
A GUI for making custom adjustments to your Waybar.

🧩 Waybar Configurator – Modern GTK4 GUI for Waybar

Waybar Configurator is a graphical editor built with GTK4 and libadwaita, designed to make customizing your Waybar
 configuration simple, visual, and safe — no manual JSON or CSS editing required.

This standalone tool reads your existing Waybar configuration (~/.config/waybar/config.jsonc and style.css), automatically detects all modules, and provides a modern GUI to tweak layout, colors, opacity, and styling — with live preview and restore features.

✨ Key Features

🧠 Automatic JSONC + CSS parsing — detects active and commented modules.

🧩 Visual module manager — enable or disable modules via switches.

🎨 Per-module style editor — edit background color, opacity, border radius, and text color.

⚙️ General settings — adjust bar layer and position (top/bottom/left/right).

💾 One-click restore — revert to the first detected configuration safely.

🔄 Live CSS preview — instantly see style changes without restarting Waybar.

🧱 100% GTK4 + libadwaita — native look and feel on modern Linux desktops (Hyprland, GNOME, etc.).

🌙 Dark mode support via Adwaita’s PREFER_DARK scheme.



🧰 Technology Stack

Python 3.11+

GTK4 / libadwaita

json5 for flexible JSONC parsing

Arch-compatible (works on any Linux with GTK4 support)

🚀 Usage
git clone https://github.com/yourname/waybar-configurator
cd waybar-configurator
python3 waybar_configurator.py


💡 The app automatically backs up your Waybar config and CSS on first launch (.backup files).
Any change is safely written back to ~/.config/waybar/.

🧩 Roadmap

 Multi-language support (English + Spanish)

 Live Waybar preview inside the window

 Module drag-and-drop reordering

 External theme import/export

 CLI launch options (--reset, --theme dark)

🧑‍💻 Author

Developed by Iván Ledesma
Project maintained under MDSoft – Modular Software Systems.
