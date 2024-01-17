import numpy as np
import mediapipe as mp


from cv_puzzle.components import utils


class UserHand:
    def __init__(self) -> None:
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self.hand_present = False

    def lefthand(
        self,
        hand_landmarks,
        frame: np.ndarray,
    ):
        """
        Process the landmarks of the left hand.

        Args:
            hand_landmarks (mp.framework.formats.landmark_pb2.NormalizedLandmarkList): Landmarks of the hand.
            frame (np.ndarray): The input frame.

        Returns:
            None
        """

        L_index = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        L_thumb = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]

        image_height, image_width, _ = frame.shape

        self.L_index_finger_x = int(L_index.x * image_width)
        self.L_index_finger_y = int(L_index.y * image_height)
        self.L_thumb_x = int(L_thumb.x * image_width)
        self.L_thumb_y = int(L_thumb.y * image_height)

    def righthand(
        self,
        hand_landmarks,
        frame: np.ndarray,
    ):
        """
        Process the landmarks of the right hand.

        Args:
            hand_landmarks (mp.framework.formats.landmark_pb2.NormalizedLandmarkList): Landmarks of the hand.
            frame (np.ndarray): The input frame.

        Returns:
            None
        """

        R_index = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        R_thumb = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]

        image_height, image_width, _ = frame.shape

        self.R_index_finger_x = int(R_index.x * image_width)
        self.R_index_finger_y = int(R_index.y * image_height)
        self.R_thumb_x = int(R_thumb.x * image_width)
        self.R_thumb_y = int(R_thumb.y * image_height)

    def hand_reset_position(self, reset_distance: int = 200):
        distance = utils.get_distance(
            self.L_thumb_x, self.L_thumb_y, self.L_index_finger_x, self.L_index_finger_y
        )
        return distance

    def hand_move_position(self, move_distance=600):
        distance = utils.get_distance(
            self.R_thumb_x, self.R_thumb_y, self.R_index_finger_x, self.R_index_finger_y
        )
        return distance

    def extract_landmark(self, frame: np.ndarray) -> np.ndarray:
        """
        Extracts landmarks from the given frame using the hands.process() method.
        Parameters:
            frame (np.ndarray): The input frame from which landmarks are to be extracted.
        Returns:
            np.ndarray: The frame with landmarks drawn on it.
        """

        results = self.hands.process(frame)

        if results.multi_hand_landmarks:
            for index, hand_landmarks in enumerate(results.multi_hand_landmarks):
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

                hand_label = results.multi_handedness[index].classification[0].label

                if hand_label == "Left":
                    self.lefthand(hand_landmarks, frame)
                    self.hand_present = "Left"
                elif hand_label == "Right":
                    self.righthand(hand_landmarks, frame)
                    self.hand_present = "Right"
                else:
                    self.hand_present = False

        return frame
