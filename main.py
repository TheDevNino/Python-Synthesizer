# PYTHON SYNTHESIZER
#
# Programmieren 1 Projekt
# HAW Hamburg - Fakultät DMI
# Studiengang Medientechnik
#
# Team: Erik Harder, Nino Cataffo
# Dozent: Thorsten Wagener
#
# Empfehlung: Digitales MIDI-Keyboard für MacOS "Mini Keys" https://apps.apple.com/de/app/mini-keys/id1611734597?mt=12
# GitHub Repository Link: https://github.com/TheDevNino/Python-Synthesizer.git

from pyo import *
from random import random
import tkinter as tk
from tkinter import ttk

def start_synth():
    # Create the midi synth.
    a1 = Synth()
    a1lp = ButLP(a1.sig(), Gui_input.lp_freq_input) #! Hier freq ändern 20k-20Hz (Logarithmisch)
    a1hp = ButHP(a1lp, freq=Gui_input.hp_freq_input) #! Hier freq ändern 20-20kHz (Logarithmisch)
    a1bp = ButBP(a1hp,freq=1000, q=5) # q ist glaube ich die breite, je höher desto stärker und schmalbandiger(glaube ich) 0 müsste aus sein
    a1ch = Chorus(a1hp,depth=3, feedback=0.5, bal=Gui_input.bal_input) # depth und feedback als fader, feedback max = 1 #! Hier balance von 1-0
    # bal für balance dry wet 1-> kein chorus, dry
    sc = Scope(a1.sig())

    # Send the synth's signal into a reverb processor.
    rev = STRev(a1ch, inpos=[0.1, 0.9], revtime=Gui_input.revtime_input, cutoff=Gui_input.reverb_input, bal=0.5) #!! Reverb Balance 0-1
    harm = Harmonizer(rev, transpo=-5, winsize=0.05) # dupliziert das signal und pitcht es um transpo halbtöne. 0 für aus, bis -12 runter

    a3 = Noisein()
    noiselp = ButLP(a3.sig(), freq=1500)
    noisehp = ButHP(noiselp, freq=200).mix(2)

    #lfouse = input("LFO JA NEIN 1: ja 0: nein: ")
    if Gui_input.lfo_active_input == 1:
        # c = Mix([harm, noisehp], voices=2)
        d = LFO(freq= Gui_input.lfo_freq_input, sharp=0.5, type=7, mul=0.5, add=1)
        e =harm*d
        f = noisehp*d
        e.out()
        f.out()
    elif Gui_input.lfo_active_input  == 0:
        harm.out()
        noisehp.out()

    #lownote = input("lower note on/off: ")#ungefilterte note eine oktave tiefer
    if Gui_input.lownote_active_input == "on":
        a2 = Synth(transpo=0.5, mul= Gui_input.lownote_loudness_input).out()

    s.gui(locals())

class SynthGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Synth GUI")
        self.root.geometry("450x800")  #Größe des GUI-Fensters
        #self.root.configure(background='white')

        # Container für Spalten-Frames
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Erstelle Frames für die zwei Spalten und den unteren Bereich
        self.top_frame = tk.Frame(self.container, height=50)# optional bg='grey'
        self.right_frame = tk.Frame(self.container)
        self.left_frame = tk.Frame(self.container)
        self.bottom_frame = tk.Frame(self.container, height=300)

        # Einstellen des oberen Frames
        self.top_frame.place(relx=0, rely=0, relwidth=1, relheight=0.05)  # Schmaler
        self.left_frame.place(relx=0, rely=0.05, relwidth=0.5, relheight=0.675)
        self.right_frame.place(relx=0.5, rely=0.05, relwidth=0.5, relheight=0.7)
        self.bottom_frame.place(relx=0, rely=0.65, relwidth=1, relheight=0.4)

        title = tk.Label(self.top_frame, text="Synth Einstellungen:")
        title.pack(side=tk.TOP, expand=True)

        self.inputs = {}  # Dictionary zum Speichern der Eingaben

        self.create_slider("Volume Synth", 0, 1, 0.01, self.right_frame)
        self.create_slider("Noise Lautstärke", 0, 1, 0.01, self.right_frame)
        self.create_toggle_button("LFO on", self.right_frame)
        self.create_slider("LFO Frequenz", 0.01, 25, 0.01, self.right_frame)
        self.create_toggle_button("Oktave tiefer", self.right_frame)
        self.create_slider("Lautstärke tieferer Oktave", 0, 1, 0.01, self.right_frame)
        self.create_slider("Attack", 0.001, 5, 0.001, self.left_frame)
        self.create_slider("Decay", 0.05, 5, 0.05, self.left_frame)
        self.create_slider("Sustain", 0.5, 10, 0.1, self.left_frame)
        self.create_slider("Release", 0.005, 5, 0.005, self.left_frame)

        self.create_type_dropdown("Waveform Osc 1", self.left_frame)
        self.create_slider("Sharpness Osc 1", 0, 1, 0.01,self.left_frame)
        self.create_type_dropdown("Waveform Osc 2", self.left_frame)
        self.create_slider("Sharpness Osc 2", 0, 1, 0.01, self.left_frame)

        self.create_log_slider("LP Frequenz", 20000, 20)
        self.create_log_slider("HP Frequenz", 20, 20000)
        self.create_slider("Chorus Balance", 0, 1, 0.01, self.right_frame)
        self.create_slider("Revtime", 0, 20, 0.1, self.right_frame)
        self.create_log_slider("Reverb LP", 20000, 20) # Cutoff

        self.submit_button = tk.Button(self.bottom_frame, text="Eingabe", command=self.submit, bg="cyan", fg="#003C6E")
        self.submit_button.pack(pady=(20, 0))  # 20 Pixel Platz oben, 0 Pixel unten

    def create_type_dropdown(self, label_text, frame):
        label = tk.Label(frame, text=label_text)
        label.pack(pady=2)

        combo_frame = tk.Frame(self.left_frame, width=110, height=20)
        combo_frame.pack_propagate(False)  # Verhindert, dass der Frame seine Größe automatisch anpasst
        combo_frame.pack(pady=0)

        self.combo = ttk.Combobox(combo_frame,
                                  values=["0: Saw up", "2: Saw down", "3: Triangle", "4: Pulse", "5: Bipolar",
                                          "6: Sample&Hold", "7: Mod. Sine"], width=50)
        self.combo.pack()
        # type 0 saw up 1 saw down 2 square 3 triangle 4 pulse 5 bipolar pulse 6 sample and hold 7 modulated sine

        self.inputs[label_text] = self.combo

    def create_slider(self, label_text, min_value, max_value, res_value, frame):
        label = tk.Label(frame, text=label_text)
        label.pack(pady=0)

        slider = tk.Scale(frame, from_=min_value, to=max_value, resolution=res_value, orient=tk.HORIZONTAL)
        slider.pack()

        self.inputs[label_text] = slider

    def create_log_slider(self, label_text, min_value, max_value):
        label = tk.Label(self.bottom_frame, text=label_text)
        label.pack(pady=5)

        log_min = math.log10(min_value)
        log_max = math.log10(max_value)
        log_slider = LogScale(self.bottom_frame, min_value=log_min, max_value=log_max)
        log_slider.pack()
        self.inputs[label_text] = log_slider

    def create_toggle_button(self, label_text, frame):
        # um .grid() unabhängig zu verwenden.
        inner_frame = tk.Frame(frame)
        inner_frame.pack(pady=2)  # oder positioniere es, wie es in dein Layout passt

        label = tk.Label(inner_frame, text=label_text)
        label.grid(row=0, column=0, sticky='w')

        var = tk.IntVar()
        toggle_button = tk.Checkbutton(inner_frame, text="", variable=var)
        toggle_button.grid(row=0, column=1)

        self.inputs[label_text] = var

    def submit(self):
        input_values = {}

        for label_text, entry in self.inputs.items():
            if isinstance(entry, LogScale):
                input_values[label_text] = entry.value
            else:
                input_values[label_text] = entry.get()

        self.noiseamp_input = input_values["Noise Lautstärke"]
        self.lfo_active_input = input_values["LFO on"]
        self.lfo_freq_input = input_values["LFO Frequenz"]
        self.lownote_active_input = input_values["Oktave tiefer"]
        self.lownote_loudness_input = input_values["Lautstärke tieferer Oktave"]
        self.attack_input = input_values["Attack"]
        self.decay_input = input_values["Decay"]
        self.release_input = input_values["Release"]
        self.sustain_input = input_values["Sustain"]
        self.mul_input = input_values["Volume Synth"]
        self.lp_freq_input = input_values["LP Frequenz"]
        self.hp_freq_input = input_values["HP Frequenz"]
        self.bal_input = input_values["Chorus Balance"]
        self.revtime_input = input_values["Revtime"]
        self.reverb_input = input_values["Reverb LP"]

        def get_osc_value(input):
            try:
                waveform_value = input
                first_character = waveform_value[0]
                return int(first_character)
            except (IndexError, ValueError) as e:
                print(f"Fehler beim Abrufen des Oszillatorwerts! {e}")
                return 0  # Gibt einen Standardwert zurück, wenn ein Fehler auftritt

        self.osc1_input = get_osc_value(input_values["Waveform Osc 1"])
        self.osc2_input = get_osc_value(input_values["Waveform Osc 2"])

        self.sharp1_input = input_values["Sharpness Osc 1"]
        self.sharp2_input = input_values["Sharpness Osc 2"]

        print(input_values)
        self.root.destroy()

        start_synth()


class LogScale(tk.Canvas):
    def __init__(self, master, min_value=0, max_value=1, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        self.min = min_value  # For calculation in on_drag
        self.max = max_value  # For calculation in on_drag
        self.value = 10 ** min_value  # Initialisiert value mit einem sicheren Wert innerhalb des gültigen Bereichs
        super().__init__(master, **kwargs)
        self.configure(width=320, height=30)
        self.bind("<Configure>", self.redraw)
        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)

    def get(self):
        return self.value

    def draw_value_text(self):
        # Löschen des vorherigen Wertes
        self.delete("slider_value_text")
        # Positionsberechnung und Textzeichnung
        slider_position_x = self.calculate_slider_x_position(self.value)
        # Stellen Sie sicher, dass der Text sichtbar ist, indem Sie ihn ein wenig über dem Slider positionieren
        x, y = slider_position_x, 28
        text = f"{round(int(self.value)):.2f}"

        # Zuerst ein Rechteck als Hintergrund zeichnen
        background_id = self.create_rectangle(x, y, x + 40, y - 20, fill="red", tags="slider_value_bg")

        # Dann den Text über das Rechteck zeichnen
        text_id = self.create_text(x + 20, y + -10, text=text, fill="white", tags="slider_value_text")

    def redraw(self, event=None):
        self.delete("all")
        self.draw_ticks()
        self.draw_slider()
        self.draw_value_text()  # Zeichnen Sie den Text am Ende

    def draw_ticks(self):
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        min_value = self.min_value
        max_value = self.max_value

        tick_count = 11
        tick_step = (max_value - min_value) / (tick_count - 1)

        for i in range(tick_count):
            tick_value = min_value + i * tick_step
            tick_x = i * canvas_width / (tick_count - 1)
            self.create_line(tick_x, canvas_height * 0.8, tick_x, canvas_height, fill="black")

            # Überprüfen, ob der Wert größer als 1000 ist
            if 10 ** tick_value >= 1000:
                # Wenn ja, den Wert durch 1000 teilen und "k" anhängen
                tick_text = f"{(10 ** tick_value) / 1000:.0f}k"
            else:
                # Andernfalls den Wert normal anzeigen
                tick_text = f"{10 ** tick_value:.0f}"

            self.create_text(tick_x, canvas_height * 0.2, text=tick_text, anchor="n")

    def draw_slider(self):
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        min_value = self.min_value
        max_value = self.max_value
        value = self.value

        slider_x = (math.log10(value) - min_value) / (max_value - min_value) * canvas_width
        self.create_rectangle(slider_x - 5, 0, slider_x + 5, canvas_height, fill="red", outline="")

    def on_click(self, event):
        self.on_drag(event)

    def on_drag(self, event):
        canvas_width = self.winfo_width()
        slider_x = event.x
        slider_x = max(0, min(slider_x, canvas_width))
        value = 10 ** (self.min_value + (slider_x / canvas_width) * (self.max_value - self.min_value))
        self.value = value

        # Löschen des vorherigen Wertes
        self.delete("slider_value_text")

        # Positionsberechnung und Textzeichnung
        slider_position_x = self.calculate_slider_x_position(value)
        self.create_text(slider_position_x, 10, text=f"{value:.2f}", fill="black", tags="slider_value_text")

        self.redraw()

    def calculate_slider_x_position(self, value):
        canvas_width = self.winfo_width()
        slider_position_x = (math.log10(value) - self.min_value) / (self.max_value - self.min_value) * canvas_width
        #print("Slider Position X:", slider_position_x)  # Zum Debuggen
        return slider_position_x


###############
class Synth:
    def __init__(self, transpo=1, mul=1):
        # Transposition factor.
        self.transpo = Sig(transpo)
        # Receive midi notes, convert pitch to Hz and manage 10 voices of polyphony.
        self.note = Notein(poly=10, scale=1, first=0, last=127)

        # Handle pitch and velocity (Notein outputs normalized amplitude (0 -> 1)).
        self.pit = self.note["pitch"] * self.transpo
        self.amp = MidiAdsr(self.note["velocity"], Gui_input.attack_input, Gui_input.decay_input, Gui_input.sustain_input, Gui_input.release_input, Gui_input.mul_input)

        # Anti-aliased stereo square waves, mixed from 10 streams to 1 stream
        # to avoid channel alternation on new notes.
        self.osc1 = LFO(self.pit, sharp=Gui_input.sharp1_input, type=Gui_input.osc1_input, mul=self.amp).mix(1) #! Sharpness 0-1, Auswahl 0-7
        self.osc2 = LFO(self.pit * 0.997, sharp=Gui_input.sharp2_input , type=Gui_input.osc2_input, mul=self.amp).mix(1)#! Sharpness 0-1, Auswahl 0-7
        #self.osc3 = Noise(mul=self.amp).mix(1)
        # type 0 saw up 1 saw down 2 square 3 triangle 4 pulse 5 bipolar pulse 6 sample and hold 7 modulated sine
        # Stereo mix.
        self.mix = Mix([self.osc1, self.osc2], voices=2)

        # High frequencies damping.
        self.damp = ButLP(self.mix, freq=5000)

        # Moving notches, using two out-of-phase sine wave oscillators.
        self.lfo = Sine(0.2, phase=[random(), random()]).range(250, 4000)
        self.notch = ButBR(self.damp, self.lfo, mul=mul)

    def out(self):
        "Sends the synth's signal to the audio output and return the object itself."
        self.notch.out()
        return self

    def sig(self):
        "Returns the synth's signal for future processing."
        return self.notch

############
class Noisein: #zum layern klingt ganz cool
    def __init__(self, transpo=1, mul=1):
        # Transposition factor.
        self.transpo = Sig(transpo)
        # Receive midi notes, convert pitch to Hz and manage 10 voices of polyphony.
        self.note = Notein(poly=10, scale=1, first=0, last=127)

        # Handle pitch and velocity (Notein outputs normalized amplitude (0 -> 1)).
        self.pit = self.note["pitch"] * self.transpo

        self.amp_noise = MidiAdsr(self.note["velocity"], attack=0.5, decay=0.1, sustain=0.7, release=1, mul=0.1,)

        # Anti-aliased stereo square waves, mixed from 10 streams to 1 stream
        # to avoid channel alternation on new notes.

        #noise on/off schalter nicht benötigt, wenn noise off -> fader auf 0 setzen.
        #noiseamp = float(input("Wert zwischen 0 und 1 für Noise Lautstärke: ")) #zwischen 0 und 1 variabel, wobei höher als 0.6 unrealistisch

        #print(f"noise {Gui_input.noiseamp_input}")
        self.osc3 = Noise(mul=self.amp_noise * Gui_input.noiseamp_input)
        # type 0 saw up 1 saw down 2 square 3 triangle 4 pulse 5 bipolar pulse 6 sample and hold 7 modulated sine
        # Stereo mix.
        self.mix = Mix([self.osc3], voices=2)

        # High frequencies damping.
        self.damp = ButLP(self.mix, freq=5000)

    def out(self):
        "Sends the synth's signal to the audio output and return the object itself."
        self.damp.out()
        return self
    def sig(self):
        "Returns the synth's signal for future processing."
        return self.damp

if __name__ == "__main__":

    s = Server()
    s.setMidiInputDevice(99)  # Open all input devices.
    s.boot()

    Gui_input = SynthGUI()
    Gui_input.root.mainloop()
