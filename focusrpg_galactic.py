import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import winsound # Ses özelliği için (Windows)

class FocusGalacticUltra(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- TEMA VE RENKLER (DEĞİŞTİRİLMEDİ) ---
        self.title("Focus RPG: Galactic Ultra")
        self.geometry("650x900")
        ctk.set_appearance_mode("dark")
        
        self.color_nebula = "#8e44ad" 
        self.color_space = "#2c3e50"  
        self.color_star = "#f1c40f"   
        self.color_void = "#1a1a2e"   

        self.db_init()
        self.load_data()
        
        # Çalışma Durumu Değişkenleri
        self.timer_running = False
        self.is_break = False
        self.combo_count = 0

        # --- ANA SEKME SİSTEMİ ---
        self.tabview = ctk.CTkTabview(self, width=600, height=850, 
                                      segmented_button_selected_color=self.color_nebula)
        self.tabview.pack(padx=20, pady=20)

        self.tab_main = self.tabview.add("MİSTİK ODAK")
        self.tab_profile = self.tabview.add("KOZMİK PROFİL")
        self.tab_shop = self.tabview.add("MARKET") # YENİ ÖZELLİK 3
        self.tab_settings = self.tabview.add("EVREN AYARLARI")

        self.setup_main_tab()
        self.setup_profile_tab()
        self.setup_shop_tab()
        self.setup_settings_tab()

    def db_init(self):
        self.conn = sqlite3.connect("focus_galactic_ultra.db")
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS user 
                     (level INT, xp INT, title TEXT, gold INT, total_mins INT, tasks_done INT)''')
        c.execute('CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, val INT)')
        c.execute('CREATE TABLE IF NOT EXISTS history (task TEXT, date TEXT)') # YENİ ÖZELLİK 6
        
        if not c.execute("SELECT * FROM user").fetchone():
            c.execute("INSERT INTO user VALUES (1, 0, 'Yıldız Gezgini', 0, 0, 0)")
        
        defaults = [('work_min', 25), ('break_min', 5), ('daily_goal', 8)]
        for k, v in defaults:
            c.execute("INSERT OR IGNORE INTO config VALUES (?, ?)", (k, v))
        self.conn.commit()

    def load_data(self):
        res = self.conn.execute("SELECT * FROM user").fetchone()
        self.level, self.xp, self.title_name, self.gold, self.total_mins, self.tasks_done = res
        self.work_min = self.conn.execute("SELECT val FROM config WHERE key='work_min'").fetchone()[0]
        self.time_left = self.work_min * 60

    # --- 1. ANA SEKME (GELİŞTİRİLMİŞ) ---
    def setup_main_tab(self):
        # RPG Barı
        self.xp_frame = ctk.CTkFrame(self.tab_main, fg_color=self.color_void, border_color=self.color_nebula, border_width=2)
        self.xp_frame.pack(fill="x", padx=10, pady=10)
        
        self.lbl_rpg = ctk.CTkLabel(self.xp_frame, text=f"✧ {self.title_name} ✧ Lvl: {self.level}", 
                                    font=("Orbitron", 18, "bold"), text_color=self.color_star)
        self.lbl_rpg.pack(pady=5)
        
        self.xp_bar = ctk.CTkProgressBar(self.xp_frame, width=450, progress_color=self.color_nebula)
        self.xp_bar.set(self.xp / (self.level * 100))
        self.xp_bar.pack(pady=10)

        # Sayaç Paneli
        self.timer_label = ctk.CTkLabel(self.tab_main, text=self.format_time(self.time_left), 
                                        font=("Consolas", 120, "bold"))
        self.timer_label.pack(pady=20)

        # YENİ ÖZELLİK 8: Hızlı Süre Seçiciler
        self.quick_frame = ctk.CTkFrame(self.tab_main, fg_color="transparent")
        self.quick_frame.pack(pady=5)
        for t in [25, 45, 60]:
            btn = ctk.CTkButton(self.quick_frame, text=f"{t}dk", width=60, fg_color=self.color_space,
                                command=lambda x=t: self.set_custom_time(x))
            btn.pack(side="left", padx=5)

        # Görev Alanı
        ctk.CTkLabel(self.tab_main, text="🌌 ŞU ANKİ KOZMİK GÖREVİN 🌌", font=("Arial", 10, "bold"), text_color=self.color_nebula).pack(pady=10)
        self.task_entry = ctk.CTkEntry(self.tab_main, placeholder_text="Görevi yazmadan portal açılmaz...", 
                                       width=400, height=40, fg_color=self.color_void)
        self.task_entry.pack(pady=5)

        self.btn_start = ctk.CTkButton(self.tab_main, text="PORTALI AÇ", height=60, width=350, 
                                       font=("Arial", 20, "bold"), fg_color=self.color_nebula, command=self.toggle_timer)
        self.btn_start.pack(pady=20)

        # YENİ ÖZELLİK 2: Günlük Hedef Barı
        self.goal_label = ctk.CTkLabel(self.tab_main, text="Günlük Enerji Hedefi", font=("Arial", 10))
        self.goal_label.pack()
        self.goal_bar = ctk.CTkProgressBar(self.tab_main, width=300, height=8, progress_color=self.color_star)
        self.goal_bar.set(min(self.total_mins / 480, 1.0)) # 8 saatlik hedef
        self.goal_bar.pack(pady=5)

    # --- 2. PROFİL VE İSTATİSTİKLER (GELİŞTİRİLMİŞ) ---
    def setup_profile_tab(self):
        for w in self.tab_profile.winfo_children(): w.destroy()
        
        profile_card = ctk.CTkFrame(self.tab_profile, fg_color=self.color_void, border_width=1)
        profile_card.pack(fill="x", padx=20, pady=20)
        
        self.prof_title = ctk.CTkLabel(profile_card, text=self.title_name, font=("Arial", 32, "bold"), text_color=self.color_star)
        self.prof_title.pack(pady=15)
        
        # YENİ ÖZELLİK 9: Detaylı İstatistikler
        stats_data = [("ALTIN", self.gold), ("SEVİYE", self.level), 
                      ("TOPLAM DK", self.total_mins), ("BİTEN GÖREV", self.tasks_done)]
        
        stats_frame = ctk.CTkFrame(self.tab_profile, fg_color="transparent")
        stats_frame.pack(pady=10)
        
        for i, (lab, val) in enumerate(stats_data):
            f = ctk.CTkFrame(stats_frame, fg_color="#0f0f1e", width=130, height=80)
            f.grid(row=i//2, column=i%2, padx=10, pady=10)
            ctk.CTkLabel(f, text=lab, font=("Arial", 9), text_color=self.color_nebula).pack(pady=2)
            ctk.CTkLabel(f, text=str(val), font=("Arial", 20, "bold")).pack()

    # --- 3. KOZMİK MARKET (YENİ SEKME) ---
    def setup_shop_tab(self):
        ctk.CTkLabel(self.tab_shop, text="KOZMİK MARKET", font=("Orbitron", 22, "bold"), text_color=self.color_star).pack(pady=20)
        
        items = [("Nebula Avcısı", 50), ("Galaksi Lordu", 150), ("Void Master", 500)]
        for name, price in items:
            f = ctk.CTkFrame(self.tab_shop, fg_color=self.color_void)
            f.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(f, text=f"✧ {name}").pack(side="left", padx=20)
            ctk.CTkButton(f, text=f"{price} Altın", width=100, height=30, 
                          fg_color=self.color_nebula, command=lambda n=name, p=price: self.buy_title(n, p)).pack(side="right", padx=10, pady=10)

    # --- 4. AYARLAR ---
    def setup_settings_tab(self):
        self.new_title_ent = ctk.CTkEntry(self.tab_settings, placeholder_text="Manuel Ünvan Değiştir...", width=350)
        self.new_title_ent.insert(0, self.title_name)
        self.new_title_ent.pack(pady=20)
        ctk.CTkButton(self.tab_settings, text="EVRENİ GÜNCELLE", command=self.update_settings).pack()

    # --- MANTIKSAL FONKSİYONLAR ---
    def set_custom_time(self, mins):
        if not self.timer_running:
            self.time_left = mins * 60
            self.timer_label.configure(text=self.format_time(self.time_left))

    def format_time(self, seconds):
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def toggle_timer(self):
        if not self.timer_running:
            if not self.task_entry.get().strip():
                messagebox.showwarning("Kozmik Engel", "Önce bir görev belirlemelisin!")
                return
            self.timer_running = True
            self.btn_start.configure(text="PORTALI DURDUR", fg_color="#e74c3c")
            self.tick()
        else:
            self.timer_running = False
            self.btn_start.configure(text="PORTALI AÇ", fg_color=self.color_nebula)

    def tick(self):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            self.timer_label.configure(text=self.format_time(self.time_left))
            self.after(1000, self.tick)
        elif self.time_left == 0 and self.timer_running:
            self.timer_running = False
            self.complete_mission()

    def complete_mission(self):
        # YENİ ÖZELLİK 4: Sesli Bildirim
        try: winsound.Beep(1000, 500); winsound.Beep(1200, 500)
        except: pass

        if not self.is_break:
            # Ödüller ve Combo (Özellik 5)
            self.combo_count += 1
            reward_xp = 50 + (self.combo_count * 10)
            self.xp += reward_xp
            self.gold += 20
            self.tasks_done += 1
            self.total_mins += (self.time_left // 60) # Aslında biten süre eklenmeli
            
            # Kayıt (Özellik 6)
            self.conn.execute("INSERT INTO history VALUES (?, ?)", (self.task_entry.get(), "Bugün"))
            
            # Seviye Atlama (Özellik 10)
            if self.xp >= (self.level * 100):
                self.xp = 0
                self.level += 1
                messagebox.showinfo("YÜKSELİŞ", f"TEBRİKLER! Seviye {self.level} oldun!")

            messagebox.showinfo("Görev Başarılı", f"Nebula enerjisi toplandı!\n+{reward_xp} XP | +20 Altın\nKombo: x{self.combo_count}")
            
            # Otomatik Mola (Özellik 1)
            self.is_break = True
            self.time_left = 5 * 60 # 5 dk mola
            self.lbl_rpg.configure(text="-- DİNLENME MODU --", text_color="#2ecc71")
        else:
            self.is_break = False
            self.time_left = 25 * 60
            self.lbl_rpg.configure(text=f"✧ {self.title_name} ✧ Lvl: {self.level}", text_color=self.color_star)
            messagebox.showinfo("Mola Bitti", "Kozmik yolculuğa devam etmeye hazır mısın?")

        self.save_all_to_db()
        self.update_ui_elements()

    def buy_title(self, name, price):
        if self.gold >= price:
            self.gold -= price
            self.title_name = name
            self.save_all_to_db()
            self.update_ui_elements()
            messagebox.showinfo("Market", f"Yeni ünvanın: {name}!")
        else:
            messagebox.showerror("Hata", "Yetersiz kozmik altın!")

    def save_all_to_db(self):
        self.conn.execute("UPDATE user SET level=?, xp=?, title=?, gold=?, total_mins=?, tasks_done=?", 
                         (self.level, self.xp, self.title_name, self.gold, self.total_mins, self.tasks_done))
        self.conn.commit()

    def update_ui_elements(self):
        self.lbl_rpg.configure(text=f"✧ {self.title_name} ✧ Lvl: {self.level}")
        self.xp_bar.set(self.xp / (self.level * 100))
        self.timer_label.configure(text=self.format_time(self.time_left))
        self.goal_bar.set(min(self.tasks_done / 10, 1.0)) # Örn: Günlük 10 görev hedefi
        self.setup_profile_tab() # Profili yenile

    def update_settings(self):
        self.title_name = self.new_title_ent.get()
        self.save_all_to_db()
        self.update_ui_elements()
        messagebox.showinfo("Sistem", "Kozmik kimlik güncellendi.")

if __name__ == "__main__":
    app = FocusGalacticUltra()
    app.mainloop()