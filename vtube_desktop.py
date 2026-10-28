#!/usr/bin/env python3
"""VTUBE OS desktop shell prototype.

This file introduces a real desktop-like launcher and taskbar for VTUBE OS, instead of
only exposing a single Control Center page. It is a foundation for the OS experience,
with actual reusable app launchers, desktop widgets, and a taskbar system.

This is intentionally lightweight and UI-first, while remaining compatible with the
existing repo's VTUBE dashboard/live-streaming concepts.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import time


BG = "#0b0d14"
PANEL = "#141827"
PANEL2 = "#1b2032"
TEXT = "#f2f4ff"
MUTED = "#9ba4bd"
ACCENT = "#9b7bff"
CYAN = "#64e6f2"
GREEN = "#67e6ac"
AMBER = "#ffca78"
RED = "#ff7c94"


class VTubeDesktopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VTUBE OS Desktop")
        self.geometry("1366x820")
        self.minsize(1100, 720)
        self.configure(bg=BG)

        self.apps = {
            "Control Center": self._app_control_center,
            "Live Studio": self._app_live_studio,
            "Avatar Studio": self._app_avatar_studio,
            "Audio Studio": self._app_audio_studio,
            "Donation Center": self._app_donation_center,
            "Connect Hub": self._app_connect_hub,
            "Settings": self._app_settings,
        }
        self.running_apps = {}

        self._build_shell()
        self._show_desktop()
        self._clock_tick()

    def _build_shell(self):
        self.desktop = tk.Frame(self, bg=BG)
        self.desktop.pack(fill="both", expand=True)

        # Top bar / taskbar
        self.taskbar = tk.Frame(self.desktop, bg="#0d111d", height=52)
        self.taskbar.pack(fill="x", side="bottom")
        self.taskbar.pack_propagate(False)

        self.start_button = tk.Button(
            self.taskbar,
            text="  VTUBE  ",
            bg=ACCENT,
            fg="#120d1d",
            font=("TkDefaultFont", 11, "bold"),
            relief="flat",
            bd=0,
            command=self._toggle_start_menu,
            cursor="hand2",
        )
        self.start_button.pack(side="left", padx=(10, 8), pady=8)

        self.taskbar_apps = tk.Frame(self.taskbar, bg="#0d111d")
        self.taskbar_apps.pack(side="left", fill="y", expand=True)

        self.clock_label = tk.Label(self.taskbar, bg="#0d111d", fg=CYAN, text="")
        self.clock_label.pack(side="right", padx=(0, 14))

        # Start menu
        self.start_menu = tk.Frame(self.desktop, bg="#151b2d", width=300, height=420)
        self.start_menu.place(x=12, y=self.winfo_reqheight() - 430 if False else 12)
        self.start_menu.place_forget()

        self.start_menu_title = tk.Label(
            self.start_menu,
            text="VTUBE OS",
            bg="#151b2d",
            fg=TEXT,
            font=("TkDefaultFont", 18, "bold"),
        )
        self.start_menu_title.pack(anchor="w", padx=16, pady=(16, 12))

        self.start_app_list = tk.Frame(self.start_menu, bg="#151b2d")
        self.start_app_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for app_name in [
            "Control Center",
            "Live Studio",
            "Avatar Studio",
            "Audio Studio",
            "Donation Center",
            "Connect Hub",
            "Settings",
        ]:
            btn = tk.Button(
                self.start_app_list,
                text=app_name,
                bg="#1c2438",
                fg=TEXT,
                relief="flat",
                activebackground="#2a3454",
                activeforeground=TEXT,
                bd=0,
                anchor="w",
                padx=12,
                pady=10,
                command=lambda name=app_name: self.launch_app(name),
            )
            btn.pack(fill="x", pady=3)

        # Desktop content area
        self.desktop_canvas = tk.Frame(self.desktop, bg=BG)
        self.desktop_canvas.pack(fill="both", expand=True, padx=10, pady=(10, 10))

        self.launcher = tk.Frame(self.desktop_canvas, bg="#101827", width=260)
        self.launcher.pack(side="left", fill="y", padx=(0, 14))
        self.launcher.pack_propagate(False)

        self.launcher_title = tk.Label(
            self.launcher,
            text="APPS",
            bg="#101827",
            fg=MUTED,
            font=("TkDefaultFont", 9, "bold"),
        )
        self.launcher_title.pack(anchor="w", padx=18, pady=(18, 10))

        self.launcher_buttons = []
        for app_name, icon in [
            ("Control Center", "◉"),
            ("Live Studio", "●"),
            ("Avatar Studio", "✦"),
            ("Audio Studio", "♫"),
            ("Donation Center", "♡"),
            ("Connect Hub", "⌁"),
            ("Settings", "⚙"),
        ]:
            btn = tk.Button(
                self.launcher,
                text=f"{icon}  {app_name}",
                bg="#101827",
                fg=TEXT,
                anchor="w",
                relief="flat",
                bd=0,
                pady=10,
                padx=16,
                command=lambda name=app_name: self.launch_app(name),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.launcher_buttons.append(btn)

        self.workspace = tk.Frame(self.desktop_canvas, bg=BG)
        self.workspace.pack(side="left", fill="both", expand=True)

        # Desktop widgets summary
        self.summary = tk.Frame(self.workspace, bg=BG)
        self.summary.pack(fill="both", expand=True)

        self._desktop_cards()

    def _clock_tick(self):
        self.clock_label.configure(text=time.strftime("%a %d %b • %H:%M:%S"))
        self.after(1000, self._clock_tick)

    def _toggle_start_menu(self):
        if self.start_menu.winfo_ismapped():
            self.start_menu.place_forget()
        else:
            self.start_menu.place(x=12, y=12)

    def _desktop_cards(self):
        for widget in self.summary.winfo_children():
            widget.destroy()

        card_data = [
            ("System", "Live ready", GREEN),
            ("Camera", "HP + Webcam", CYAN),
            ("Audio", "Mic + Mixer", ACCENT),
            ("Live", "RTMP ready", AMBER),
        ]

        row = tk.Frame(self.summary, bg=BG)
        row.pack(fill="x", padx=10, pady=12)

        for title, value, color in card_data:
            w = tk.Frame(row, bg=PANEL, padx=18, pady=18, width=220, height=110)
            w.pack(side="left", fill="y", expand=True, padx=(0, 12))
            w.pack_propagate(False)
            tk.Label(w, text=title.upper(), bg=PANEL, fg=MUTED, font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
            tk.Label(w, text=value, bg=PANEL, fg=color, font=("TkDefaultFont", 20, "bold")).pack(anchor="w", pady=(10, 0))

        bottom = tk.Frame(self.summary, bg=BG)
        bottom.pack(fill="both", expand=True, padx=10, pady=(0, 12))

        left = tk.Frame(bottom, bg=PANEL, padx=18, pady=18)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))
        tk.Label(left, text="Quick access", bg=PANEL, fg=TEXT, font=("TkDefaultFont", 15, "bold")).pack(anchor="w")
        for label in [
            "• Start live stream",
            "• Connect phone camera",
            "• Prepare avatar scene",
            "• Open donation overlay",
        ]:
            tk.Label(left, text=label, bg=PANEL, fg=MUTED, font=("TkDefaultFont", 11)).pack(anchor="w", pady=7)

        right = tk.Frame(bottom, bg=PANEL, padx=18, pady=18)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="System health", bg=PANEL, fg=TEXT, font=("TkDefaultFont", 15, "bold")).pack(anchor="w")
        tk.Label(right, text="CPU: 32%", bg=PANEL, fg=GREEN, font=("TkDefaultFont", 12)).pack(anchor="w", pady=8)
        tk.Label(right, text="GPU: Normal", bg=PANEL, fg=CYAN, font=("TkDefaultFont", 12)).pack(anchor="w", pady=8)
        tk.Label(right, text="Network: Local LAN ready", bg=PANEL, fg=AMBER, font=("TkDefaultFont", 12)).pack(anchor="w", pady=8)

    def _clear_workspace(self):
        for w in self.workspace.winfo_children():
            w.destroy()

    def _show_desktop(self):
        self._clear_workspace()
        self._desktop_cards()

    def launch_app(self, name):
        self.start_menu.place_forget()
        self._clear_workspace()
        try:
            self.apps[name]()
        except Exception:
            self._show_desktop()

    def _taskbar_button(self, name):
        btn = tk.Button(
            self.taskbar_apps,
            text=name,
            bg="#151b2d",
            fg=TEXT,
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            command=lambda n=name: self._focus_taskbar_app(n),
        )
        btn.pack(side="left", padx=4, pady=8)
        return btn

    def _focus_taskbar_app(self, name):
        if name in self.running_apps:
            self.running_apps[name].lift()

    def _add_taskbar_app(self, name):
        if name in self.running_apps:
            return
        btn = self._taskbar_button(name)
        self.running_apps[name] = btn

    def _app_control_center(self):
        panel = tk.Frame(self.workspace, bg=PANEL, padx=24, pady=20)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="VTUBE Control Center", bg=PANEL, fg=TEXT, font=("TkDefaultFont", 24, "bold")).pack(anchor="w")
        tk.Label(panel, text="Konfigurasi sistem, stream, kamera, audio, dan status koneksi HP.", bg=PANEL, fg=MUTED, wraplength=900, justify="left").pack(anchor="w", pady=(10, 18))

        cards = [
            ("Status", "Live ready", GREEN),
            ("Camera", "Phone + Webcam", CYAN),
            ("Audio", "Mic active", ACCENT),
            ("Stream", "RTMP ready", AMBER),
        ]

        row = tk.Frame(panel, bg=PANEL)
        row.pack(fill="x", pady=10)
        for title, value, color in cards:
            c = tk.Frame(row, bg="#192236", padx=18, pady=18)
            c.pack(side="left", fill="y", expand=True, padx=(0, 12))
            tk.Label(c, text=title.upper(), bg="#192236", fg=MUTED, font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
            tk.Label(c, text=value, bg="#192236", fg=color, font=("TkDefaultFont", 20, "bold")).pack(anchor="w", pady=(8, 0))

        actions = tk.Frame(panel, bg=PANEL)
        actions.pack(fill="x", pady=(18, 0))
        for label, cmd in [
            ("Open Live Studio", lambda: self.launch_app("Live Studio")),
            ("Open Avatar Studio", lambda: self.launch_app("Avatar Studio")),
            ("Open Connect Hub", lambda: self.launch_app("Connect Hub")),
        ]:
            btn = tk.Button(actions, text=label, bg=ACCENT, fg="#130d1f", relief="flat", bd=0, padx=18, pady=10, command=cmd)
            btn.pack(side="left", padx=(0, 10))

        self._add_taskbar_app("Control Center")

    def _app_live_studio(self):
        panel = tk.Frame(self.workspace, bg=PANEL, padx=24, pady=20)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Live Studio", bg=PANEL, fg=TEXT, font=("TkDefaultFont", 24, "bold")).pack(anchor="w")
        tk.Label(panel, text="Komposisi scene, kamera/layar HP, audio, dan target stream.", bg=PANEL, fg=MUTED, wraplength=900, justify="left").pack(anchor="w", pady=(10, 14))

        preview = tk.Frame(panel, bg="#111827", height=300)
        preview.pack(fill="x")
        preview.pack_propagate(False)
        tk.Label(preview, text="LIVE PREVIEW", bg="#111827", fg=CYAN, font=("TkDefaultFont", 22, "bold")).place(relx=0.5, rely=0.5, anchor="center")

        controls = tk.Frame(panel, bg=PANEL)
        controls.pack(fill="x", pady=(20, 0))
        for label, action in [
            ("Start VTUBE live", lambda: None),
            ("Stop live", lambda: None),
            ("Add avatar", lambda: self.launch_app("Avatar Studio")),
            ("Open donation", lambda: self.launch_app("Donation Center")),
        ]:
            tk.Button(controls, text=label, bg=PANEL2, fg=TEXT, relief="flat", bd=0, padx=12, pady=9, command=action).pack(side="left", padx=(0, 10))

        self._add_taskbar_app("Live Studio")

    def _app_avatar_studio(self):
        panel = tk.Frame(self.workspace, bg=PANEL, padx=24, pady=20)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Avatar Studio", bg=PANEL, fg=TEXT, font=("TkDefaultFont", 24, "bold")).pack(anchor="w")
        tk.Label(panel, text="Buat avatar 2D/3D, atur ekspresi, warna, rambut, dan scene profile.", bg=PANEL, fg=MUTED, wraplength=900, justify="left").pack(anchor="w", pady=(10, 16))

        left = tk.Frame(panel, bg="#121a2a", width=320)
        left.pack(side="left", fill="y", padx=(0, 18))
        left.pack_propagate(False)
        tk.Label(left, text="Avatar preview", bg="#121a2a", fg=CYAN, font=("TkDefaultFont", 14, "bold")).pack(anchor="w", padx=18, pady=(18, 10))
        tk.Label(left, text="◉", bg="#121a2a", fg=ACCENT, font=("TkDefaultFont", 48, "bold")).place(relx=0.5, rely=0.5, anchor="center")

        right = tk.Frame(panel, bg=PANEL)
        right.pack(fill="both", expand=True)
        for label in ["Nama avatar", "Template", "Warna rambut", "Ekspresi wajah", "Pakaian", "Lanjutan 3D"]:
            tk.Label(right, text=label, bg=PANEL, fg=TEXT, anchor="w", justify="left").pack(anchor="w", pady=8)

        self._add_taskbar_app("Avatar Studio")

    def _app_audio_studio(self):
        panel = tk.Frame(self.workspace, bg=PANEL, padx=24, pady=20)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Audio Studio", bg=PANEL, fg=TEXT, font=("TkDefaultFont", 24, "bold")).pack(anchor="w")
        tk.Label(panel, text="Input mic PC/HP, noise suppression, gain, monitoring, dan sinkronisasi audio.", bg=PANEL, fg=MUTED, wraplength=900, justify="left").pack(anchor="w", pady=(10, 16))
        for section in ["Input Mic", "Output Device", "Noise Gate", "EQ Preset"]:
            row = tk.Frame(panel, bg="#192236", padx=16, pady=12)
            row.pack(fill="x", pady=8)
            tk.Label(row, text=section, bg="#192236", fg=TEXT, font=("TkDefaultFont", 12, "bold")).pack(anchor="w")

        self._add_taskbar_app("Audio Studio")

    def _app_donation_center(self):
        panel = tk.Frame(self.workspace, bg=PANEL, padx=24, pady=20)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Donation Center", bg=PANEL, fg=TEXT, font=("TkDefaultFont", 24, "bold")).pack(anchor="w")
        tk.Label(panel, text="Target donasi, overlay, notifikasi, TTS, dan simulasi donasi untuk testing.", bg=PANEL, fg=MUTED, wraplength=900, justify="left").pack(anchor="w", pady=(10, 16))

        values = [
            ("Target", "Rp 100.000", GREEN),
            ("Sudah terkumpul", "Rp 0", CYAN),
            ("Simulasi", "Rp 5.000", AMBER),
        ]
        row = tk.Frame(panel, bg=PANEL)
        row.pack(fill="x")
        for title, value, color in values:
            c = tk.Frame(row, bg="#192236", padx=18, pady=18)
            c.pack(side="left", fill="y", expand=True, padx=(0, 12))
            tk.Label(c, text=title.upper(), bg="#192236", fg=MUTED, font=("TkDefaultFont", 9, "bold")).pack(anchor="w")
            tk.Label(c, text=value, bg="#192236", fg=color, font=("TkDefaultFont", 18, "bold")).pack(anchor="w", pady=(8, 0))

        self._add_taskbar_app("Donation Center")

    def _app_connect_hub(self):
        panel = tk.Frame(self.workspace, bg=PANEL, padx=24, pady=20)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Connect Hub", bg=PANEL, fg=TEXT, font=("TkDefaultFont", 24, "bold")).pack(anchor="w")
        tk.Label(panel, text="Koneksi HP ke laptop via LAN, pemetaan token, camera, mic, dan screen share.", bg=PANEL, fg=MUTED, wraplength=900, justify="left").pack(anchor="w", pady=(10, 16))

        settings = [
            ("Phone IP", "192.168.1.42"),
            ("Pair code", "ABC123"),
            ("Status", "Connected"),
            ("Mode", "Wi‑Fi Local"),
        ]
        for label, value in settings:
            frame = tk.Frame(panel, bg="#192236", padx=16, pady=12)
            frame.pack(fill="x", pady=6)
            tk.Label(frame, text=label, bg="#192236", fg=MUTED, font=("TkDefaultFont", 10, "bold")).pack(side="left")
            tk.Label(frame, text=value, bg="#192236", fg=TEXT, font=("TkDefaultFont", 11, "bold")).pack(side="right")

        self._add_taskbar_app("Connect Hub")

    def _app_settings(self):
        panel = tk.Frame(self.workspace, bg=PANEL, padx=24, pady=20)
        panel.pack(fill="both", expand=True)
        tk.Label(panel, text="Settings", bg=PANEL, fg=TEXT, font=("TkDefaultFont", 24, "bold")).pack(anchor="w")
        tk.Label(panel, text="Jaringan, bahasa, tema, privasi, backup, update, dan keamanan perangkat.", bg=PANEL, fg=MUTED, wraplength=900, justify="left").pack(anchor="w", pady=(10, 16))

        for label in ["Network", "Display", "Audio", "Privacy", "Security", "Updates"]:
            row = tk.Frame(panel, bg="#192236", padx=16, pady=12)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label, bg="#192236", fg=TEXT, font=("TkDefaultFont", 12, "bold")).pack(anchor="w")

        self._add_taskbar_app("Settings")


if __name__ == "__main__":
    app = VTubeDesktopApp()
    app.mainloop()

# End of file
