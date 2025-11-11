import tkinter as tk
from tkinter import ttk
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class AudioSignalSynthesizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Garso signalų sintezatorius")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Configure root grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main_frame grid weights
        self.main_frame.grid_rowconfigure(6, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Style configuration for larger fonts
        self.style = ttk.Style()
        self.base_font_size = 18
        self.style.configure('Large.TLabel', font=('Segoe UI', self.base_font_size))
        self.style.configure('Large.TCombobox', font=('Segoe UI', self.base_font_size))
        self.style.configure('Large.TEntry', font=('Segoe UI', self.base_font_size))
        self.style.configure('Large.TButton', font=('Segoe UI', self.base_font_size, 'bold'), padding=10)
        
        # Bind resize event
        self.root.bind('<Configure>', self.on_resize)

        # Bind resize event
        self.root.bind('<Configure>', self.on_resize)

        ttk.Label(self.main_frame, text="Garso tipas:", style='Large.TLabel').grid(row=0, column=0, sticky=tk.W, pady=10, padx=5)
        self.signal_type = tk.StringVar(value="Sinusoidinė banga")
        self.signal_combo = ttk.Combobox(self.main_frame, textvariable=self.signal_type, 
            values=["Sinusoidinė banga",
                    "Stačiakampė banga",
                    "Pjūklo formos banga",
                    "Trikampė banga",
                    "Baltasis triukšmas"],
            state="readonly", width=25, font=('Segoe UI', 12))
        self.signal_combo.grid(row=0, column=1, pady=10, padx=10, sticky=(tk.W, tk.E))
        
        # Configure dropdown list font size
        self.root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 14))

        ttk.Label(self.main_frame, text="Trukmė (sekundėmis):", style='Large.TLabel').grid(row=1, column=0, sticky=tk.W, pady=10, padx=5)
        self.duration = tk.StringVar(value="2.0")
        self.duration_entry = ttk.Entry(self.main_frame, textvariable=self.duration, width=27, font=('Segoe UI', 12))
        self.duration_entry.grid(row=1, column=1, pady=10, padx=10, sticky=(tk.W, tk.E))
        
        ttk.Label(self.main_frame, text="Amplitudė (0-1):", style='Large.TLabel').grid(row=2, column=0, sticky=tk.W, pady=10, padx=5)
        self.amplitude = tk.StringVar(value="0.5")
        self.amplitude_entry = ttk.Entry(self.main_frame, textvariable=self.amplitude, width=27, font=('Segoe UI', 12))
        self.amplitude_entry.grid(row=2, column=1, pady=10, padx=10, sticky=(tk.W, tk.E))

        # Button frame for generate and play/stop
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        self.generate_btn = ttk.Button(button_frame, text="Sintezuoti", command=self.generate_audio, style='Large.TButton')
        self.generate_btn.pack(side=tk.LEFT, padx=10)
        
        self.play_stop_btn = ttk.Button(button_frame, text="Groti", command=self.toggle_play_stop, style='Large.TButton', state='disabled')
        self.play_stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Audio state
        self.audio_data = None
        self.sample_rate = 44100
        self.is_playing = False
        
        self.status_label = ttk.Label(self.main_frame, text="", foreground="green", font=('Segoe UI', 11))
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5, padx=60)

        # Waveform display
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.ax.set_xlabel("Laikas (s)")
        self.ax.set_ylabel("Amplitudė")
        self.ax.set_title("Garso bangos forma")
        self.ax.grid(True, alpha=0.3)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """Handle window close event"""
        sd.stop()  # Stop any playing audio
        plt.close('all')  # Close all matplotlib figures
        self.root.quit()  # Stop the mainloop
        self.root.destroy()  # Close the window
    
    def on_resize(self, event):
        """Adjust font sizes and widget sizes based on window size"""
        if event.widget == self.root:
            # Calculate new font size based on window width
            width = self.root.winfo_width()
            # Scale font size: base is 18 at 900px, scale proportionally
            new_font_size = max(12, min(30, int(18 * (width / 900))))
            entry_font_size = max(10, min(24, int(12 * (width / 900))))
            
            # Scale widget widths: base is 27 at 900px, allow much larger scaling
            new_width = max(20, min(100, int(27 * (width / 900))))
            
            # Scale dropdown list font
            dropdown_font_size = max(12, min(28, int(14 * (width / 900))))
            self.root.option_add('*TCombobox*Listbox.font', ('Segoe UI', dropdown_font_size))
            
            # Update styles
            self.style.configure('Large.TLabel', font=('Segoe UI', new_font_size))
            self.style.configure('Large.TButton', font=('Segoe UI', new_font_size, 'bold'), padding=10)
            
            # Update widget fonts and sizes directly
            self.signal_combo.configure(font=('Segoe UI', entry_font_size), width=new_width)
            self.duration_entry.configure(font=('Segoe UI', entry_font_size), width=new_width)
            self.amplitude_entry.configure(font=('Segoe UI', entry_font_size), width=new_width)
            self.status_label.configure(font=('Segoe UI', max(9, entry_font_size - 1)))

    def generate_audio(self):
        signal_type = self.signal_type.get()
        duration = float(self.duration.get())
        amplitude = float(self.amplitude.get())
        frequency = float(440)  # A4 note, more reasonable default
        
        if duration <= 0:
            raise ValueError("Duration must be positive")
        if not 0 <= amplitude <= 1:
            raise ValueError("Amplitude must be between 0 and 1")
        if frequency <= 0:
            raise ValueError("Frequency must be positive")
        
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        if signal_type == "Sinusoidinė banga":
            audio = amplitude * np.sin(2 * np.pi * frequency * t)
        elif signal_type == "Stačiakampė banga":
            audio = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
        elif signal_type == "Pjūklo formos banga":
            audio = amplitude * 2 * (frequency * t - np.floor(frequency * t + 0.5))
        elif signal_type == "Trikampė banga":
            audio = amplitude * 2 * np.abs(2 * (frequency * t - np.floor(frequency * t + 0.5))) - amplitude
        elif signal_type == "Baltasis triukšmas":
            audio = amplitude * np.random.uniform(-1, 1, len(t))
        
        # Display waveform - show only a few cycles for clarity
        # Calculate how many samples to show (max 0.05 seconds or 10 cycles, whichever is less)
        cycles_to_show = 10
        display_duration = min(0.05, cycles_to_show / frequency, duration)
        display_samples = int(sample_rate * display_duration)
        
        # Scale time to show full duration on x-axis
        display_t_scaled = np.linspace(0, duration, len(t[:display_samples]))
        
        self.ax.clear()
        self.ax.plot(display_t_scaled, audio[:display_samples], linewidth=1.2)
        self.ax.set_xlabel(f"Laikas (s)", fontsize=18)
        self.ax.set_ylabel("Amplitudė", fontsize=18)
        self.ax.set_title(f"Garso bangos forma: {signal_type} (Trukmė: {duration}s)", fontsize=16)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(0, duration)
        self.ax.set_ylim(-1.2 * amplitude if amplitude > 0 else -0.1, 1.2 * amplitude if amplitude > 0 else 0.1)
        self.canvas.draw()
        
        # Store audio data
        self.audio_data = audio
        self.sample_rate = sample_rate
        
        # Enable play button
        self.play_stop_btn.config(state='normal')
        self.status_label.config(text=f"Garso signalas sugeneruotas", foreground="green")
    
    def toggle_play_stop(self):
        """Play or stop the audio"""
        if self.is_playing:
            # Stop audio
            sd.stop()
            self.is_playing = False
            self.play_stop_btn.config(text="Groti")
            self.status_label.config(text="Sustabdyta", foreground="orange")
        else:
            # Play audio
            if self.audio_data is not None:
                sd.play(self.audio_data, self.sample_rate)
                self.is_playing = True
                self.play_stop_btn.config(text="Stabdyti")
                signal_type = self.signal_type.get()
                self.status_label.config(text=f"Grojama...", foreground="green")
                
                # Start thread to wait for playback to finish
                threading.Thread(target=self.wait_for_playback, daemon=True).start()
    
    def wait_for_playback(self):
        """Wait for audio playback to finish"""
        sd.wait()
        if self.is_playing:  # Only update if not manually stopped
            self.is_playing = False
            self.root.after(0, self.on_audio_finished)
    
    def on_audio_finished(self):
        """Called when audio finishes playing"""
        self.play_stop_btn.config(text="Groti")
        self.status_label.config(text="Grojimas baigtas", foreground="red")

def main():
    root = tk.Tk()
    app = AudioSignalSynthesizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
