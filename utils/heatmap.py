import cv2
import numpy as np
from typing import List, Dict, Tuple, Any

class HeatmapGenerator:
    """
    Generates and maintains a real-time heatmap overlay of person movement 
    across video frames for the RetailEye AI project.
    """

    def __init__(self, frame_width: int, frame_height: int, decay_factor: float = 0.995):
        """
        Initializes the HeatmapGenerator.

        Args:
            frame_width (int): Width of the video frames.
            frame_height (int): Height of the video frames.
            decay_factor (float): Multiplier applied each frame to fade older heatmap intensities.
        """
        self.width = frame_width
        self.height = frame_height
        self.decay_factor = decay_factor

        # Maintain persistence over time initialized to zero
        self.accumulator = np.zeros((self.height, self.width), dtype=np.float32)

        # Precompute a 2D Gaussian kernel blob (sigma=20) to add directly to the accumulator
        # This is significantly faster for real-time systems than blurring the entire accumulator
        self.sigma = 20
        # Kernel size covers ~±3 sigma
        self.kernel_size = self.sigma * 6
        if self.kernel_size % 2 == 0:
            self.kernel_size += 1
            
        self.half_size = self.kernel_size // 2
        
        # Build 2D Gaussian
        x, y = np.meshgrid(
            np.arange(-self.half_size, self.half_size + 1),
            np.arange(-self.half_size, self.half_size + 1)
        )
        self.gaussian_kernel = np.exp(-(x**2 + y**2) / (2.0 * self.sigma**2)).astype(np.float32)

    def update(self, tracks: List[Dict[str, Any]]) -> None:
        """
        Updates the heatmap accumulator with new person center points and decays old values.

        Args:
            tracks (List[Dict[str, Any]]): List of track dictionaries from PersonTracker.
                Expects each track to have a "center" key with (x, y) tuple.
        """
        for track in tracks:
            cx, cy = track.get("center", (0, 0))
            
            # Define bounding box for the kernel on the main accumulator
            y1 = max(0, cy - self.half_size)
            y2 = min(self.height, cy + self.half_size + 1)
            x1 = max(0, cx - self.half_size)
            x2 = min(self.width, cx + self.half_size + 1)

            # Define bounding box for cropping the kernel itself (if center is near an edge)
            ky1 = y1 - (cy - self.half_size)
            ky2 = ky1 + (y2 - y1)
            kx1 = x1 - (cx - self.half_size)
            kx2 = kx1 + (x2 - x1)

            # Add the sliced gaussian blob to the accumulator ROI
            if y1 < y2 and x1 < x2:
                self.accumulator[y1:y2, x1:x2] += self.gaussian_kernel[ky1:ky2, kx1:kx2]

        # Apply exponential decay to the entire accumulator to fade historical traces
        self.accumulator *= self.decay_factor

    def get_heatmap_overlay(self, frame: np.ndarray) -> np.ndarray:
        """
        Processes the active accumulator into a visual colormap and blends it onto the frame.

        Args:
            frame (np.ndarray): Original BGR OpenCV frame.

        Returns:
            np.ndarray: Final frame showing the combined visual heatmap overlay.
        """
        # Normalize the accumulator to an 8-bit image (0-255) dynamically spanning the max heat
        max_val = np.max(self.accumulator)
        if max_val > 0.0:
            normalized_acc = (self.accumulator / max_val * 255.0).astype(np.uint8)
        else:
            normalized_acc = np.zeros_like(self.accumulator, dtype=np.uint8)

        # Apply JET colormap mapping 0 to blue, 255 to red
        heatmap_colored = cv2.applyColorMap(normalized_acc, cv2.COLORMAP_JET)

        # To prevent the entire screen from becoming a flat opaque blue, 
        # create a mask representing regions strictly with zero heat, mapping them to black
        # (Though standard cv2.addWeighted processes everything linearly, this looks better)
        zero_mask = normalized_acc == 0
        heatmap_colored[zero_mask] = frame[zero_mask]

        # Blend the heatmap with the original frame (Alpha = 0.5)
        blended_frame = cv2.addWeighted(heatmap_colored, 0.5, frame, 0.5, 0)
        return blended_frame

    def get_hotspots(self, top_n: int = 5) -> List[Tuple[int, int, float]]:
        """
        Retrieves the exact coordinates of the highest heatmap intensity concentrations.

        Args:
            top_n (int): Number of top peaks to return. Default is 5.

        Returns:
            List[Tuple[int, int, float]]: A list of tuples containing (x, y, intensity).
        """
        # Return empty immediately if accumulator is completely empty
        if np.max(self.accumulator) <= 0.0:
            return []

        flat_idx = np.argsort(self.accumulator.ravel())[-top_n:][::-1]
        
        hotspots = []
        for idx in flat_idx:
            intensity = float(self.accumulator.ravel()[idx])
            if intensity <= 0.0:
                continue
            y, x = np.unravel_index(idx, self.accumulator.shape)
            hotspots.append((int(x), int(y), intensity))
            
        return hotspots

    def reset(self) -> None:
        """
        Resets the heatmap accumulator, wiping all current history.
        """
        self.accumulator.fill(0.0)
