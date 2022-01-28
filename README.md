# M-Audio Repository

Credits:
 - https://github.com/ashokfernandez/Yin-Pitch-Tracking
 - pydub library

### Prerequisites:
1. pip install -r python/requirments.txt

### Label Audio from `.wav` file:
   1. Split the file into chunks using `python python/split.py python/data/test1.wav python/data/temp 10 -27`. Parameters 10 & -27 are min_silence_length and silence threshold (might need tweaking depending on file)
   2. Estimate frequencies using `python python/batch_extract.py data/temp/test1`. This file has 2 implementations - FFT & Yin which can be switched by removing comment.