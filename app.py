#!/usr/bin/env python3
"""VTUBE OS Control Center — functional early prototype.

Working now: navigation, scene selection, draggable scene elements, overlay preview,
donation simulation, local profile persistence, 2D avatar editor/SVG overlays,
and basic system stats.
Not yet implemented: a multi-source scene compositor, animated avatar tracking,
platform integrations, or a production-safe remote phone service.
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import platform, os, json, time, threading, subprocess, shutil, socket, urllib.request, urllib.parse
from pathlib import Path
import argparse
import re
from vtube_avatar import (
    COLOR_FIELDS, EXPRESSIONS, HAIR_STYLES, OUTFITS, TEMPLATES,
    new_character, render_avatar_svg,
)
from vtube_live import (
    FRAME_RATES, RESOLUTIONS, VIDEO_BITRATES, build_stream_command,
    phone_stream_url, rtmp_target, write_stream_overlay,
)

APP_DIR = Path.home() / ".config" / "vtube-os"
PROFILE_FILE = APP_DIR / "profiles.json"
BG, PANEL, PANEL2 = "#0b0d14", "#141827", "#1b2032"
TEXT, MUTED, ACCENT, CYAN = "#f2f4ff", "#9ba4bd", "#9b7bff", "#64e6f2"
GREEN, AMBER, RED = "#67e6ac", "#ffca78", "#ff7c94"
SCENES = ["Starting Soon", "Gameplay", "Just Chatting", "BRB", "Ending"]

def load_profiles():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"Default VTuber": {"scene": "Starting Soon", "donation_goal": 100000,
                "donation_total": 0, "theme": "#9b7bff"},
                "Mobile Gaming": {"scene": "Gameplay", "donation_goal": 100000,
                "donation_total": 0, "theme": "#64e6f2"},
                "Just Chatting": {"scene": "Just Chatting", "donation_goal": 100000,
                "donation_total": 0, "theme": "#ff7c94"},
                "Low Resource": {"scene": "Starting Soon", "donation_goal": 100000,
                "donation_total": 0, "theme": "#67e6ac"}}

def save_profiles(data):
    APP_DIR.mkdir(parents=True, exist_ok=True)
    tmp = PROFILE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(PROFILE_FILE)

class VTubeApp(tk.Tk):
    def __init__(self, start_page="Dashboard"):
        super().__init__()
        self.start_page = start_page
        self.title(f"VTUBE OS — {start_page}")
        self.geometry("1240x800")
        self.minsize(980, 650)
        self.configure(bg=BG)
        self.profiles = load_profiles()
        self.profile = tk.StringVar(value=next(iter(self.profiles)))
        self.scene = tk.StringVar(value=self.profiles[self.profile.get()].get("scene", SCENES[0]))
        self.status_var = tk.StringVar(value="Ready · Local prototype")
        self.live_armed = False
        self.donation_total = int(self.profiles[self.profile.get()].get("donation_total", 0))
        self.donation_goal = int(self.profiles[self.profile.get()].get("donation_goal", 100000))
        self.scene_items = []
        self.selected_item = None
        self.overlay_window = None
        self.overlay_label = None
        self.stream_settings = self._load_stream_settings()
        self.donation_goal = max(1,int(self.stream_settings.get("donation_goal",self.donation_goal)))
        self.active_character = self._load_active_character()
        self.live_process = None
        self.live_log_handle = None
        self.live_poll_job = None
        self._style()
        self._layout()
        self.protocol("WM_DELETE_WINDOW",self.close_app)
        self.show_page(start_page)
        self.after(1200, self._clock)

    def _style(self):
        s = ttk.Style(self)
        try: s.theme_use("clam")
        except tk.TclError: pass
        s.configure("Treeview", background=PANEL, foreground=TEXT, fieldbackground=PANEL, rowheight=28)
        s.configure("TCombobox", fieldbackground=PANEL2, background=PANEL2, foreground=TEXT)
        s.configure("TProgressbar", troughcolor=PANEL2, background=ACCENT)

    def _layout(self):
        top = tk.Frame(self, bg="#101321", height=66); top.pack(fill="x"); top.pack_propagate(False)
        tk.Label(top, text="VTUBE", bg="#101321", fg=TEXT, font=("TkDefaultFont", 22, "bold")).pack(side="left", padx=(20, 2))
        tk.Label(top, text="OS", bg="#101321", fg=ACCENT, font=("TkDefaultFont", 22, "bold")).pack(side="left")
        tk.Label(top, text="  LIVE WITHOUT THE FUSS", bg="#101321", fg=MUTED, font=("TkDefaultFont", 9, "bold")).pack(side="left", padx=16)
        self.clock_label = tk.Label(top, text="", bg="#101321", fg=CYAN); self.clock_label.pack(side="right", padx=20)
        body = tk.Frame(self, bg=BG); body.pack(fill="both", expand=True)
        nav = tk.Frame(body, bg="#101321", width=205); nav.pack(side="left", fill="y"); nav.pack_propagate(False)
        tk.Label(nav, text="WORKSPACE", bg="#101321", fg=MUTED, font=("TkDefaultFont", 9, "bold")).pack(anchor="w", padx=18, pady=(20, 10))
        self.nav_buttons = {}
        for name, glyph in [("Dashboard","⌂"),("Live Studio","◉"),("Avatar Studio","✦"),("Audio Studio","♫"),
                            ("Donation Center","♡"),("VTUBE Connect","⌁"),("Feature Center","✧"),("Profiles","▤"),("Settings","⚙")]:
            b=tk.Button(nav,text=f"  {glyph}   {name}",anchor="w",relief="flat",bd=0,padx=12,pady=11,
                bg="#101321",fg=TEXT,activebackground="#292440",activeforeground=TEXT,
                command=lambda n=name:self.show_page(n))
            b.pack(fill="x", padx=8, pady=2); self.nav_buttons[name]=b
        foot=tk.Frame(nav,bg="#101321"); foot.pack(side="bottom",fill="x",padx=16,pady=18)
        tk.Label(foot,text="VTUBE OS ALPHA",bg="#101321",fg=ACCENT,font=("TkDefaultFont",9,"bold")).pack(anchor="w")
        tk.Label(foot,text="Integrated VTuber workspace",bg="#101321",fg=MUTED,font=("TkDefaultFont",8)).pack(anchor="w",pady=(4,0))
        self.content=tk.Frame(body,bg=BG); self.content.pack(side="left",fill="both",expand=True,padx=22,pady=20)
        status=tk.Frame(self,bg="#101321",height=30); status.pack(fill="x",side="bottom"); status.pack_propagate(False)
        tk.Label(status,textvariable=self.status_var,bg="#101321",fg=MUTED).pack(side="left",padx=14,pady=5)
        tk.Label(status,text="Alpha prototype · see README for working vs planned features",bg="#101321",fg="#747e99").pack(side="right",padx=14)

    def _clock(self):
        self.clock_label.configure(text=time.strftime("%a, %d %b  ·  %H:%M:%S"))
        self.after(1000,self._clock)

    def clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def title_block(self,title,subtitle):
        tk.Label(self.content,text=title,bg=BG,fg=TEXT,font=("TkDefaultFont",23,"bold")).pack(anchor="w")
        tk.Label(self.content,text=subtitle,bg=BG,fg=MUTED,wraplength=900,justify="left").pack(anchor="w",pady=(4,18))

    def card(self,parent,title,value,note,color=ACCENT):
        f=tk.Frame(parent,bg=PANEL,highlightbackground="#252b40",highlightthickness=1,padx=14,pady=13)
        tk.Label(f,text=title.upper(),bg=PANEL,fg=MUTED,font=("TkDefaultFont",9,"bold")).pack(anchor="w")
        tk.Label(f,text=value,bg=PANEL,fg=color,font=("TkDefaultFont",17,"bold")).pack(anchor="w",pady=(7,2))
        tk.Label(f,text=note,bg=PANEL,fg=MUTED,wraplength=220,justify="left").pack(anchor="w")
        return f

    def btn(self,parent,text,command,primary=False):
        return tk.Button(parent,text=text,command=command,relief="flat",bd=0,padx=13,pady=9,
            bg=ACCENT if primary else PANEL2,fg="#100d1c" if primary else TEXT,
            activebackground="#b5a0ff" if primary else "#292f46",cursor="hand2")

    def section(self,parent,title,detail=""):
        tk.Label(parent,text=title,bg=PANEL,fg=TEXT,font=("TkDefaultFont",12,"bold")).pack(anchor="w")
        if detail: tk.Label(parent,text=detail,bg=PANEL,fg=MUTED,wraplength=560,justify="left").pack(anchor="w",pady=(5,0))

    def show_page(self,name):
        self.current_page=name
        for n,b in self.nav_buttons.items(): b.configure(bg="#292440" if n==name else "#101321",fg=CYAN if n==name else TEXT)
        self.clear()
        {"Dashboard":self.page_dashboard,"Live Studio":self.page_live_studio,"Avatar Studio":self.page_avatar,
         "Audio Studio":self.page_audio,"Donation Center":self.page_donations,"VTUBE Connect":self.page_connect,
         "Feature Center":self.page_features,"Profiles":self.page_profiles,"Settings":self.page_settings}[name]()

    def _load_stream_settings(self):
        path=APP_DIR/"stream-settings.json"
        if not path.exists():return {"donation_link":"","qr_image":"","donation_goal":self.donation_goal}
        try:
            data=json.loads(path.read_text(encoding="utf-8"))
            return {"donation_link":data.get("donation_link",""),
                    "qr_image":data.get("qr_image",""),
                    "donation_goal":int(data.get("donation_goal",self.donation_goal)),
                    "stream_server":data.get("stream_server",""),
                    "stream_key":data.get("stream_key",""),
                    "video_source":data.get("video_source","phone-screen"),
                    "audio_source":data.get("audio_source","phone-mic"),
                    "resolution":data.get("resolution","1280x720"),
                    "fps":int(data.get("fps",30)),
                    "bitrate":data.get("bitrate","4500 kbps"),
                    "phone_host":data.get("phone_host",""),
                    "pair_code":data.get("pair_code",""),
                    "camera_device":data.get("camera_device","")}
        except (OSError,ValueError,TypeError) as error:
            messagebox.showwarning("VTUBE settings",f"Pengaturan donasi tidak bisa dibaca; memakai nilai awal.\n{error}")
            return {"donation_link":"","qr_image":"","donation_goal":self.donation_goal}

    def _load_active_character(self):
        path=APP_DIR/"active-character.json"
        if not path.exists():return new_character()
        try:
            data=json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data,dict):raise ValueError("Format karakter harus berupa objek JSON.")
            template=data.get("template","Luna")
            defaults=new_character(template if template in TEMPLATES else "Luna")
            defaults.update(data)
            for field in COLOR_FIELDS:
                if not re.fullmatch(r"#[0-9A-Fa-f]{6}",str(defaults.get(field,""))):
                    defaults[field]=new_character(defaults["template"])[field]
            if defaults.get("outfit") not in OUTFITS:defaults["outfit"]="Hoodie"
            if defaults.get("hair_style") not in HAIR_STYLES:defaults["hair_style"]="Long"
            if defaults.get("expression") not in EXPRESSIONS:defaults["expression"]="Smile"
            defaults["name"]=str(defaults.get("name","VTUBE Avatar"))
            return defaults
        except (OSError,ValueError,TypeError) as error:
            messagebox.showwarning("Avatar Studio",f"Karakter aktif tidak bisa dibaca; memakai Luna.\n{error}")
            return new_character()

    def _save_active_character(self,data):
        try:
            APP_DIR.mkdir(parents=True,exist_ok=True)
            path=APP_DIR/"active-character.json";tmp=path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
            tmp.replace(path)
        except OSError as error:
            messagebox.showerror("Avatar Studio",f"Karakter aktif tidak dapat disimpan: {error}")

    def _save_stream_settings(self):
        self.stream_settings.update({"donation_goal":self.donation_goal})
        if hasattr(self,"donation_link_var"):
            link=self.donation_link_var.get().strip()
            if link:
                parsed=urllib.parse.urlsplit(link)
                if parsed.scheme not in ("http","https") or not parsed.netloc:
                    messagebox.showerror("Link donasi","Masukkan link lengkap yang diawali https:// atau http://.")
                    return False
            self.stream_settings["donation_link"]=link
        if hasattr(self,"stream_server_var"):
            self.stream_settings.update({
                "stream_server":self.stream_server_var.get().strip(),
                "stream_key":self.stream_key_var.get().strip(),
                "video_source":self.live_video_source_var.get(),
                "audio_source":self.live_audio_source_var.get(),
                "resolution":self.live_resolution_var.get(),
                "fps":int(self.live_fps_var.get()),
                "bitrate":self.live_bitrate_var.get(),
                "phone_host":self.live_phone_host_var.get().strip(),
                "pair_code":self.live_pair_code_var.get().strip().upper(),
            })
        try:
            APP_DIR.mkdir(parents=True,exist_ok=True)
            path=APP_DIR/"stream-settings.json";tmp=path.with_suffix(".tmp")
            descriptor=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600)
            os.fchmod(descriptor,0o600)
            with os.fdopen(descriptor,"w",encoding="utf-8") as settings_file:
                settings_file.write(json.dumps(self.stream_settings,indent=2,ensure_ascii=False))
            tmp.replace(path)
            path.chmod(0o600)
            return True
        except OSError as error:
            messagebox.showerror("VTUBE settings",f"Tidak dapat menyimpan pengaturan donasi: {error}")
            return False

    def page_dashboard(self):
        self.title_block("VTUBE OS","A single workspace for avatar, phone feeds, audio and integrated live streaming.")
        row=tk.Frame(self.content,bg=BG); row.pack(fill="x")
        cards=[("Live status","OFFLINE","Configure RTMP in VTUBE Live Studio",AMBER),
               ("Avatar","2D ready","Customize, save, and export an avatar overlay",ACCENT),
               ("Camera","Not connected","USB camera or phone camera",CYAN),
               ("Donations",f"Rp {self.donation_total:,}",f"Goal Rp {self.donation_goal:,}",GREEN)]
        for args in cards:self.card(row,*args).pack(side="left",fill="both",expand=True,padx=(0,9))
        lower=tk.Frame(self.content,bg=BG); lower.pack(fill="both",expand=True,pady=(16,0))
        left=tk.Frame(lower,bg=PANEL,padx=16,pady=16);left.pack(side="left",fill="both",expand=True,padx=(0,10))
        self.section(left,"Quick start","Pick a profile and scene. The UI remembers your profile locally.")
        ttk.Combobox(left,textvariable=self.profile,values=list(self.profiles),state="readonly",width=28).pack(anchor="w",pady=(14,8))
        ttk.Combobox(left,textvariable=self.scene,values=SCENES,state="readonly",width=28).pack(anchor="w",pady=4)
        self.btn(left,"Open Live Studio →",lambda:self.show_page("Live Studio"),True).pack(anchor="w",pady=(14,0))
        right=tk.Frame(lower,bg=PANEL,padx=16,pady=16);right.pack(side="left",fill="both",expand=True)
        self.section(right,"Live checklist","The VTUBE media engine composes and streams directly to RTMP.")
        for s,c in [("○  2D avatar + donation overlay",CYAN),("○  Camera or phone screen",ACCENT),("○  Microphone input",GREEN),("○  RTMP destination/key",AMBER)]:
            tk.Label(right,text=s,bg=PANEL,fg=c,font=("TkDefaultFont",11)).pack(anchor="w",pady=8)
        self.btn(right,"Test donation overlay",lambda:self.show_page("Donation Center")).pack(anchor="w",pady=8)

    def page_live_studio(self):
        self.title_block("Live Studio","The canvas is a layout mockup. Live output currently includes one selected video source plus the static avatar/donation overlay.")
        controls=tk.Frame(self.content,bg=BG);controls.pack(fill="x",pady=(0,10))
        tk.Label(controls,text="SCENE",bg=BG,fg=MUTED).pack(side="left",padx=(0,8))
        ttk.Combobox(controls,textvariable=self.scene,values=SCENES,state="readonly",width=20).pack(side="left")
        self.btn(controls,"Add text",lambda:self.add_scene_item("Text")).pack(side="left",padx=6)
        self.btn(controls,"Add avatar placeholder",lambda:self.add_scene_item("Avatar")).pack(side="left",padx=6)
        self.btn(controls,"Add gameplay placeholder",lambda:self.add_scene_item("Gameplay")).pack(side="left",padx=6)
        self.btn(controls,"Donation alert test",self.simulate_donation).pack(side="left",padx=6)
        self.btn(controls,"Save profile",self.save_current_profile,True).pack(side="right")
        stream_controls=tk.Frame(self.content,bg=BG);stream_controls.pack(fill="x",pady=(0,8))
        self.btn(stream_controls,"Save live setup",self.save_live_settings).pack(side="left",padx=(0,8))
        self.btn(stream_controls,"Start VTUBE live",self.start_live_stream,True).pack(side="left",padx=8)
        self.btn(stream_controls,"Stop live",self.stop_live_stream).pack(side="left",padx=8)
        self.live_status_var=tk.StringVar(value="VTUBE live engine ready · RTMP config needed")
        settings=tk.Frame(self.content,bg=PANEL,padx=12,pady=8);settings.pack(fill="x",pady=(0,8))
        self.section(settings,"VTUBE live engine","Live video composition and RTMP/RTMPS streaming run inside VTUBE. Configure your platform's ingest URL and stream key.")
        self.stream_server_var=tk.StringVar(value=self.stream_settings.get("stream_server",""))
        self.stream_key_var=tk.StringVar(value=self.stream_settings.get("stream_key",""))
        self.live_video_source_var=tk.StringVar(value=self.stream_settings.get("video_source","phone-screen"))
        self.live_audio_source_var=tk.StringVar(value=self.stream_settings.get("audio_source","phone-mic"))
        self.live_resolution_var=tk.StringVar(value=self.stream_settings.get("resolution","1280x720"))
        self.live_fps_var=tk.StringVar(value=str(self.stream_settings.get("fps",30)))
        self.live_bitrate_var=tk.StringVar(value=self.stream_settings.get("bitrate","4500 kbps"))
        self.live_phone_host_var=tk.StringVar(value=self.stream_settings.get("phone_host",""))
        self.live_pair_code_var=tk.StringVar(value=self.stream_settings.get("pair_code",""))
        server_row=tk.Frame(settings,bg=PANEL);server_row.pack(fill="x",pady=(7,3))
        tk.Label(server_row,text="RTMP server",bg=PANEL,fg=TEXT).pack(side="left")
        tk.Entry(server_row,textvariable=self.stream_server_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=43).pack(side="left",padx=(6,12),ipady=4)
        tk.Label(server_row,text="Stream key",bg=PANEL,fg=TEXT).pack(side="left")
        tk.Entry(server_row,textvariable=self.stream_key_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=28,show="•").pack(side="left",padx=6,ipady=4)
        source_row=tk.Frame(settings,bg=PANEL);source_row.pack(fill="x",pady=3)
        tk.Label(source_row,text="Video",bg=PANEL,fg=TEXT).pack(side="left")
        ttk.Combobox(source_row,textvariable=self.live_video_source_var,values=("phone-screen","phone-camera","webcam","desktop"),state="readonly",width=15).pack(side="left",padx=5)
        tk.Label(source_row,text="Audio",bg=PANEL,fg=TEXT).pack(side="left",padx=(8,0))
        ttk.Combobox(source_row,textvariable=self.live_audio_source_var,values=("phone-mic","system-mic","none"),state="readonly",width=14).pack(side="left",padx=5)
        tk.Label(source_row,text="Resolution",bg=PANEL,fg=TEXT).pack(side="left",padx=(8,0))
        ttk.Combobox(source_row,textvariable=self.live_resolution_var,values=tuple(RESOLUTIONS),state="readonly",width=12).pack(side="left",padx=5)
        ttk.Combobox(source_row,textvariable=self.live_fps_var,values=tuple(str(rate) for rate in FRAME_RATES),state="readonly",width=5).pack(side="left",padx=4)
        ttk.Combobox(source_row,textvariable=self.live_bitrate_var,values=tuple(VIDEO_BITRATES),state="readonly",width=12).pack(side="left",padx=4)
        phone_row=tk.Frame(settings,bg=PANEL);phone_row.pack(fill="x",pady=3)
        tk.Label(phone_row,text="Phone IPv4",bg=PANEL,fg=TEXT).pack(side="left")
        tk.Entry(phone_row,textvariable=self.live_phone_host_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=18).pack(side="left",padx=6,ipady=4)
        tk.Label(phone_row,text="Pair code",bg=PANEL,fg=TEXT).pack(side="left",padx=(8,0))
        tk.Entry(phone_row,textvariable=self.live_pair_code_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=10,show="•").pack(side="left",padx=6,ipady=4)
        tk.Label(phone_row,textvariable=self.live_status_var,bg=PANEL,fg=CYAN,wraplength=550,justify="left").pack(side="left",padx=12)
        area=tk.Frame(self.content,bg=BG);area.pack(fill="both",expand=True)
        self.canvas=tk.Canvas(area,bg="#080a10",highlightbackground="#34304f",highlightthickness=1)
        self.canvas.pack(side="left",fill="both",expand=True,padx=(0,12))
        side=tk.Frame(area,bg=PANEL,width=230,padx=12,pady=12);side.pack(side="right",fill="y");side.pack_propagate(False)
        self.section(side,"Scene elements","Drag blocks to position them.")
        self.item_list=tk.Listbox(side,bg=PANEL2,fg=TEXT,selectbackground="#49406e",relief="flat",height=12)
        self.item_list.pack(fill="x",pady=(10,10))
        self.btn(side,"Remove selected",self.remove_selected).pack(fill="x")
        tk.Label(side,text="Tip: drag an item on the preview canvas.",bg=PANEL,fg=MUTED,wraplength=190,justify="left").pack(anchor="w",pady=14)
        self.scene_items=[]
        self._draw_default_scene()
        self.canvas.bind("<ButtonPress-1>",self.drag_start)
        self.canvas.bind("<B1-Motion>",self.drag_move)
        self.canvas.bind("<ButtonRelease-1>",self.drag_end)
        self.item_list.bind("<<ListboxSelect>>",self.select_from_list)

    def _draw_default_scene(self):
        self.canvas.delete("all"); self.scene_items=[]
        self.canvas.create_rectangle(20,20,680,390,outline="#34304f",width=2,fill="#111525")
        self.canvas.create_text(350,42,text=self.scene.get().upper(),fill=CYAN,font=("TkDefaultFont",13,"bold"),tags=("item","scene_title"))
        self.scene_items.append({"id":"scene_title","name":"Scene title","kind":"Text"})
        self.canvas.create_rectangle(35,65,475,345,outline="#4a4568",dash=(4,4),fill="#151a2a",tags=("item","gameplay"))
        self.canvas.create_text(255,205,text="GAMEPLAY CAPTURE\nSOURCE NOT CONNECTED",fill="#8d91aa",font=("TkDefaultFont",13,"bold"),justify="center",tags=("item","gameplay_label"))
        self.scene_items.append({"id":"gameplay","name":"Gameplay placeholder","kind":"Gameplay"})
        avatar=self.active_character
        self.canvas.create_rectangle(500,80,650,270,outline=ACCENT,width=2,fill="#201b32",tags=("item","avatar"))
        self.canvas.create_oval(540,93,610,163,fill=avatar["hair_color"],outline="#332B42",width=2,tags=("item","avatar"))
        self.canvas.create_polygon(542,150,562,143,590,143,608,152,620,245,528,245,fill=avatar["outfit_color"],outline="#332B42",width=2,tags=("item","avatar"))
        self.canvas.create_oval(546,103,604,169,fill=avatar["skin_color"],outline="#332B42",width=2,tags=("item","avatar"))
        self.canvas.create_arc(544,91,606,155,start=0,extent=180,fill=avatar["hair_color"],outline="#332B42",width=2,tags=("item","avatar"))
        self.canvas.create_oval(558,128,566,140,fill=avatar["eye_color"],outline="",tags=("item","avatar"))
        self.canvas.create_oval(584,128,592,140,fill=avatar["eye_color"],outline="",tags=("item","avatar"))
        self.canvas.create_arc(566,139,584,155,start=205,extent=130,style="arc",outline="#9D5366",width=2,tags=("item","avatar"))
        self.canvas.create_text(575,257,text=avatar["name"],fill="#d8caff",font=("TkDefaultFont",9,"bold"),tags=("item","avatar"))
        self.scene_items.append({"id":"avatar","name":"Avatar placeholder","kind":"Avatar"})
        self.canvas.create_text(350,365,text="VTUBE OS · LIVE PREVIEW MOCKUP",fill="#6e7691",font=("TkDefaultFont",9),tags=("item","watermark"))
        self.scene_items.append({"id":"watermark","name":"Watermark","kind":"Text"})
        self._refresh_item_list()

    def _refresh_item_list(self):
        if not hasattr(self,"item_list") or not self.item_list.winfo_exists():return
        self.item_list.delete(0,"end")
        for it in self.scene_items:self.item_list.insert("end",it["name"])

    def add_scene_item(self,kind):
        if not hasattr(self,"canvas") or not self.canvas.winfo_exists():
            messagebox.showinfo("Live Studio","Buka Live Studio dahulu.");return
        idx=len(self.scene_items)+1; tag=f"custom_{idx}"
        if kind=="Text":
            self.canvas.create_text(350,120+idx*12,text="Edit text in next milestone",fill=TEXT,font=("TkDefaultFont",14,"bold"),tags=("item",tag))
        elif kind=="Avatar":
            self.canvas.create_rectangle(500,100,630,260,outline=ACCENT,width=2,fill="#201b32",tags=("item",tag))
            self.canvas.create_text(565,180,text="AVATAR\nSOURCE",fill="#d8caff",tags=("item",tag))
        else:
            self.canvas.create_rectangle(60,90,300,250,outline=CYAN,dash=(4,4),fill="#151a2a",tags=("item",tag))
            self.canvas.create_text(180,170,text="GAMEPLAY SOURCE",fill=CYAN,tags=("item",tag))
        self.scene_items.append({"id":tag,"name":f"{kind} {idx}","kind":kind});self._refresh_item_list()
        self.status_var.set(f"Added {kind} placeholder to scene")

    def drag_start(self,event):
        item=self.canvas.find_closest(event.x,event.y)
        if item:
            tags=self.canvas.gettags(item)
            if "item" in tags:self.selected_item=item;self._last_xy=(event.x,event.y)

    def drag_move(self,event):
        if self.selected_item:
            dx,dy=event.x-self._last_xy[0],event.y-self._last_xy[1]
            self.canvas.move(self.selected_item,dx,dy);self._last_xy=(event.x,event.y)

    def drag_end(self,event):
        self.selected_item=None

    def select_from_list(self,event=None):
        sel=self.item_list.curselection()
        if sel and sel[0]<len(self.scene_items):
            tag=self.scene_items[sel[0]]["id"]
            items=self.canvas.find_withtag(tag)
            if items:self.canvas.itemconfigure(items[0],width=3)

    def remove_selected(self):
        sel=self.item_list.curselection()
        if not sel:return
        it=self.scene_items.pop(sel[0])
        self.canvas.delete(it["id"])
        # Some placeholder objects use separate label tags; rebuild for predictable state.
        self._draw_default_scene()
        self.status_var.set("Scene reset after removing item; default layout restored")

    def save_current_profile(self):
        name=self.profile.get()
        self.profiles.setdefault(name,{})
        self.profiles[name].update({"scene":self.scene.get(),"donation_goal":self.donation_goal,
                                    "donation_total":self.donation_total})
        save_profiles(self.profiles)
        self.status_var.set(f"Saved profile: {name}")
        messagebox.showinfo("VTUBE OS",f"Profile '{name}' saved locally.")

    def page_avatar(self):
        self.title_block("Avatar Studio","Atur template 2D dan lihat hasilnya langsung. Karakter tersimpan lokal dan dirender langsung oleh VTUBE Live.")
        split=tk.Frame(self.content,bg=BG);split.pack(fill="both",expand=True)
        preview=tk.Frame(split,bg=PANEL,padx=12,pady=12);preview.pack(side="left",fill="y",padx=(0,12))
        self.section(preview,"LIVE PREVIEW","Preview ilustrasi mengikuti pilihan warna dan pakaian.")
        self.avatar_canvas=tk.Canvas(preview,width=330,height=445,bg="#24283a",highlightthickness=0)
        self.avatar_canvas.pack(pady=(10,0))
        editor=tk.Frame(split,bg=PANEL,padx=16,pady=14);editor.pack(side="left",fill="both",expand=True)
        self.section(editor,"Karakter baru / tersimpan","Template Luna, Nova, dan Kiro adalah ilustrasi original VTUBE; bukan model 3D.")
        self.avatar_name_var=tk.StringVar(value=self.active_character.get("name","Luna"))
        self.avatar_template_var=tk.StringVar(value=self.active_character.get("template","Luna"))
        self.avatar_outfit_var=tk.StringVar(value=self.active_character.get("outfit","Hoodie"))
        self.avatar_hair_style_var=tk.StringVar(value=self.active_character.get("hair_style","Long"))
        self.avatar_expression_var=tk.StringVar(value=self.active_character.get("expression","Smile"))
        self.avatar_color_vars={key:tk.StringVar(value=self.active_character.get(key, TEMPLATES["Luna"][key])) for key in COLOR_FIELDS}
        self.saved_avatar_var=tk.StringVar()
        row=tk.Frame(editor,bg=PANEL);row.pack(fill="x",pady=(10,5))
        tk.Label(row,text="Nama karakter",bg=PANEL,fg=TEXT).pack(side="left")
        tk.Entry(row,textvariable=self.avatar_name_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=22).pack(side="left",padx=8,ipady=5)
        tk.Label(row,text="Template",bg=PANEL,fg=TEXT).pack(side="left",padx=(10,4))
        template_box=ttk.Combobox(row,textvariable=self.avatar_template_var,values=list(TEMPLATES),state="readonly",width=12)
        template_box.pack(side="left")
        template_box.bind("<<ComboboxSelected>>",self.select_avatar_template)
        row=tk.Frame(editor,bg=PANEL);row.pack(fill="x",pady=5)
        tk.Label(row,text="Pakaian",bg=PANEL,fg=TEXT).pack(side="left")
        ttk.Combobox(row,textvariable=self.avatar_outfit_var,values=OUTFITS,state="readonly",width=16).pack(side="left",padx=(8,18))
        tk.Label(row,text="Gaya rambut",bg=PANEL,fg=TEXT).pack(side="left")
        ttk.Combobox(row,textvariable=self.avatar_hair_style_var,values=HAIR_STYLES,state="readonly",width=14).pack(side="left",padx=8)
        row=tk.Frame(editor,bg=PANEL);row.pack(fill="x",pady=5)
        tk.Label(row,text="Ekspresi",bg=PANEL,fg=TEXT).pack(side="left")
        ttk.Combobox(row,textvariable=self.avatar_expression_var,values=EXPRESSIONS,state="readonly",width=16).pack(side="left",padx=8)
        swatches=tk.Frame(editor,bg=PANEL);swatches.pack(fill="x",pady=8)
        for key,label in (("hair_color","Rambut"),("outfit_color","Pakaian"),("eye_color","Mata"),("skin_color","Kulit")):
            box=tk.Frame(swatches,bg=PANEL);box.pack(side="left",expand=True,fill="x",padx=3)
            tk.Label(box,text=label,bg=PANEL,fg=MUTED).pack(anchor="w")
            button=tk.Button(box,textvariable=self.avatar_color_vars[key],relief="flat",bd=0,fg="#ffffff",
                command=lambda field=key:self.choose_avatar_color(field))
            button.pack(fill="x",pady=3,ipady=5)
            self.avatar_color_vars[key].trace_add("write",lambda *_args,b=button,v=self.avatar_color_vars[key]:b.configure(bg=v.get()))
            button.configure(bg=self.avatar_color_vars[key].get())
        self.avatar_saved_box=ttk.Combobox(editor,textvariable=self.saved_avatar_var,state="readonly",width=26)
        self.avatar_saved_box.pack(anchor="w",pady=(8,4))
        actions=tk.Frame(editor,bg=PANEL);actions.pack(fill="x",pady=4)
        self.btn(actions,"Load",self.load_avatar).pack(side="left",padx=(0,5))
        self.btn(actions,"New template",self.reset_avatar).pack(side="left",padx=5)
        self.btn(actions,"Save character",self.save_avatar,True).pack(side="left",padx=5)
        self.btn(editor,"Export character SVG",self.export_avatar).pack(anchor="w",pady=5)
        tk.Label(editor,text="Ekspor SVG transparan dan overlay siaran VTUBE tersedia. Ini avatar ilustrasi 2D; rigging, lip-sync, dan tracking belum termasuk.",bg=PANEL,fg=AMBER,wraplength=490,justify="left").pack(anchor="w",pady=(8,0))
        for variable in (self.avatar_name_var,self.avatar_outfit_var,self.avatar_hair_style_var,self.avatar_expression_var,*self.avatar_color_vars.values()):
            variable.trace_add("write",lambda *_args:self.update_avatar_preview())
        self.refresh_avatar_list()
        self.update_avatar_preview()

    def _avatar_data_from_controls(self):
        data={"name":self.avatar_name_var.get().strip() or "VTUBE Avatar",
              "template":self.avatar_template_var.get(),"outfit":self.avatar_outfit_var.get(),
              "hair_style":self.avatar_hair_style_var.get(),"expression":self.avatar_expression_var.get()}
        data.update({field:var.get() for field,var in self.avatar_color_vars.items()})
        return data

    def update_avatar_preview(self):
        if not hasattr(self,"avatar_canvas") or not self.avatar_canvas.winfo_exists():return
        data=self._avatar_data_from_controls()
        self.active_character=data
        c=self.avatar_canvas;c.delete("all")
        c.create_rectangle(0,0,330,445,fill="#24283a",outline="")
        c.create_oval(95,18,235,158,fill=data["hair_color"],outline="#332B42",width=3)
        skin=data["skin_color"];hair=data["hair_color"];outfit=data["outfit_color"];eye=data["eye_color"]
        c.create_polygon(107,278,81,355,75,411,117,415,137,313,fill=skin,outline="#332B42",width=3)
        c.create_polygon(223,278,249,355,255,411,213,415,193,313,fill=skin,outline="#332B42",width=3)
        c.create_polygon(112,271,165,245,219,271,245,410,85,410,fill=outfit,outline="#332B42",width=4)
        if data["outfit"]=="Formal":
            c.create_polygon(164,275,165,305,165,395,195,395,195,305,196,275,fill="#F3F0F7",outline="#332B42",width=2)
            c.create_polygon(164,275,180,302,165,320,154,290,fill="#D75D78",outline="#332B42")
        elif data["outfit"]=="Fantasy":
            c.create_polygon(165,278,180,301,165,323,150,301,fill="#E9C66D",outline="#332B42")
            c.create_line(130,343,210,343,fill="#E9C66D",width=6)
        elif data["outfit"] in ("Hoodie","Jacket"):
            c.create_arc(138,265,202,333,start=0,extent=-180,style="arc",outline="#D8E6EA",width=6)
            if data["outfit"]=="Jacket":c.create_line(180,300,180,410,fill="#D8E6EA",width=4)
        else:
            c.create_line(143,340,217,340,fill="#D7DCEF",width=5)
        if data["hair_style"]=="Twin tails":
            c.create_polygon(105,93,72,104,52,209,82,229,111,148,fill=hair,outline="#332B42",width=3)
            c.create_polygon(218,93,251,104,271,209,241,229,212,148,fill=hair,outline="#332B42",width=3)
        elif data["hair_style"]=="Long":
            c.create_polygon(103,91,93,192,103,263,129,268,138,130,fill=hair,outline="#332B42",width=3)
            c.create_polygon(217,91,227,192,217,263,191,268,182,130,fill=hair,outline="#332B42",width=3)
        elif data["hair_style"]=="Side":
            c.create_polygon(100,82,85,143,105,207,124,159,fill=hair,outline="#332B42",width=3)
        c.create_oval(105,58,225,222,fill=skin,outline="#332B42",width=3)
        c.create_polygon(105,117,112,59,170,41,218,58,229,111,195,88,161,96,123,128,fill=hair,outline="#332B42",width=3)
        c.create_oval(130,124,146,153,fill="#ffffff",outline="#332B42",width=2)
        c.create_oval(184,124,200,153,fill="#ffffff",outline="#332B42",width=2)
        c.create_oval(136,131,144,148,fill=eye,outline="")
        c.create_oval(190,131,198,148,fill=eye,outline="")
        c.create_line(127,114,148,111,fill="#332B42",width=3)
        c.create_line(182,111,203,114,fill="#332B42",width=3)
        if data["expression"]=="Surprised":c.create_oval(162,168,173,184,fill="#9D5366",outline="")
        elif data["expression"]=="Neutral":c.create_line(157,176,178,176,fill="#9D5366",width=3)
        else:c.create_arc(153,160,182,188,start=205,extent=130,style="arc",outline="#9D5366",width=3)
        c.create_text(165,432,text=data["name"],fill=TEXT,font=("TkDefaultFont",11,"bold"))

    def select_avatar_template(self,event=None):
        data=new_character(self.avatar_template_var.get())
        for field in COLOR_FIELDS:self.avatar_color_vars[field].set(data[field])
        self.avatar_outfit_var.set(data["outfit"]);self.avatar_hair_style_var.set(data["hair_style"])
        self.avatar_expression_var.set(data["expression"])
        self.update_avatar_preview()

    def choose_avatar_color(self,field):
        color=colorchooser.askcolor(title=f"Pilih warna {field.replace('_color','')}",initialcolor=self.avatar_color_vars[field].get())
        if color and color[1]:self.avatar_color_vars[field].set(color[1].upper())

    def _avatar_directory(self):
        folder=APP_DIR/"characters";folder.mkdir(parents=True,exist_ok=True);return folder

    def refresh_avatar_list(self):
        names=sorted(path.stem for path in self._avatar_directory().glob("*.json"))
        self.avatar_saved_box.configure(values=names)
        if names and not self.saved_avatar_var.get():self.saved_avatar_var.set(names[0])

    def reset_avatar(self):
        data=new_character(self.avatar_template_var.get())
        self.avatar_name_var.set(data["name"])
        self.avatar_outfit_var.set(data["outfit"]);self.avatar_hair_style_var.set(data["hair_style"])
        self.avatar_expression_var.set(data["expression"])
        for field in COLOR_FIELDS:self.avatar_color_vars[field].set(data[field])
        self.status_var.set("Template baru dimuat · belum disimpan")

    def save_avatar(self):
        data=self._avatar_data_from_controls()
        filename=re.sub(r"[^A-Za-z0-9_-]+","-",data["name"]).strip("-")[:48]
        if not filename:
            messagebox.showerror("Nama karakter","Masukkan nama karakter yang valid.");return
        try:
            target=self._avatar_directory()/f"{filename}.json"
            target.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf-8")
            self.active_character=data;self._save_active_character(data);self.saved_avatar_var.set(filename);self.refresh_avatar_list()
            self.status_var.set(f"Karakter disimpan · {data['name']}")
            messagebox.showinfo("Avatar Studio",f"Karakter tersimpan:\n{target}")
        except OSError as error:
            messagebox.showerror("Simpan karakter",f"Tidak dapat menyimpan karakter: {error}")

    def load_avatar(self):
        filename=self.saved_avatar_var.get()
        if not filename:return messagebox.showinfo("Avatar Studio","Belum ada karakter tersimpan.")
        try:
            data=json.loads((self._avatar_directory()/f"{filename}.json").read_text(encoding="utf-8"))
            self._set_avatar_controls(data);self.active_character=self._avatar_data_from_controls();self._save_active_character(self.active_character)
            self.status_var.set(f"Karakter dimuat · {data.get('name',filename)}")
        except (OSError,ValueError) as error:
            messagebox.showerror("Avatar Studio",f"Tidak dapat memuat karakter: {error}")

    def _set_avatar_controls(self,data):
        template=data.get("template","Luna")
        self.avatar_template_var.set(template if template in TEMPLATES else "Luna")
        self.avatar_name_var.set(data.get("name","VTUBE Avatar"))
        self.avatar_outfit_var.set(data.get("outfit","Hoodie"))
        self.avatar_hair_style_var.set(data.get("hair_style","Long"))
        self.avatar_expression_var.set(data.get("expression","Smile"))
        defaults=new_character(self.avatar_template_var.get())
        for field in COLOR_FIELDS:
            value=str(data.get(field,defaults[field]))
            self.avatar_color_vars[field].set(value if re.fullmatch(r"#[0-9A-Fa-f]{6}",value) else defaults[field])
        self.update_avatar_preview()

    def export_avatar(self):
        data=self._avatar_data_from_controls()
        target=filedialog.asksaveasfilename(title="Ekspor avatar SVG",defaultextension=".svg",
            initialfile=f"{data['name']}.svg",filetypes=[("SVG vector image","*.svg")])
        if not target:return
        try:
            Path(target).write_text(render_avatar_svg(data),encoding="utf-8")
            self.active_character=data
            self._save_active_character(data)
            self.status_var.set(f"Avatar SVG diekspor · {target}")
            messagebox.showinfo("Ekspor avatar",f"Ilustrasi SVG transparan berhasil diekspor:\n{target}")
        except OSError as error:
            messagebox.showerror("Ekspor avatar",f"Tidak dapat mengekspor SVG: {error}")

    def _audio_sources(self):
        try:
            r=subprocess.run(["pactl","list","short","sources"],capture_output=True,text=True,timeout=4)
            if r.returncode==0:
                return [(line.split("\t")[1], line.split("\t")[1]) for line in r.stdout.splitlines() if len(line.split("\t"))>=2 and not line.split("\t")[1].endswith(".monitor")]
        except Exception: pass
        return []

    def _audio_sinks(self):
        try:
            r=subprocess.run(["pactl","list","short","sinks"],capture_output=True,text=True,timeout=4)
            if r.returncode==0:
                return [(line.split("\t")[1], line.split("\t")[1]) for line in r.stdout.splitlines() if len(line.split("\t"))>=2]
        except Exception: pass
        return []

    def _camera_devices(self):
        devs=[]
        import glob
        for path in sorted(glob.glob('/dev/video*')):
            devs.append((path,path))
        return devs

    def close_app(self):
        self.stop_live_stream(show_message=False)
        self.destroy()

    def save_live_settings(self):
        if self._save_stream_settings():
            self.status_var.set("Pengaturan siaran VTUBE disimpan")
            messagebox.showinfo("VTUBE Live","Server, konfigurasi sumber dan pengaturan siaran disimpan di profil lokal khusus pengguna.")

    def start_live_stream(self):
        if self.live_process and self.live_process.poll() is None:
            return messagebox.showinfo("VTUBE Live","Siaran VTUBE sudah berjalan.")
        if hasattr(self,"camera_var") and self.camera_var.get():
            self.stream_settings["camera_device"]=self.camera_var.get()
        if not self._save_stream_settings():
            return
        ffmpeg=shutil.which("ffmpeg")
        if not ffmpeg:
            return messagebox.showerror("VTUBE Live","Media engine VTUBE (FFmpeg) tidak ditemukan pada image OS.")
        try:
            target=rtmp_target(self.stream_server_var.get(),self.stream_key_var.get())
            width,height=RESOLUTIONS[self.live_resolution_var.get()]
            fps=int(self.live_fps_var.get())
            bitrate=VIDEO_BITRATES[self.live_bitrate_var.get()]
            phone_host=self.live_phone_host_var.get().strip()
            pair_code=self.live_pair_code_var.get().strip()
            source=self.live_video_source_var.get()
            audio=self.live_audio_source_var.get()
            if source.startswith("phone-") or audio=="phone-mic":
                phone_stream_url(phone_host,pair_code,"screen.mjpeg")
            camera_device=""
            if source=="webcam":
                devices=self._camera_devices()
                if not devices:raise ValueError("Kamera laptop/USB tidak terdeteksi di /dev/video*.")
                camera_device=self.stream_settings.get("camera_device",devices[0][0])
                if camera_device not in {device for device,_label in devices}:
                    raise ValueError("Pilih ulang kamera lokal di VTUBE Connect Hub.")
            audio_device="default"
            if audio=="system-mic":
                result=subprocess.run(["pactl","get-default-source"],capture_output=True,text=True,timeout=4)
                if result.returncode:raise RuntimeError(result.stderr.strip() or "Tidak dapat membaca input mikrofon sistem.")
                audio_device=result.stdout.strip()
            if source=="desktop" and not os.environ.get("DISPLAY"):
                raise ValueError("Desktop capture memerlukan sesi desktop X11 yang aktif.")

            overlay_path=APP_DIR/"live-overlay.png"
            qr_name=self.stream_settings.get("qr_image","")
            qr_path=APP_DIR/qr_name if qr_name else ""
            if qr_path and not Path(qr_path).is_file():
                raise ValueError("File QR yang tersimpan tidak ditemukan. Pilih ulang gambar QR di Donation Center.")
            write_stream_overlay(
                overlay_path,self.active_character,self.donation_goal,
                self.stream_settings.get("donation_link",""),qr_path,
            )
            command=build_stream_command(
                ffmpeg,source,audio,target,width,height,fps,bitrate,str(overlay_path),
                phone_host=phone_host,pair_code=pair_code,camera_device=camera_device,
                display=os.environ.get("DISPLAY",""),audio_device=audio_device,
            )
            log_directory=APP_DIR/"logs";log_directory.mkdir(parents=True,exist_ok=True)
            log_path=log_directory/"live-engine.log"
            self.live_log_handle=log_path.open("ab")
            self.live_process=subprocess.Popen(
                command,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                stderr=self.live_log_handle,start_new_session=True,
            )
            self.live_status_var.set("VTUBE LIVE · sedang menghubungkan ke RTMP")
            self.status_var.set("VTUBE internal media engine started")
            self.live_poll_job=self.after(1000,self._poll_live_stream)
        except (KeyError,ValueError,OSError,RuntimeError,subprocess.SubprocessError) as error:
            self.live_status_var.set("VTUBE Live belum berjalan")
            messagebox.showerror("VTUBE Live",str(error))

    def _poll_live_stream(self):
        self.live_poll_job=None
        process=self.live_process
        if not process:return
        result=process.poll()
        if result is None:
            self.live_status_var.set("VTUBE LIVE · media engine aktif")
            self.live_poll_job=self.after(1000,self._poll_live_stream)
            return
        log_path=APP_DIR/"logs"/"live-engine.log"
        detail=""
        try:
            detail=log_path.read_text(encoding="utf-8",errors="replace")[-5000:].strip()
        except OSError as error:
            detail=f"Tidak bisa membaca log engine: {error}"
        self.live_process=None
        if self.live_log_handle:self.live_log_handle.close();self.live_log_handle=None
        self.live_status_var.set(f"VTUBE Live berhenti (exit {result})")
        self.status_var.set("VTUBE internal media engine stopped")
        if detail:messagebox.showerror("VTUBE Live",f"Media engine berhenti dengan kode {result}.\n\n{detail[-1800:]}")
        else:messagebox.showerror("VTUBE Live",f"Media engine berhenti dengan kode {result}.")

    def stop_live_stream(self,show_message=True):
        if self.live_poll_job:
            self.after_cancel(self.live_poll_job);self.live_poll_job=None
        process=self.live_process
        self.live_process=None
        if process and process.poll() is None:
            process.terminate()
            try:process.wait(timeout=4)
            except subprocess.TimeoutExpired:
                process.kill();process.wait(timeout=4)
        if self.live_log_handle:
            self.live_log_handle.close();self.live_log_handle=None
        if hasattr(self,"live_status_var"):self.live_status_var.set("VTUBE Live stopped")
        if show_message:self.status_var.set("VTUBE live stream stopped")

    def page_audio(self):
        self.title_block("Audio & Microphone Hub","Pilih mikrofon laptop, headset USB, sound card, atau mikrofon HP setelah HP terhubung sebagai sumber audio.")
        p=tk.Frame(self.content,bg=PANEL,padx=18,pady=18);p.pack(fill="both",expand=True)
        self.section(p,"Input microphone","Daftar perangkat berasal dari PipeWire/PulseAudio pada Linux. Sambungkan perangkat dulu lalu tekan Refresh.")
        self.audio_input_var=tk.StringVar()
        sources=self._audio_sources()
        self.audio_input_box=ttk.Combobox(p,textvariable=self.audio_input_var,values=[x[0] for x in sources],state="readonly",width=72)
        self.audio_input_box.pack(anchor="w",pady=(10,5))
        if sources:self.audio_input_box.current(0)
        row=tk.Frame(p,bg=PANEL);row.pack(anchor="w",pady=5)
        self.btn(row,"Refresh devices",self.refresh_audio_devices).pack(side="left",padx=(0,8))
        self.btn(row,"Set as system microphone",self.set_default_microphone,True).pack(side="left",padx=(0,8))
        tk.Label(p,text="Pilih input mikrofon di sini, atau pilih phone-mic pada Live Studio untuk menerima PCM dari VTUBE Connect langsung di engine live VTUBE.",bg=PANEL,fg=CYAN,wraplength=850,justify="left").pack(anchor="w",pady=(18,8))
        self.section(p,"Audio output / headphones")
        sinks=self._audio_sinks();self.audio_output_var=tk.StringVar()
        self.audio_output_box=ttk.Combobox(p,textvariable=self.audio_output_var,values=[x[0] for x in sinks],state="readonly",width=72)
        self.audio_output_box.pack(anchor="w",pady=8)
        if sinks:self.audio_output_box.current(0)
        self.btn(p,"Set as system output",self.set_default_output).pack(anchor="w")
        tk.Label(p,text="Catatan: pengaturan ini memilih perangkat default sistem. Mixer per-sumber, noise suppression, gate, compressor dan audio sync akan dibuat sebagai modul VTUBE berikutnya.",bg=PANEL,fg=MUTED,wraplength=850,justify="left").pack(anchor="w",pady=18)

    def refresh_audio_devices(self):
        sources=self._audio_sources();sinks=self._audio_sinks()
        if hasattr(self,"audio_input_box") and self.audio_input_box.winfo_exists():
            self.audio_input_box.configure(values=[x[0] for x in sources]);self.audio_input_var.set(sources[0][0] if sources else "")
            self.audio_output_box.configure(values=[x[0] for x in sinks]);self.audio_output_var.set(sinks[0][0] if sinks else "")
        self.status_var.set(f"Audio devices refreshed · {len(sources)} input(s), {len(sinks)} output(s)")
        if not sources:messagebox.showinfo("Audio devices","Belum ada input audio terdeteksi oleh pactl. Pastikan PipeWire/PulseAudio aktif dan perangkat tersambung.")

    def set_default_microphone(self):
        name=self.audio_input_var.get()
        if not name:return messagebox.showwarning("Microphone","Tidak ada input yang dipilih.")
        try:
            r=subprocess.run(["pactl","set-default-source",name],capture_output=True,text=True,timeout=4)
            if r.returncode:raise RuntimeError(r.stderr.strip() or "pactl failed")
            self.status_var.set(f"Default microphone set · {name}");messagebox.showinfo("Microphone",f"Mikrofon default sistem diatur ke:\n{name}")
        except Exception as e:messagebox.showerror("Microphone",f"Tidak bisa mengubah input default: {e}")

    def set_default_output(self):
        name=self.audio_output_var.get()
        if not name:return messagebox.showwarning("Audio output","Tidak ada output yang dipilih.")
        try:
            r=subprocess.run(["pactl","set-default-sink",name],capture_output=True,text=True,timeout=4)
            if r.returncode:raise RuntimeError(r.stderr.strip() or "pactl failed")
            self.status_var.set(f"Default output set · {name}");messagebox.showinfo("Audio output",f"Output default diatur ke:\n{name}")
        except Exception as e:messagebox.showerror("Audio output",f"Tidak bisa mengubah output default: {e}")

    def page_donations(self):
        self.title_block("Donation Center","Atur target, tautan Saweria, dan gambar QR untuk ditampilkan langsung oleh VTUBE Live. Notifikasi transaksi nyata memerlukan webhook resmi.")
        p=tk.Frame(self.content,bg=PANEL,padx=18,pady=18);p.pack(fill="both",expand=True)
        tk.Label(p,text="DONATION GOAL (IDR)",bg=PANEL,fg=MUTED).pack(anchor="w")
        self.goal_var=tk.StringVar(value=str(self.donation_goal))
        tk.Entry(p,textvariable=self.goal_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat").pack(anchor="w",pady=(5,12))
        tk.Label(p,text="TOTAL RECEIVED (TEST / LOCAL)",bg=PANEL,fg=MUTED).pack(anchor="w")
        self.total_label=tk.Label(p,text=f"Rp {self.donation_total:,}",bg=PANEL,fg=GREEN,font=("TkDefaultFont",20,"bold"));self.total_label.pack(anchor="w",pady=5)
        self.progress=ttk.Progressbar(p,length=500,maximum=100,value=min(100,self.donation_total/max(1,self.donation_goal)*100));self.progress.pack(anchor="w",pady=8)
        self.btn(p,"Save goal",self.save_goal).pack(anchor="w",pady=6)
        self.btn(p,"Simulate Rp 5.000 donation",lambda:self.add_donation(5000,"Supporter"),True).pack(anchor="w",pady=6)
        self.btn(p,"Simulate custom donation",self.custom_donation).pack(anchor="w",pady=6)
        self.btn(p,"Show overlay preview",self.open_overlay).pack(anchor="w",pady=6)
        self.section(p,"Link Saweria dan QR donasi","Link dan QR dirender langsung ke video siaran VTUBE; pembayaran dan pembaruan goal otomatis belum terhubung.")
        self.donation_link_var=tk.StringVar(value=self.stream_settings.get("donation_link",""))
        tk.Entry(p,textvariable=self.donation_link_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=72).pack(anchor="w",pady=(7,5),ipady=6)
        qrrow=tk.Frame(p,bg=PANEL);qrrow.pack(fill="x",pady=4)
        self.qr_status=tk.Label(qrrow,text=self.stream_settings.get("qr_image") or "QR belum dipilih",bg=PANEL,fg=MUTED,wraplength=480,justify="left")
        self.qr_status.pack(side="left",anchor="w")
        self.btn(qrrow,"Choose QR image",self.choose_donation_qr).pack(side="left",padx=10)
        self.btn(qrrow,"Clear QR",self.clear_donation_qr).pack(side="left",padx=5)
        actions=tk.Frame(p,bg=PANEL);actions.pack(anchor="w",pady=8)
        self.btn(actions,"Save link / QR",self.save_donation_settings).pack(side="left",padx=(0,8))
        self.btn(actions,"Buka Live Studio",lambda:self.show_page("Live Studio"),True).pack(side="left",padx=8)
        tk.Label(p,text="Saat siaran dimulai, aplikasi VTUBE menggabungkan layar/kamera, avatar dan panel donasi lalu mengirim video ke server RTMP/RTMPS. Goal masih nilai manual; alert di atas hanya simulasi.",bg=PANEL,fg=AMBER,wraplength=780,justify="left").pack(anchor="w",pady=8)

    def save_goal(self):
        try:self.donation_goal=max(1,int(self.goal_var.get()))
        except ValueError:messagebox.showerror("Invalid goal","Enter a whole number in rupiah.");return
        self.save_current_profile();self._save_stream_settings();self.update_donation_ui()

    def choose_donation_qr(self):
        source=filedialog.askopenfilename(title="Pilih gambar QR donasi",
            filetypes=[("PNG or JPEG image","*.png *.jpg *.jpeg"),("All files","*.*")])
        if not source:return
        suffix=Path(source).suffix.lower()
        if suffix not in (".png",".jpg",".jpeg"):
            messagebox.showerror("QR donasi","Pilih gambar PNG atau JPEG.");return
        try:
            APP_DIR.mkdir(parents=True,exist_ok=True)
            target=APP_DIR/f"donation-qr{suffix}"
            if Path(source).resolve()!=target.resolve():shutil.copy2(source,target)
            self.stream_settings["qr_image"]=target.name
            self.qr_status.configure(text=f"Gambar QR tersimpan: {target.name}")
        except OSError as error:messagebox.showerror("QR donasi",f"Tidak dapat menyalin gambar QR: {error}")

    def clear_donation_qr(self):
        self.stream_settings["qr_image"]=""
        self.qr_status.configure(text="QR belum dipilih")
        self.status_var.set("QR dihapus dari pengaturan overlay")

    def save_donation_settings(self):
        link=self.donation_link_var.get().strip()
        if link:
            parsed=urllib.parse.urlsplit(link)
            if parsed.scheme not in ("http","https") or not parsed.netloc:
                messagebox.showerror("Link donasi","Masukkan link lengkap yang diawali https:// atau http://.");return
        if self._save_stream_settings():
            self.status_var.set("Link dan QR donasi tersimpan lokal")
            messagebox.showinfo("Donation Center","Link, QR, dan goal tersimpan untuk overlay. Notifikasi pembayaran nyata belum diintegrasikan.")

    def custom_donation(self):
        w=tk.Toplevel(self);w.title("Test donation");w.configure(bg=PANEL);w.geometry("330x190")
        amount=tk.StringVar(value="10000");who=tk.StringVar(value="Supporter")
        tk.Label(w,text="Name",bg=PANEL,fg=TEXT).pack(anchor="w",padx=14,pady=(12,3))
        tk.Entry(w,textvariable=who).pack(fill="x",padx=14)
        tk.Label(w,text="Amount (IDR)",bg=PANEL,fg=TEXT).pack(anchor="w",padx=14,pady=(8,3))
        tk.Entry(w,textvariable=amount).pack(fill="x",padx=14)
        def go():
            try:a=int(amount.get())
            except ValueError:messagebox.showerror("Invalid","Amount must be a number.",parent=w);return
            self.add_donation(a,who.get().strip() or "Supporter");w.destroy()
        self.btn(w,"Trigger test alert",go,True).pack(anchor="e",padx=14,pady=12)

    def add_donation(self,amount,who):
        if amount<0:return
        self.donation_total+=amount
        self.update_donation_ui()
        self.profiles.setdefault(self.profile.get(),{}).update({"donation_total":self.donation_total,"donation_goal":self.donation_goal})
        save_profiles(self.profiles)
        self.show_alert(who,amount)
        self.status_var.set(f"Test donation alert · Rp {amount:,}")

    def update_donation_ui(self):
        if hasattr(self,"total_label") and self.total_label.winfo_exists():self.total_label.configure(text=f"Rp {self.donation_total:,}")
        if hasattr(self,"progress") and self.progress.winfo_exists():self.progress.configure(value=min(100,self.donation_total/max(1,self.donation_goal)*100))

    def open_overlay(self):
        if self.overlay_window and self.overlay_window.winfo_exists():
            self.overlay_window.deiconify();self.overlay_window.lift();return
        w=tk.Toplevel(self);w.title("VTUBE Donation Overlay Preview");w.geometry("520x180+80+80");w.configure(bg="#101321")
        w.attributes("-topmost",True);self.overlay_window=w
        tk.Label(w,text="VTUBE DONATION ALERT PREVIEW",bg="#101321",fg=CYAN,font=("TkDefaultFont",10,"bold")).pack(pady=(18,8))
        self.overlay_label=tk.Label(w,text="Waiting for a test alert…",bg="#101321",fg=TEXT,font=("TkDefaultFont",18,"bold"),wraplength=470)
        self.overlay_label.pack(pady=14)
        tk.Label(w,text="Preview only · no real payment connected",bg="#101321",fg=MUTED).pack()

    def show_alert(self,who,amount):
        self.open_overlay()
        if self.overlay_label and self.overlay_label.winfo_exists():
            self.overlay_label.configure(text=f"{who} donated Rp {amount:,} ✦")
            self.overlay_window.after(6000,lambda:self.overlay_label.configure(text="Waiting for a test alert…") if self.overlay_label and self.overlay_label.winfo_exists() else None)

    def page_connect(self):
        self.title_block("VTUBE Connect Hub","Hubungkan VTUBE Connect di Android ke Control Center melalui jaringan lokal.")
        modes=tk.Frame(self.content,bg=PANEL,padx=16,pady=14);modes.pack(fill="x",pady=(0,12))
        self.section(modes,"Pilih mode input")
        self.input_mode_var=tk.StringVar(value="Webcam USB / kamera laptop")
        self.input_mode_box=ttk.Combobox(modes,textvariable=self.input_mode_var,state="readonly",width=42,values=["Webcam USB / kamera laptop","Kamera HP via VTUBE Connect","Kamera IP / URL stream","Capture card HDMI / USB","Mikrofon eksternal USB / headset","HP sebagai kamera + mikrofon","Mobile gaming capture"])
        self.input_mode_box.pack(anchor="w",pady=8)
        self.input_mode_box.bind("<<ComboboxSelected>>",lambda e:self.update_connect_mode())
        row=tk.Frame(self.content,bg=BG);row.pack(fill="x")
        for title,value,note,color in [("USB","Deteksi lokal","Webcam/capture card via /dev/video*",GREEN),("Wi-Fi","VTUBE Connect","Preview HP eksperimental melalui jaringan lokal",CYAN),("Audio","Input system","Mikrofon USB/headset via PipeWire",ACCENT)]:
            self.card(row,title,value,note,color).pack(side="left",fill="both",expand=True,padx=(0,10))
        p=tk.Frame(self.content,bg=PANEL,padx=18,pady=16);p.pack(fill="both",expand=True,pady=(12,0))
        self.section(p,"Kamera yang terdeteksi","Pilih perangkat /dev/video* untuk dipakai sebagai sumber video oleh engine VTUBE Live.")
        self.camera_var=tk.StringVar();self.camera_box=ttk.Combobox(p,textvariable=self.camera_var,state="readonly",width=60)
        self.camera_box.pack(anchor="w",pady=8)
        self.refresh_camera_devices()
        row2=tk.Frame(p,bg=PANEL);row2.pack(anchor="w",pady=4)
        self.btn(row2,"Refresh camera list",self.refresh_camera_devices).pack(side="left",padx=(0,8))
        self.btn(row2,"Open Audio Studio",lambda:self.show_page("Audio Studio")).pack(side="left")
        self.section(p,"Pair Android melalui Wi-Fi","Di VTUBE Connect, tekan Start lalu salin alamat IP HP dan Pair code yang tampil. Untuk berbagi layar, tekan Share phone screen di Android dan setujui dialog izin sistem. Laptop dan HP harus di jaringan lokal tepercaya; jangan buka port aplikasi ke internet.")
        pairrow=tk.Frame(p,bg=PANEL);pairrow.pack(fill="x",pady=7)
        tk.Label(pairrow,text="Alamat IP HP",bg=PANEL,fg=TEXT).pack(side="left",padx=(0,8))
        self.phone_host_var=tk.StringVar(value=self.stream_settings.get("phone_host",""))
        tk.Entry(pairrow,textvariable=self.phone_host_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=22).pack(side="left",ipady=7,padx=(0,12))
        tk.Label(pairrow,text="Pair code",bg=PANEL,fg=TEXT).pack(side="left",padx=(0,8))
        self.phone_token_var=tk.StringVar(value=self.stream_settings.get("pair_code",""))
        tk.Entry(pairrow,textvariable=self.phone_token_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=12,show="•").pack(side="left",ipady=7,padx=(0,12))
        self.btn(pairrow,"Check connection",self.check_phone_connection,True).pack(side="left")
        self.btn(p,"Pakai sumber HP di Live Studio",self.use_phone_in_live,True).pack(anchor="w",pady=6)
        self.connect_status=tk.Label(p,text="Belum terhubung · pair code hanya berlaku selama server Android berjalan.",bg=PANEL,fg=AMBER,wraplength=850,justify="left")
        self.connect_status.pack(anchor="w",pady=(10,0))
        self.connect_help=tk.Label(p,text="Kamera, layar, dan mikrofon HP dapat dipilih sebagai sumber oleh VTUBE Live setelah izin eksplisit. Sambungan ini masih prototipe jaringan lokal. Remote control jarak jauh, USB, dan relay internet belum tersedia.",bg=PANEL,fg=MUTED,wraplength=850,justify="left")
        self.connect_help.pack(anchor="w",pady=(12,0))

    def _phone_endpoint(self, path):
        host=self.phone_host_var.get().strip()
        token=self.phone_token_var.get().strip().upper()
        try:
            return phone_stream_url(host,token,path)
        except ValueError as error:
            raise ValueError("Masukkan IPv4 privat HP dan Pair code 6 karakter yang valid.") from error

    def check_phone_connection(self):
        try: url=self._phone_endpoint("status")
        except ValueError as e: return messagebox.showwarning("VTUBE Connect",str(e))
        self.stream_settings["phone_host"]=self.phone_host_var.get().strip()
        self.stream_settings["pair_code"]=self.phone_token_var.get().strip().upper()
        if hasattr(self,"live_phone_host_var"):
            self.live_phone_host_var.set(self.stream_settings["phone_host"])
            self.live_pair_code_var.set(self.stream_settings["pair_code"])
        if not self._save_stream_settings():return
        self.connect_status.configure(text="Memeriksa koneksi ke HP…",fg=CYAN)
        def worker():
            try:
                with urllib.request.urlopen(url,timeout=4) as response:
                    data=json.loads(response.read().decode("utf-8"))
                if data.get("status")!="ok": raise RuntimeError("Respons status tidak dikenali")
                msg="Terhubung ke VTUBE Connect · kamera dan mikrofon tersedia saat dipilih."
                color=GREEN
            except Exception as e:
                msg=f"Koneksi gagal: {e}. Pastikan aplikasi aktif, IP dan Pair code benar, serta firewall mengizinkan port 8765."
                color=AMBER
            self.after(0,lambda:self.connect_status.configure(text=msg,fg=color) if self.connect_status.winfo_exists() else None)
        threading.Thread(target=worker,daemon=True).start()

    def use_phone_in_live(self):
        try:
            phone_stream_url(self.phone_host_var.get(),self.phone_token_var.get(),"screen.mjpeg")
        except ValueError as error:
            return messagebox.showwarning("VTUBE Connect",str(error))
        self.stream_settings.update({
            "phone_host":self.phone_host_var.get().strip(),
            "pair_code":self.phone_token_var.get().strip().upper(),
            "video_source":"phone-screen",
            "audio_source":"phone-mic",
        })
        if hasattr(self,"live_phone_host_var"):
            self.live_phone_host_var.set(self.stream_settings["phone_host"])
            self.live_pair_code_var.set(self.stream_settings["pair_code"])
            self.live_video_source_var.set("phone-screen")
            self.live_audio_source_var.set("phone-mic")
        if not self._save_stream_settings():return
        self.status_var.set("Sumber HP dipilih untuk VTUBE Live")
        self.show_page("Live Studio")

    def update_connect_mode(self):
        mode=self.input_mode_var.get()
        if mode=="Kamera IP / URL stream":
            msg="Masukkan URL stream dari aplikasi kamera HP yang kompatibel. Pastikan laptop dan HP dapat saling menjangkau melalui jaringan."
        elif mode=="Capture card HDMI / USB":
            msg="Hubungkan capture card; jika didukung Linux, perangkat akan muncul sebagai /dev/video* dan bisa dipilih sebagai sumber di Live Studio."
        elif mode=="Mikrofon eksternal USB / headset":
            msg="Buka Audio Studio untuk melihat input yang terdeteksi dan memilih mikrofon default sistem."
        elif mode in ("Kamera HP via VTUBE Connect","HP sebagai kamera + mikrofon","Mobile gaming capture"):
            msg="VTUBE Connect tersedia sebagai proyek sumber di folder vtube-connect/android; APK belum dibuat. Setelah aplikasi dijalankan, tekan Start, lalu gunakan Share phone screen dan setujui izin Android untuk berbagi layar. Kamera, layar, dan audio tersedia melalui endpoint lokal eksperimental; koneksi jarak jauh dan tracking wajah belum tersedia."
        else:
            msg="Pilih perangkat /dev/video* untuk sumber video di Live Studio. Mikrofon dipilih terpisah di Audio Studio."
        self.connect_help.configure(text=msg)

    def refresh_camera_devices(self):
        devices=self._camera_devices()
        if hasattr(self,"camera_box") and self.camera_box.winfo_exists():
            available=[device for device,_label in devices]
            selected=self.camera_var.get()
            if selected not in available:
                selected=self.stream_settings.get("camera_device","")
            if selected not in available:selected=available[0] if available else ""
            self.camera_box.configure(values=available);self.camera_var.set(selected)
            if selected:self.stream_settings["camera_device"]=selected
        self.status_var.set(f"Camera scan complete · {len(devices)} local video device(s)")
        if not devices: self.status_var.set("No /dev/video* device found · connect a webcam/capture card or configure an IP stream")

    def page_features(self):
        self.title_block("Feature Center", "Peta fitur VTUBE OS: status implementasi dibuat transparan agar fitur simulasi tidak dikira sudah terhubung ke layanan nyata.")
        sections = [
            ("LIVE STUDIO", ["Live RTMP internal VTUBE dengan FFmpeg — tersedia sebagai prototipe", "Komposisi avatar 2D, goal dan QR ditangani engine VTUBE", "Sumber video: layar/kamera HP, webcam, atau desktop X11", "Koneksi platform lain, preview berperforma tinggi, dan encoder hardware — pengembangan"]),
            ("AVATAR & TRACKING", ["Editor ilustrasi 2D: preview, template, warna, pakaian, ekspresi — aktif", "Simpan/muat karakter lokal dan ekspor SVG — aktif", "Impor VRM/Live2D, rigging, face/hand tracking — pengembangan", "Lip-sync, emote dan hotkey avatar — rancangan"]),
            ("DEVICE & AUDIO", ["Deteksi kamera Linux /dev/video* — aktif", "Pilih mikrofon/output via PipeWire/PulseAudio — aktif", "Kamera, layar, dan mikrofon HP setelah izin Android — endpoint lokal eksperimental", "USB/relay internet dan pairing produksi — pengembangan"]),
            ("STREAM & COMMUNITY", ["Goal, link Saweria dan QR dirender di stream internal — aktif", "Donation alert simulasi — aktif (bukan transaksi nyata)", "Saweria webhook/API resmi — belum terhubung", "Chat YouTube/Twitch/TikTok — integrasi sesuai API/izin platform", "Backup, plugin API, bug report, roadmap — tahap awal"]),
            ("SYSTEM & MODES", ["PC VTuber, webcam, mic eksternal, mobile gaming — pilihan mode UI", "Remote control HP — endpoint prototipe di jaringan lokal", "Privacy/permissions dan status perangkat — dasar", "Internet relay, encryption hardening, installer/recovery — pengembangan"]),
        ]
        for title, items in sections:
            box=tk.Frame(self.content,bg=PANEL,padx=16,pady=12); box.pack(fill="x",pady=5)
            self.section(box,title)
            for item in items:
                color=GREEN if "aktif" in item or "bisa diuji" in item or "disertakan" in item else AMBER
                tk.Label(box,text="•  "+item,bg=PANEL,fg=color,wraplength=900,justify="left").pack(anchor="w",pady=3)
        self.btn(self.content,"Open VTUBE Connect Hub",lambda:self.show_page("VTUBE Connect"),True).pack(anchor="w",pady=10)

    def page_profiles(self):
        self.title_block("Profiles","Store per-game scenes and donation settings on this computer.")
        for name, data in self.profiles.items():
            row=tk.Frame(self.content,bg=PANEL,padx=14,pady=12);row.pack(fill="x",pady=5)
            tk.Label(row,text=name,bg=PANEL,fg=TEXT,font=("TkDefaultFont",11,"bold")).pack(anchor="w")
            tk.Label(row,text=f"Scene: {data.get('scene','Starting Soon')} · Goal: Rp {data.get('donation_goal',100000):,}",bg=PANEL,fg=MUTED).pack(anchor="w",pady=4)
            self.btn(row,"Use profile",lambda n=name:self.use_profile(n)).pack(anchor="e")
        self.btn(self.content,"Save current profile",self.save_current_profile,True).pack(anchor="w",pady=12)

    def use_profile(self,name):
        self.profile.set(name);data=self.profiles.get(name,{})
        self.scene.set(data.get("scene",SCENES[0]));self.donation_goal=int(data.get("donation_goal",100000));self.donation_total=int(data.get("donation_total",0))
        self.status_var.set(f"Profile loaded · {name}");self.show_page("Dashboard")

    def page_settings(self):
        self.title_block("Settings & System","Build information and tools.")
        p=tk.Frame(self.content,bg=PANEL,padx=18,pady=18);p.pack(fill="both",expand=True)
        info=f"Host: {platform.system()} {platform.release()} · Architecture: {platform.machine()} · Python {platform.python_version()}"
        tk.Label(p,text=info,bg=PANEL,fg=CYAN,wraplength=850,justify="left").pack(anchor="w",pady=(0,15))
        self.section(p,"Prototype implementation status")
        for t in ["Available: desktop navigation, scene-layout prototype, draggable placeholders and local profiles",
                  "Available: donation goal and simulated alert overlay (no real payment integration)",
                  "Available: Linux camera discovery/preview and PipeWire/PulseAudio device selection",
                  "Available prototype: 2D avatar editor, live color preview, local character save/load and SVG export",
                  "Experimental: VTUBE Connect Android source with local-network camera/audio/screen endpoints (screen share requires Android permission)",
                  "Planned: real-time scene compositor, recording/stream encoding and platform connections",
                  "Planned: 3D VRM/Live2D, face tracking, production secure transport and donation event webhook",
                  "Build runs through GitHub Actions: tools/build-iso.sh"]:
            tk.Label(p,text="•  "+t,bg=PANEL,fg=TEXT,wraplength=850,justify="left").pack(anchor="w",pady=6)
        self.btn(p,"Open project README",lambda:messagebox.showinfo("README","See README.md and docs/ROADMAP.md in the project folder.")).pack(anchor="w",pady=15)

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="VTUBE OS desktop applications")
    parser.add_argument("--page",choices=["Dashboard","Live Studio","Avatar Studio","Audio Studio","Donation Center","VTUBE Connect","Feature Center","Profiles","Settings"],default="Dashboard",help="Open a VTUBE OS module directly")
    args=parser.parse_args()
    VTubeApp(start_page=args.page).mainloop()
