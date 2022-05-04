"""
This library is in created for Staff generation using LilyPond
http://lilypond.org/manuals.html
"""
import os

from PIL import Image, ImageChops

class StaffGenerator:
    def __init__(self):
        return None

    def trim_staff(self, im):
        # Remove the bottom of the image
        width, height = im.size
        top = 0
        bottom = height - (0.1 * height)
        left = 0
        right = width
        im = im.crop((left, top, right, bottom))

        bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

    def clean_notes(self, notes):
        out = []
        for string in notes:
            # transfer octave to ' * n (ly format)
            octave = int(''.join(i for i in string if i.isdigit()))
            note_plain = ''.join(i for i in string if not i.isdigit())
            note_plain = note_plain #+ "'"*octave

            if octave == 3:
                pass
            elif octave > 3:
                note_plain = note_plain + "'"*(octave - 3)
            elif octave < 3:
                note_plain = note_plain + ","*(3 - octave)

            # convert to lowercase
            note_lower = note_plain.lower()
            # replace sharp with is
            final = note_lower.replace("#", "is")
            out.append(final)
        return out

    def write_ly(self, notes):
        # requires notes to be cleaned using clean_notes
        try:
            os.remove("demo.ly")
        except:
            print("demo.ly already removed")

        f = open("demo.ly", "w")
        f.write('music = {\n\\clef "treble_8"{\n')
        for i in notes:
            f.write(i + " ")
        f.write("\n}}")
        f.write('\n\\new StaffGroup << \n \\new Staff{\n\\clef "treble_8"\n\\music}>>')
        f.close()

    def save_pdf(self):
        """
        A placeholder for the get PDF function which will
        save the PDF file to apps location.
        :return:
        """
        os.system("lilypond -s --formats=pdf demo.ly")  # sorry...
        print("PDF saved")

    def main(self, notes, on_exit=print("Done")):
        clean = self.clean_notes(notes)
        self.write_ly(clean)  # write the .ly file

        #subprocess.run(["lilypond", "-s", "--formats=png", "demo.ly"])  # sorry...
        os.system("lilypond -s --formats=png demo.ly")  # sorry...

        im = Image.open("demo.png")
        # trim the image and save
        im = self.trim_staff(im)
        im.save("demo.png")
        on_exit()




