#
# Python decode morse realtime based on audio Power not Frequency!
# James Wilkinson 2020
#
# Do imports...
import pyaudio
import struct
import math
from datetime import datetime

# Setup audio capture object.
thresh = 0.001 #0.00025 #0.0005 #1 #4 #6 4
sample_period = 0.015 #0.005 #0.015 #0.010 #0.005 #0.015 2.5 5 00.1 0.02... 
RATE = 44100
sample_cycles = int(RATE*sample_period)
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
FORMAT=pyaudio.paInt16
pa=pyaudio.PyAudio()
stream = pa.open(format = FORMAT,                      
         channels = CHANNELS,                          
         rate = RATE,                                  
         input = True,                                 
         frames_per_buffer = sample_cycles)

# Setup decoder variables..
mark=0
space=2000
dot=1
dash=3
bd=1
df=0
x="..TEMNAIOGKDWRUS.!QZYCXBJP.L.FVH09.8...7.(.../=61....+.&2!..3.45.......:....,.....)..;........-..'...@.......\"...._?............"
#x="__TEMNAIOGKDWRUS_!QZYCXBJP_L_FVH09_8___7_(___/=61____+_&2!__3_45_______:____,_____)__;________-__'___@____.__\"_____?____________"
# Main detect and decode loop.
while True:
    sample=stream.read(sample_cycles)   # Grab a sample
    count = len(sample)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, sample )
    sum_squares = 0.0
    for i in shorts:
        n = i * SHORT_NORMALIZE
        sum_squares += n*n
    amp=math.sqrt( sum_squares / count ) # Calculate it's 'power' level using sum squares method.
    if amp > thresh:                     # Compare to threshold.
        mark=mark+1                      # Mark
        space=0                          # or
    else:                                # Space...
        space=space+1
        if mark > 0:               # This is fine...
            if mark > dash:
                dash = mark
                dot = dash / 4     # This is dot calc.. and dash setting.
            if mark > 2.5 * dot:
                bd += bd           # If it's a dash, rotate left... (x2)
                df=1
            else:
                if mark>0.3 * dot:                        # Anything below 1/3 a dot is dumped...?! Doesn't seem to need it...
                    bd += bd + 1                          # If it's a dot, rotate left (x2) and add 1.
            mark=0                                        # Rest mark...
        if space > 2 * dot and space < 10000:              # If char space, decode char.
            print((x[bd & 127]),end="", flush=True )                   # Using direct decode..
            bd = 1                                        # Rest the morse char...
            space=space+10000                              # Prevent this action repeating.
            if df:                                        # If we have had a dash...
                dash=dash-(dash*.1)                       # Adjust the speed up, so will drift to faster speed.
                df=0                                      # Clear dash flag.
            dot=dash/4                                    # And reset the dot size.
        elif space > (10000 + (dot * 6)) and space < 20000: # Check for end of word...
            print(" ",end="", flush=True )                             # Print space
        #    print(dash)
            space=20000                                    # Prevent this action repeating.
        elif space > (20000 + (dot * 10)) and space < 60000: # waz 6 Check for end of sentance. was 6
            print(flush=True )                                       # Print newline if so.
            space=60000                                    # Prevent this action repeating.
# Eof
