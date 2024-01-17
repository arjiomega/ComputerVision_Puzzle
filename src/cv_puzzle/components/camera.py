from typing import Callable, Any

import cv2
import numpy as np


class Camera:
    def __init__(self) -> None:
        self.camera_capture = cv2.VideoCapture(0)

    @staticmethod
    def startcam(
        func: Callable[[Any, np.ndarray], np.ndarray]
    ) -> Callable[[Any], None]:
        """
        Decorator function that starts the camera and applies a given function to each frame.

        Args:
        func (Callable[[Any, np.ndarray], np.ndarray]): The function to be applied to each frame.

        Returns:
        Callable[[Any], None]: The decorated function.
        """

        def inner(self: Any) -> None:
            """
            Inner function that reads frames from the camera, applies the given function,
            and displays the processed frame.

            Args:
            self (Any): The object instance.

            Returns:
            None
            """
            while True:
                _, frame = self.camera_capture.read()
                frame = func(self, frame)
                cv2.imshow("Computer Vision Puzzle", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        return inner

    def stopcam(self: Any) -> None:
        """
        Stop the camera capture and close all windows.

        Args:
            self: The object instance.

        Returns:
            None
        """
        self.camera_capture.release()
        cv2.destroyAllWindows()
