import cv2
import numpy as np
from cv_puzzle.components import camera, userhand, puzzle


class CVPuzzle(camera.Camera):
    def __init__(self) -> None:
        super().__init__()
        self.puzzle = puzzle.Puzzle()
        self.userhand = userhand.UserHand()

    @camera.Camera.startcam
    def run(self, frame: np.ndarray) -> np.ndarray:
        """
        Runs the CVPuzzle application on a given frame.

        Args:
            frame (np.ndarray): The input frame to process.

        Returns:
            np.ndarray: The processed frame.
        """

        # Flip the frame horizontally
        frame = cv2.flip(frame, 1)

        # Extract hand landmarks from the frame
        frame = self.userhand.extract_landmark(frame)

        # Draw the puzzle on the frame
        frame = self.puzzle.draw(frame)

        # Move the puzzle based on user's hand movement
        self.puzzle.move(self.userhand)

        # Show the goal state of the puzzle
        frame = self.puzzle.goal(frame)

        return frame


def main():
    # Create an instance of CVPuzzle
    app = CVPuzzle()

    # Run the application
    app.run()

    # Stop the camera
    app.stopcam()


if __name__ == "__main__":
    main()
