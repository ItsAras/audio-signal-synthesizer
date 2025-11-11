import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import sounddevice as sd


class AudioSignalSynthesizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Garso signalų sintezatorius")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Signal Type
        ttk.Label(main_frame, text="Garso tipas:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.signal_type = tk.StringVar(value="Sinusoidinė banga")
        signal_combo = ttk.Combobox(main_frame, textvariable=self.signal_type, 
                                     values=["Sinusoidinė banga", "Stačiakampė banga", "Pjūklo formos banga", "Trikampė banga", "Baltasis triukšmas"],
                                     state="readonly", width=25)
        signal_combo.grid(row=0, column=1, pady=5, padx=10)
        
        # Audio Length
        ttk.Label(main_frame, text="Trukmė (sekundėmis):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.duration = tk.StringVar(value="2.0")
        duration_entry = ttk.Entry(main_frame, textvariable=self.duration, width=27)
        duration_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # Amplitude
        ttk.Label(main_frame, text="Amplitudė (0-1):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.amplitude = tk.StringVar(value="0.5")
        amplitude_entry = ttk.Entry(main_frame, textvariable=self.amplitude, width=27)
        amplitude_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Generate Button
        generate_btn = ttk.Button(main_frame, text="Generate", command=self.generate_audio)
        generate_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="", foreground="green")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
    def generate_audio(self):
        try:
            # Get values
            signal_type = self.signal_type.get()
            duration = float(self.duration.get())
            amplitude = float(self.amplitude.get())
            frequency = float(self.frequency.get())
            
            # Validate inputs
            if duration <= 0:
                raise ValueError("Duration must be positive")
            if not 0 <= amplitude <= 1:
                raise ValueError("Amplitude must be between 0 and 1")
            if frequency <= 0:
                raise ValueError("Frequency must be positive")
            
            # Generate audio
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            
            if signal_type == "Sine":
                audio = amplitude * np.sin(2 * np.pi * frequency * t)
            elif signal_type == "Square":
                audio = amplitude * np.sign(np.sin(2 * np.pi * frequency * t))
            elif signal_type == "Sawtooth":
                audio = amplitude * 2 * (t * frequency - np.floor(0.5 + t * frequency))
            elif signal_type == "Triangle":
                audio = amplitude * 2 * np.abs(2 * (t * frequency - np.floor(0.5 + t * frequency))) - 1
            elif signal_type == "White Noise":
                audio = amplitude * np.random.uniform(-1, 1, len(t))
            
            # Play audio
            sd.play(audio, sample_rate)
            self.status_label.config(text=f"Playing {signal_type} wave...", foreground="green")
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


def main():
    root = tk.Tk()
    app = AudioSignalSynthesizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
