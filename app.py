#!/usr/bin/env python3
"""VTUBE OS Control Center — functional early prototype.

Working now: navigation, scene selection, draggable scene elements, overlay preview,
donation simulation, local profile persistence, and basic system stats.
Not yet implemented: real camera capture, avatar rendering, audio routing, platform
authentication, video encoding/compositing, and a production-safe remote phone service.
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog
import platform, os, json, time, threading, subprocess, shutil, socket, webbrowser
from pathlib import Path

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
    def __init__(self):
        super().__init__()
        self.title("VTUBE OS — Control Center")
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
        self._style()
        self._layout()
        self.show_page("Dashboard")
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

    def page_dashboard(self):
        self.title_block("VTUBE Control Center","A single workflow for avatar, gameplay, audio, alerts and live setup.")
        row=tk.Frame(self.content,bg=BG); row.pack(fill="x")
        cards=[("Live status","OFFLINE","Encoder/stream pipeline not connected yet",AMBER),
               ("Avatar","Template ready","Preset avatar prototype · VRM renderer pending",ACCENT),
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
        self.section(right,"Live checklist","Real device and platform services are still milestones.")
        for s,c in [("○  Scene and overlay editor",CYAN),("○  Avatar renderer",ACCENT),("○  Camera and microphone",GREEN),("○  Stream destination",AMBER)]:
            tk.Label(right,text=s,bg=PANEL,fg=c,font=("TkDefaultFont",11)).pack(anchor="w",pady=8)
        self.btn(right,"Test donation overlay",lambda:self.show_page("Donation Center")).pack(anchor="w",pady=8)

    def page_live_studio(self):
        self.title_block("Live Studio","Select a scene, drag elements around the canvas, and preview a simple stream layout.")
        controls=tk.Frame(self.content,bg=BG);controls.pack(fill="x",pady=(0,10))
        tk.Label(controls,text="SCENE",bg=BG,fg=MUTED).pack(side="left",padx=(0,8))
        ttk.Combobox(controls,textvariable=self.scene,values=SCENES,state="readonly",width=20).pack(side="left")
        self.btn(controls,"Add text",lambda:self.add_scene_item("Text")).pack(side="left",padx=6)
        self.btn(controls,"Add avatar placeholder",lambda:self.add_scene_item("Avatar")).pack(side="left",padx=6)
        self.btn(controls,"Add gameplay placeholder",lambda:self.add_scene_item("Gameplay")).pack(side="left",padx=6)
        self.btn(controls,"Donation alert test",self.simulate_donation).pack(side="left",padx=6)
        self.btn(controls,"Save profile",self.save_current_profile,True).pack(side="right")
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
        self.canvas.create_rectangle(500,80,650,270,outline=ACCENT,width=2,fill="#201b32",tags=("item","avatar"))
        self.canvas.create_text(575,165,text="VTUBE\nAVATAR\nPLACEHOLDER",fill="#d8caff",font=("TkDefaultFont",12,"bold"),justify="center",tags=("item","avatar_label"))
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
        self.title_block("Avatar Studio","Starter character presets and customization plan. Full 2D/3D renderer is a later milestone.")
        row=tk.Frame(self.content,bg=BG);row.pack(fill="x")
        for title,value,note,color in [("Character preset","Luna / Nova / Kiro","Original starter presets planned",ACCENT),
            ("Hair color","#9B7BFF","Color choice can be saved",CYAN),("Outfit","Streetwear","Model assets not bundled yet",GREEN)]:
            self.card(row,title,value,note,color).pack(side="left",fill="both",expand=True,padx=(0,10))
        p=tk.Frame(self.content,bg=PANEL,padx=18,pady=18);p.pack(fill="both",expand=True,pady=(16,0))
        self.section(p,"Character customization","These controls save a concept profile; they do not recolor a 3D model until the renderer is integrated.")
        self.avatar_name=tk.StringVar(value="Luna")
        self.hair=tk.StringVar(value="#9B7BFF");self.outfit=tk.StringVar(value="Streetwear")
        r=tk.Frame(p,bg=PANEL);r.pack(anchor="w",pady=12)
        tk.Label(r,text="Preset",bg=PANEL,fg=TEXT).pack(side="left",padx=(0,8))
        ttk.Combobox(r,textvariable=self.avatar_name,values=["Luna","Nova","Kiro"],state="readonly",width=16).pack(side="left")
        r2=tk.Frame(p,bg=PANEL);r2.pack(anchor="w",pady=10)
        tk.Label(r2,text="Hair color",bg=PANEL,fg=TEXT).pack(side="left",padx=(0,8))
        tk.Label(r2,textvariable=self.hair,bg=PANEL,fg=self.hair.get()).pack(side="left",padx=8)
        self.btn(r2,"Choose color",self.choose_hair).pack(side="left")
        r3=tk.Frame(p,bg=PANEL);r3.pack(anchor="w",pady=10)
        tk.Label(r3,text="Outfit",bg=PANEL,fg=TEXT).pack(side="left",padx=(0,8))
        ttk.Combobox(r3,textvariable=self.outfit,values=["Streetwear","Gamer hoodie","Fantasy","Casual","Formal"],state="readonly",width=20).pack(side="left")
        self.btn(p,"Save avatar concept",self.save_avatar,True).pack(anchor="w",pady=12)
        tk.Label(p,text="Note: the first build contains no licensed commercial character model. Original model templates will be added as assets.",bg=PANEL,fg=AMBER,wraplength=780,justify="left").pack(anchor="w",pady=8)

    def choose_hair(self):
        c=colorchooser.askcolor(title="Choose hair color",initialcolor=self.hair.get())
        if c and c[1]:self.hair.set(c[1])

    def save_avatar(self):
        data={"preset":self.avatar_name.get(),"hair_color":self.hair.get(),"outfit":self.outfit.get()}
        APP_DIR.mkdir(parents=True,exist_ok=True)
        (APP_DIR/"avatar.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
        messagebox.showinfo("Avatar Studio","Avatar concept saved locally. Model rendering is not connected yet.")

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
        self.btn(row,"Open sound settings",lambda:self.run_system_tool(["pavucontrol"],"Install pavucontrol first if unavailable.")).pack(side="left")
        tk.Label(p,text="HP sebagai mikrofon: pilih mode VTUBE Connect, lalu sambungkan melalui aplikasi VTUBE Connect saat aplikasi Android tersedia. Alternatifnya, jika aplikasi HP menyediakan audio sink/source yang kompatibel dengan Linux, refresh perangkat di sini.",bg=PANEL,fg=CYAN,wraplength=850,justify="left").pack(anchor="w",pady=(18,8))
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
        self.title_block("Donation Center","Test donation alerts and set a goal. Live Saweria integration needs a verified official event/webhook method.")
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
        tk.Label(p,text="Simulation only: test donations do not contact Saweria and do not represent real payments.",bg=PANEL,fg=AMBER,wraplength=780,justify="left").pack(anchor="w",pady=12)

    def save_goal(self):
        try:self.donation_goal=max(1,int(self.goal_var.get()))
        except ValueError:messagebox.showerror("Invalid goal","Enter a whole number in rupiah.");return
        self.save_current_profile();self.update_donation_ui()

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
        self.title_block("VTUBE Connect Hub","Pusat pemilihan sumber kamera, mikrofon, koneksi HP, dan perangkat eksternal.")
        modes=tk.Frame(self.content,bg=PANEL,padx=16,pady=14);modes.pack(fill="x",pady=(0,12))
        self.section(modes,"Pilih mode input")
        self.input_mode_var=tk.StringVar(value="Webcam USB / kamera laptop")
        self.input_mode_box=ttk.Combobox(modes,textvariable=self.input_mode_var,state="readonly",width=42,values=["Webcam USB / kamera laptop","Kamera HP via VTUBE Connect","Kamera IP / URL stream","Capture card HDMI / USB","Mikrofon eksternal USB / headset","HP sebagai kamera + mikrofon","Mobile gaming capture"])
        self.input_mode_box.pack(anchor="w",pady=8)
        self.input_mode_box.bind("<<ComboboxSelected>>",lambda e:self.update_connect_mode())
        row=tk.Frame(self.content,bg=BG);row.pack(fill="x")
        for title,value,note,color in [("USB","Deteksi lokal","Webcam/capture card via /dev/video*",GREEN),("Wi-Fi","HP / IP stream","Perlu aplikasi/stream HP yang kompatibel",CYAN),("Audio","Input system","Mikrofon USB/headset via PipeWire",ACCENT)]:
            self.card(row,title,value,note,color).pack(side="left",fill="both",expand=True,padx=(0,10))
        p=tk.Frame(self.content,bg=PANEL,padx=18,pady=16);p.pack(fill="both",expand=True,pady=(12,0))
        self.section(p,"Kamera yang terdeteksi","Daftar perangkat Linux lokal. Kamera HP tidak akan muncul di sini kecuali sudah dipublikasikan sebagai kamera IP/USB oleh aplikasi atau driver yang kompatibel.")
        self.camera_var=tk.StringVar();self.camera_box=ttk.Combobox(p,textvariable=self.camera_var,state="readonly",width=60)
        self.camera_box.pack(anchor="w",pady=8)
        self.refresh_camera_devices()
        row2=tk.Frame(p,bg=PANEL);row2.pack(anchor="w",pady=4)
        self.btn(row2,"Refresh camera list",self.refresh_camera_devices).pack(side="left",padx=(0,8))
        self.btn(row2,"Test camera preview",self.test_camera_preview,True).pack(side="left",padx=(0,8))
        self.btn(row2,"Open Audio Studio",lambda:self.show_page("Audio Studio")).pack(side="left")
        self.section(p,"Hubungkan HP / kamera IP","Masukkan URL stream jika aplikasi kamera HP yang kamu gunakan menyediakan URL MJPEG/RTSP. Ini menguji/membuka sumber lewat pemutar yang tersedia; bukan pairing VTUBE Connect native.")
        self.phone_url_var=tk.StringVar(value="http://192.168.1.100:8080/video")
        urlrow=tk.Frame(p,bg=PANEL);urlrow.pack(fill="x",pady=7)
        tk.Entry(urlrow,textvariable=self.phone_url_var,bg=PANEL2,fg=TEXT,insertbackground=TEXT,relief="flat",width=62).pack(side="left",ipady=7)
        self.btn(urlrow,"Open stream",self.open_phone_stream,True).pack(side="left",padx=8)
        self.connect_help=tk.Label(p,text="Mode webcam USB: pilih perangkat /dev/video dan tes preview. Mode HP native memerlukan aplikasi Android VTUBE Connect yang belum dibuat pada build ini; USB/Wi-Fi pairing terenkripsi dan remote control masih pekerjaan berikutnya.",bg=PANEL,fg=AMBER,wraplength=850,justify="left")
        self.connect_help.pack(anchor="w",pady=(12,0))

    def update_connect_mode(self):
        mode=self.input_mode_var.get()
        if mode=="Kamera IP / URL stream":
            msg="Masukkan URL stream dari aplikasi kamera HP yang kompatibel. Pastikan laptop dan HP dapat saling menjangkau melalui jaringan."
        elif mode=="Capture card HDMI / USB":
            msg="Hubungkan capture card; jika didukung Linux, perangkat akan muncul sebagai /dev/video*. Pilih lalu tekan Test camera preview."
        elif mode=="Mikrofon eksternal USB / headset":
            msg="Buka Audio Studio untuk melihat input yang terdeteksi dan memilih mikrofon default sistem."
        elif mode in ("Kamera HP via VTUBE Connect","HP sebagai kamera + mikrofon","Mobile gaming capture"):
            msg="Aplikasi Android VTUBE Connect kini disertakan sebagai proyek sumber di folder vtube-connect/android. Build APK di Android Studio; izinkan kamera/mikrofon di HP, lalu gunakan alamat stream yang tampil di aplikasi. Pada tahap ini kamera MJPEG dan endpoint audio lokal tersedia dalam kode sumber; pairing internet jarak jauh, tracking wajah penuh, dan screen capture gaming masih tahap pengembangan."
        else:
            msg="Pilih perangkat /dev/video*, lalu tekan Test camera preview. Mikrofon dipilih terpisah di Audio Studio."
        self.connect_help.configure(text=msg)

    def refresh_camera_devices(self):
        devices=self._camera_devices()
        if hasattr(self,"camera_box") and self.camera_box.winfo_exists():
            self.camera_box.configure(values=[x[0] for x in devices]);self.camera_var.set(devices[0][0] if devices else "")
        self.status_var.set(f"Camera scan complete · {len(devices)} local video device(s)")
        if not devices: self.status_var.set("No /dev/video* device found · connect a webcam/capture card or configure an IP stream")

    def test_camera_preview(self):
        device=self.camera_var.get()
        if not device:return messagebox.showinfo("Camera test","Tidak ada kamera lokal terdeteksi. Coba sambungkan webcam USB/capture card, atau gunakan URL stream HP jika tersedia.")
        # Prefer ffplay; fall back to mpv. This is a device test, not the built-in VTUBE compositor.
        player=shutil.which("ffplay")
        if player:
            cmd=[player,"-f","v4l2","-i",device]
        elif shutil.which("mpv"):
            cmd=[shutil.which("mpv"),f"av://v4l2:{device}","--profile=low-latency"]
        else:
            return messagebox.showinfo("Camera test","Kamera ditemukan, tetapi pemutar preview belum tersedia. Instal ffmpeg (ffplay) atau mpv untuk tes sementara. Preview terintegrasi VTUBE akan dibuat di tahap berikutnya.")
        try:subprocess.Popen(cmd);self.status_var.set(f"Camera test opened · {device}")
        except Exception as e:messagebox.showerror("Camera test",str(e))

    def open_phone_stream(self):
        url=self.phone_url_var.get().strip()
        if not url.startswith(("http://","https://","rtsp://")):
            return messagebox.showerror("Stream URL","URL harus diawali http://, https://, atau rtsp://")
        player=shutil.which("ffplay")
        if player:
            try:subprocess.Popen([player,"-fflags","nobuffer","-i",url]);self.status_var.set("Opened external IP stream test")
            except Exception as e:messagebox.showerror("Stream",str(e))
        else:
            try:webbrowser.open(url);self.status_var.set("Opened stream URL in browser")
            except Exception as e:messagebox.showerror("Stream",f"Tidak bisa membuka URL: {e}")

    def page_features(self):
        self.title_block("Feature Center", "Peta fitur VTUBE OS: status implementasi dibuat transparan agar fitur simulasi tidak dikira sudah terhubung ke layanan nyata.")
        sections = [
            ("LIVE STUDIO", ["Scene canvas dan elemen draggable — prototype aktif", "Simpan profile dan pilihan scene — aktif", "Capture multi-source dan compositor real-time — pengembangan", "Encode/record/stream FFmpeg terintegrasi — pengembangan"]),
            ("AVATAR & TRACKING", ["Preset avatar konseptual — aktif", "Impor VRM/Live2D dan renderer 2D/3D — pengembangan", "Face/hand tracking — pengembangan", "Ekspresi, emote, hotkey — rancangan"]),
            ("DEVICE & AUDIO", ["Deteksi kamera Linux /dev/video* — aktif", "Pilih mikrofon/output via PipeWire/PulseAudio — aktif", "Kamera HP via MJPEG URL — bisa diuji jika HP menyediakan stream", "VTUBE Connect Android source — disertakan; perlu build dan uji perangkat", "USB/Wi-Fi pairing produksi dan audio HP native — pengembangan"]),
            ("STREAM & COMMUNITY", ["Donation alert simulasi dan goal rupiah — aktif (bukan transaksi nyata)", "Saweria webhook/API resmi — belum terhubung", "Chat YouTube/Twitch/TikTok — integrasi sesuai API/izin platform", "Overlay HTML dan aset — starter", "Backup, plugin API, bug report, roadmap — tahap awal"]),
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
        for t in ["Working: navigation, scene canvas placeholders, draggable scene elements, local profiles",
                  "Working: donation goal and simulated alert overlay",
                  "Planned: real camera capture, real avatar rendering and face tracking",
                  "Planned: audio mixer/processing and scene compositing",
                  "Planned: built-in FFmpeg/GStreamer encoding and platform connections",
                  "Planned: VTUBE Connect Android app and secure transport",
                  "Build script: tools/build-iso.sh"]:
            tk.Label(p,text="•  "+t,bg=PANEL,fg=TEXT,wraplength=850,justify="left").pack(anchor="w",pady=6)
        self.btn(p,"Open project README",lambda:messagebox.showinfo("README","See README.md and docs/ROADMAP.md in the project folder.")).pack(anchor="w",pady=15)

if __name__=="__main__":
    VTubeApp().mainloop()
