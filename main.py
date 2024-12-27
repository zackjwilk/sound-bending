import cv2
import mediapipe as mp
from mediapipe.tasks import python
import threading
import time
import mido

# midi setup
try:
    midi = mido.open_output("loopMIDI Port 1") # load loopMIDI port as output
except IOError:
    print("Error: Could not find MIDI output port. Make sure loopMIDI is running and the names match.")
    exit(1)

# constants
DEBOUNCE = 0.5  # 500 ms
HAND_LANDMARK_COLOR = (255, 255, 255)
HAND_CONNECTION_COLOR = (255, 0, 50)
RECT_COLOR = (255, 0, 50)
TEXT_COLOR = (255, 0, 50)
FONT_SCALE = 0.6
FONT_THICKNESS = 1
MODEL_PATH = "gesture_recognizer.task"
NUM_HANDS = 1

# globals
recording = False
undoing = False
vocoding = False
reverb = 0
delay = 0
pan = 0
last_record_time = 0
last_undo_time = 0
recording_lock = threading.Lock()

# helpers
def toggle_record():
    """
    Toggle audio recording.
    """
    global last_record_time

    if time.time() - last_record_time >= DEBOUNCE:
        last_record_time = time.time()
        with recording_lock:
            val = 1 if recording else 0
            midi.send(mido.Message("note_off", channel=1, note=val))
            # ^ channel 1 indicates toggle record, channel 2 undo, etc.

def undo():
    """
    Undo most recent action.
    """
    global last_undo_time

    if time.time() - last_undo_time >= DEBOUNCE:
        last_undo_time = time.time()
        midi.send(mido.Message("note_off", channel=2))

def secret_finger():
    """
    Send MIDI message with reverb and delay values.
    """
    midi.send(mido.Message("note_off", channel=3, note=int(reverb), velocity=int(delay)))
    # ^ uses note to send reverb value and velocity to send delay value

def panning():
    """
    Send MIDI message with pan value.
    """
    midi.send(mido.Message("note_off", channel=4, note=int(pan)))

def vocoder():
    """
    Toggle vocoder.
    """
    midi.send(mido.Message("note_off", channel=5))

def toggle_loop():
    midi.send(mido.Message("note_off", channel=6))

# main gesture recognizer class
class GestureRecognizer:
    def __init__(self):
        self.lock = threading.Lock()
        self.current_gestures = []

    def main(self):
        # gesture recognizer setup
        GestureRecognizer = mp.tasks.vision.GestureRecognizer
        GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
        RunningMode = mp.tasks.vision.RunningMode

        recognizer_options = GestureRecognizerOptions(
            base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=RunningMode.LIVE_STREAM,
            num_hands=NUM_HANDS,
            result_callback=self.__result_callback)
        recognizer = GestureRecognizer.create_from_options(recognizer_options)

        hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=NUM_HANDS,
            min_detection_confidence=0.65,
            min_tracking_confidence=0.65)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Unable to access the camera.")
            return

        timestamp = 0
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame = self.process_frame(frame, hands, recognizer, timestamp)
                timestamp += 1

                cv2.imshow("sound-bending", frame)
                if cv2.waitKey(5) & 0xFF == ord('q'):
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
            exit(0)

    def process_frame(self, frame, hands, recognizer, timestamp):
        """
        Process frame for hand landmarks and gestures
        """
        global reverb, delay, pan

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)
        frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        landmark_style = mp.solutions.drawing_utils.DrawingSpec(color=HAND_LANDMARK_COLOR, thickness=1)
        connection_style = mp.solutions.drawing_utils.DrawingSpec(color=HAND_CONNECTION_COLOR, thickness=1)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=landmark_style,
                    connection_drawing_spec=connection_style
                )

                # calculate hand bounding rectangle
                min_x, max_x = float("inf"), float("-inf")
                min_y, max_y = float("inf"), float("-inf")
                for landmark in hand_landmarks.landmark:
                    x = round(landmark.x * frame.shape[1])
                    y = round(landmark.y * frame.shape[0])
                    min_x, max_x = min(x, min_x), max(x, max_x)
                    min_y, max_y = min(y, min_y), max(y, max_y)

                cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), RECT_COLOR, 1)

                # pointer finger tip (landmark 8)
                pointer_x = round(hand_landmarks.landmark[8].x * frame.shape[1])
                pointer_y = round(hand_landmarks.landmark[8].y * frame.shape[0])
                pointer_x = min(max(0, pointer_x), frame.shape[1])
                pointer_y = min(max(0, pointer_y), frame.shape[0])

                # middle finger knuckle (landmark 9)
                middle_x = round(hand_landmarks.landmark[9].x * frame.shape[1])

                # calculate reverb, delay, and pan
                reverb = round(pointer_x / frame.shape[1] * 100, 1)
                delay = round((1 - pointer_y / frame.shape[0]) * 100, 1)
                pan = round(middle_x / frame.shape[1] * 100, 1)

                # gesture recognition
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                recognizer.recognize_async(mp_image, timestamp)

                self.put_gestures(frame, (min_x, min_y - 20), (pointer_x, pointer_y))

        return frame

    def put_gestures(self, frame, coords, pointer_coords):
        """
        Draw rectangle around hand to image and write name
        of current gesture above it.
        """
        gesture_names = {
            "None": "",
            "Closed_Fist": "fist",
            "Open_Palm": f"x={pan}",
            "Pointing_Up": f"x={reverb}, y={delay}",
            "Thumb_Down": "boooooo",
            "Thumb_Up": "yayyyyyy",
            "Victory": "peace",
            "ILoveYou": "rock"
        }

        with self.lock:
            gestures = self.current_gestures

        for gesture in gestures:
            cv2.putText(frame, gesture_names[gesture], coords, cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 0, 50), 1, cv2.LINE_AA)

            if gesture == "Pointing_Up":
                # draw lines on x and y axes through tip of pointer finger
                cv2.rectangle(frame, (pointer_coords[0], 0), (pointer_coords[0], frame.shape[0]), RECT_COLOR, 1)
                cv2.rectangle(frame, (0, pointer_coords[1]), (frame.shape[1], pointer_coords[1]), RECT_COLOR, 1)

    def __result_callback(self, result, output_image, timestamp_ms):
        """
        Callback for gesture recognition results.
        """
        global recording, undoing, vocoding

        with self.lock:
            self.current_gestures = []
            if result and result.gestures:
                for gesture_data in result.gestures:
                    gesture_name = gesture_data[0].category_name

                    if gesture_name == "Victory":
                        if not recording:
                            recording = True
                            toggle_record()
                    elif recording:
                        recording = False
                        toggle_record()

                    if gesture_name == "Open_Palm":
                        panning()
                    """
                        if not undoing:
                            undoing = True
                            undo()
                    elif undoing:
                        undoing = False
                    """

                    if gesture_name == "Pointing_Up":
                        secret_finger()

                    if gesture_name == "ILoveYou":
                        if not vocoding:
                            vocoding = True
                            vocoder()
                    elif vocoding:
                        vocoding = False

                    toggle_loop()

                    self.current_gestures.append(gesture_name)

if __name__ == "__main__":
    GestureRecognizer().main()
