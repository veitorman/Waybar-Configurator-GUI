# Waybar-Configurator-GUI
A GUI for making custom adjustments to your Waybar.

🧩 Waybar Configurator – Modern GTK4 GUI for Waybar

As a Linux user for decades, i always try to come back to Linux for testing, developing and getting the best out of my hardware, so in this case, I was having too much time wasted on Hyprland to set custom themes out (wich i know it's kinda the purpose of having arch+hyprland) but Linus Torvalds Said once, "I wanted to be easy to install so that i can just get on with my life", so here we are, i hope you find this tool useful, it's unfinished because I want to add more functions and has some errors but you will find it easy to understand. *this is a work in progress*

---

Waybar Configurator is a graphical editor built with GTK4 and libadwaita, designed to make customizing your Waybar configuration simple, visual, and safe — no manual JSON or CSS editing required.

This standalone tool reads your existing Waybar configuration (~/.config/waybar/config.jsonc and style.css), automatically detects all modules, and provides a modern GUI to tweak layout, colors, opacity, and styling — with live preview and restore features.

<img src="https://github.com/veitorman/Waybar-Configurator-GUI/blob/main/demo2.gif" alt="Preview Functions">
Early version 0.6b


<img src="https://github.com/veitorman/Waybar-Configurator-GUI/blob/main/release1.gif" alt="Preview Functions">
new version 1.0a

---


## ✨ Key Features

🧠 Automatic JSONC + CSS parsing — detects active and commented modules.

🧩 Visual module manager — enable or disable modules via switches.

🎨 Per-module style editor — edit background color, opacity, border radius, and text color.

⚙️ General settings — adjust bar layer and position (top/bottom/left/right).

💾 One-click restore — revert to the first detected configuration safely.

🔄 Live CSS preview — instantly see style changes without restarting Waybar.

🧱 100% GTK4 + libadwaita — native look and feel on modern Linux desktops (Hyprland, GNOME, etc.).

🌙 Dark mode support via Adwaita’s PREFER_DARK scheme.


---



## 🧰 Technology Stack

Python 3.11+

GTK4 / libadwaita

json5 for flexible JSONC parsing

Arch-compatible (works on any Linux with GTK4 support)


---

## 🚀 Usage

First of all make sure you have all the dependencies that this needs.

bash
sudo pacman -S python-gobject gtk4 libadwaita python-json5




then just run the next ones:


$ git clone https://github.com/veitorman/waybar-configurator-GUI

$ cd waybar-configurator

$ python3 waybar_configurator.py

---

💡 The app automatically backs up your Waybar config and CSS on first launch (.backup files).
Any change is safely written back to ~/.config/waybar/.

🧩 Roadmap

 IN PROGRESS - Multi-language support (English + Spanish) it has them in configuration but until now i didn't make them work, sorry.

 IN PROGRESS - Live Waybar preview inside the window

 IN PROGRESS - Module drag-and-drop reordering

 IN PROGRESS - Modules editor / modules ON/OFF sliders (they show but they don't work correctly yet)

 IN PROGRESS - Font selector

 IN PROGRESS - more modules

 IN PROGRESS - more detailed module editor (i want to be able to edit more actions and that)

 ---

 What actually works now:

-External theme import/export

-CLI launch options (--reset, --theme dark)

-Module detection based on your JSON

-changing colors, opcaity and borders for each module (or setting ALL at once(

-it has some default themes you can play with

-share your themes by exporting them!

-set your theme as default

-load custom themes that you made without having to export them, just click and load them.


So i hope this is usefull, im willing to make more of this for hyprland - arch - wayland users because i really like it and i kinda try to make people feel more comfortable using arch.

💖 Support

If you find this project useful:

⭐ Star the repo on GitHub

☕ Donate: PayPal.me/veitorman  (i will buy more hardware to test things out or just more coffee) 



