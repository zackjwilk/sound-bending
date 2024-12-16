# name=sound_bending

import midi
import transport
import mixer
import general

count = 0

def toggle_record():
    """
    Toggle audio recording.
    """
    global count
    transport.record()
    if count == 0:
        transport.start()
        count += 1
    print("Toggled recording.")

def undo():
    """
    Undo most recent action.
    """
    general.undo()
    print("Undo.")

def update_reverb_delay(reverb, delay):
    """
    Set volume of Reverb and Delay tracks on mixer.
    """
    mixer.setTrackVolume(2, reverb/100)
    mixer.setTrackVolume(3, delay/100)

def distortion():
    """
    Toggle distortion.
    """
    mixer.enableTrack(4)

def OnMidiMsg(event):
    event.handled = False
    if event.midiId == midi.MIDI_NOTEOFF:
        channel = event.status & 0x0F
        if channel == 1:
            toggle_record()
        elif channel == 2:
            undo()
        elif channel == 3:
            reverb = event.note
            delay = event.velocity
            update_reverb_delay(reverb, delay)
        elif channel == 4:
            distortion()
