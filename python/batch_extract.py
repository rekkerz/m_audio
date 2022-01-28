"""
This file is a batch method for extracting frequencies using extract_frequency.py
"""

import sys
import os


def arg_error(arg, input):
    print("Incorrect parameter input: {} \t : {} \n\n".format(arg, input))
    print("Enter the following arguments:\n"
          "arg1 = path to folder containing samples\n")
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

    arr = os.listdir(path)  # Retrieve file names
    arr = sorted(arr, key=lambda x: int(x.split(".")[0]))  # Sort the array accordingly
    #print(arr)
    for i in arr:
        file_path = path + "/" + i
        print("\n" + file_path)
        # 2 Methods for calculating frequency: Yin & FFT
        # os.system("python extract_frequency.py {}".format(file_path))
        os.system("python fft.py {}".format(file_path))

    # data/temp/test1/51.wav
