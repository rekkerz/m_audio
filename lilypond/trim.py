import os
import subprocess

from PIL import Image, ImageChops

def trim(im):
    # Remove the bottom of the image
    width, height = im.size
    top = 0
    bottom = height - 100
    left = 0
    right = width
    im = im.crop((left, top, right, bottom))

    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def clean_notes(notes):
    out = []
    for string in notes:
        # remove octave
        note_plain = ''.join(i for i in string if not i.isdigit())
        # convert to lowercase
        note_lower = note_plain.lower()
        # replace sharp with is
        final = note_lower.replace("#", "is")
        out.append(final)

    return out

def write_ly(notes):
    # requires notes to be cleaned using clean_notes
    f = open("demo.ly", "w")
    f.write("\\relative{\n\\clef treble\n")
    for i in notes:
        f.write(i + " ")
    f.write("\n}")
    f.close()

if __name__ == '__main__':
    notes = ['A#2', 'F11', 'A3', 'A#3', 'D3', 'F3', 'A2', 'A#2', 'A2', 'F11', "A2", "A4", "B1"]

    clean = clean_notes(notes)
    print(clean)

    write_ly(clean)

    # run lilypad
    subprocess.run(["lilypond", "-s", "--formats=png", "demo.ly"])
    #os.system("lilypond -s --formats=png demo.ly")

    im = Image.open("../python/app/demo.png")
    im = trim(im)
    #im.show()
    im.save("demo_clean.png")
