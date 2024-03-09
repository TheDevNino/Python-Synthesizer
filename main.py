from pyo import *
from random import random
import tkinter as tk

##################
class SynthGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Synth GUI")
        self.root.geometry("380x920")  #Größe des GUI-Fensters
        #self.root.configure(background='white')


        title = tk.Label(self.root, text="Einstellungen")
        title.pack()

        self.inputs = {}  # Dictionary zum Speichern der Eingaben

        self.create_slider("Noise Lautstärke", 0, 1, 0.01)
        self.create_toggle_button("LFO on")
        self.create_slider("LFO Frequenz", 0.01, 25, 0.01)
        self.create_toggle_button("Oktave tiefer")
        self.create_slider("Lautstärke tieferer Oktave", 0, 1, 0.01)
        self.create_slider("Attack", 0.001, 5, 0.001)
        self.create_slider("Decay", 0.05, 5, 0.05)
        self.create_slider("Release", 0.005, 5, 0.005)
        self.create_slider("Sustain", 0.5, 10, 0.1)
        self.create_slider("Multiplikator", 0, 1, 0.01)

        # Weitere Eingabefelder hinzufügen bei Bedarf

        self.submit_button = tk.Button(self.root, text="Eingabe", command=self.submit, bg="cyan", fg="#003C6E")
        self.submit_button.pack()

    def create_slider(self, label_text, min_value, max_value, res_value):
        label = tk.Label(self.root, text=label_text)
        label.pack(pady=5)

        slider = tk.Scale(self.root, from_=min_value, to=max_value, resolution=res_value, orient=tk.HORIZONTAL)
        slider.pack()

        self.inputs[label_text] = slider

    def create_toggle_button(self, label_text):
        label = tk.Label(self.root, text=label_text)
        label.pack(pady=5)

        var = tk.IntVar()

        toggle_button = tk.Checkbutton(self.root, text="", variable=var)
        toggle_button.pack()

        self.inputs[label_text] = var

    def submit(self):
        input_values = {}

        for label_text, entry in self.inputs.items():
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
        self.mul_input = input_values["Multiplikator"]

        print(input_values)

        #self.root.destroy()



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
        self.osc1 = LFO(self.pit, sharp=0.5, type=2, mul=self.amp).mix(1)
        self.osc2 = LFO(self.pit * 0.997, sharp=0.5, type=4, mul=self.amp).mix(1)
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

        print(f"noise {Gui_input.noiseamp_input}")
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

    # Create the midi synth.
    a1 = Synth()
    a1lp = ButLP(a1.sig(), 20000)
    a1hp = ButHP(a1lp, freq=20)
    a1bp = ButBP(a1hp,freq=1000, q=5) # q ist glaube ich die breite, je höher desto stärker und schmalbandiger(glaube ich) 0 müsste aus sein
    a1ch = Chorus(a1bp,depth=3, feedback=0.5, bal=0.3) # depth und feedback als fader, feedback max = 1
    # bal für balance dry wet 1-> kein chorus, dry
    sc = Scope(a1.sig())

    # Send the synth's signal into a reverb processor.
    rev = STRev(a1ch, inpos=[0.1, 0.9], revtime=15, cutoff=4000, bal=0.15) #revtime und cutoff als fader
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