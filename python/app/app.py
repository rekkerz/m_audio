import pathlib
import threading
import time

import pyaudio
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showerror, showinfo, showwarning

from classes.scrollimage import ScrollableImage
from classes.audio import AudioHandler
from classes.staffgen import StaffGenerator
from classes.model import Model

import speech_recognition as s_r

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "first_layout.ui"


class FirstLayoutApp:
    def __init__(self, master=None):
        # build ui
        self.mic_map = None
        self.build_ui(master=master)

        # Local variables
        self.selected_mic = tk.StringVar()
        self.selected_mic_level = tk.DoubleVar()

        # set up microphones
        self.set_microphones()

        # set up variables
        self.mic_options.configure(textvariable=self.selected_mic)
        self.mic_level.configure(variable=self.selected_mic_level)

        self.listen_for_notes = False
        self.stop_thread = False

        self.note_listener_thread = threading.Thread(target=self.note_listener)
        self.note_listener_thread.start()

        # self.note_listener_thread = multiprocessing.Process(target=self.note_listener)
        self.notes = []

        self.note_writer = None
        self.staff_gen = StaffGenerator()

        self.test_threshold.configure(command=self.save_pdf)

        self.notes_played = 0

        self.audio = None

    def build_ui(self, master):
        """ A function that contains the code from Pygubu to build the application - Simply copy & paste """
        self.mainwindow = tk.Tk() if master is None else tk.Toplevel(master)
        self.mainwindow.protocol('WM_DELETE_WINDOW', self.terminate)

        self.dashboard = ttk.Frame(self.mainwindow)

        self.mic_select = ttk.Frame(self.dashboard)

        self.mic_label = ttk.Label(self.mic_select)
        self.mic_label.configure(text='Select Microphone')
        self.mic_label.place(anchor='nw', relwidth='0.60', relx='0.03', rely='0.0', x='0', y='0')

        self.mic_options = ttk.Combobox(self.mic_select)
        self.mic_options.place(anchor='nw', relx='0.03', rely='0.30', x='0', y='0')

        self.mic_level = tk.Scale(self.mic_select)
        self.mic_level.configure(digits='0', from_='0', orient='horizontal', repeatdelay='0')
        self.mic_level.configure(showvalue='true', sliderrelief='flat', to='100')
        self.mic_level.place(anchor='nw', relheight='0.61', relwidth='0.3', relx='0.53', rely='0.36', x='0', y='0')

        self.refresh = tk.Button(self.mic_select)
        self.refresh.configure(text='refresh')
        self.refresh.place(anchor='nw', relx='0.03', rely='0.6', x='0', y='0')
        self.refresh.configure(command=self.set_microphones)
        self.threshold_label = tk.Label(self.mic_select)
        self.threshold_label.configure(text='threshold')
        self.threshold_label.place(anchor='nw', relx='0.58', x='0', y='0')
        self.test_threshold = tk.Button(self.mic_select)
        self.test_threshold.configure(text='save')

        self.test_threshold.place(anchor='nw', relx='0.86', rely='0.34', x='0', y='0')
        self.mic_select.configure(borderwidth='2', relief='raised')
        self.mic_select.place(anchor='nw', relheight='1.0', relwidth='0.50', x='0', y='0')
        self.control = tk.Frame(self.dashboard)
        self.start = tk.Button(self.control)
        self.start.configure(text='start')
        self.start.place(anchor='nw', relheight='0.42', relwidth='0.25', relx='0.05', rely='0.25', x='0', y='0')
        self.start.configure(command=self.start_audio)
        self.stop = tk.Button(self.control)
        self.stop.configure(compound='top', text='stop')
        self.stop.place(anchor='nw', relheight='0.42', relwidth='0.25', relx='0.35', rely='0.25', x='0', y='0')
        self.stop.configure(command=self.stop_audio)

        self.record = tk.Button(self.control)
        self.record.configure(text='tabify')
        self.record.place(anchor='nw', relheight='0.42', relwidth='0.25', relx='0.65', rely='0.25', x='0', y='0')
        self.record.configure(command=self.tabify)

        self.control.configure(height='200', width='200')
        self.control.place(anchor='nw', relheight='1', relwidth='0.5', relx='0.5', x='0', y='0')
        self.dashboard.configure(relief='ridge')
        self.dashboard.place(anchor='nw', relheight='0.15', relwidth='1.0', relx='0.0', rely='0.0', x='0', y='0')

        self.display = ttk.Frame(self.mainwindow)
        self.display.configure(height='200', width='200')
        self.display.place(anchor='nw', relheight='0.85', relwidth='1.0', rely='0.15', x='0', y='0')

        self.staff_display = ttk.Frame(self.display)
        self.staff_display.configure(height='100', width='200')
        self.staff_display.place(anchor='nw', relheight='0.85', relwidth='1.0', rely='0.15', x='0', y='0')

        self.note_display = tk.Text(self.display)
        self.note_display.configure(height='10', width='50')
        _text_ = "Execute tabify to fill this with tab notation"
        self.note_display.insert('0.0', _text_)
        self.note_display.place(anchor='nw', relheight='0.5', relwidth='1.0', relx='0.0', rely='0.5', x='0', y='0')

        self.mainwindow.configure(height='480', width='640')
        self.mainwindow.minsize(640, 480)

    def run(self):
        self.model = Model()
        self.mainwindow.mainloop()

    def terminate(self):
        print("Terminating the application...")
        self.listen_for_notes = False
        self.stop_thread = True
        self.mainwindow.destroy()
        if self.note_writer != None:
            self.note_writer.terminate()
        exit(0)

    def update_staff(self):
        img = tk.PhotoImage(file="demo.png")
        self.image_window = ScrollableImage(self.staff_display, image=img,
                                            scrollbarwidth=2)

        self.image_window.configure(height='200', width='200')
        self.image_window.place(anchor='nw', relheight='1.0', relwidth='1.0', rely='0', x='0', y='0')

    def display_staff(self, notes):
        # Generate the staff
        self.staff_gen.main(notes, on_exit=self.update_staff)

    def note_listener(self):
        # This is a multithreaded function which listens for
        # increase of notes and synchronizes the two lists
        while True:
            if self.stop_thread:  # stop thread flag
                break

            if self.listen_for_notes:
                if self.audio == None:
                    time.sleep(2)
                    continue
                else:
                    if self.notes_played < self.audio.notes_played:
                        self.notes_played = self.audio.notes_played
                        # print("Number of notes played = ", self.notes_played)
                        threading.Thread(target=self.display_staff(self.audio.detected_notes))

            else:
                time.sleep(1)
                continue

    def start_audio(self):
        threshhold_percentage = self.selected_mic_level.get()
        threshold = (threshhold_percentage/100) * -200
        self.audio = AudioHandler(threshold)
        if self.selected_mic.get() == "":
            showerror(
                title="Select a microphone",
                message="Microphone not selected!"
            )
        else:
            mic = self.mic_map[self.selected_mic.get()]
            self.audio.start(mic)  # start with the selected mic
            self.listen_for_notes = True  # start listening for notes

    def stop_audio(self):
        if self.audio == None:
            showwarning(
                title="Nothing to stop",
                message="Audio is not currently running, nothing to stop."
            )
            return
        self.audio.stop()
        # self.audio = None  # clear the audio

        self.listen_for_notes = False  # stop listening for notes

    def seq_to_text(self, sequence):
        tuning = ["E", "B", "G", "D", "A", "e"]
        tab_lists = {"E": [],
                     "B": [],
                     "G": [],
                     "D": [],
                     "A": [],
                     "e": []}

        for i in sequence:
            string = tuning[i[0]-1]
            filler = "-" * len(str(i[1])) # get the length of "-" to match chars
            for key in tab_lists.keys():
                if key == string:
                    tab_lists[key].append(str(i[1]))
                else:
                    tab_lists[key].append(filler)
                tab_lists[key].append("-")

        return "e| " + str("".join(tab_lists["e"])) + "\n" \
               + "B| " + str("".join(tab_lists["B"])) + "\n" \
               + "G| " + str("".join(tab_lists["G"])) + "\n" \
               + "D| " + str("".join(tab_lists["D"])) + "\n" \
               + "A| " + str("".join(tab_lists["A"])) + "\n" \
               + "E| " + str("".join(tab_lists["E"]))

    def tabify(self):
        # Obtain the sequence
        if self.audio is None or len(self.audio.detected_notes) == 0:
            showwarning(
                title="Nothing to Tabify",
                message="Record some notes first using the start button"
            )
            return

        # Filter out impossible notes
        sequence = self.audio.detected_notes
        clean_sequence = []
        for i in sequence:
            listed = list(i)
            if int(listed[-1]) <= 6 and int(listed[-1]) >= 2:
                clean_sequence.append(i)

        #print(clean_sequence)

        # Classify sequence using the Model module
        estimation = self.model.eval_sequence(clean_sequence)

        #print(estimation)
        text = self.seq_to_text(estimation)

        # display the text in the text box
        self.note_display.delete("1.0", "end-1c")
        self.note_display.insert('0.0', text)

    def set_microphones(self):
        mics, value_map = self.get_audio_devices()
        self.mic_map = value_map
        self.mic_options.configure(values=mics)  # NOTE: If you change microphone box id, this will break
        self.mic_options.option_clear()
        #print("set_microphone")

    def get_audio_devices(self):
        p = pyaudio.PyAudio()
        mics = []
        indx = []
        for i in range(p.get_device_count()):
            name = p.get_device_info_by_index(i).get('name')
            if name.split(" ")[0] == "Microphone":
                stripped_name = " ".join(name.split(" ")[1:])
                stripped_name = [char for char in stripped_name]
                stripped_name = "".join(stripped_name[1:-1]).strip()

                if stripped_name not in mics:
                    mics.append(stripped_name)
                    indx.append(i)

        # Convert to dictionary
        dictionary = {}
        for i, v in enumerate(mics):
            device_indx = indx[i]
            dictionary[v] = device_indx

        return mics, dictionary

    def save_pdf(self):
        if self.staff_gen == None or self.audio == None or len(self.audio.detected_notes) == 0:
            showwarning(
                title="Nothing to save",
                message="Nothing to save to PDF."
            )
            return

        else:
            self.staff_gen.save_pdf()

if __name__ == '__main__':
    app = FirstLayoutApp()
    app.run()
