# sound-bending
---
**INSPIRED BY THE GREAT IMOGEN HEAP'S Mi.Mu GLOVES!!!**\
**CAN BE A LITTLE GLITCHY; PLEASE CUT ME SOME SLACK I'M TRYING MY BEST!!!**

---
## Setup
Clone the repository:

`git clone https://github.com/zackjwilk/sound-bending.git`

Install dependencies with pip:

`pip install -r sound-bending/requirements.txt`

(if you run into issues installing rtmidi, try installing [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) first)

Install:
* [FL Studio](https://www.image-line.com/fl-studio/)
* [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)

Copy the `sound_bending` folder, open your Image-Line user data folder (in Documents by default), navigate to `FL Studio`>`Settings`>`Hardware` and paste the folder inside.

Create a new loopMIDI port called `loopMIDI Port 1`

Open `template.flp`

In the FL Studio menu, navigate to `Options`>`MIDI Settings` and enable `loopMIDI Port` in the input menu. Select `sound_bending` in the controller type dropdown box.
Activate Track 1 on the mixer as microphone input.

Run `main.py` (make sure it's in the same directory as `gesture_recognizer.task`)

Click the circle button at the bottom of the "Input" track on the mixer to enable recording from this track. Then, turn off the recording countdown in FL Studio by clicking the 3.2.1 button to the right of the record button and BPM counter. After recording, when prompted where you would like to record to, select "Record into playlist as audio clip," toggle "Do not ask this again," and proceed.

## Features
### Hand Gestures
* **Peace sign - Toggle recording** (I was originally going to use a closed fist gesture to toggle recording to stay true to Imogen Heap's design but switched to the peace sign to avoid accidentally toggling recording by detecting a fist when transitioning between other gestures)
* **Open palm - Control panning**
* **Pointing up - Control reverb + delay**
  + Reverb is calculated from x-coordinate of tip of pointer finger (move right = increase)
  + Delay is calculated from y-coordinate of tip of pointer finger (move up = increase)
* **Rock sign - Toggle vocoder**
  + To change the chord used for the vocoder, click the Vocoder track in the mixer, open Vocodex, and select the keys from the piano at the bottom.
 
For the pointing up gesture, the effects controlled by the x and y coordinates of the tip of the pointer finger can be customized by simply changing the plugins on tracks 2 and 3 on the mixer. The distortion effect can also be replaced.

## How it works
sound-bending uses MediaPipe for Python to track hand landmarks through the webcam video stream. It recognizes the gestures the user is making with their hands, and responds by sending signals to FL Studio. FL Studio allows for MIDI scripting, which is why loopMIDI is required. loopMIDI creates the MIDI port to act as a connected MIDI controller. The Python program sends MIDI signals with the channel, note, and velocity values as vessels for data to manipulate the FL Studio script——like whether to record or add reverb/delay and how much.

This project was made in a few days after being inspired from revisiting Imogen Heap's Tiny Desk performance. I hope to expand on it soon after experimenting with it some more.
