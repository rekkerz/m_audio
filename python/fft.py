import math
import sys

import librosa
import numpy as np

def arg_error(arg, input):
    print("Incorrect parameter input: {} \t : {} \n\n".format(arg, input))
    print("Enter the following arguments:\n"
          "arg1 = path to wav file\n")
    exit(400)

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


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please enter all required script arguments")
        arg_error("all", "None")

    path = str(sys.argv[1])
    try:
        x, sr = librosa.load(path)
    except:
        arg_error("arg1", sys.argv[1])

    # Round the length down and clip the audio file down
    length = len(x) / sr
    x = x[0: int(length * sr) + 1]

    print("Sound clip is {} seconds long".format((len(x)-1)/sr))

    # Perform Fast Fourier Transform
    c = np.fft.fft(x)
    fr = np.array(range(0, len(x))) / length  # Frequency range

    # condition = fr < 1200  # Guitar is limited to producing 40-1200 Hz
    # plt.plot(fr[condition], np.abs(c[condition]))
    # plt.show()

    # Taking the highest value of c between range of guitar & converting to f
    f = fr[np.argmax(c[0:1200])]
    try:
        note, octave = frequency_to_note(f)
    except:
        print("Couldn't convert note, naming defaults")
        note, octave = "X", "X"

    print("{}, {}{}".format(round(f,3), note, octave))
