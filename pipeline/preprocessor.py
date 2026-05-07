import cv2
import numpy as np
from typing import Generator


class FramePreprocessor:
    """
    Preprocesses video frames for YOLOv8 inference and tracking in the RetailEye AI system.
    """

    def __init__(self, target_width: int = 640, target_height: int = 640, apply_denoising: bool = False):
        """
        Initialize the FramePreprocessor.

        Args:
            target_width (int): Target width for the neural network.
            target_height (int): Target height for the neural network.
            apply_denoising (bool): Whether to apply Gaussian blur denoising.
        """
        self.target_width = target_width
        self.target_height = target_height
        self.apply_denoising = apply_denoising

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Preprocesses a raw OpenCV frame.
        Steps include letterboxing, optional denoising, BGR to RGB conversion, and normalization.

        Args:
            frame (np.ndarray): Raw BGR frame from OpenCV.

        Returns:
            np.ndarray: Preprocessed, normalized RGB frame.
        """
        # 1. Letterbox resizing (maintain aspect ratio)
        h, w = frame.shape[:2]
        scale = min(self.target_width / w, self.target_height / h)
        new_w, new_h = int(w * scale), int(h * scale)

        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Calculate padding to reach target dimensions
        top = (self.target_height - new_h) // 2
        bottom = self.target_height - new_h - top
        left = (self.target_width - new_w) // 2
        right = self.target_width - new_w - left

        # YOLO default padded border value is typically 114
        padded_frame = cv2.copyMakeBorder(
            resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
        )

        # 2. Optional Denoising
        if self.apply_denoising:
            padded_frame = cv2.GaussianBlur(padded_frame, (5, 5), 0)

        # 3. BGR to RGB conversion
        rgb_frame = cv2.cvtColor(padded_frame, cv2.COLOR_BGR2RGB)

        # 4. Normalize pixel values to 0-1 range
        normalized_frame = rgb_frame.astype(np.float32) / 255.0

        return normalized_frame

    def extract_frames_from_video(self, video_path: str, sample_rate_fps: float) -> Generator[np.ndarray, None, None]:
        """
        Extracts and preprocesses frames from a video file at a specified sample rate.

        Args:
            video_path (str): Path to the video file.
            sample_rate_fps (float): Desired extraction rate in frames per second.

        Yields:
            np.ndarray: Preprocessed frame ready for inference.
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        video_fps = cap.get(cv2.CAP_PROP_FPS)
        # Fallback if frame rate is not readable
        if video_fps <= 0:
            video_fps = 30.0

        # Determine how many source frames to step forward to match the target sample_rate
        # For example, if video is 30 FPS and sample_rate_fps is 5, we keep 1 frame every 6 frames.
        frame_interval = max(1, int(round(video_fps / sample_rate_fps)))

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Yield frame if it aligns with the requested sample interval
            if frame_count % frame_interval == 0:
                yield self.process_frame(frame)

            frame_count += 1

        cap.release()
