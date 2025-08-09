import cv2
import mediapipe as mp
import random
import time

# Init
cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

tipIds = [4, 8, 12, 16, 20]
choices = ["Rock", "Paper", "Scissors"]
user_score = 0
computer_score = 0
result = ""
computer_move = "Waiting..."

def get_user_move(fingers):
    if fingers == 0:
        return "Rock"
    elif fingers == 2:
        return "Scissors"
    elif fingers == 5:
        return "Paper"
    else:
        return "Invalid"

def get_winner(user, computer):
    global user_score, computer_score
    if user == computer:
        return "Draw"
    elif (user == "Rock" and computer == "Scissors") or \
         (user == "Scissors" and computer == "Paper") or \
         (user == "Paper" and computer == "Rock"):
        user_score += 1
        return "You Win!"
    else:
        computer_score += 1
        return "Computer Wins"

last_move_time = 0
delay = 0.5  # seconds between moves
# Set window name
# Set window name
cv2.namedWindow("Rock Paper Scissors Game", cv2.WINDOW_NORMAL)

# Get one frame to know actual size
success, frame = cap.read()
if success:
    frame_height, frame_width = frame.shape[:2]
    scale = 1.2  # 1.0 = normal, higher means bigger window
    cv2.resizeWindow("Rock Paper Scissors Game",
                     int(frame_width * scale),
                     int(frame_height * scale))

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    lmList = []
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))

    user_move = "Waiting..."
    if lmList:
        fingers = []

        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        totalFingers = fingers.count(1)
        user_move = get_user_move(totalFingers)

        # Time-based decision trigger
        if time.time() - last_move_time > delay and user_move in choices:
            computer_move = random.choice(choices)
            result = get_winner(user_move, computer_move)
            last_move_time = time.time()

    # Draw UI
    cv2.putText(img, f'Your Move: {user_move}', (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(img, f'Computer Move: {computer_move}', (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
    cv2.putText(img, f'Result: {result}', (10, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)
    cv2.putText(img, f'You: {user_score}   Computer: {computer_score}', (10, 180),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 255), 2)
    cv2.putText(img, f'Show gesture every {delay}s', (10, 220),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    cv2.imshow("Rock Paper Scissors Game", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
