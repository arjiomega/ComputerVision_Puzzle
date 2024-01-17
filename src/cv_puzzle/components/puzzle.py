import cv2
import numpy as np
from cv_puzzle.components import utils, userhand


class Puzzle:
    """
    This is a sample class.

    :param math: The math module.
    :type math: module
    :param datetime: The datetime module.
    :type datetime: module
    """

    def __init__(self):
        self.puzzle_squares = self.generate_puzzle_squares(
            pos_x=0, pos_y=0, square_size=50, spacing=10
        )
        self.goal_squares = self.generate_puzzle_squares(
            pos_x=200, pos_y=200, square_size=80, spacing=10
        )

    def generate_puzzle_squares(
        self, pos_x, pos_y, square_size, spacing=10
    ) -> tuple[list, list]:
        """
        Generate puzzle squares given the position, size, and spacing.

        Args:
            pos_x (int): The x-coordinate of the starting position.
            pos_y (int): The y-coordinate of the starting position.
            square_size (int): The size of each square.
            spacing (int, optional): The spacing between squares. Defaults to 10.

        Returns:
            tuple[list, list]: A tuple containing two lists. The first list represents the x-coordinates of the squares, and the second list represents the y-coordinates of the squares.
        """
        square_x = [0] * 9
        square_y = [0] * 9

        counter = 0
        for idx in range(9):
            square_x[idx] = pos_x + spacing + square_size * counter
            counter += 1
            counter = 0 if counter == 3 else counter

        square_y[:3] = [pos_y + spacing + square_size * 0] * 3
        square_y[3:6] = [pos_y + spacing + square_size * 1] * 3
        square_y[6:] = [pos_y + spacing + square_size * 2] * 3

        return square_x, square_y

    def reset_position(self, square_size):
        self.puzzle_squares = self.generate_puzzle_squares(
            pos_x=0, pos_y=0, square_size=50, spacing=10
        )

    def draw_puzzle(
        self,
        frame: np.ndarray,
        squares: tuple[list, list],
        square_size: int,
        square_color: tuple,
    ) -> np.ndarray:
        """
        Draws a puzzle on the given frame using the provided squares, square size, and square color.
        Parameters:
            frame (np.ndarray): The frame on which the puzzle will be drawn.
            squares (list of tuples): The coordinates of the squares in the puzzle.
            square_size (int): The size of each square in pixels.
            square_color (tuple): The color of the squares, specified as a tuple of (B, G, R) values.
        Returns:
            np.ndarray: The frame with the puzzle drawn on it.
        """

        for i, (x_pos, y_pos) in enumerate(zip(*squares)):
            start_coords = (x_pos, y_pos)
            end_coords = tuple(x + square_size for x in start_coords)

            # fill
            cv2.rectangle(frame, start_coords, end_coords, square_color, -1)
            # border
            cv2.rectangle(frame, start_coords, end_coords, (255, 255, 255), thickness=2)

            # number inside boxes
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = str(i + 1)
            textsize = cv2.getTextSize(text, font, 1, 2)[0]
            textX = start_coords[0] + (square_size // 2) - (textsize[0] // 2)
            textY = start_coords[1] + (square_size // 2) + (textsize[1] // 2)
            cv2.putText(
                frame, text, (textX, textY), font, 1, (255, 255, 255), 2, cv2.LINE_AA
            )

        return frame

    def draw(self, frame: np.ndarray) -> np.ndarray:
        """
        Draws the puzzle on the given frame.
        Parameters:
            frame (np.ndarray): The frame on which the puzzle will be drawn.
        Returns:
            np.ndarray: The frame with the puzzle drawn on it.
        """

        square_size = 50
        goal_size = 80

        square_color = (255, 0, 0)  # Blue
        goal_color = (0, 0, 255)  # Red (Not activated)

        frame = self.draw_puzzle(frame, self.goal_squares, goal_size, goal_color)
        frame = self.draw_puzzle(frame, self.puzzle_squares, square_size, square_color)

        return frame

    def move(self, userhand: userhand.UserHand):
        """
        Moves the puzzle squares based on the position of the user's hand.
        Args:
            userhand: An instance of the UserHand class representing the user's hand.
        Returns:
            None
        """

        # Calculate the distance between the thumb and index finger
        if userhand.hand_present == "Right":
            distance = utils.get_distance(
                userhand.R_thumb_x,
                userhand.R_thumb_y,
                userhand.R_index_finger_x,
                userhand.R_index_finger_y,
            )
            if distance < 1000:
                # Get distances of the right index finger to each square
                distance_list = [
                    utils.get_distance(
                        x, y, userhand.R_index_finger_x, userhand.R_index_finger_y
                    )
                    for x, y in zip(*self.puzzle_squares)
                ]

                idx = distance_list.index(min(distance_list))
                square_size = 50

                rule_x = (
                    self.puzzle_squares[0][idx]
                    < userhand.R_index_finger_x
                    < self.puzzle_squares[0][idx] + square_size
                )
                rule_y = (
                    self.puzzle_squares[1][idx]
                    < userhand.R_index_finger_y
                    < self.puzzle_squares[1][idx] + square_size
                )

                if rule_x and rule_y:
                    # Move the square to the position of the index finger
                    self.puzzle_squares[0][idx] = (
                        userhand.R_index_finger_x - square_size // 2
                    )
                    self.puzzle_squares[1][idx] = (
                        userhand.R_index_finger_y - square_size // 2
                    )

    def goal(self, frame: np.ndarray):
        """
        Draw goal squares on the frame.
        Args:
            frame: The frame to draw the goal squares on.
        Returns:
            The frame with the goal squares drawn.
        """
        # Define square size, goal size, and goal color
        square_size = 50
        goal_size = 80
        goal_color = (0, 255, 0)

        # Calculate the distances between each goal square and puzzle square
        distance_list = [
            [
                utils.get_distance(goal_x, goal_y, square_x, square_y)
                for square_x, square_y in zip(*self.puzzle_squares)
            ]
            for goal_x, goal_y in zip(*self.goal_squares)
        ]

        # Find the index of the minimum distance for each puzzle square
        min_goal_idx = [
            True
            if square == square_i_to_goal_dists.index(min(square_i_to_goal_dists))
            else False
            for square, square_i_to_goal_dists in enumerate(distance_list)
        ]

        # Iterate over each goal square
        for goal_i, (goal_x, goal_y) in enumerate(zip(*self.goal_squares)):
            # Iterate over each puzzle square
            for square_x, square_y in zip(*self.puzzle_squares):
                # Check if the puzzle square is within the goal square
                rule_x = goal_x < square_x < goal_x + goal_size
                rule_y = goal_y < square_y < goal_y + goal_size

                if rule_x and rule_y and min_goal_idx[goal_i]:
                    # Define the start and end coordinates of the goal square
                    start_coords = (goal_x, goal_y)
                    end_coords = tuple(x + goal_size for x in start_coords)

                    # Fill the goal square
                    cv2.rectangle(frame, start_coords, end_coords, goal_color, -1)
                    # Draw the border of the goal square
                    cv2.rectangle(
                        frame, start_coords, end_coords, (255, 255, 255), thickness=2
                    )

                    # Add the number inside the goal square
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    text = str(goal_i + 1)
                    textsize = cv2.getTextSize(text, font, 1, 2)[0]
                    textX = start_coords[0] + (goal_size // 2) - (textsize[0] // 2)
                    textY = start_coords[1] + (goal_size // 2) + (textsize[1] // 2)
                    cv2.putText(
                        frame,
                        text,
                        (textX, textY),
                        font,
                        1,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

        return frame
