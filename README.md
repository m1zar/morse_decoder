# morse_decoder
Decode morse code from audio. 

Made to decode the messages in the Titanic Morse Messages video on Youtube. https://www.youtube.com/watch?v=FxRN2nP_9dA

If you can, select your audio output mix as the microphone and set the volume quite low. Failing that use a microphone next to your speakers, and try to be quiet!

This decodes all the morse, in all the speeds and frequency ranges used in the video. And it works for other morse videos and even some live morse, but it's really basic.

Enjoy... 

Reuqires Python 3.x and install pyaudio (pip install pyaudio)

NEW: morse8.py, writen for those without an audio output mix (non realtek sound card). This requires 'pip install pyaduiowpatch', this should work for any system to decode playing audio.
