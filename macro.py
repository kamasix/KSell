import pyautogui
import keyboard
import time
import os
import sys
import pydirectinput
import pygetwindow as gw
import json
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import shutil
import webbrowser

pydirectinput.PAUSE = 0.1

GAME_WINDOW_TITLE = None

# Fix paths for PyInstaller executable
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGES_FOLDER = os.path.join(BASE_DIR, 'images')
ORES_FOLDER = os.path.join(IMAGES_FOLDER, 'ores')
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
DEFAULT_HOTKEY = 'f8'

try:
    import cv2
    HAS_OPENCV = True
    print("OpenCV loaded")
except ImportError:
    HAS_OPENCV = False
    print("OpenCV unavailable")

def find_image_on_screen(image_name, timeout=10, save_debug=False, confidence=0.7):
    image_path = os.path.join(IMAGES_FOLDER, image_name)
    if not os.path.exists(image_path):
        print(f"ERROR: {image_path} not found")
        return None
    
    print(f"Searching: {image_name}")
    start_time = time.time()
    attempts = 0
    
    while time.time() - start_time < timeout:
        attempts += 1
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence) if HAS_OPENCV else pyautogui.locateOnScreen(image_path, grayscale=True)
            if location:
                center = pyautogui.center(location)
                print(f"✓ Found at {center}")
                return center
        except:
            pass
        
        if attempts % 6 == 0:
            print(f"Still searching... {int(time.time() - start_time)}s")
        time.sleep(0.5)
    
    print(f"✗ Not found in {timeout}s")
    if save_debug:
        pyautogui.screenshot().save(os.path.join(IMAGES_FOLDER, f"debug_{image_name}"))
    return None

def click_image(image_name, timeout=10, save_debug=True, confidence=0.7):
    position = find_image_on_screen(image_name, timeout, save_debug, confidence)
    if position:
        pyautogui.moveTo(position[0], position[1])
        time.sleep(0.05)
        pydirectinput.moveRel(1, 0)
        time.sleep(0.05)
        pydirectinput.click()
        print("✓ Clicked")
        return True
    return False

def focus_game_window():
    global GAME_WINDOW_TITLE
    active_window = gw.getActiveWindow()
    if active_window:
        GAME_WINDOW_TITLE = active_window.title
        print(f"Game window: {GAME_WINDOW_TITLE}")
        return True
    print("WARNING: Click on game window first!")
    return False

def ensure_game_focus():
    if GAME_WINDOW_TITLE:
        try:
            windows = gw.getWindowsWithTitle(GAME_WINDOW_TITLE)
            if windows and not windows[0].isActive:
                windows[0].activate()
                time.sleep(0.2)
            return True
        except:
            pass
    return False

def run_macro():
    print("=== MACRO STARTED ===")
    
    if not GAME_WINDOW_TITLE and not focus_game_window():
        return
    
    ensure_game_focus()
    time.sleep(0.3)
    
    print("Opening Stash...")
    pydirectinput.press('t')
    time.sleep(0.5)
    
    print("Searching for Stash...")
    stash_found = find_image_on_screen("stash.png", timeout=10, save_debug=True, confidence=0.6)
    if not stash_found:
        print("ERROR: Stash not found")
        return
    
    print("Clicking Stash")
    pyautogui.moveTo(stash_found[0], stash_found[1])
    time.sleep(0.05)
    pydirectinput.moveRel(1, 0)
    time.sleep(0.05)
    pydirectinput.click()
    time.sleep(0.5)
    
    print("Clicking Sell Items")
    if not click_image("sell_items.png", timeout=10, confidence=0.6):
        print("ERROR: Sell Items not found")
        return
    
    print("Waiting 2 seconds...")
    time.sleep(2)
    
    print("Selling items...")
    sell_items()
    print("=== MACRO COMPLETED ===")

def get_hotkey():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f).get('hotkey', DEFAULT_HOTKEY)
        except:
            pass
    return DEFAULT_HOTKEY

def sell_items():
    if not os.path.exists(ORES_FOLDER):
        print("WARNING: Ores folder not found!")
        return
    
    items = [f for f in os.listdir(ORES_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not items:
        print(f"WARNING: No images in {ORES_FOLDER}")
        return
    
    print(f"Items to sell: {len(items)}")
    print(f"Items list: {', '.join([os.path.splitext(f)[0] for f in items])}")
    total_sold = 0
    
    for item in items:
        item_name = os.path.splitext(item)[0]
        print(f"Searching: {item_name}")
        try:
            item_path = os.path.join(ORES_FOLDER, item)
            locations = list(pyautogui.locateAllOnScreen(item_path, confidence=0.65))
            
            if locations:
                print(f"  Found {item_name} ({len(locations)}x) - clicking...")
                loc = locations[0]
                center = pyautogui.center(loc)
                pyautogui.moveTo(center[0], center[1])
                time.sleep(0.05)
                pydirectinput.moveRel(1, 0)
                time.sleep(0.05)
                pydirectinput.click()
                time.sleep(0.3)
                
                # Click Max button
                max_found = click_image("max.png", timeout=2, save_debug=False, confidence=0.7)
                if max_found:
                    time.sleep(0.2)
                
                # Click Select button
                select_found = click_image("select.png", timeout=2, save_debug=False, confidence=0.7)
                if select_found:
                    time.sleep(0.2)
                
                total_sold += 1
            else:
                print("  Not found on screen")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Click Accept at the end
    print("Clicking Accept...")
    time.sleep(0.5)
    if click_image("accept.png", timeout=5, save_debug=True, confidence=0.7):
        time.sleep(0.5)
        print("Clicking Yes...")
        click_image("yes.png", timeout=5, save_debug=True, confidence=0.7)
    
    # Close window if x.png appears
    time.sleep(0.5)
    print("Looking for X button...")
    if click_image("x.png", timeout=3, save_debug=False, confidence=0.7):
        print("✓ Closed window")
    
    print(f"✓ Sold {total_sold} items!")

class ItemManagerUI:
    def __init__(self):
        # Initialize folders and config
        self.initialize_workspace()
        
        self.root = tk.Tk()
        self.root.title("KSell")
        self.root.geometry("750x550")
        self.root.minsize(500, 400)
        self.root.configure(bg="#1e1e1e")
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        config = self.load_config()
        self.hotkey = config.get('hotkey', 'f8')
        self.timer_minutes = config.get('timer_minutes', 10)
        self.macro_active = False
        self.macro_started = False
        self.create_ui()
        self.start_macro_listener()
        self.start_auto_timer()
        self.start_auto_clicker()
    
    def initialize_workspace(self):
        # Create images folder if it doesn't exist
        if not os.path.exists(IMAGES_FOLDER):
            os.makedirs(IMAGES_FOLDER)
            print(f"Created folder: {IMAGES_FOLDER}")
        
        # Create ores subfolder if it doesn't exist
        if not os.path.exists(ORES_FOLDER):
            os.makedirs(ORES_FOLDER)
            print(f"Created folder: {ORES_FOLDER}")
        
        # Create config.json with defaults if it doesn't exist
        if not os.path.exists(CONFIG_FILE):
            default_config = {'hotkey': 'f8', 'timer_minutes': 10}
            with open(CONFIG_FILE, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created config file: {CONFIG_FILE}")
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'hotkey': 'f8', 'timer_minutes': 10}
    
    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'hotkey': self.hotkey, 'timer_minutes': self.timer_minutes}, f, indent=4)
        self.update_status("Configuration saved!")
    
    def create_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - image gallery
        left_panel = tk.Frame(main_frame, bg="#1e1e1e")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        gallery_frame = tk.LabelFrame(left_panel, text="📦 Items to Sell", 
                                     font=("Segoe UI", 10, "bold"), bg="#2d2d30", fg="#ffffff", 
                                     padx=5, pady=5, relief=tk.FLAT, bd=2, highlightbackground="#404040", highlightthickness=2)
        gallery_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(gallery_frame, bg="#2d2d30", troughcolor="#1e1e1e", 
                                bd=0, width=12, activebackground="#505050", 
                                highlightthickness=0, relief=tk.FLAT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)
        
        self.gallery_canvas = tk.Canvas(gallery_frame, yscrollcommand=scrollbar.set,
                                       bg="#1e1e1e", borderwidth=0, highlightthickness=0)
        self.gallery_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.gallery_canvas.yview)
        
        self.gallery_inner = tk.Frame(self.gallery_canvas, bg="#1e1e1e")
        self.gallery_canvas.create_window((0, 0), window=self.gallery_inner, anchor="nw")
        
        self.load_items_gallery()
        
        # Right panel - compact controls
        right_panel = tk.Frame(main_frame, bg="#1e1e1e", width=220)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Settings section
        settings_frame = tk.LabelFrame(right_panel, text="⚙️ Settings", 
                                      font=("Segoe UI", 10, "bold"), bg="#2d2d30", fg="#ffffff", 
                                      padx=8, pady=8, relief=tk.FLAT, bd=2, highlightbackground="#404040", highlightthickness=2)
        settings_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(settings_frame, text="Hotkey:", font=("Segoe UI", 9), bg="#2d2d30", fg="#cccccc").pack(anchor=tk.W)
        hotkey_frame = tk.Frame(settings_frame, bg="#2d2d30")
        hotkey_frame.pack(fill=tk.X, pady=(2, 8))
        self.hotkey_entry = tk.Entry(hotkey_frame, font=("Segoe UI", 11, "bold"), 
                                     justify=tk.CENTER,
                                     bg="#3c3c3c", fg="#ffffff", insertbackground="#ffffff", 
                                     relief=tk.FLAT, borderwidth=0, highlightbackground="#505050", highlightthickness=2)
        self.hotkey_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=4)
        tk.Button(hotkey_frame, text="✓", command=self.save_hotkey, bg="#505050", fg="#ffffff",
                 font=("Segoe UI", 10, "bold"), width=4, cursor="hand2", relief=tk.FLAT, bd=0,
                 activebackground="#606060").pack(side=tk.LEFT, ipady=4)
        
        tk.Label(settings_frame, text="Auto-sell timer (min):", font=("Segoe UI", 9), bg="#2d2d30", fg="#cccccc").pack(anchor=tk.W)
        timer_frame = tk.Frame(settings_frame, bg="#2d2d30")
        timer_frame.pack(fill=tk.X, pady=(2, 0))
        self.timer_entry = tk.Entry(timer_frame, font=("Segoe UI", 11), justify=tk.CENTER,
                                    bg="#3c3c3c", fg="#ffffff", insertbackground="#ffffff", 
                                    relief=tk.FLAT, borderwidth=0, highlightbackground="#505050", highlightthickness=2)
        self.timer_entry.insert(0, str(self.timer_minutes))
        self.timer_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=4)
        tk.Button(timer_frame, text="✓", command=self.save_timer, bg="#505050", fg="#ffffff",
                 font=("Segoe UI", 10, "bold"), width=4, cursor="hand2", relief=tk.FLAT, bd=0,
                 activebackground="#606060").pack(side=tk.LEFT, ipady=4)
        
        # Actions section
        actions_frame = tk.LabelFrame(right_panel, text="🔧 Actions", 
                                     font=("Segoe UI", 10, "bold"), bg="#2d2d30", fg="#ffffff", 
                                     padx=8, pady=8, relief=tk.FLAT, bd=2, highlightbackground="#404040", highlightthickness=2)
        actions_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Button(actions_frame, text="➕ Add Item", command=self.add_image, bg="#505050", fg="#ffffff",
                 font=("Segoe UI", 9, "bold"), cursor="hand2", relief=tk.FLAT, bd=0, height=1,
                 activebackground="#606060").pack(fill=tk.X, pady=2)
        tk.Button(actions_frame, text="🔄 Refresh", command=self.load_items_gallery, bg="#3e3e42", fg="#ffffff",
                 font=("Segoe UI", 9), cursor="hand2", relief=tk.FLAT, bd=0, height=1,
                 activebackground="#4e4e52").pack(fill=tk.X, pady=2)
        tk.Button(actions_frame, text="🎮 Roblox Profile", command=self.open_profile, bg="#3e3e42", fg="#ffffff",
                 font=("Segoe UI", 9), cursor="hand2", relief=tk.FLAT, bd=0, height=1,
                 activebackground="#4e4e52").pack(fill=tk.X, pady=2)
        tk.Button(actions_frame, text="💬 Discord Server", command=self.open_discord, bg="#3e3e42", fg="#ffffff",
                 font=("Segoe UI", 9), cursor="hand2", relief=tk.FLAT, bd=0, height=1,
                 activebackground="#4e4e52").pack(fill=tk.X, pady=2)
        
        # Status section
        status_frame = tk.LabelFrame(right_panel, text="🎮 Status", 
                                    font=("Segoe UI", 10, "bold"), bg="#2d2d30", fg="#ffffff", 
                                    padx=8, pady=8, relief=tk.FLAT, bd=2, highlightbackground="#404040", highlightthickness=2)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.macro_status = tk.Label(status_frame, text="● Ready", bg="#2d2d30",
                                     font=("Segoe UI", 10, "bold"), fg="#cccccc")
        self.macro_status.pack(pady=5)
        
        tk.Label(status_frame, text=f"Press {self.hotkey.upper()} to start", bg="#2d2d30",
                font=("Segoe UI", 9), fg="#ffffff").pack()
        tk.Label(status_frame, text="F4/ESC to exit", bg="#2d2d30",
                font=("Segoe UI", 8), fg="#808080").pack(pady=(2, 0))
    
    def load_items_gallery(self):
        # Clear gallery
        for widget in self.gallery_inner.winfo_children():
            widget.destroy()
        
        if not os.path.exists(ORES_FOLDER):
            os.makedirs(ORES_FOLDER)
            tk.Label(self.gallery_inner, text="No items - click 'Add Item'", 
                    font=("Segoe UI", 9), bg="#1e1e1e", fg="#808080").pack(pady=20)
            self.gallery_canvas.update_idletasks()
            self.gallery_canvas.config(scrollregion=self.gallery_canvas.bbox("all"))
            return
        
        items = [f for f in os.listdir(ORES_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not items:
            tk.Label(self.gallery_inner, text="No items - click 'Add Item'", 
                    font=("Segoe UI", 9), bg="#1e1e1e", fg="#808080").pack(pady=20)
            self.gallery_canvas.update_idletasks()
            self.gallery_canvas.config(scrollregion=self.gallery_canvas.bbox("all"))
            return
        
        # Display items with thumbnails
        for item in sorted(items):
            item_frame = tk.Frame(self.gallery_inner, bg="#2d2d30", relief=tk.FLAT, bd=0, highlightbackground="#404040", highlightthickness=2)
            item_frame.pack(fill=tk.X, padx=5, pady=3)
            
            try:
                from PIL import Image, ImageTk
                img_path = os.path.join(ORES_FOLDER, item)
                img = Image.open(img_path)
                img.thumbnail((40, 40))
                photo = ImageTk.PhotoImage(img)
                
                img_label = tk.Label(item_frame, image=photo, bg="#2d2d30")
                img_label.image = photo
                img_label.pack(side=tk.LEFT, padx=5, pady=5)
            except:
                tk.Label(item_frame, text="🖼️", font=("Segoe UI", 12), bg="#2d2d30").pack(side=tk.LEFT, padx=5)
            
            # Remove extension from display name
            display_name = os.path.splitext(item)[0]
            name_label = tk.Label(item_frame, text=display_name, font=("Segoe UI", 9, "bold"), 
                                 bg="#2d2d30", fg="#ffffff", anchor=tk.W)
            name_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.gallery_canvas.update_idletasks()
        self.gallery_canvas.config(scrollregion=self.gallery_canvas.bbox("all"))
        self.update_status(f"Loaded {len(items)} items")
    
    def add_image(self):
        filename = filedialog.askopenfilename(
            title="Select item image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        )
        if filename:
            basename = os.path.basename(filename)
            destination = os.path.join(ORES_FOLDER, basename)
            try:
                shutil.copy(filename, destination)
                self.load_items_gallery()
                self.update_status(f"✓ Added: {basename}")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot copy file:\n{e}")
    
    def open_profile(self):
        webbrowser.open("https://www.roblox.com/users/556065198/profile")
        self.update_status("✓ Opened Roblox profile")
    
    def open_discord(self):
        webbrowser.open("https://discord.gg/PNchkgyMtZ")
        self.update_status("✓ Opened Discord server")
    
    def save_hotkey(self):
        new_hotkey = self.hotkey_entry.get().strip().lower()
        if new_hotkey and len(new_hotkey) <= 10:
            # Remove old hotkey
            try:
                keyboard.remove_hotkey(self.hotkey)
            except:
                pass
            
            self.hotkey = new_hotkey
            self.save_config()
            
            # Add new hotkey
            keyboard.add_hotkey(self.hotkey, self.on_macro_start)
            
            self.update_status(f"✓ Hotkey changed to {new_hotkey.upper()}!")
        else:
            messagebox.showwarning("Invalid", "Enter a valid key (e.g., f1, f8, f10)")
    
    def save_timer(self):
        try:
            minutes = int(self.timer_entry.get())
            if minutes > 0:
                self.timer_minutes = minutes
                self.save_config()
                self.update_status(f"✓ Timer set to {minutes} minutes!")
            else:
                messagebox.showwarning("Invalid", "Enter a positive number")
        except ValueError:
            messagebox.showwarning("Invalid", "Enter a valid number")
    
    def update_status(self, message):
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
    
    def start_macro_listener(self):
        def listener():
            keyboard.add_hotkey(self.hotkey, self.on_macro_start)
            keyboard.add_hotkey('esc', self.on_exit)
            keyboard.add_hotkey('f4', self.on_exit)
            keyboard.wait()
        threading.Thread(target=listener, daemon=True).start()
    
    def start_auto_timer(self):
        # Auto-run every X minutes after first manual run
        interval_ms = self.timer_minutes * 60 * 1000
        def auto_run():
            self.on_macro_start()
            self.root.after(interval_ms, auto_run)
        
        self.root.after(interval_ms, auto_run)
    
    def start_auto_clicker(self):
        def clicker():
            screen_width, screen_height = pyautogui.size()
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            while True:
                if self.macro_started and not self.macro_active:
                    try:
                        pyautogui.click(center_x, center_y)
                    except:
                        pass
                time.sleep(0.05)
        
        threading.Thread(target=clicker, daemon=True).start()
    
    def on_macro_start(self):
        self.macro_started = True
        self.macro_status.config(text="● Running", fg="#4ec9b0")
        self.update_status("⚡ Running...")
        threading.Thread(target=self.run_macro_thread, daemon=True).start()
    
    def run_macro_thread(self):
        self.macro_active = True
        try:
            run_macro()
            self.root.after(100, lambda: self.update_status("✓ Macro completed!"))
            self.root.after(100, lambda: self.macro_status.config(text="● Ready", fg="#ce9178"))
        except Exception as e:
            print(f"ERROR: {e}")
            self.root.after(100, lambda: self.macro_status.config(text="● Error", fg="#f48771"))
            self.root.after(100, lambda: self.update_status(f"✗ Error: {e}"))
        finally:
            self.macro_active = False
    
    def on_exit(self):
        os._exit(0)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    print("Starting KSell...")
    app = ItemManagerUI()
    app.run()
