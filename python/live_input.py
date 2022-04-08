"""
Initial experimentation with live input
"""
import numpy as np
import pyaudio
import time
import librosa
import pydub
import math
import keyboard


def frequency_to_note(frequency):
    # define constants that control the algorithm
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']  # these are the 12 notes in each octave
    OCTAVE_MULTIPLIER = 2  # going up an octave multiplies by 2
    KNOWN_NOTE_NAME, KNOWN_NOTE_OCTAVE, KNOWN_NOTE_FREQUENCY = ('A', 4, 440)  # A4 = 440 Hz

    # calculate the distance to the known note
    # since notes are spread evenly, going up a note will multiply by a constant
    # so we can use log to know how many times a frequency was multiplied to get from the known note to our note
    # this will give a positive integer value for notes higher than the known note, and a negative value for notes lower than it (and zero for the same note)
    note_multiplier = OCTAVE_MULTIPLIER ** (1 / len(NOTES))
    frequency_relative_to_known_note = frequency / KNOWN_NOTE_FREQUENCY
    distance_from_known_note = math.log(frequency_relative_to_known_note, note_multiplier)

    # round to make up for floating point inaccuracies
    distance_from_known_note = round(distance_from_known_note)

    # using the distance in notes and the octave and name of the known note,
    # we can calculate the octave and name of our note
    # NOTE: the "absolute index" doesn't have any actual meaning, since it doesn't care what its zero point is. it is just useful for calculation
    known_note_index_in_octave = NOTES.index(KNOWN_NOTE_NAME)
    known_note_absolute_index = KNOWN_NOTE_OCTAVE * len(NOTES) + known_note_index_in_octave
    note_absolute_index = known_note_absolute_index + distance_from_known_note
    note_octave, note_index_in_octave = note_absolute_index // len(NOTES), note_absolute_index % len(NOTES)
    note_name = NOTES[note_index_in_octave]

    return note_name, note_octave


class AudioHandler(object):
    def __init__(self, threshold):
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2  # 1024 * 2
        self.p = None
        self.stream = None

        self.mic_threshold = threshold  # TODO: Set otherwise.

        #self.asg_chunks = []
        self.librosa_chunks = []
        self.detected_notes = []

        self.start_i = None
        self.counter = 0

    def start(self, mic):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=1,
                                  rate=self.RATE,
                                  input=True,
                                  output=False,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.CHUNK)

    def stop(self):
        self.stream.close()
        self.p.terminate()

    def estimate_freq(self, s1, s2):
        data = self.librosa_chunks[s1: s2]
        joined = np.concatenate(data)
        length = len(joined) / self.RATE
        print("Sample length: ", length)

        c = np.fft.fft(joined)
        fr = np.array(range(0, len(joined))) / length

        highest = np.argmax(c[0:2400])
        f = fr[highest]  # Frequency range of a guitar

        print("Highest peak found to be {}".format(highest))


        # Get the 5 highest
        likely = []

        ind = np.argpartition(c[0:2400], -5)[-5:]
        top = fr[ind]
        print(top)

        for i in ind:
            offset = highest - i

            freq = fr[i]

            if abs(offset) < 40:
                if freq > 0 and freq < 2400:
                    note, octave = frequency_to_note(freq)
                    recording = "{}{}".format(note, octave)

                    if recording not in likely:
                        likely.append(recording)

        print(likely)

        try:
            note, octave = frequency_to_note(f)
        except:
            print("Couldn't convert note, naming defaults")
            note, octave = "X", "X"

        if note != "X" and octave != "X":
            self.detected_notes.append("{}{}".format(note, octave))

        print("{}, {}{}".format(round(f, 3), note, octave))

    def get_db(self, data):
        audio_segment = pydub.AudioSegment(
            data,
            frame_rate=self.RATE,
            sample_width=data.dtype.itemsize,
            channels=self.CHANNELS
        )
        return audio_segment.dBFS

    def callback(self, in_data, frame_count, time_info, flag):
        # Get both float and int decodings of data
        librosa_array = np.frombuffer(in_data, dtype=np.float32)
        asg_array = np.array(librosa_array * (1 << 15), dtype=np.int32)

        # Adding to array for later usage
        self.librosa_chunks.append(librosa_array)
        #self.asg_chunks.append(asg_array)

        # Threshold detection
        if self.start_i is None and self.get_db(asg_array) > self.mic_threshold:
            self.start_i = self.counter
        elif self.start_i is not None and self.get_db(asg_array) < self.mic_threshold:
            # print("cuttoff detected: ({},{})".format(self.start_i, self.counter))
            self.estimate_freq(self.start_i, self.counter)
            self.start_i = None

        self.counter += 1
        return None, pyaudio.paContinue

    def mainloop(self):
        while (self.stream.is_active()):
            if keyboard.read_key() == "s" or keyboard.read_key() == "S":
                print(self.detected_notes)
                audio.stop()
                exit(0)
            else:
                continue



if __name__ == '__main__':
    audio = AudioHandler(-125)  # Set the mic threshold
    audio.start(2)              # Set the mic number
    print("Started recording... Press S/s to stop the program.")
    audio.mainloop()

