# -- --- .--. ... . 
# Python decode morse realtime based on audio Power not Frequency!
# James Wilkinson 2023
#
# Do imports...
import struct
import math
from datetime import datetime
import pyaudiowpatch as pyaudio
import wave

# Setup audio capture object.
thresh = 0.01 
sample_period = 0.015 
RATE = 44100
sample_cycles = int(RATE*sample_period)
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
FORMAT=pyaudio.paInt16

# Setup decoder variables..
mark=0
space=2000
dot=1
dash=3
bd=1
df=0
#x="..TEMNAIOGKDWRUS.!QZYCXBJP.L.FVH09.8...7.(.../=61....+.&2!..3.45.......:....,.....)..;........-..'...@.......\"...._?............"
x=list("..TEMNAIOGKDWRUS.!QZYCXBJP.L.FVH09.8...7.(.../=61....+.&2!..3.45.......:....,.....)..;........-..'...@.......\"...._?............")

with pyaudio.PyAudio() as p:
    # Get default WASAPI info
    wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
    # Get default WASAPI speakers
    default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
    if not default_speakers["isLoopbackDevice"]:
        for loopback in p.get_loopback_device_info_generator():
            if default_speakers["name"] in loopback["name"]:
                default_speakers = loopback
                break
        else:
            print("Default loopback output device not found.\n\nRun `python -m pyaudiowpatch` to check available devices.\nExiting...\n")
            exit()
    print(f"Recording from: ({default_speakers['index']}){default_speakers['name']}")
    # Decode the morse as the sound comes in....
    def callback(in_data, frame_count, time_info, status):
        global mark, space, dot, dash, bd, df, x
        count = len(in_data)/2
        format = "%dh"%(count)
        shorts = struct.unpack( format, in_data )
        sum_squares = 0.0
        for i in shorts:
            n = i * SHORT_NORMALIZE
            sum_squares += n*n
        amp=math.sqrt( sum_squares / count )      # Calculate it's 'power' level using sum squares method.
        if amp > thresh:                          # Compare to threshold.
            mark=mark+1                           # Mark
            space=0                               # or
        else:                                     # Space...
            space=space+1
            if mark > 0:                          # This is fine...
                if mark > dash and mark<(dash*5): #Added max dash... prob a bad idea.
                    dash = mark
                    dot = dash / 4                # This is dot calc.. and dash setting.
                if mark > 2.5 * dot:
                    bd += bd                      # If it's a dash, rotate left... (x2)
                    df=1
                else:
                    if mark>0.3 * dot:                          # Anything below 1/3 a dot is dumped...?! Doesn't seem to need it...
                        bd += bd + 1                            # If it's a dot, rotate left (x2) and add 1.
                mark=0                                          # Rest mark...
            if space > 2 * dot and space < 10000:               # If char space, decode char.
                print((x[bd & 127]),end="", flush=True )        # Using direct decode..
                bd = 1                                          # Rest the morse char...
                space=space+10000                               # Prevent this action repeating.
                if df:                                          # If we have had a dash...
                    dash=dash-(dash*.1)                         # Adjust the speed up, so will drift to faster speed.
                    df=0                                        # Clear dash flag.
                dot=dash/4                                      # And reset the dot size.
            elif space > (10000 + (dot * 6)) and space < 20000: # Check for end of word...
                print(" ",end="", flush=True )                             # Print space
                space=20000                                     # Prevent this action repeating.
            elif space > (20000 + (dot * 10)) and space < 60000:# waz 6 Check for end of sentance. was 6
                print(flush=True )                                       # Print newline if so.
                space=60000                                     # Prevent this action repeating.
        return (in_data, pyaudio.paContinue)
    # Setup the sound stream with a call to the decoder...
    with p.open(format=pyaudio.paInt16,
            channels=default_speakers["maxInputChannels"],
            rate=int(default_speakers["defaultSampleRate"]),
            frames_per_buffer=662,                              # was pyaudio.get_sample_size(pyaudio.paInt16)
            input=True,
            input_device_index=default_speakers["index"],
            stream_callback=callback
    ) as stream:
        input("Decoding...\n")
