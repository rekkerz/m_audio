class Mapper():
    def __init__(self, tuning):
        self.tuning = tuning # TODO: Check tuning is ok


    def generate_maps(self):
        """
        Generates the id to note and id to location maps.
        """
        alphabet = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

        note_map = dict()
        loc_map = dict()

        counter = 0
        for note in alphabet: # for 7 notes in the alphabet
            for j in range(5): # for 5 octave range of guitar
                octave = j + 2 # starting octave 2
                msg = "{}{} - {}".format(note, octave, counter)
                #print(msg)

                key = "{}{}".format(note, octave)

                note_map[key] = counter+1 # set note to counter as id e.g. C2 = 1 ; 0 is reserved for padding

                counter += 1

        #print(note_map)
        note_map_back = dict(map(reversed, note_map.items()))
        #print(note_map_back)

        counter = 0
        for string in range(6):
            string += 1
            for fret in range(25):
                #print(string, fret)
                key = (string, fret)

                loc_map[key] = counter + 1

                counter += 1

        #print(loc_map)
        loc_map_back = dict(map(reversed, loc_map.items()))
        #print(loc_map_back)

        return note_map, note_map_back, loc_map, loc_map_back





if __name__ == '__main__':
    tuning = ["E", "A", "D", "G", "B", "E"]
    Mapper(tuning)
