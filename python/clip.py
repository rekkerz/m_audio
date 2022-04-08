"""
A script for clipping the audio files
"""
import os
from scipy.io import wavfile

data = "D:\\Dev\\DATA\\nsynth-train\\audio"  # Path to directory containing data

if __name__ == '__main__':

    files = os.listdir(data)

    for raw_file in files:
        if raw_file.split("_")[0] == "guitar":
            print(raw_file)
            path = data + "\\" + raw_file
            print(path)

            out_path = data + "\\" + "trim_" + raw_file
            print("Outpath: ", out_path)

            sr, audio = wavfile.read(path)
            print(sr)

            start = 0
            end = 1
            endSample = int(end * sr)


            wavfile.write(out_path, sr * 2, audio[0:endSample])