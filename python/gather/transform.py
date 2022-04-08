import csv
import os


class Transform:

    def __init__(self, path):
        if os.path.exists(path):
            self.path = path
        else:
            return Exception("Error, file not found.")

    def return_as_array(self):
        file = open(self.path, "r")
        file_lines = [line.strip("\n") for line in file if line != "\n"]

        if len(file_lines) == 0:
            print("Blank file error")
            return

        if len(file_lines) % 6 != 0:
            print("File didn't match the 6 string format")
            return

        verses = int(len(file_lines) / 6)

        u = 0
        v = 6

        out = []

        for i in range(verses):
            verse = file_lines[u:v]
            parsed_lines = self.parse_lines(verse)
            u += 6
            v += 6
            out.append(parsed_lines)

        return out

    def parse_lines(self, lines):
        """
        Feed an array of single strings, returns an array of tuples.

        :param lines:
        :return:
        """
        # num_lines = len(lines[0].split("|"))

        lines = [line.split("|")[1] for line in lines]

        # Taking the length of first line as length that will match all other lines
        length = len(lines[0])  # TODO: Check this doesn't need fixing

        blank_line = "-" * 6

        out = []
        temp = []  # array of 6 strings

        for i in range(length):
            line, next_lines = self.read_next(lines)

            if "".join(line) == blank_line:  # if it's a line of all blanks

                if len(temp) != 0:  # check that temp container is empty
                    out.append(tuple(temp))
                    temp = []

                out.append(tuple(line))  # add to out straight away
                lines = next_lines
                continue

            if len(temp) == 0:  # on first addition
                temp = line
            else:
                # append the new digits to line
                for j, v in enumerate(line):
                    if v == "-":
                        continue
                    temp[j] = temp[j] + str(line[j])
            lines = next_lines

        return out

    def read_next(self, lines):
        """
        lines in format --3-4-5- etc
        :param lines:
        :return:
        """
        try:
            arr = [line[0] for line in lines]
            new_lines = [line[1:] for line in lines]
        except:
            return None, None

        return arr, new_lines

    def is_spec_char(self, char):
        allowed_chars = ["/"]
        # if char in allowed_chars:
        #    return True
        return char in allowed_chars

    def tab_array_to_note(self, line):
        """

        :param line: tuple containing one iteration of the tab
        :return: the note that would be produced from [A,B,C,D,E,F,G] with appropriate sharp and octave.
        """
        if line == ("-", "-", "-", "-", "-", "-"):
            print("blank line detected")
            return None


    def line_to_notes(self, line, guitar_map):
        """
        A utility function to convert a line to notes (works on standard tuning)

        :param line: A tuple containing the tab definition e.g. ('-', '-', '3', '-', '2', '-')
        :return: A tuple in format (E4, A5, ...) containing notes played
        """
        if line == ('-', '-', '-', '-', '-', '-'):
            #print("Blank line detected, skipping")
            return None, None

        notes = []
        positions = []

        for y_pos, x_pos in enumerate(line):
            y_pos += 1  # has to be done so strings start with 1 not 0

            # Clean the x_pos
            x_pos = str.strip(x_pos, "- p b ~ x s t T") # Remove the common symbols

            if "/" in x_pos or "h" in x_pos or "\\" in x_pos: # skip slide notation
                continue

            if x_pos == "":
                continue # skip blank x_pos

            try: # adding this here to catch all symbols in our dataset
                x_pos = int(x_pos)
            except:
                message = "Error detected on converting {} to int. " \
                          "Try adding extra symbols".format(x_pos)
                print(message)
                continue

            pos = (y_pos, x_pos)
            try:
                note = guitar_map[pos]
            except:
                print("Note not found, skipping")
                continue

            #print(pos, note)
            notes.append(note)
            positions.append(pos)

        return notes, positions

    def generate_notes(self, arr, guitar_map):
        notes = []
        positions = []
        for verse in arr:
            for line in verse:
                n, p = trans.line_to_notes(line, guitar_map)

                if n == None:
                    continue

                if len(n) == 0 or len(p) == 0 or len(n) != len(p):
                    continue

                notes.append(n)
                positions.append(p)
        return notes, positions


"""
    Required format:
    notes = [[A3],[E3, C3], ...]
    positions = [[(5,0)],[(4,2),(2,1)], ...]
    where notes correlate to position i.e. len(notes) = len(positions)
"""

def get_next_char(current_char):
    alphabet = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    i = alphabet.index(current_char)

    if i == len(alphabet)-1: # case it's the last index
        return alphabet[0]

    return alphabet[i+1]

def generate_map():
    # Init dictionary
    map = dict()
    tuning = ["E", "B", "G", "D", "A", "E"]

    for s in range(6):  # For each string
        current = tuning[s]

        if s == 0 or s == 1:
            octave = 2
        elif s == 5:
            octave = 4
        else:
            octave = 3

        for t in range(25):  # for each fret
            # print("{}{} is located <{},{}>".format(current, octave, s+1, t))
            note = current+str(octave)
            pos = (s+1, t)
            map[pos] = note # set the position

            current = get_next_char(current)
            if current == "C":
                octave += 1

    return map

if __name__ == '__main__':

    dir = "../data/tabs"
    x = os.listdir(dir)

    print("Located {} files to transform.".format(len(x)))

    # input("Hit enter to start ... ")

    my_guitar_map = generate_map()

    # Convert to clean array format
    clean = []
    with open('tabs.csv', 'w', newline='') as csvfile:
        fieldnames = ["filename", "notes", "positions"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in x:
            path = dir + "/" + i
            # print(path)
            trans = Transform(path)

            try:
                arr = trans.return_as_array()
            except:
                print("skipped file: {}".format(path))

            if arr != None:
                print(path)
                #print(arr)
                clean.append(arr)
                notes, positions = trans.generate_notes(arr, my_guitar_map)

                #print(notes)
                #print(positions)

                if len(notes) == 0 or len(positions) == 0:
                    # skip if they're blank
                    continue

                writer.writerow({
                    "filename": i,
                    "notes": notes,
                    "positions": positions
                })



    print("Finished transformation of {} files".format(len(clean)))

    """
    print("Testing line_to_notes() function... ")

    trans = Transform(dir + "/" + "zach-bryan_november-air-tabs-3450725.txt")
    arr = trans.return_as_array()
    print(arr)

    notes, positions = trans.generate_notes(arr, my_guitar_map)

    print(notes)
    print(positions)
    """

    """
    notes = []
    positions = []
    for verse in arr:
        for line in verse:
            n, p = trans.line_to_notes(line)

            if n == None:
                continue
            notes.append(n)
            positions.append(p)

    print(notes)
    print(positions)
    """
