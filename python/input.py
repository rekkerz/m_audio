"""
This is a Live Input script which takes live input using selected audio device.
To select the audio device, run with -select flag which would display the possible audio options.

Requirements:
-select: flag which would list possible audio options

:arg1: audio option (integer)
"""
import io
import os

import librosa
import pyaudio
import wave
import speech_recognition as s_r  # TODO: Replace with pydub's native method
import sys
import numpy as np
import math

from sklearn.preprocessing import StandardScaler

import pydub


# Taken from stackoverflow
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


def arg_error(arg, input):
    print("Incorrect parameter input: {} \t : {} \n".format(arg, input))
    print("Enter the following arguments:\n"
          "-select: to list microphone index\n"
          "arg1 (int): audio option\n")
    exit(400)


def list_inputs():
    # Replace with  pyaudio.get_default_input_device_info()
    # https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream.__init__
    x = s_r.Microphone.list_microphone_names()[0:5]  # Limiting choice to top 5
    print("List of microphones: ")
    for i, mic in enumerate(x):
        print(i, ":", mic)


def detect_note(audio):
    """
    Detect note using the FFT implementation.

    :param audio: frames collected via stream from pydub.
    :return: Note that's being played
    """
    print(audio)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please enter all required script arguments")
        arg_error("all", "None")

    if len(sys.argv) == 2 and sys.argv[1] == "-select":
        list_inputs()
        exit()

    mic = False  # Assuming default device if none provided
    threshold = -40  # default threshold

    if len(sys.argv) == 3:
        mic = int(sys.argv[1])
        threshold = int(sys.argv[2])

    FORMAT = pyaudio.paInt32
    CHANNELS = 1
    RATE = 44100
    CHUNK = int(RATE / 40)  # RATE / 1  # seconds per chunk (eg. 1 = 1 second; 2=0.5s)
    RECORD_SECONDS = 5  # TODO: Change to not terminate.
    WAVE_OUTPUT_FILENAME = "data/temp/live/output.wav"

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    input_device_index=mic,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")

    frames = []
    converted = []

    indices = []
    start_i = None
    file_count = 0

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        # Obtain the data
        data = stream.read(CHUNK)
        frames.append(data)

        # Convert to np array
        data_sample = np.frombuffer(data, dtype=np.int32)

        audio_segment = pydub.AudioSegment(
            data,
            frame_rate=RATE,
            sample_width=data_sample.dtype.itemsize,
            channels=CHANNELS
        )

        loudness = audio_segment.dBFS
        """ Thought here:
        When loudness is greater than X, put marker on frame number
        and when it returns back below X, slice the audio.
        """
        # print("dBFS: {}".format(loudness))

        if start_i is not None and loudness < threshold:
            indices.append((start_i, i))
            start_i = None

            asg_d = b"".join(frames[start_i:i])

            data_sample = np.frombuffer(asg_d, dtype=np.int64)
            data_float = np.array(data_sample, dtype=np.float32)

            scaler = StandardScaler(with_std=True)
            scaled = scaler.fit_transform(data_float)

            print(scaled)

            #detect_note(frames[start_i:i])
            """ TODO:
            - figure out how to open in the same format as librosa 
            - perform FFT on the sample    
            """

        if start_i is None and loudness > threshold:  # TODO: Play around with this
            print("Note detected... ")
            start_i = i
            # Multithread here -> every frame from here gets frequency evaluated in parallel

    print(int(RATE / CHUNK * RECORD_SECONDS))
    print(indices)

    print("* done recording")
    # Close streams
    stream.stop_stream()
    stream.close()
    p.terminate()

    # Now to test let's export all samples.
    print("Outputting audio samples..")
    for n, index in enumerate(indices):
        output_filename = "data/temp/live/{}.wav".format(n)
        print(output_filename)
        wf = wave.open(output_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames[index[0]:index[1]]))
        wf.close()
        os.system("python fft.py {}".format(output_filename))
