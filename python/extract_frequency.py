"""
This script extracts the frequency of the signal. Expects file to be .wav format.

It uses a pre-compiled version of Yin.exe which is compiled using https://github.com/ashokfernandez/Yin-Pitch-Tracking

Returns: frequency (measured in Hz) and likelihood of correct guess (0.1 = 10%).

Arguments:
    arg1 = path to file
"""

import sys
import os
import wave, struct

def arg_error(arg, input):
    print("Incorrect parameter input: {} \t : {} \n\n".format(arg, input))
    print("Enter the following arguments:\n"
          "arg1 = path to file\n")
    exit(400)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please enter all required script arguments")
        arg_error("all", "None")

    path = str(sys.argv[1])

    # Check file exists
    try:
        if not os.path.exists(path):
            raise Exception
    except:
        arg_error("arg1", sys.argv[1])

    """
    Implementation below taken from audioExtract in the original Yin repository.
    """
    waveFile = wave.open(path, 'r')
    length = waveFile.getnframes()

    audioData = []

    # Extract all the samples from the audio file into an array
    for i in range(0,length):
        waveData = waveFile.readframes(1)
        data = struct.unpack("<h", waveData)
        audioData.append(data[0])


    # SCALE THE SAMPLES TO A NEW BIT RATE
    max16Bit = (2 ** 16) / 2 # - Over two because it's +/-16bits (half positive, half negative)

    # Figure out what the max value is for the desired bit level
    desiredBits = 10
    maxDesired = (2 ** desiredBits) / 2

    # Now loop thorugh all vales, normalise them to 1 then scale to the new max value
    for i in range(len(audioData)):
        normalisedSample = float(audioData[i]) / max16Bit
        scaledSample = int(normalisedSample * maxDesired)
        audioData[i] = scaledSample

    f = open('../yin/audioData.txt', 'w')

    # Write all lines to file
    for sample in audioData:
        f.write('%i,\n' % sample)

    # Close the file
    f.close()

    """
    Now that header file is present, run the executable. 
    """

    os.system("..\yin\main.exe ../yin/audioData.txt {}".format(len(audioData)))