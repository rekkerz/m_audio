import os
import random
import time

import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.preprocessing.sequence import pad_sequences


class Model:
    def __init__(self):
        """
        Initializes the model
        """
        self.note_map, self.note_map_back, self.loc_map, self.loc_map_back = self.generate_maps()

        self.model = keras.models.load_model("classes/embed_model")

        # for self run, uncomment
        #self.model = keras.models.load_model("embed_model")

        self.max_seq_length = self.model.layers[1].output_shape[1]  # grab the max sequence length for padding

    def generate_maps(self):
        """
        Generates the id to note and id to location maps.
        """
        alphabet = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        note_map = dict()
        loc_map = dict()

        counter = 0
        for note in alphabet:  # for 7 notes in the alphabet
            for j in range(5):  # for 5 octave range of guitar
                octave = j + 2  # starting octave 2
                msg = "{}{} - {}".format(note, octave, counter)

                key = "{}{}".format(note, octave)

                note_map[key] = counter + 1  # set note to counter as id e.g. C2 = 1 ; 0 is reserved for padding

                counter += 1

        note_map_back = dict(map(reversed, note_map.items()))

        counter = 0
        for string in range(6):
            string += 1
            for fret in range(25):
                key = (string, fret)

                loc_map[key] = counter + 1

                counter += 1

        loc_map_back = dict(map(reversed, loc_map.items()))

        return note_map, note_map_back, loc_map, loc_map_back

    def pad_sequence(self, seq_encoded):
        return pad_sequences(seq_encoded, maxlen=self.max_seq_length, padding='post')

    def eval_sequence(self, sequence):
        # Expects sequence to be a 1 dimensional array
        encoded = []
        for note in sequence:  # encode the sequence
            encoded.append(self.note_map[note])
        padded = self.pad_sequence([encoded])  # pad the sequence

        prediction = self.model.predict(padded, verbose=False)  # make the prediction

        decoded = []
        for note in prediction[0]:
            indx = np.argmax(note)
            if indx == 0:  # This is our end of sequence terminator
                break

            decoded.append(self.loc_map_back[indx])
        return decoded


""" """
# example usage
if __name__ == '__main__':
    model = Model()

    """

    permitted_notes = ["A2","A3","A4","A5","B2","B3","B4","B5", "C2","C3","C4","C5","D2","D3",
                       "D4","D5", "E2","E3","E4","E5", "F2","F3","F4","F5","G2","G3","G4","G5"]
    sequences = {}

    for length in range(50):
        length += 1 # this will be the length of our sequence
        length_sequences = [] # this will store the sequences of the said length

        for i in range(100): # we generate 100 sequences of each length
            seq = []
            for i in range(length):
                seq.append(random.choice(permitted_notes))
            length_sequences.append(seq)
        sequences[length] = length_sequences

    #print(sequences)

    for key in sequences.keys():
        total_exec_times = 0
        for seq in sequences[key]:
            start = time.time()
            model.eval_sequence(seq)
            total_exec_times += (time.time() - start)

        average_exec_time = total_exec_times/len(sequences[key])
        print("Average execution time for {} note sequence was {} seconds".format(key, round(average_exec_time, 3) ))

    """

    sequence = ["E4", "A2", "B3", "G3", "E4", "A2", "B3", "F2"]


    #start = time.time()
    guess = model.eval_sequence(sequence)
    #end = time.time()

    #print("Executed in: {} seconds".format(end-start))
    print(guess)

