# sound-bending
---
**INSPIRED BY THE GREAT IMOGEN HEAP'S Mi.Mu GLOVES!!!**

---
## Setup
Clone the repository:

`git clone https://github.com/zackjwilk/sound-bending.git`

Install dependencies with pip:

`pip install -r sound-bending/requirements.txt`

Install:
* [FL Studio](https://www.image-line.com/fl-studio/)
* [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)

Copy the `sound_bending` folder, open your Image-Line user data folder (in Documents by default), navigate to `FL Studio`>`Settings`>`Hardware` and paste the folder inside.

Create a new loopMIDI port called `loopMIDI Port 1`

Open `template.flp`

In the FL Studio menu, navigate to `Options`>`MIDI Settings` and enable `loopMIDI Port` in the input menu. Select `sound_bending` in the controller type dropdown box.
Activate Track 1 on the mixer as microphone input.

Run `main.py`

## Features
---
### Hand Gestures
* Peace sign - Toggle recording
* Open palm - Undo most recent action
* Pointing up - control reverb + delay
  + Reverb is calculated from x-coordinate of tip of pointer finger (move right = increase)
  + Delay is calculated from y-coordinate of tip of pointer finger (move up = increase)
* Rock sign - Toggle distortion
 
For the pointing up gesture, the effects controlled by the x and y coordinates of the tip of the pointer finger can be customized by simply changing the plugins on tracks 2 and 3 on the mixer. The distortion effect can also be replaced.
