# name=sound_bending

import midi
import transport
import mixer
import general
import time

count = 0
record_start = 0

def recording():
    """
    Returns True if currently recording.
    Returns False if not.
    """
    global count
    return count % 2 == 1

def toggle_record(toggle, change_time=True):
    """
    Toggle audio recording.
    """
    global count, record_start

    if toggle == count % 2:
        return # if recording value from both scripts don't line up, don't toggle record

    transport.record()
    if count == 0:
        transport.start() # play track if this is first recording
    count += 1
    if change_time:
        record_start = time.time()
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

def toggle_loop():
    """
    Set song position to beginning if end of loop
    reached.
    """
    song_pos = transport.getSongPos(0)
    song_len = transport.getSongLength(0)
    if count > 1 and recording() and song_pos >= song_len: # if end of loop reached
        toggle_record(0, False)
        transport.setSongPos(0.0)
        toggle_record(1, False) # wrap around to beginning of loop

def record_cutoff():
    """
    Stop recording if max length reached.
    """
    global count, record_start

    record_len = time.time() - record_start
    song_len = transport.getSongLength(0)/1000 # convert ms to s
    if count > 1 and recording() and record_len >= song_len:
        toggle_record(0)

def OnMidiMsg(event):
    event.handled = False
    if event.midiId == midi.MIDI_NOTEOFF:
        channel = event.status & 0x0F
        if channel == 1:
            toggle_record(event.note) # note of 0 = stop record, 1 = start record
        elif channel == 2:
            undo()
        elif channel == 3:
            reverb = event.note
            delay = event.velocity
            update_reverb_delay(reverb, delay)
        elif channel == 4:
            distortion()
        elif channel == 5:
            toggle_loop()
            record_cutoff()
