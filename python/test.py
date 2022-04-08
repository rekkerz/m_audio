"""
This script is for testing the accuracy and efficiency of AMDF pitch detection on nsynth dataset.
nsynth data = https://magenta.tensorflow.org/datasets/nsynth
"""

import os
import sys
import subprocess
import csv

data = "D:\\Dev\\DATA\\nsynth-train\\audio"  # Path to directory containing data
file_path = "D:\\Dev\\repos\\m_audio\\python\\fft.py"
python = "D:\\Dev\\repos\\m_audio\\venv\\Scripts\\python.exe"

if __name__ == '__main__':
    guitar_files = []
    files = os.listdir(data)

    # Remove all instruments except guitar from dataset
    print("Total files: ",len(files))
    for raw_file in files:
        id = raw_file.split("_")
        if id[0] == "trim" and id[1] == "guitar":
            guitar_files.append(raw_file)
    print("Guitar files: ", len(guitar_files))

    results = []  # Results will contain a tuple of (expected_frequency, actual_frequency, computational_time)
    # Run the script on each guitar file and collect results
    with open("fft_results.csv", "w") as csvfile:
        fieldnames = ["expected", "result", "time"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for i, guitar_file in enumerate(guitar_files):

            midi_f = float(guitar_file.split("-")[1]) # midi frequency
            # Convert frequency to normal frequency using formula
            # https://en.wikipedia.org/wiki/MIDI_tuning_standard
            f = 2 ** ((midi_f - 69.0)/12) * 440

            path = data + "\\" + guitar_file  # Get the full path of the file

            script = python + " " + file_path + " " + path
            out = subprocess.check_output(script, shell=True)
            try:
                split = str(out.decode("utf-8")).split(",")
                res_f = float(split[0].strip())
                time = float(split[1].strip())
                results.append((f, res_f, time))
                writer.writerow({
                    "expected": f,
                    "result": res_f,
                    "time": time
                })
                print ("Working on file: ", path, "\tExpected: ",
                       f , "\tResult: ", res_f, "\tTime:", time)
            except:
                print("F0 estimation error")

    """
    # Write results to csv file
    with open("fft_results.csv", "w") as csvfile:
        fieldnames = ["expected", "result", "time"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for i in results:
            writer.writerow({
                "expected": i[0],
                "result": i[1],
                "time": i[2]
            })

        csvfile.close()
    """

    # TODO: Note for future - I am NOT including file opening time, only execution of method.
    # TODO: Measure the time taken to open files in librosa vs wav cos seems like librosa is p slow

