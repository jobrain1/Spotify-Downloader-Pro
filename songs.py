import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import json
import os

# Einstellungen-Datei
SETTINGS_FILE = "settings.json"

# Standard-Einstellungen
settings = {
    "dark_mode": False,
    "default_save_path": ""
}

# Lade Einstellungen, falls vorhanden
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        settings.update(json.load(f))

# Farben für Dark- und Light-Mode
LIGHT_BG = "#F2F2F7"
DARK_BG = "#1E1E1E"
BUTTON_COLOR = "#007AFF"
TEXT_COLOR_LIGHT = "#000000"
TEXT_COLOR_DARK = "#FFFFFF"

# Hauptfenster
root = tk.Tk()
root.title("🎵 Spotify Downloader")
root.geometry("500x450")
root.minsize(500, 450)
root.configure(bg=LIGHT_BG if not settings["dark_mode"] else DARK_BG)

# Fortschrittsbalken speichern
progress_bars = {}

# Funktion zum Speichern der Einstellungen
def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# Funktion zum Wechseln des Dark- und Light-Modes
def toggle_theme():
    settings["dark_mode"] = not settings["dark_mode"]
    save_settings()
    apply_theme()

# Funktion zum Anwenden des Themes
def apply_theme():
    new_bg = DARK_BG if settings["dark_mode"] else LIGHT_BG
    new_text_color = TEXT_COLOR_DARK if settings["dark_mode"] else TEXT_COLOR_LIGHT
    root.configure(bg=new_bg)
    frame_buttons.configure(bg=new_bg)

    for widget in [label_links, label_path, status_label]:
        widget.configure(bg=new_bg, fg=new_text_color)

    entry_path.configure(bg="#FFFFFF" if not settings["dark_mode"] else "#333333", fg=new_text_color)
    text_links.configure(bg="#FFFFFF" if not settings["dark_mode"] else "#333333", fg=new_text_color)

# Funktion zum Ordner auswählen
def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder_selected)

# Funktion zum Spotify-Download mit Fortschrittsanzeige
def download_songs():
    links = text_links.get("1.0", tk.END).strip().split("\n")
    save_path = entry_path.get().strip()

    if not links or not save_path:
        messagebox.showerror("❌ Fehler", "Bitte gib mindestens einen Link und einen Speicherort an.")
        return

    status_label.config(text="⏳ Download läuft...")

    for bar in progress_bars.values():
        bar.destroy()
    progress_bars.clear()

    def run_download():
        for link in links:
            if link.startswith("https://open.spotify.com/"):
                status_label.config(text=f"📥 Lade herunter: {link[:30]}...")

                progress = ttk.Progressbar(root, length=300, mode="determinate")
                progress.pack(pady=2)
                progress_bars[link] = progress

                try:
                    process = subprocess.Popen(["python", "-m", "spotdl", link, "--output", save_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    while process.poll() is None:
                        progress["value"] += 5
                        root.update_idletasks()
                    
                    progress["value"] = 100  
                except subprocess.CalledProcessError:
                    messagebox.showerror("Fehler", f"❌ Fehler beim Download von: {link}")

            else:
                messagebox.showwarning("⚠️ Warnung", f"Ungültiger Link übersprungen: {link}")

        messagebox.showinfo("✅ Fertig", "Alle Downloads abgeschlossen!")
        status_label.config(text="✅ Download abgeschlossen!")

    thread = threading.Thread(target=run_download)
    thread.start()

# Einstellungen-Fenster öffnen
def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("⚙️ Einstellungen")
    settings_window.geometry("300x250")
    settings_window.configure(bg=LIGHT_BG if not settings["dark_mode"] else DARK_BG)

    def set_default_path():
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            settings["default_save_path"] = folder_selected
            save_settings()
            messagebox.showinfo("✅ Gespeichert", f"Standard-Speicherort: {folder_selected}")

    lbl_settings = tk.Label(settings_window, text="🔧 Einstellungen", font=("Helvetica", 14), bg=settings_window["bg"], fg=TEXT_COLOR_DARK if settings["dark_mode"] else TEXT_COLOR_LIGHT)
    lbl_settings.pack(pady=10)

    btn_toggle_theme = tk.Button(settings_window, text="🌙 Dark Mode umschalten", command=toggle_theme, font=("Helvetica", 12), bg=BUTTON_COLOR, fg="white", relief="flat", padx=10, pady=5)
    btn_toggle_theme.pack(pady=5)

    btn_set_path = tk.Button(settings_window, text="💾 Standard-Speicherort setzen", command=set_default_path, font=("Helvetica", 12), bg=BUTTON_COLOR, fg="white", relief="flat", padx=10, pady=5)
    btn_set_path.pack(pady=5)

    btn_about = tk.Button(settings_window, text="ℹ️ Über dieses Programm", command=lambda: messagebox.showinfo("Über", "Spotify Downloader v1.0\nErstellt von BrainGHG (Jonas)"), font=("Helvetica", 12), bg=BUTTON_COLOR, fg="white", relief="flat", padx=10, pady=5)
    btn_about.pack(pady=5)

# Labels & Eingabefelder
label_links = tk.Label(root, text="🎶 Spotify Links (einer pro Zeile):", bg=root["bg"], font=("Helvetica", 12))
label_links.pack(pady=5)
text_links = tk.Text(root, height=5, width=50, font=("Helvetica", 12), relief="flat")
text_links.pack(pady=5)

label_path = tk.Label(root, text="💾 Speicherort wählen:", bg=root["bg"], font=("Helvetica", 12))
label_path.pack(pady=5)
entry_path = tk.Entry(root, width=40, font=("Helvetica", 12), relief="flat")
entry_path.pack(pady=5)

if settings["default_save_path"]:
    entry_path.insert(0, settings["default_save_path"])

# Button-Container
frame_buttons = tk.Frame(root, bg=root["bg"])
frame_buttons.pack(pady=10)

style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=6)

btn_browse = ttk.Button(frame_buttons, text="📂 Ordner auswählen", command=browse_folder)
btn_browse.pack(side=tk.LEFT, padx=5)

btn_download = ttk.Button(frame_buttons, text="⬇️ Download starten", command=download_songs)
btn_download.pack(side=tk.LEFT, padx=5)

# Settings-Button
settings_button = tk.Button(root, text="⚙️ Einstellungen", command=open_settings, font=("Helvetica", 12), bg=BUTTON_COLOR, fg="white", relief="flat", padx=10, pady=5)
settings_button.pack(pady=5)

# Statuslabel
status_label = tk.Label(root, text="Bereit", bg=root["bg"], font=("Helvetica", 12, "italic"))
status_label.pack(pady=10)

# Theme anwenden
apply_theme()

# Start GUI
root.mainloop()
