import tkinter as tk
from tkinter import ttk
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class AudioSignalSynthesizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Garso signalų sintezatorius")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(main_frame, text="Garso tipas:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.signal_type = tk.StringVar(value="Sinusoidinė banga")
        signal_combo = ttk.Combobox(main_frame, textvariable=self.signal_type, 
                                     values=["Sinusoidinė banga", "Stačiakampė banga", "Pjūklo formos banga", "Trikampė banga", "Baltasis triukšmas"],
                                     state="readonly", width=25)
        signal_combo.grid(row=0, column=1, pady=5, padx=10)

        ttk.Label(main_frame, text="Trukmė (sekundėmis):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.duration = tk.StringVar(value="2.0")
        duration_entry = ttk.Entry(main_frame, textvariable=self.duration, width=27)
        duration_entry.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(main_frame, text="Amplitudė (0-1):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.amplitude = tk.StringVar(value="0.5")
        amplitude_entry = ttk.Entry(main_frame, textvariable=self.amplitude, width=27)
        amplitude_entry.grid(row=2, column=1, pady=5, padx=10)

        generate_btn = ttk.Button(main_frame, text="Generuoti", command=self.generate_audio)
        generate_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.status_label = ttk.Label(main_frame, text="", foreground="green")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)

        # Waveform display
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, pady=10)
        
        self.ax.set_xlabel("Laikas (s)")
        self.ax.set_ylabel("Amplitudė")
        self.ax.set_title("Garso bangos forma")
        self.ax.grid(True, alpha=0.3)

    def generate_audio(self):
        signal_type = self.signal_type.get()
        duration = float(self.duration.get())
        amplitude = float(self.amplitude.get())
        frequency = float(1000)
        
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
            audio = amplitude * 2 * (t * frequency - np.floor(0.5 + t * frequency))
        elif signal_type == "Trikampė banga":
            audio = amplitude * 2 * np.abs(2 * (t * frequency - np.floor(0.5 + t * frequency))) - 1
        elif signal_type == "Baltasis triukšmas":
            audio = amplitude * np.random.uniform(-1, 1, len(t))
        
        # Display waveform (show only first 0.05 seconds for clarity)
        display_duration = min(0.05, duration)
        display_samples = int(sample_rate * display_duration)
        
        self.ax.clear()
        self.ax.plot(t[:display_samples], audio[:display_samples], linewidth=0.5)
        self.ax.set_xlabel("Laikas (s)")
        self.ax.set_ylabel("Amplitudė")
        self.ax.set_title(f"Garso bangos forma: {signal_type}")
        self.ax.grid(True, alpha=0.3)
        self.ax.set_xlim(0, display_duration)
        self.ax.set_ylim(-1, 1)
        self.canvas.draw()
        
        sd.play(audio, sample_rate)
        self.status_label.config(text=f"Grojama {signal_type}...", foreground="green")

def main():
    root = tk.Tk()
    app = AudioSignalSynthesizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
