#!/usr/bin/env python3
# Waybar Configurator v1.0b – Community Edition (EN/ES + Modules Editor)
# Author: veitorman
# Features:
#  - Sidebar: Home, Built-in Themes, User Themes, Add current, Save default, Import, Export, Save&Restart, Settings
#  - Built-in themes embedded (transparent #waybar, modules 68–85% opacity)
#  - Auto-load user's default theme on startup
#  - Right panel: modules-from-JSON with switches, per-module styles, workspaces (container/button/active/text)
#  - Live CSS preview, Save, Restore
#  - NEW: 🧩 Modules Editor popup (add/remove/zone assign)
#  - NEW: i18n (EN/ES) via ~/.config/waybar-configurator/lang/*.json + settings.json

import re
import shutil
import subprocess
import json
from datetime import datetime
from pathlib import Path
import json5

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, Gdk

# ===== Theme preference (dark) =====
Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.PREFER_DARK)

# ===== Paths =====
HOME          = Path.home()
CFG_DIR       = HOME / ".config" / "waybar-configurator"
LANG_DIR      = CFG_DIR / "lang"
SETTINGS_JSON = CFG_DIR / "settings.json"

WAYBAR_DIR    = HOME / ".config" / "waybar"
CONFIG_JSONC  = WAYBAR_DIR / "config.jsonc"
STYLE_CSS     = WAYBAR_DIR / "style.css"
BACKUP_CONFIG = WAYBAR_DIR / "config.jsonc.backup"
BACKUP_CSS    = WAYBAR_DIR / "style.css.backup"
META_FILE     = WAYBAR_DIR / ".waybar-configurator.meta"

STORAGE_DIR        = HOME / ".local" / "share" / "waybar-configurator"
THEMES_DIR         = STORAGE_DIR / "themes"
USER_THEMES_DIR    = STORAGE_DIR / "user_themes"
DEFAULT_THEME_FILE = STORAGE_DIR / "default_theme.css"

for d in (CFG_DIR, LANG_DIR, STORAGE_DIR, THEMES_DIR, USER_THEMES_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ===== URLs =====
GITHUB_URL = "https://github.com/veitorman/Waybar-Configurator-GUI"
PAYPAL_URL = "https://www.paypal.com/paypalme/veitorman"

# ===== Icons for module list =====
ICON_HINTS = {
    "cpu": "", "memory": "", "battery": "", "clock": "", "clock#date": "",
    "custom/spotify": "", "custom/weather": "", "network": "", "backlight": "",
    "wireplumber": "", "pulseaudio": "", "tray": "", "hyprland/workspaces": "",
    "custom/power": "", "custom/screenshot_t": "", "temperature": "",
    "custom/storage": "", "mpd": "", "hyprland/window": "",
}

# ===== Built-in themes (embedded CSS) =====
BUILTIN_THEMES = {
    "🌑 Dark Emerald": """
#waybar { background-color: rgba(0,0,0,0.0); color: #e0e0e0; }
#workspaces { background-color: rgba(17,24,39,0.85); border-radius: 14px; }
#workspaces button { background-color: rgba(17,24,39,0.85); border-radius: 6px; color: #e8e8e8; }
#workspaces button.active { background-color: rgba(2,89,57,0.95); border-radius: 6px; color: #ffffff; }
#clock,#battery,#cpu,#memory,#disk,#temperature,#backlight,#network,#pulseaudio,#wireplumber,#custom-media,#mode,#idle_inhibitor,#mpd,#bluetooth,#custom-spotify,#custom-weather,#custom-screenshot_t,#custom-power,#tray,#custom-storage {
  background-color: rgba(17,24,39,0.85); border-radius: 14px; color: #e0e0e0;
}
""",
    "🌅 Sunrise Blue": """
#waybar { background-color: rgba(0,0,0,0.0); color: #ffffff; }
#workspaces { background-color: rgba(10,25,47,0.85); border-radius: 14px; }
#workspaces button { background-color: rgba(10,25,47,0.85); border-radius: 6px; color: #ffffff; }
#workspaces button.active { background-color: rgba(255,179,71,0.95); border-radius: 6px; color: #1a1a1a; }
#clock,#battery,#cpu,#memory,#disk,#temperature,#backlight,#network,#pulseaudio,#wireplumber,#custom-media,#mode,#idle_inhibitor,#mpd,#bluetooth,#custom-spotify,#custom-weather,#custom-screenshot_t,#custom-power,#tray,#custom-storage {
  background-color: rgba(10,25,47,0.78); border-radius: 14px; color: #ffffff;
}
""",
    "🌆 Sunset Orange": """
#waybar { background-color: rgba(0,0,0,0.0); color: #f5f5f5; }
#workspaces { background-color: rgba(28,27,26,0.85); border-radius: 14px; }
#workspaces button { background-color: rgba(28,27,26,0.85); border-radius: 6px; color: #f5f5f5; }
#workspaces button.active { background-color: rgba(255,112,67,0.95); border-radius: 6px; color: #1a1a1a; }
#clock,#battery,#cpu,#memory,#disk,#temperature,#backlight,#network,#pulseaudio,#wireplumber,#custom-media,#mode,#idle_inhibitor,#mpd,#bluetooth,#custom-spotify,#custom-weather,#custom-screenshot_t,#custom-power,#tray,#custom-storage {
  background-color: rgba(28,27,26,0.80); border-radius: 14px; color: #f5f5f5;
}
""",
    "🌸 Sakura Light": """
#waybar { background-color: rgba(0,0,0,0.0); color: #2e2e2e; }
#workspaces { background-color: rgba(248,241,241,0.68); border-radius: 14px; }
#workspaces button { background-color: rgba(255,183,197,0.82); border-radius: 6px; color: #2e2e2e; }
#workspaces button.active { background-color: rgba(255,183,197,0.95); border-radius: 6px; color: #1a1a1a; }
#clock,#battery,#cpu,#memory,#disk,#temperature,#backlight,#network,#pulseaudio,#wireplumber,#custom-media,#mode,#idle_inhibitor,#mpd,#bluetooth,#custom-spotify,#custom-weather,#custom-screenshot_t,#custom-power,#tray,#custom-storage {
  background-color: rgba(248,241,241,0.72); border-radius: 14px; color: #2e2e2e;
}
""",
    "🧊 Glacier Minimal": """
#waybar { background-color: rgba(0,0,0,0.0); color: #1e1e1e; }
#workspaces { background-color: rgba(232,240,248,0.80); border-radius: 14px; }
#workspaces button { background-color: rgba(232,240,248,0.80); border-radius: 6px; color: #1e1e1e; }
#workspaces button.active { background-color: rgba(0,122,204,0.92); border-radius: 6px; color: #ffffff; }
#clock,#battery,#cpu,#memory,#disk,#temperature,#backlight,#network,#pulseaudio,#wireplumber,#custom-media,#mode,#idle_inhibitor,#mpd,#bluetooth,#custom-spotify,#custom-weather,#custom-screenshot_t,#custom-power,#tray,#custom-storage {
  background-color: rgba(255,255,255,0.80); border-radius: 14px; color: #1e1e1e;
}
""",
}

# ===== i18n =====
I18N = {}
def i18n_load(lang_code: str):
    global I18N
    I18N = {}
    path = LANG_DIR / f"{lang_code}.json"
    if path.exists():
        try:
            I18N = json.loads(path.read_text("utf-8"))
        except Exception:
            I18N = {}
    # Fallback: si no existe clave, devolvemos key
def _(key: str) -> str:
    return I18N.get(key, key)

def settings_load():
    if SETTINGS_JSON.exists():
        try:
            return json.loads(SETTINGS_JSON.read_text("utf-8"))
        except Exception:
            pass
    return {"language":"en"}

def settings_save(data: dict):
    SETTINGS_JSON.write_text(json.dumps(data, indent=2), "utf-8")

SET = settings_load()
i18n_load(SET.get("language","en"))

# ===== File helpers =====
def read_text(p: Path) -> str:
    return p.read_text("utf-8") if p.exists() else ""

def write_text(p: Path, s: str):
    p.write_text(s, "utf-8")

def read_jsonc(p: Path) -> dict:
    try:
        return json5.loads(read_text(p)) if p.exists() else {}
    except Exception:
        return {}

def ensure_backup():
    if META_FILE.exists():
        return
    if CONFIG_JSONC.exists():
        shutil.copy2(CONFIG_JSONC, BACKUP_CONFIG)
    if STYLE_CSS.exists():
        shutil.copy2(STYLE_CSS, BACKUP_CSS)
    META_FILE.write_text("backup_done\n")

def restore_defaults():
    if BACKUP_CONFIG.exists():
        shutil.copy2(BACKUP_CONFIG, CONFIG_JSONC)
    if BACKUP_CSS.exists():
        shutil.copy2(BACKUP_CSS, STYLE_CSS)

def restart_waybar():
    subprocess.Popen(["bash", "-c", "pkill waybar; sleep 1; waybar & disown"])

# ===== CSS helpers =====
def rgba_from_hex(hx: str):
    rgba = Gdk.RGBA()
    try:
        if rgba.parse(hx):
            return rgba
    except Exception:
        pass
    return None

def hex_from_rgba(rgba: Gdk.RGBA) -> str:
    r = int(rgba.red * 255); g = int(rgba.green * 255); b = int(rgba.blue * 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def hex_to_rgb_tuple(hx: str):
    hx = hx.strip().lstrip("#")
    if len(hx) == 3:
        hx = "".join(ch*2 for ch in hx)
    return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))

def rgba_css(hex_color: str, alpha: float) -> str:
    r, g, b = hex_to_rgb_tuple(hex_color)
    a = max(0.0, min(1.0, float(alpha)))
    return f"rgba({r}, {g}, {b}, {a:.2f})"

def css_find_block(css: str, selector: str):
    pat = rf"(^|\n)\s*{re.escape(selector)}\s*\{{(.*?)\}}"
    m = re.search(pat, css, flags=re.S | re.M)
    if not m:
        return None, None, None
    return m.start(2), m.end(2), m.group(2)

def css_get_property(css: str, selector: str, prop: str):
    s, e, inner = css_find_block(css, selector)
    if inner is None:
        return None
    pm = re.search(rf"(^|\n)\s*{re.escape(prop)}\s*:\s*([^;]+);", inner, flags=re.S | re.M)
    return pm.group(2).strip() if pm else None

def css_set_property(css: str, selector: str, prop: str, value: str):
    s, e, inner = css_find_block(css, selector)
    if inner is None:
        block = f"\n{selector} {{\n  {prop}: {value};\n}}\n"
        return css + ("" if css.endswith("\n") else "\n") + block
    pat = rf"(^|\n)\s*{re.escape(prop)}\s*:\s*([^;]+);"
    if re.search(pat, inner, flags=re.S | re.M):
        inner2 = re.sub(pat, rf"\1{prop}: {value};", inner, flags=re.S | re.M)
    else:
        inner2 = inner.rstrip() + f"\n  {prop}: {value};\n"
    return css[:s] + inner2 + css[e:]

def module_to_selector(mod: str) -> str:
    base = mod.split("#", 1)[0]
    if base.startswith("custom/"):
        return "#" + base.replace("/", "-")
    if base.startswith("hyprland/"):
        return "#" + base.split("/", 1)[1]
    return "#" + base

def extract_css_ids(css_text: str) -> list[str]:
    ids = set()
    for m in re.finditer(r"\n\s*#([a-zA-Z0-9_\-]+)\s*\{", css_text):
        ids.add(m.group(1))
    mods = []
    for idname in sorted(ids):
        if idname.startswith("custom-"):
            mods.append("custom/" + idname.split("custom-")[1])
        elif idname in ("workspaces", "window"):
            mods.append("hyprland/" + idname)
        else:
            mods.append(idname)
    return mods

# ===== UI widgets =====
class ColorRow(Gtk.Box):
    def __init__(self, label_txt: str, initial_hex: str):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.set_hexpand(True)
        self.lab = Gtk.Label(label=label_txt, xalign=0)
        self.entry = Gtk.Entry(text=initial_hex or "#ffffff")
        self.entry.set_width_chars(9)
        self.btn = Gtk.ColorDialogButton(dialog=Gtk.ColorDialog())
        rgba = rgba_from_hex(initial_hex or "#ffffff") or Gdk.RGBA(1, 1, 1, 1)
        self.btn.set_rgba(rgba)
        self.append(self.lab); self.append(self.entry); self.append(self.btn)
        self.entry.connect("changed", self.on_entry)
        self.btn.connect("notify::rgba", self.on_pick)
    def on_entry(self, *_):
        rgba = rgba_from_hex(self.entry.get_text())
        if rgba: self.btn.set_rgba(rgba)
    def on_pick(self, *_):
        self.entry.set_text(hex_from_rgba(self.btn.get_rgba()))
    def value(self) -> str:
        return self.entry.get_text().strip() or "#ffffff"

class OpacityRow(Gtk.Box):
    def __init__(self, initial_percent: int):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.set_hexpand(True)
        self.lab = Gtk.Label(label=_("Opacity (%)"), xalign=0)
        self.spin = Gtk.SpinButton.new_with_range(0, 100, 1)
        self.spin.set_value(max(0, min(100, int(initial_percent))))
        self.append(self.lab); self.append(self.spin)
    def value(self) -> int:
        return int(self.spin.get_value())

class ModuleStyleRow(Gtk.Box):
    def __init__(self, module_name, initial_bg_hex, initial_alpha, initial_radius, initial_text_hex, apply_to_all_cb, live_cb):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.module_name = module_name
        self.apply_to_all_cb = apply_to_all_cb
        self.live_cb = live_cb

        title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        icon = Gtk.Label(label="🎛")
        lab = Gtk.Label(label=module_name, xalign=0); lab.add_css_class("title-4")
        title.append(icon); title.append(lab)
        self.append(title)

        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.bg_picker = ColorRow(_("Background"), initial_bg_hex)
        row1.append(self.bg_picker)
        self.opacity = OpacityRow(int(round((initial_alpha if initial_alpha is not None else 0.85) * 100)))
        row1.append(self.opacity)
        self.append(row1)

        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row2.append(Gtk.Label(label=_("Radius (px):"), xalign=0))
        self.radius = Gtk.SpinButton.new_with_range(0, 30, 1); self.radius.set_value(initial_radius)
        row2.append(self.radius)
        self.text_picker = ColorRow(_("Text"), initial_text_hex or "#ffffff")
        row2.append(self.text_picker)
        self.append(row2)

        row3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_all = Gtk.Button(label=_("Apply bg+opacity+radius to ALL"))
        btn_all.connect("clicked", lambda *_: self.apply_to_all_cb(self.get_style_payload()))
        row3.append(btn_all)
        self.append(row3)

        self.bg_picker.entry.connect("changed", self._live)
        self.bg_picker.btn.connect("notify::rgba", self._live)
        self.text_picker.entry.connect("changed", self._live)
        self.text_picker.btn.connect("notify::rgba", self._live)
        self.opacity.spin.connect("value-changed", self._live)
        self.radius.connect("value-changed", self._live)

    def get_style_payload(self):
        alpha = max(0, min(100, self.opacity.value())) / 100.0
        return {
            "module": self.module_name,
            "bg_hex": self.bg_picker.value(),
            "alpha": alpha,
            "radius": int(self.radius.get_value()),
            "text_hex": self.text_picker.value(),
        }
    def _live(self, *_):
        if self.live_cb: self.live_cb(self.get_style_payload())

class WorkspacesStyleRow(Gtk.Box):
    def __init__(self, apply_to_all_cb, live_cb, css_text: str):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.apply_to_all_cb = apply_to_all_cb
        self.live_cb = live_cb

        self.sel_container = "#workspaces"
        self.sel_button    = "#workspaces button"
        self.sel_active    = "#workspaces button.active"

        def _read_rgba_and_radius(selector, default_hex="#111827", default_alpha=0.85, default_rad=14):
            bg_val = css_get_property(css_text, selector, "background-color") or ""
            hh, aa = default_hex, default_alpha
            m = re.match(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)", bg_val or "", flags=re.I)
            if m:
                r,g,b,a = map(float, m.groups()); hh = f"#{int(r):02x}{int(g):02x}{int(b):02x}"; aa = float(a)
            elif isinstance(bg_val, str) and bg_val.strip().startswith("#"):
                hh = bg_val.strip(); aa = 1.0
            rad_val = css_get_property(css_text, selector, "border-radius") or f"{default_rad}px"
            try: rr = int(rad_val.strip().rstrip("px"))
            except: rr = default_rad
            return hh, aa, rr

        cont_hex, cont_alpha, cont_rad = _read_rgba_and_radius(self.sel_container, "#111827", 0.85, 14)
        btn_hex,  btn_alpha,  btn_rad  = _read_rgba_and_radius(self.sel_button,    "#111827", 0.85, 6)
        act_hex,  act_alpha,  act_rad  = _read_rgba_and_radius(self.sel_active,    "#025939", 0.95, 6)

        txt_hex = css_get_property(css_text, self.sel_button, "color") or "#ffffff"
        if not (isinstance(txt_hex, str) and txt_hex.strip().startswith("#")):
            txt_hex = "#ffffff"

        title = Gtk.Label(label="hyprland/workspaces (container + button + active + text)", xalign=0)
        title.add_css_class("title-4")
        self.append(title)

        # Container
        sec1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sec1.append(Gtk.Label(label=_("Container background"), xalign=0))
        row1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.cont_bg = ColorRow(_("Background"), cont_hex)
        self.cont_op = OpacityRow(int(round(cont_alpha * 100)))
        self.cont_rad = Gtk.SpinButton.new_with_range(0, 30, 1); self.cont_rad.set_value(cont_rad)
        row1.append(self.cont_bg); row1.append(self.cont_op)
        row1.append(Gtk.Label(label=_("Radius (px):"), xalign=0)); row1.append(self.cont_rad)
        sec1.append(row1); self.append(sec1)

        # Button
        sec2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sec2.append(Gtk.Label(label=_("Button background"), xalign=0))
        row2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.btn_bg = ColorRow(_("Background"), btn_hex)
        self.btn_op = OpacityRow(int(round(btn_alpha * 100)))
        self.btn_rad = Gtk.SpinButton.new_with_range(0, 30, 1); self.btn_rad.set_value(btn_rad)
        row2.append(self.btn_bg); row2.append(self.btn_op)
        row2.append(Gtk.Label(label=_("Radius (px):"), xalign=0)); row2.append(self.btn_rad)
        sec2.append(row2); self.append(sec2)

        # Active
        secA = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        secA.append(Gtk.Label(label=_("Active button background"), xalign=0))
        rowA = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.act_bg = ColorRow(_("Background"), act_hex)
        self.act_op = OpacityRow(int(round(act_alpha * 100)))
        self.act_rad = Gtk.SpinButton.new_with_range(0, 30, 1); self.act_rad.set_value(act_rad)
        rowA.append(self.act_bg); rowA.append(self.act_op)
        rowA.append(Gtk.Label(label=_("Radius (px):"), xalign=0)); rowA.append(self.act_rad)
        secA.append(rowA); self.append(secA)

        # Text
        sec3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sec3.append(Gtk.Label(label=_("Text (on button)"), xalign=0))
        self.txt_color = ColorRow(_("Text"), txt_hex)
        sec3.append(self.txt_color); self.append(sec3)

        act = Gtk.Button(label=_("Apply bg+opacity+radius to ALL (use container values)"))
        act.connect("clicked", lambda *_: self.apply_to_all_cb(self.payload_container()))
        self.append(act)

        for w in [
            (self.cont_bg.entry, "changed"), (self.cont_bg.btn, "notify::rgba"),
            (self.cont_op.spin, "value-changed"), self.cont_rad,
            (self.btn_bg.entry, "changed"), (self.btn_bg.btn, "notify::rgba"),
            (self.btn_op.spin, "value-changed"), self.btn_rad,
            (self.act_bg.entry, "changed"), (self.act_bg.btn, "notify::rgba"),
            (self.act_op.spin, "value-changed"), self.act_rad,
            (self.txt_color.entry, "changed"), (self.txt_color.btn, "notify::rgba"),
        ]:
            if isinstance(w, tuple):
                w[0].connect(w[1], self._live)
            elif isinstance(w, Gtk.SpinButton):
                w.connect("value-changed", self._live)

    def payload_container(self):
        return {"module": "hyprland/workspaces","target": "container",
                "bg_hex": self.cont_bg.value(),
                "alpha": max(0, min(100, self.cont_op.value())) / 100.0,
                "radius": int(self.cont_rad.get_value())}
    def payload_button(self):
        return {"module": "hyprland/workspaces","target": "button",
                "bg_hex": self.btn_bg.value(),
                "alpha": max(0, min(100, self.btn_op.value())) / 100.0,
                "radius": int(self.btn_rad.get_value())}
    def payload_active(self):
        return {"module": "hyprland/workspaces","target": "active",
                "bg_hex": self.act_bg.value(),
                "alpha": max(0, min(100, self.act_op.value())) / 100.0,
                "radius": int(self.act_rad.get_value())}
    def payload_text(self):
        return {"module": "hyprland/workspaces","target": "text",
                "text_hex": self.txt_color.value()}
    def _live(self, *_):
        if self.live_cb:
            self.live_cb(self.payload_container())
            self.live_cb(self.payload_button())
            self.live_cb(self.payload_active())
            self.live_cb(self.payload_text())

# ===== App principal =====
class App(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.veitorman.WaybarConfigurator",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

        self.cfg_text = ""; self.cfg = {}; self.css_text = ""
        self.modules_box = None
        self.styles_box = None
        self.module_rows = {}       # name -> row
        self.module_switches = {}   # name -> Gtk.Switch
        self.style_rows = {}        # name -> ModuleStyleRow | WorkspacesStyleRow
        self.css_provider = Gtk.CssProvider()
        self.toast_overlay = None

        # Sidebar refs
        self.user_themes_list_box = None

        # Modules editor state
        self.module_check = {}  # name -> (Gtk.CheckButton, Gtk.ComboBoxText)

    # ----- Helpers UI -----
    def clear_box(self, box: Gtk.Box):
        child = box.get_first_child()
        while child:
            nxt = child.get_next_sibling()
            box.remove(child)
            child = nxt

    # ----- IO -----
    def load_all(self):
        self.cfg_text = read_text(CONFIG_JSONC)
        self.cfg = read_jsonc(CONFIG_JSONC)
        self.css_text = read_text(STYLE_CSS)

    # ----- Export/Import -----
    def export_theme_zip(self):
        THEMES_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        out = THEMES_DIR / f"waybar-theme-{ts}.zip"
        import zipfile
        with zipfile.ZipFile(out, "w") as z:
            if CONFIG_JSONC.exists(): z.write(CONFIG_JSONC, "config.jsonc")
            if STYLE_CSS.exists():   z.write(STYLE_CSS,   "style.css")
        return out

    def import_theme_zip(self, filepath: str):
        import zipfile
        with zipfile.ZipFile(filepath, "r") as z:
            z.extractall(WAYBAR_DIR)

    # ----- Themes ops -----
    def apply_builtin_theme(self, name: str):
        css = BUILTIN_THEMES.get(name)
        if not css:
            self.toast(_("Theme not found"))
            return
        write_text(STYLE_CSS, css)
        self.css_text = css
        self.refresh_styles_section()
        self.apply_preview_css()
        self.toast(f"{_('Applied theme')}: {name}")

    def refresh_user_themes_list(self):
        if not self.user_themes_list_box:
            return
        self.clear_box(self.user_themes_list_box)
        found = False
        for p in sorted(USER_THEMES_DIR.glob("*.css")):
            found = True
            btn = Gtk.Button(label=p.stem)
            btn.connect("clicked", lambda _b, path=p: self.apply_user_theme(path))
            self.user_themes_list_box.append(btn)
        if not found:
            lbl = Gtk.Label(label=_("(no user themes yet)"), xalign=0)
            lbl.add_css_class("dim-label")
            self.user_themes_list_box.append(lbl)

    def apply_user_theme(self, path: Path):
        try:
            css = read_text(path)
            write_text(STYLE_CSS, css)
            self.css_text = css
            self.refresh_styles_section()
            self.apply_preview_css()
            self.toast(f"{_('User theme applied')}: {path.stem}")
        except Exception as e:
            self.toast(f"{_('Error applying theme')}: {e}")

    def add_current_theme(self, parent):
        dialog = Adw.MessageDialog.new(parent, _("Add current theme"), _("Save current CSS as user theme"))
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.set_margin_top(8); box.set_margin_bottom(8); box.set_margin_start(8); box.set_margin_end(8)
        box.append(Gtk.Label(label=_("Name:"), xalign=0))
        entry = Gtk.Entry()
        box.append(entry)
        dialog.set_extra_child(box)
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("ok", _("Add"))
        dialog.set_default_response("ok")
        dialog.set_close_response("cancel")
        dialog.present()
        def _resp(_d, resp):
            if resp == "ok":
                name = entry.get_text().strip()
                if name:
                    path = USER_THEMES_DIR / f"{name}.css"
                    try:
                        write_text(path, self.css_text or read_text(STYLE_CSS))
                        self.toast(f"{_('Saved theme')}: {name}")
                        self.refresh_user_themes_list()
                    except Exception as e:
                        self.toast(f"{_('Error saving theme')}: {e}")
        dialog.connect("response", _resp)

    def save_default_setup(self):
        try:
            write_text(DEFAULT_THEME_FILE, self.css_text or read_text(STYLE_CSS))
            self.toast(_("Default setup saved"))
        except Exception as e:
            self.toast(f"{_('Error saving default')}: {e}")

    def auto_apply_default_on_start(self):
        if DEFAULT_THEME_FILE.exists():
            try:
                css = read_text(DEFAULT_THEME_FILE)
                write_text(STYLE_CSS, css)
                self.css_text = css
            except Exception:
                pass

    # ----- Settings dialog -----
    def open_settings_dialog(self, parent):
        dialog = Adw.MessageDialog.new(parent, _("About Waybar Configurator"), _("Community Edition"))
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_margin_top(12); box.set_margin_bottom(12); box.set_margin_start(12); box.set_margin_end(12)

        about = Gtk.Label(
            label=("As a Linux user for decades, i always try to come back to Linux for testing, "
                   "developing and getting the best out of my hardware, so in this case, I was having "
                   "too much time wasted on Hyprland to set custom themes out (wich i know it's kinda "
                   "the purpose of having arch+hyprland) but Linus Torvalds Said once, "
                   "\"I wanted to be easy to install so that i can just get on with my life\", "
                   "so here we are, i hope you find this tool useful, it's unfinished because I want "
                   "to add more functions and has some errors but you will find it easy to understand."),
            xalign=0
        )
        about.set_wrap(True)
        box.append(about)

        # Language selector
        lang_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lang_box.append(Gtk.Label(label=_("Language:"), xalign=0))
        lang_combo = Gtk.ComboBoxText()
        lang_combo.append("en", "English")
        lang_combo.append("es", "Español")
        lang_combo.set_active_id(SET.get("language","en"))
        lang_box.append(lang_combo)
        apply_lang = Gtk.Button(label=_("Apply language"))
        def _set_lang(_b):
            SET["language"] = lang_combo.get_active_id() or "en"
            settings_save(SET)
            i18n_load(SET["language"])
            self.toast(_("Language applied. Restart UI to fully reflect."))
        apply_lang.connect("clicked", _set_lang)
        lang_box.append(apply_lang)
        box.append(lang_box)

        links = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        btn_git = Gtk.Button(label="🌐 GitHub")
        btn_git.connect("clicked", lambda *_: Gio.AppInfo.launch_default_for_uri(GITHUB_URL))
        btn_pay = Gtk.Button(label="💙 Donate (PayPal)")
        btn_pay.connect("clicked", lambda *_: Gio.AppInfo.launch_default_for_uri(PAYPAL_URL))
        links.append(btn_git); links.append(btn_pay)
        box.append(links)

        dialog.set_extra_child(box)
        dialog.add_response("close", _("Close"))
        dialog.set_close_response("close")
        dialog.present()

    # ----- Modules Editor -----
    def open_modules_editor(self):
        win = Adw.ApplicationWindow.new(self)
        win.set_title(_("Modules Editor"))
        win.set_default_size(700, 560)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8,
                        margin_top=12, margin_bottom=12, margin_start=16, margin_end=16)

        info = Gtk.Label(label=_("Select which modules you want enabled and where they should appear."), xalign=0)
        info.set_wrap(True)
        outer.append(info)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        outer.append(scrolled)

        grid = Gtk.Grid(column_spacing=10, row_spacing=6)
        scrolled.set_child(grid)

        # Lista base de módulos "generalizados"
        base_modules = [
            "hyprland/workspaces",
            "clock#date",
            "custom/weather",
            "cpu", "memory", "battery", "backlight", "temperature", "network",
            "wireplumber", "pulseaudio", "tray",
            "custom/spotify", "custom/power", "custom/screenshot_t", "custom/storage",
            "hyprland/window", "mpd"
        ]

        # Estado actual
        left   = [n for (n, a) in self._read_modules_zone_textual("modules-left")   if a]
        center = [n for (n, a) in self._read_modules_zone_textual("modules-center") if a]
        right  = [n for (n, a) in self._read_modules_zone_textual("modules-right")  if a]

        self.module_check = {}
        # Headers
        grid.attach(Gtk.Label(label=_("Module"), xalign=0), 0, 0, 1, 1)
        grid.attach(Gtk.Label(label=_("Enabled"), xalign=0), 1, 0, 1, 1)
        grid.attach(Gtk.Label(label=_("Zone"), xalign=0), 2, 0, 1, 1)

        for idx, m in enumerate(base_modules, start=1):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            name_lbl = Gtk.Label(label=m, xalign=0); name_lbl.set_hexpand(True)

            check = Gtk.CheckButton()
            pos_combo = Gtk.ComboBoxText()
            for zid in ("left","center","right"):
                pos_combo.append(zid, zid.capitalize())

            # Preselección si ya está activo
            preset = None
            if m in left: preset = "left"
            elif m in center: preset = "center"
            elif m in right: preset = "right"
            if preset:
                check.set_active(True)
                pos_combo.set_active_id(preset)
            else:
                pos_combo.set_active_id("left")

            grid.attach(name_lbl, 0, idx, 1, 1)
            grid.attach(check,    1, idx, 1, 1)
            grid.attach(pos_combo,2, idx, 1, 1)

            self.module_check[m] = (check, pos_combo)

        # Botones
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, margin_top=10)
        apply_btn = Gtk.Button(label="💾 " + _("Apply"))
        cancel_btn = Gtk.Button(label="❌ " + _("Cancel"))
        btn_box.append(apply_btn); btn_box.append(cancel_btn)
        outer.append(btn_box)

        apply_btn.connect("clicked", lambda *_: self.apply_modules_from_editor(win))
        cancel_btn.connect("clicked", lambda *_: win.close())

        win.set_content(outer)
        win.present()

    def apply_modules_from_editor(self, dialog_win):
        left, center, right = [], [], []
        for name, (check, combo) in self.module_check.items():
            if check.get_active():
                pos = combo.get_active_id()
                if pos == "left":
                    left.append(name)
                elif pos == "center":
                    center.append(name)
                else:
                    right.append(name)
        # Reescribimos los arrays en el JSONC (sin comentarios aquí)
        cfg = read_jsonc(CONFIG_JSONC)
        cfg["modules-left"] = left
        cfg["modules-center"] = center
        cfg["modules-right"] = right
        write_text(CONFIG_JSONC, json5.dumps(cfg, indent=2))
        self.cfg = cfg
        self.cfg_text = read_text(CONFIG_JSONC)
        self.refresh_modules_section()
        self.toast(_("Modules updated"))
        dialog_win.close()

    # ----- Activate -----
    def on_activate(self, _app):
        ensure_backup()
        self.auto_apply_default_on_start()
        self.load_all()

        win = Adw.ApplicationWindow(application=self, title="Waybar Configurator v1.0b")
        win.set_default_size(1200, 780); win.set_resizable(True)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        win.set_content(hbox)

        # === Sidebar permanente ===
        sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8,
                          margin_top=12, margin_bottom=12, margin_start=12, margin_end=8)
        sidebar.set_size_request(280, -1)

        title = Gtk.Label(label="Waybar Configurator", xalign=0); title.add_css_class("title-3")
        sidebar.append(title)

        # Home / Manual Edit Mode
        btn_home = Gtk.Button(label="🏠 " + _("Home (Manual Edit)"))
        btn_home.connect("clicked", lambda *_: self.on_home_clicked())
        sidebar.append(btn_home)

        # Modules Editor
        btn_mods = Gtk.Button(label="🧩 " + _("Modules Editor"))
        btn_mods.connect("clicked", lambda *_: self.open_modules_editor())
        sidebar.append(btn_mods)

        # Built-in Themes
        themes_lbl = Gtk.Label(label="🎨 " + _("Themes"), xalign=0); themes_lbl.add_css_class("title-4")
        sidebar.append(themes_lbl)
        for name in BUILTIN_THEMES.keys():
            btn = Gtk.Button(label=name)
            btn.connect("clicked", lambda _b, nm=name: self.apply_builtin_theme(nm))
            sidebar.append(btn)
        more_btn = Gtk.Button(label="➕ " + _("More soon…"))
        more_btn.set_sensitive(False)
        sidebar.append(more_btn)

        sidebar.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        u_lbl = Gtk.Label(label="👤 " + _("User Themes"), xalign=0); u_lbl.add_css_class("title-4")
        sidebar.append(u_lbl)

        self.user_themes_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        frame = Gtk.Frame()
        frame.set_child(self.user_themes_list_box)
        frame.set_hexpand(True)
        sidebar.append(frame)
        self.refresh_user_themes_list()

        add_cur = Gtk.Button(label="➕ " + _("Add current theme"))
        add_cur.connect("clicked", lambda *_: self.add_current_theme(win))
        sidebar.append(add_cur)

        save_def = Gtk.Button(label="❤️ " + _("Save as default setup"))
        save_def.add_css_class("destructive-action")
        save_def.connect("clicked", lambda *_: self.save_default_setup())
        sidebar.append(save_def)

        sidebar.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))
        btn_import = Gtk.Button(label="📂 " + _("Import"))
        btn_import.connect("clicked", self.on_import_clicked)
        sidebar.append(btn_import)

        btn_export = Gtk.Button(label="💾 " + _("Export"))
        btn_export.connect("clicked", self.on_export_clicked)
        sidebar.append(btn_export)

        btn_sr = Gtk.Button(label="🔄 " + _("Save & Restart"))
        btn_sr.connect("clicked", self.on_save_restart_clicked)
        sidebar.append(btn_sr)

        btn_cfg = Gtk.Button(label="⚙️ " + _("Settings"))
        btn_cfg.connect("clicked", lambda *_: self.open_settings_dialog(win))
        sidebar.append(btn_cfg)

        foot = Gtk.Label(label="v1.0b – by veitorman", xalign=0.5)
        foot.add_css_class("dim-label")
        sidebar.append(foot)

        hbox.append(sidebar)

        # === Panel derecho ===
        root = Adw.ToolbarView()
        header = Adw.HeaderBar()
        btn_save = Gtk.Button(label=_("Save")); btn_save.add_css_class("suggested-action")
        btn_restore = Gtk.Button(label=_("Restore")); btn_restore.add_css_class("destructive-action")
        btn_save.connect("clicked", self.on_save_clicked)
        btn_restore.connect("clicked", self.on_restore_clicked)
        header.pack_start(btn_restore); header.pack_end(btn_save)
        root.add_top_bar(header)

        self.toast_overlay = Adw.ToastOverlay()
        root.set_content(self.toast_overlay)
        self.toast_overlay.set_vexpand(True)

        scrolled = Gtk.ScrolledWindow(); scrolled.set_vexpand(True)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16,
                          margin_top=12, margin_bottom=24, margin_start=16, margin_end=16)
        content.set_vexpand(True)
        scrolled.set_child(content)
        self.toast_overlay.set_child(scrolled)

        content.append(self.title("🧩  " + _("Modules (from JSON)")))
        self.modules_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        content.append(self.modules_box)
        self.refresh_modules_section()

        content.append(self.title("🎨  " + _("Per-module styles (grouped by zone)")))
        self.styles_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        content.append(self.styles_box)
        self.refresh_styles_section()

        self.apply_preview_css()

        hbox.append(root)
        win.present()

    def title(self, txt):
        l = Gtk.Label(label=txt, xalign=0); l.add_css_class("title-3"); return l

    # ---------- Lectura textual módulos (preserva //) ----------
    def _read_modules_zone_textual(self, key: str):
        text = self.cfg_text
        pat = rf'"{re.escape(key)}"\s*:\s*\[(.*?)\]'
        m = re.search(pat, text, flags=re.S)
        result = []
        if not m:
            for name in self.cfg.get(key, []):
                result.append((name, True))
            return result
        inner = m.group(1)
        for line in inner.splitlines():
            s = line.strip().rstrip(",")
            if not s: continue
            active = True
            if s.startswith("//"):
                active = False
                s = s[2:].strip()
            q = re.match(r'^"(.+)"$', s)
            name = q.group(1) if q else s.strip('" ')
            if name: result.append((name, active))
        if not result and key in self.cfg:
            result = [(x, True) for x in self.cfg[key]]
        return result

    # ---------- Sección MÓDULOS ----------
    def refresh_modules_section(self):
        self.clear_box(self.modules_box)
        self.module_rows.clear()
        self.module_switches.clear()

        for zone in ("modules-left","modules-center","modules-right"):
            zlab = Gtk.Label(label=zone, xalign=0); zlab.add_css_class("title-4")
            self.modules_box.append(zlab)
            for name, active in self._read_modules_zone_textual(zone):
                row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8,
                              margin_start=6, margin_end=6)
                icon = Gtk.Label(label=ICON_HINTS.get(name.split("#")[0], ""))
                lab = Gtk.Label(label=name, xalign=0); lab.set_hexpand(True)
                sw = Gtk.Switch(active=active)
                row.append(icon); row.append(lab); row.append(sw)
                self.modules_box.append(row)
                self.module_rows[name] = row
                self.module_switches[name] = sw

    # ---------- Sección ESTILOS ----------
    def refresh_styles_section(self):
        self.clear_box(self.styles_box)
        self.style_rows.clear()

        zones = {
            "modules-left":   [n for (n, _) in self._read_modules_zone_textual("modules-left")],
            "modules-center": [n for (n, _) in self._read_modules_zone_textual("modules-center")],
            "modules-right":  [n for (n, _) in self._read_modules_zone_textual("modules-right")],
        }
        seen = set(n for arr in zones.values() for n in arr)

        css_only = []
        for css_mod in extract_css_ids(self.css_text):
            if css_mod not in seen:
                css_only.append(css_mod)

        def add_zone(title_text, names):
            ztitle = Gtk.Label(label=title_text, xalign=0); ztitle.add_css_class("title-4")
            self.styles_box.append(ztitle)
            for name in names:
                if name == "hyprland/workspaces":
                    row = WorkspacesStyleRow(self.apply_style_to_all, self.on_live_style_change, self.css_text)
                    self.styles_box.append(row)
                    self.style_rows["hyprland/workspaces"] = row
                    continue

                sel = module_to_selector(name)
                text_hex = css_get_property(self.css_text, sel, "color") or "#ffffff"
                if not (isinstance(text_hex, str) and text_hex.strip().startswith("#")):
                    text_hex = "#ffffff"

                bg_val = css_get_property(self.css_text, sel, "background-color") or ""
                bg_hex, alpha = "#111827", 0.85
                m_rgba = re.match(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9.]+)\s*\)", bg_val or "", flags=re.I)
                if m_rgba:
                    r,g,b,a = map(float, m_rgba.groups())
                    bg_hex = f"#{int(r):02x}{int(g):02x}{int(b):02x}"; alpha = float(a)
                elif isinstance(bg_val, str) and bg_val.strip().startswith("#"):
                    bg_hex = bg_val.strip(); alpha = 1.0

                rad_val = css_get_property(self.css_text, sel, "border-radius") or "14px"
                try: radius = int(rad_val.strip().rstrip("px"))
                except: radius = 14

                row = ModuleStyleRow(
                    module_name=name,
                    initial_bg_hex=bg_hex,
                    initial_alpha=alpha,
                    initial_radius=radius,
                    initial_text_hex=text_hex,
                    apply_to_all_cb=self.apply_style_to_all,
                    live_cb=self.on_live_style_change,
                )
                self.styles_box.append(row)
                self.style_rows[name] = row

        add_zone("modules-left", zones["modules-left"])
        add_zone("modules-center", zones["modules-center"])
        add_zone("modules-right", zones["modules-right"])

        if css_only:
            add_zone(_("Others (CSS only)"), css_only)

    # ---------- Aplicar a TODOS + live CSS ----------
    def apply_style_to_all(self, payload: dict):
        if payload.get("module") == "hyprland/workspaces" and payload.get("target") == "container":
            for key, mrow in self.style_rows.items():
                if key == "hyprland/workspaces":
                    continue
                if isinstance(mrow, ModuleStyleRow):
                    mrow.bg_picker.entry.set_text(payload["bg_hex"])
                    mrow.opacity.spin.set_value(int(round(payload["alpha"] * 100)))
                    mrow.radius.set_value(payload["radius"])
            self.apply_preview_css()
            self.toast(_("Applied to all from Workspaces (container)"))
            return

        if "bg_hex" in payload and "alpha" in payload and "radius" in payload:
            for key, mrow in self.style_rows.items():
                if isinstance(mrow, ModuleStyleRow):
                    if key == payload.get("module"):
                        continue
                    mrow.bg_picker.entry.set_text(payload["bg_hex"])
                    mrow.opacity.spin.set_value(int(round(payload["alpha"] * 100)))
                    mrow.radius.set_value(payload["radius"])
            self.apply_preview_css()
            self.toast(f"{_('Applied to all from')}: {payload.get('module','(module)')}")

    def on_live_style_change(self, payload: dict):
        css = self.css_text or ""
        if payload.get("module") == "hyprland/workspaces":
            if payload.get("target") == "container":
                css = css_set_property(css, "#workspaces", "background-color", rgba_css(payload["bg_hex"], payload["alpha"]))
                css = css_set_property(css, "#workspaces", "border-radius", f"{payload['radius']}px")
            elif payload.get("target") == "button":
                css = css_set_property(css, "#workspaces button", "background-color", rgba_css(payload["bg_hex"], payload["alpha"]))
                css = css_set_property(css, "#workspaces button", "border-radius", f"{payload['radius']}px")
            elif payload.get("target") == "active":
                css = css_set_property(css, "#workspaces button.active", "background-color", rgba_css(payload["bg_hex"], payload["alpha"]))
                css = css_set_property(css, "#workspaces button.active", "border-radius", f"{payload['radius']}px")
            elif payload.get("target") == "text":
                css = css_set_property(css, "#workspaces button", "color", payload["text_hex"])
        else:
            sel = module_to_selector(payload["module"])
            css = css_set_property(css, sel, "background-color", rgba_css(payload["bg_hex"], payload["alpha"]))
            css = css_set_property(css, sel, "border-radius", f"{payload['radius']}px")
            css = css_set_property(css, sel, "color", payload["text_hex"])

        try:
            self.css_provider.load_from_data(css.encode("utf-8"))
            display = Gdk.Display.get_default()
            Gtk.StyleContext.add_provider_for_display(display, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        except Exception:
            pass

    def apply_preview_css(self):
        css = self.css_text or ""
        for key, row in self.style_rows.items():
            if key == "hyprland/workspaces" and isinstance(row, WorkspacesStyleRow):
                p1 = row.payload_container()
                p2 = row.payload_button()
                pA = row.payload_active()
                p3 = row.payload_text()
                css = css_set_property(css, "#workspaces", "background-color", rgba_css(p1["bg_hex"], p1["alpha"]))
                css = css_set_property(css, "#workspaces", "border-radius", f"{p1['radius']}px")
                css = css_set_property(css, "#workspaces button", "background-color", rgba_css(p2["bg_hex"], p2["alpha"]))
                css = css_set_property(css, "#workspaces button", "border-radius", f"{p2['radius']}px")
                css = css_set_property(css, "#workspaces button.active", "background-color", rgba_css(pA["bg_hex"], pA["alpha"]))
                css = css_set_property(css, "#workspaces button.active", "border-radius", f"{pA['radius']}px")
                css = css_set_property(css, "#workspaces button", "color", p3["text_hex"])
            elif isinstance(row, ModuleStyleRow):
                sel = module_to_selector(key)
                p = row.get_style_payload()
                css = css_set_property(css, sel, "background-color", rgba_css(p["bg_hex"], p["alpha"]))
                css = css_set_property(css, sel, "border-radius", f"{p['radius']}px")
                css = css_set_property(css, sel, "color", p["text_hex"])
        try:
            self.css_provider.load_from_data(css.encode("utf-8"))
            display = Gdk.Display.get_default()
            Gtk.StyleContext.add_provider_for_display(display, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        except Exception:
            pass

    # ---------- Guardar ----------
    def on_save_clicked(self, _btn):
        # 1) Módulos (preservar orden y comentar desactivados)
        def collect_zone_text(key: str) -> str:
            names = [n for (n, _) in self._read_modules_zone_textual(key)]
            lines = []
            for n in names:
                active = self.module_switches.get(n, Gtk.Switch()).get_active()
                item = f'"{n}"'
                if not active:
                    item = f"// {item}"
                lines.append("    " + item)
            return "[\n" + (",\n".join(lines) + ("\n" if lines else "")) + "  ]"

        cfg = read_jsonc(CONFIG_JSONC)
        dumped = json5.dumps(cfg, indent=2)
        left_txt   = collect_zone_text("modules-left")
        center_txt = collect_zone_text("modules-center")
        right_txt  = collect_zone_text("modules-right")

        def repl(key, arrtxt, text):
            pat = rf'("{re.escape(key)}"\s*:\s*)\[(.*?)\]'
            if re.search(pat, text, flags=re.S):
                return re.sub(pat, rf"\1{arrtxt}", text, flags=re.S)
            return text.replace("{", "{\n  " + f'"{key}": {arrtxt},' + "\n", 1)

        dumped = repl("modules-left", left_txt, dumped)
        dumped = repl("modules-center", center_txt, dumped)
        dumped = repl("modules-right", right_txt, dumped)
        write_text(CONFIG_JSONC, dumped)
        self.cfg_text = read_text(CONFIG_JSONC)

        # 2) CSS por módulo
        css = self.css_text
        for key, row in self.style_rows.items():
            if key == "hyprland/workspaces" and isinstance(row, WorkspacesStyleRow):
                p1 = row.payload_container()
                p2 = row.payload_button()
                pA = row.payload_active()
                p3 = row.payload_text()
                css = css_set_property(css, "#workspaces", "background-color", rgba_css(p1["bg_hex"], p1["alpha"]))
                css = css_set_property(css, "#workspaces", "border-radius", f"{p1['radius']}px")
                css = css_set_property(css, "#workspaces button", "background-color", rgba_css(p2["bg_hex"], p2["alpha"]))
                css = css_set_property(css, "#workspaces button", "border-radius", f"{p2['radius']}px")
                css = css_set_property(css, "#workspaces button.active", "background-color", rgba_css(pA["bg_hex"], pA["alpha"]))
                css = css_set_property(css, "#workspaces button.active", "border-radius", f"{pA['radius']}px")
                css = css_set_property(css, "#workspaces button", "color", p3["text_hex"])
            elif isinstance(row, ModuleStyleRow):
                sel = module_to_selector(key)
                p = row.get_style_payload()
                css = css_set_property(css, sel, "background-color", rgba_css(p["bg_hex"], p["alpha"]))
                css = css_set_property(css, sel, "border-radius", f"{p['radius']}px")
                css = css_set_property(css, sel, "color", p["text_hex"])

        write_text(STYLE_CSS, css)
        self.css_text = css
        self.toast(_("Saved"))

    # ---------- Restaurar ----------
    def on_restore_clicked(self, _btn):
        restore_defaults()
        self.load_all()
        self.refresh_modules_section()
        self.refresh_styles_section()
        self.apply_preview_css()
        self.toast(_("Restored from backup"))

    # ---------- Sidebar buttons ----------
    def on_import_clicked(self, _btn):
        dialog = Gtk.FileChooserNative.new(
            _("Import theme (.zip with config.jsonc and style.css)"),
            None, Gtk.FileChooserAction.OPEN, _("_Import"), _("_Cancel")
        )
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            try:
                self.import_theme_zip(dialog.get_file().get_path())
                self.toast(_("Theme imported"))
                self.load_all()
                self.refresh_modules_section()
                self.refresh_styles_section()
                self.apply_preview_css()
            except Exception as e:
                self.toast(f"{_('Error importing')}: {e}")
        dialog.destroy()

    def on_export_clicked(self, _btn):
        try:
            out = self.export_theme_zip()
            self.toast(f"{_('Exported')}: {out}")
        except Exception as e:
            self.toast(f"{_('Error exporting')}: {e}")

    def on_save_restart_clicked(self, _btn):
        self.on_save_clicked(_btn)
        restart_waybar()
        self.toast(_("Waybar restarted"))

    # ---------- Botón HOME ----------
    def on_home_clicked(self):
        self.load_all()
        self.refresh_modules_section()
        self.refresh_styles_section()
        self.apply_preview_css()
        self.toast(_("Manual edit mode enabled"))

    # ---------- Toast ----------
    def toast(self, msg: str):
        if self.toast_overlay:
            t = Adw.Toast.new(msg); t.set_timeout(3)
            self.toast_overlay.add_toast(t)
        print(msg)

# ===== Main =====
if __name__ == "__main__":
    app = App()
    app.run([])

