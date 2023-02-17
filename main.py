import cv2
import mediapipe as mp
import copy
import numpy as np
# Initialize the MediaPipe Hand Tracking module
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

# Set the size and position of the square
square_size = 50
square_x = [0]*9
square_y = [0]*9

counter = 0
for idx in range(9):
    square_x[idx] = 0+10+square_size*counter
    counter += 1
    counter = 0 if counter == 3 else counter

square_y[:3] = [0+10+square_size*0] * 3
square_y[3:6] = [0+10+square_size*1] * 3
square_y[6:] = [0+10+square_size*2] * 3

goal_size = 80
goal_square_x = [0]*9
goal_square_y = [0]*9

counter = 0
for idx in range(9):
    goal_square_x[idx] = 200+10+goal_size*counter
    counter += 1
    counter = 0 if counter == 3 else counter

goal_square_y[:3] = [200+10+goal_size*0] * 3
goal_square_y[3:6] = [200+10+goal_size*1] * 3
goal_square_y[6:] = [200+10+goal_size*2] * 3





# Create a VideoCapture object for the camera
cap = cv2.VideoCapture(0)

# Set the camera resolution and frame rate
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height =cap.get(cv2.CAP_PROP_FRAME_HEIGHT)



img = cv2.imread("./data/cat.jpg")
img_resized = cv2.resize(img,(int(frame_width/3),int(frame_height/3)))
img_height, img_width, _ = img_resized.shape

# image initial position
x = 50
y = 50

while True:
    # Capture a frame from the camera
    success, frame = cap.read()

    if not success:
        break

    # Flip the frame horizontally for a mirror effect
    frame = cv2.flip(frame, 1)

    # Process the frame with the MediaPipe Hand Tracking module
    results = hands.process(frame)

    # Extract the hand landmarks from the results
    if results.multi_hand_landmarks:
        for index,hand_landmarks in enumerate(results.multi_hand_landmarks):
            #print(f"index {index}")
            mp_drawing.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            hand_label = results.multi_handedness[index].classification[0].label

            image_height, image_width, _ = frame.shape

            if hand_label == "Left":
                print("left")
                L_index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                L_thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                L_index_finger_x = int(L_index.x * image_width)
                L_index_finger_y = int(L_index.y * image_height)
                L_thumb_x = int(L_thumb.x * image_width)
                L_thumb_y = int(L_thumb.y * image_height)

                if (L_thumb_x - L_index_finger_x) ** 2 + (L_thumb_y - L_index_finger_y) ** 2 < 600:
                    counter = 0
                    for idx in range(9):
                        square_x[idx] = 0+10+square_size*counter
                        counter += 1
                        counter = 0 if counter == 3 else counter

                    square_y[:3] = [0+10+square_size*0] * 3
                    square_y[3:6] = [0+10+square_size*1] * 3
                    square_y[6:] = [0+10+square_size*2] * 3

            # right hand
            elif hand_label == "Right":
                print("right")
                R_index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                R_thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

                R_index_finger_x = int(R_index.x * image_width)
                R_index_finger_y = int(R_index.y * image_height)
                R_thumb_x = int(R_thumb.x * image_width)
                R_thumb_y = int(R_thumb.y * image_height)

                if (R_thumb_x - R_index_finger_x) ** 2 + (R_thumb_y - R_index_finger_y) ** 2 < 600:
                    #print("distance ",(thumb_x - index_finger_x) ** 2 + (thumb_y - index_finger_y) ** 2)

                    # create an image explaining this idea
                    # compare squared distance between index_finger and all boxes and choose the box with smallest distance
                    distance_list = [(x - R_index_finger_x) ** 2 + (y - R_index_finger_y) ** 2 for x,y in zip(square_x,square_y)]

                    # index of the box closest to your index finger
                    idx = distance_list.index(min(distance_list))


                    rule_x = square_x[idx] < R_index_finger_x < square_x[idx]+square_size
                    rule_y = square_y[idx] < R_index_finger_y < square_y[idx]+square_size

                    if rule_x and rule_y:
                        # Move the square to the position of the index finger
                        square_x[idx] = R_index_finger_x - square_size // 2
                        square_y[idx] = R_index_finger_y - square_size // 2
            else:
                print("unknown hand")


    # End of getting data from hands
    ###############################################################################################################################

    # 9 SQUARES
    # Draw the square on the frame
    box_start_coords,box_end_coords = zip(*[((sqr_x,sqr_y),(sqr_x+square_size,sqr_y+square_size)) for sqr_x,sqr_y in zip(square_x,square_y)])


    ########################################
    # GOAL
    goal_start_coords,goal_end_coords = zip(*[((sqr_x,sqr_y),(sqr_x+goal_size,sqr_y+goal_size)) for sqr_x,sqr_y in zip(goal_square_x,goal_square_y)])
    ## color of each box
    goal_colors = [(0,0,255)] * 9

    # find closest box for each goal || sample shape output: [(box_0,box_1,box_2,...),(box_0,box_1,box_2,...),...] and [goal_0,goal_1,goal_2,...]
    goal_distance_list = [[(goal_x - box_x) ** 2 + (goal_y - box_y) ** 2 for box_x,box_y in box_start_coords] for goal_x,goal_y in goal_start_coords]

    # index of closest box for each goal
    min_goal_idx = [[i for i, x in enumerate(t) if x == min(t)] for t in goal_distance_list]

    # Extract the first (and only) element from each inner list
    min_goal_idx = [next(iter(x), 0) for x in min_goal_idx]

    for i in range(len(goal_start_coords)):

        # idx of box closest to the current goal (goal[i])
        goal_idx = min_goal_idx[i]

        goal_rule_x = goal_square_x[goal_idx] < square_x[goal_idx] < goal_square_x[goal_idx]+goal_size
        goal_rule_y = goal_square_y[goal_idx] < square_y[goal_idx] < goal_square_y[goal_idx]+goal_size

        if goal_rule_x and goal_rule_y:
            goal_colors[goal_idx] = (0,255,0)

        # fill
        cv2.rectangle(
            frame,
            goal_start_coords[i],
            goal_end_coords[i],
            goal_colors[i],
            -1,
        )
        # border
        cv2.rectangle(
            frame,
            goal_start_coords[i],
            goal_end_coords[i],
            (0,0,0),
            2,
        )

    #######################################

    for i in range(len(box_start_coords)):

        # fill
        cv2.rectangle(
            frame,
            box_start_coords[i],
            box_end_coords[i],
            (255,0,0),
            -1,
        )
        # border
        cv2.rectangle(
            frame,
            box_start_coords[i],
            box_end_coords[i],
            (255, 255, 255),
            thickness=2,
        )

        # number inside boxes
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = str(i+1)
        textsize = cv2.getTextSize(text,font,1,2)[0]
        textX = int(((  box_start_coords[i][0]    )+ textsize[0]/2))
        textY = int(((  box_start_coords[i][1]    )+ textsize[1]))
        #cv2.putText(frame,text,(textX,textY),font,1,(255,255,255),2,cv2.LINE_AA)
        cv2.putText(frame,text,(box_start_coords[i][0]+(square_size//2)-(textsize[0]//2),box_start_coords[i][1]+(square_size//2)+(textsize[1]//2)),font,1,(255,255,255),2,cv2.LINE_AA)




    # add the image over the video capture frame
    #frame[y:y+img_height,x:x+img_width] = img_resized

    # Display the frame with the square
    cv2.imshow('Hand Tracking', frame)

    # Exit if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the VideoCapture object and close all windows
cap.release()
cv2.destroyAllWindows()