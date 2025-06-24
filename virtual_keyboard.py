import cv2
import time
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller, Key

# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Define the virtual keyboard layout
keyboard_keys = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    ["SPACE", "ENTER", "BACKSPACE"]
]

# Initialize hand detector
detector = HandDetector(detectionCon=0.8, minTrackCon=0.2)
keyboard = Controller()

# Initialize variables to track previous key and time
previous_key = None
key_press_time = 0
press_delay = 0.2  # Delay in seconds between key presses

# Set initial values for keyboard layout
key_width = 90
key_height = 90
padding = 10

# Calculate offsets to center the keyboard
rows = len(keyboard_keys)
cols = max(len(row) for row in keyboard_keys)
total_width = cols * (key_width + padding) - padding
total_height = rows * (key_height + padding) - padding
offset_x = (1080 - total_width) // 2
offset_y = (720 - total_height) // 2

# Function to draw the keyboard
def draw_keyboard(img, keys):
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            key_x = offset_x + j * (key_width + padding)
            key_y = offset_y + i * (key_height + padding)

            # Adjust the size for the last row buttons
            if key == "SPACE":
                button_width = key_width * 6 + padding * 5
                key_x = offset_x  # Start from the left
            elif key == "ENTER" or key == "BACKSPACE":
                button_width = key_width * 2 + padding
                key_x = offset_x + total_width - button_width if key == "BACKSPACE" else offset_x + total_width - 2 * (key_width + padding) - button_width - padding
            else:
                button_width = key_width

            # Draw key as a simple rectangle
            cv2.rectangle(img, (key_x, key_y), (key_x + button_width, key_y + key_height),
                          (211, 211, 211), cv2.FILLED)  # Light gray color
            cv2.rectangle(img, (key_x, key_y), (key_x + button_width, key_y + key_height),
                          (169, 169, 169), 2)  # Darker gray border

            # Draw text on the key
            font_scale = 0.8 if key in ["SPACE", "ENTER", "BACKSPACE"] else 1
            text_size = cv2.getTextSize(key, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
            text_x = key_x + (button_width - text_size[0]) // 2
            text_y = key_y + (key_height + text_size[1]) // 2
            cv2.putText(img, key, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, (0, 0, 0), 2)  # Black text

# Main loop to capture video and detect hand movements
while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)

    if hands:
        hand = hands[0]
        center_x, center_y = hand['center']  # Get center of the hand

        # Logic to determine which key is pressed based on hand position
        for i, row in enumerate(keyboard_keys):
            for j, key in enumerate(row):
                key_x = offset_x + j * (key_width + padding)
                key_y = offset_y + i * (key_height + padding)

                # Adjust the size for the last row buttons
                if key == "SPACE":
                    button_width = key_width * 6 + padding * 5
                    key_x = offset_x  # Start from the left
                elif key == "ENTER" or key == "BACKSPACE":
                    button_width = key_width * 2 + padding
                    key_x = offset_x + total_width - button_width if key == "BACKSPACE" else offset_x + total_width - 2 * (key_width + padding) - button_width - padding
                else:
                    button_width = key_width

                if key_x < center_x < key_x + button_width and key_y < center_y < key_y + key_height:
                    current_time = time.time()

                    if previous_key == key and (current_time - key_press_time) < press_delay:
                        continue

                    # Press the key
                    if key == "SPACE":
                        keyboard.press(Key.space)
                        keyboard.release(Key.space)
                    elif key == "ENTER":
                        keyboard.press(Key.enter)
                        keyboard.release(Key.enter)
                    elif key == "BACKSPACE":
                        keyboard.press(Key.backspace)
                        keyboard.release(Key.backspace)
                    else:
                        keyboard.press(key)
                        keyboard.release(key)

                    previous_key = key
                    key_press_time = current_time
                    break
        else:
            previous_key = None

    draw_keyboard(img, keyboard_keys)
    cv2.imshow("Virtual Keyboard", img)

    if cv2.waitKey(1) & 0xFF == 27:  # Exit on ESC key
        break

cap.release()
cv2.destroyAllWindows()
