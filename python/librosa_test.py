import numpy as np
import pyaudio
import time
import librosa
import pydub
import math


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
    def __init__(self):
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2
        self.p = None
        self.stream = None

        self.mic_threshold = -125  # TODO: Set otherwise.

        self.asg_chunks = []
        self.librosa_chunks = []

        self.start_i = None
        self.counter = 0

    def start(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  input_device_index=1,
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

        f = fr[np.argmax(c[0:1200])]

        try:
            note, octave = frequency_to_note(f)
        except:
            print("Couldn't convert note, naming defaults")
            note, octave = "X", "X"

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
        self.asg_chunks.append(asg_array)

        # Threshold
        if self.start_i is None and self.get_db(asg_array) > self.mic_threshold:
            self.start_i = self.counter
        elif self.start_i is not None and self.get_db(asg_array) < self.mic_threshold:
            # print("cuttoff detected: ({},{})".format(self.start_i, self.counter))
            self.estimate_freq(self.start_i, self.counter)
            self.start_i = None

        self.counter += 1
        return None, pyaudio.paContinue

    def mainloop(self):
        while (
        self.stream.is_active()):  # if using button you can set self.stream to 0 (self.stream = 0), otherwise you can use a stop condition
            time.sleep(2.0)


if __name__ == '__main__':
    audio = AudioHandler()
    audio.start()  # open the the stream
    print("Started recording...")
    audio.mainloop()  # main operations with librosa
    audio.stop()
