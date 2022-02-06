#!/usr/bin/python
"""
This script allows splitting an audio file into chunks
    which uses split_on_silence function provided by pydub
    additionally trims the silent parts after splitting to enhance note detection.

Arguments:
    arg1 = filename/path to file
    arg2 = export path
    arg3 = min_silence_len ~~ Specify that a silent chunk must be at least 1 seconds or 1000 ms long.
    arg4 = silence_thresh  ~~ Consider a chunk silent if it's quieter than -16 dBFS.
"""

import sys
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence


def arg_error(arg, input):
    print("Incorrect parameter input: {} \t : {} \n\n".format(arg, input))
    print("Enter the following arguments:\n"
          "arg1 = filename\n"
          "arg2 = export path\n"
          "arg3 = min_silence_len ~~ Specify that a silent chunk must be at least 1 seconds or 1000 ms long.)\n"
          "arg4 = silence_thresh  ~~ Consider a chunk silent if it's quieter than -16 dBFS.\n")
    exit(400)


def detect_leading_silence(sound, silence_threshold=-27.0, chunk_size=1):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms
    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0  # ms
    while sound[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold:
        trim_ms += chunk_size
    return trim_ms


def get_inputs():
    """
    A wrapper for script arguments
    :return: song_path, song_format, export_path, arg3, arg4
    """
    try:  # Open song
        song_path = str(sys.argv[1])

        if not os.path.exists(song_path):
            raise Exception
        else:
            # Obtain files format
            song_format = song_path.split("/")[-1].split(".")[-1]
    except:
        arg_error("arg1", sys.argv[1])

    try:  # Locate export folder
        export_path = str(sys.argv[2])
        if not os.path.isdir(export_path):
            os.mkdir(export_path)
    except:
        arg_error("arg2", sys.argv[2])

    try:  # arg3 must be integer
        arg3 = int(sys.argv[3])
    except:
        arg_error("arg3", sys.argv[3])

    try:  # arg4 must be integer
        arg4 = int(sys.argv[4])
    except:
        arg_error("arg4", sys.argv[4])

    return song_path, song_format, export_path, arg3, arg4


if __name__ == '__main__':
    try:
        song_path, song_format, export_path, arg3, arg4 = get_inputs()
    except:
        print("Input error - please refer to the script.")
        exit(400)

    song = AudioSegment.from_file(song_path, format=song_format)

    chunks = split_on_silence(
        song,
        min_silence_len=arg3,
        silence_thresh=arg4
    )

    print("Located {} chunks with \n\t "
          "min_silence_len={} \n\t silence_thresh={}".format(len(chunks), arg3, arg4))

    # Create export folder with songs name
    path = export_path + "/" + song_path.split("/")[-1].split(".")[0]  # Export path + song name (without format)

    if not os.path.exists(path):
        try:
            os.mkdir(path)
        except:
            print("Error making the path for export")

    # Temporary solution
    # TODO: Replace with a flag -e which would export the files
    input("Press any key to begin export")

    for i, chunk in enumerate(chunks):
        # Trim silent parts of the chunk
        # TODO: Test the threshold and chunk size works with other samples.
        start_trim = detect_leading_silence(chunk, silence_threshold=arg4)
        end_trim = detect_leading_silence(chunk.reverse(), silence_threshold=arg4)
        duration = len(chunk)
        trimmed_sound = chunk[start_trim:duration - end_trim]

        export_file_path = path + "/" + str(i) + "." + song_format
        print("Exporting {} of length {}".format(export_file_path, len(trimmed_sound)))

        trimmed_sound.export(export_file_path, format=song_format)
