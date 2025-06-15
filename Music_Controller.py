import cv2
import mediapipe as mp
import numpy as np
import math
import pygame

# Initialize pygame mixer for music playback
pygame.mixer.init()

# Music playlist
playlist = [
    "C:/Users/ASUS/Music/Haara Hu Baba Par Tujhpe Bharosa Hai Mp3 Song.mp3",
    "C:/Users/ASUS/Music/I had to fall.mp3",
    "C:/Users/ASUS/Music/infiny_prayer_Mahataria_ra.mp3"
]
current_track = 0
pygame.mixer.music.load(playlist[current_track])
pygame.mixer.music.play(-1)  # Play in a loop
print(f"Playing: {playlist[current_track]}")

# Initialize Mediapipe for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)

# Function to calculate distance between two points
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# Function to switch track
def switch_track(direction):
    global current_track
    pygame.mixer.music.stop()
    if direction == "next":
        current_track = (current_track + 1) % len(playlist)
    elif direction == "prev":
        current_track = (current_track - 1) % len(playlist)
    pygame.mixer.music.load(playlist[current_track])
    pygame.mixer.music.play(-1)
    print(f"Playing: {playlist[current_track]}")

# Flags for gestures
is_paused = False

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get landmarks for thumb tip and index tip
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            # Convert to pixel coordinates
            h, w, _ = img.shape
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
            middle_x, middle_y = int(middle_tip.x * w), int(middle_tip.y * h)

            # Draw circles on landmarks
            cv2.circle(img, (thumb_x, thumb_y), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (index_x, index_y), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (middle_x, middle_y), 10, (255, 0, 0), cv2.FILLED)

            # Calculate distance between thumb and index tip
            distance_thumb_index = calculate_distance(thumb_x, thumb_y, index_x, index_y)

            # Play/Pause Gesture: Circle made with thumb and index finger
            if distance_thumb_index < 30:
                if not is_paused:
                    pygame.mixer.music.pause()
                    is_paused = True
                    print("Music Paused")
                else:
                    pygame.mixer.music.unpause()
                    is_paused = False
                    print("Music Playing")

            # Volume Control: Distance between thumb and index finger
            volume = np.interp(distance_thumb_index, [30, 200], [0.0, 1.0])
            pygame.mixer.music.set_volume(volume)

            # Next Song Gesture: Distance between index and middle fingers decreases significantly
            distance_index_middle = calculate_distance(index_x, index_y, middle_x, middle_y)
            if distance_index_middle < 30:
                switch_track("next")

            # Previous Song Gesture: Spread index and middle fingers widely
            if distance_index_middle > 150:
                switch_track("prev")

            # Display volume level on screen
            cv2.putText(img, f'Volume: {int(volume * 100)}%', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Hand Gesture Music Controller", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
        break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.music.stop()
print("Program exited and music stopped.")
