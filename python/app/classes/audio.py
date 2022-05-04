import math
import numpy as np
import pyaudio
import pydub

class AudioHandler(object):
    def __init__(self, threshold):
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2  # 1024 * 2
        self.p = None
        self.stream = None

        self.mic_threshold = threshold

        #self.asg_chunks = []
        self.librosa_chunks = []
        self.detected_notes = []

        self.notes_played = 0

        self.start_i = None
        self.counter = 0

    def start(self, mic):
        print("Audio started")
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=1,
                                  rate=self.RATE,
                                  input=True,
                                  output=False,
                                  stream_callback=self.callback,
                                  frames_per_buffer=self.CHUNK)

    def stop(self):
        print("Audio stopped")
        self.stream.close()
        self.p.terminate()

    def estimate_freq(self, s1, s2):
        data = self.librosa_chunks[s1: s2]
        joined = np.concatenate(data)
        length = len(joined) / self.RATE
        # print("Sample length: ", length)

        c = np.fft.fft(joined)
        fr = np.array(range(0, len(joined))) / length

        highest = np.argmax(c)
        f = fr[highest]  # Frequency range of a guitar

        # find top 5 frequencies
        ind = np.argpartition(c, -5)[-5:]  # find top 5
        top = fr[ind]
        #print("Top frequencies: ", top)

        most_likely = []
        notes = []
        # filter through the top to find most likely
        for freq in top:
            if 0 < freq < 1200:
                most_likely.append(freq)
                note, octave = self.frequency_to_note(freq)
                notes.append(note)

        print("Most likely: \t", most_likely)
        print("Notes: \t", notes)

        if len(most_likely) == 0:
            return None, None, None

        f = min(most_likely)

        try:
            note, octave = self.frequency_to_note(f)
        except:
            print("Couldn't convert note, naming defaults")
            note, octave = "X", "X"

        print("Highest peak found to be {} as {}{} \n".format(f, note, octave))

        if note != "X" and octave != "X" and octave >= 2 and octave <= 6:
            self.detected_notes.append("{}{}".format(note, octave))
            self.notes_played += 1

        return round(f, 3), note, octave


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

        self.librosa_chunks.append(librosa_array)

        # Threshold detection
        if self.start_i is None and self.get_db(asg_array) > self.mic_threshold:
            self.start_i = self.counter
        elif self.start_i is not None and self.get_db(asg_array) < self.mic_threshold \
            or self.start_i is not None and (self.counter- self.start_i) > 10: # limit length

            print("cuttoff detected: ({},{})".format(self.start_i, self.counter))
            self.estimate_freq(self.start_i, self.counter)
            #self.create_score(self.detected_notes)
            #self.send_udp(self.start_i, self.counter)
            self.start_i = None

        self.counter += 1
        return None, pyaudio.paContinue

    def create_score(self, notes):
        # simply write a temp file that will store the lilypad notation of the notes
        # step 1: clean notes
        out = []
        for string in notes:
            # remove octave
            note_plain = ''.join(i for i in string if not i.isdigit())
            # convert to lowercase
            note_lower = note_plain.lower()
            # replace sharp with is
            final = note_lower.replace("#", "is")
            out.append(final)

        notes = out
        # step 2: write the file
        f = open("demo2.ly", "w")
        f.write("\\relative{\n\\clef treble\n")
        for i in notes:
            f.write(i + " ")
        f.write("\n}")
        f.close()
    
    def test(self):
        self.start()

    def frequency_to_note(self, frequency):
        NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        OCTAVE_MULTIPLIER = 2
        KNOWN_NOTE_NAME, KNOWN_NOTE_OCTAVE, KNOWN_NOTE_FREQUENCY = ('A', 4, 440)
        note_multiplier = OCTAVE_MULTIPLIER ** (1 / len(NOTES))
        frequency_relative_to_known_note = frequency / KNOWN_NOTE_FREQUENCY
        distance_from_known_note = math.log(frequency_relative_to_known_note, note_multiplier)
        distance_from_known_note = round(distance_from_known_note)
        known_note_index_in_octave = NOTES.index(KNOWN_NOTE_NAME)
        known_note_absolute_index = KNOWN_NOTE_OCTAVE * len(NOTES) + known_note_index_in_octave
        note_absolute_index = known_note_absolute_index + distance_from_known_note
        note_octave, note_index_in_octave = note_absolute_index // len(NOTES), note_absolute_index % len(NOTES)
        note_name = NOTES[note_index_in_octave]
        return note_name, note_octave