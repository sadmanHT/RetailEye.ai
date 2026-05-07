import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from deep_sort_realtime.deepsort_tracker import DeepSort

class PersonTracker:
    """
    Multi-object tracker using DeepSORT to associate and track persons
    across consecutive video frames in the RetailEye AI project.
    """

    def __init__(
        self,
        max_age: int = 30,
        n_init: int = 3,
        max_cosine_distance: float = 0.3
    ):
        """
        Initialize the PersonTracker with DeepSORT configuration.

        Args:
            max_age (int): Maximum number of missed misses before a track is deleted. Default: 30.
            n_init (int): Number of consecutive detections before a track is confirmed. Default: 3.
            max_cosine_distance (float): Cosine distance threshold for matching. Default: 0.3.
        """
        self.tracker = DeepSort(
            max_age=max_age,
            n_init=n_init,
            max_cosine_distance=max_cosine_distance,
            embedder="mobilenet" # Uses MobileNet for appearance feature extraction by default
        )
        
    def update(self, detections: List[Dict[str, Any]], frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Updates the DeepSORT tracker with the latest frame's detections.

        Args:
            detections (List[Dict[str, Any]]): List of detections from the Detector.
                Expected keys: 'bbox' (x1, y1, x2, y2), 'confidence', 'class_id', 'class_name'.
            frame (np.ndarray): The current OpenCV BGR frame.

        Returns:
            List[Dict[str, Any]]: A list of track dictionaries containing track_id,
                bbox, class_name, confidence, center, and is_confirmed status.
        """
        # 1. Format detections for deep-sort-realtime input
        # DeepSort expects a list of tuples: ( [left, top, w, h], confidence, detection_class )
        deep_sort_detections = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            cls_name = det["class_name"]
            
            w = x2 - x1
            h = y2 - y1
            deep_sort_detections.append(([x1, y1, w, h], conf, cls_name))

        # 2. Update tracker
        tracked_objects = self.tracker.update_tracks(deep_sort_detections, frame=frame)

        # 3. Format output
        results = []
        for track in tracked_objects:
            # Reconstruct the bbox to [x1, y1, x2, y2]
            ltrb = track.to_ltrb()
            tx1, ty1, tx2, ty2 = map(int, ltrb)
            
            # Compute center dot of the bounding box
            cx = (tx1 + tx2) // 2
            cy = (ty1 + ty2) // 2
            
            # Safely handle track representation
            if track.track_id is None:
                continue
                
            results.append({
                "track_id": int(track.track_id),
                "bbox": [tx1, ty1, tx2, ty2],
                "class_name": track.get_det_class() or "unknown",
                "confidence": track.get_det_conf() or 0.0,
                "center": (cx, cy),
                "is_confirmed": track.is_confirmed()
            })
            
        return results

    def get_active_tracks(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters the track list to only return confirmed, active tracks.

        Args:
            tracks (List[Dict[str, Any]]): The full list of track dictionaries from `update`.

        Returns:
            List[Dict[str, Any]]: Confirmed tracks only.
        """
        return [track for track in tracks if track["is_confirmed"]]

    def draw_tracks(self, frame: np.ndarray, tracks: List[Dict[str, Any]]) -> np.ndarray:
        """
        Draws track IDs, bounding boxes, and center points on the frame.
        Assigns a unique and stable color to each track ID.

        Args:
            frame (np.ndarray): The BGR OpenCV frame.
            tracks (List[Dict[str, Any]]): List of track dictionaries.

        Returns:
            np.ndarray: The annotated frame.
        """
        annotated_frame = frame.copy()

        for track in tracks:
            # We typically only visualize confirmed tracks, but we draw whatever relies in the list
            track_id = track["track_id"]
            x1, y1, x2, y2 = track["bbox"]
            cx, cy = track["center"]

            # Generate a pseudo-random color consistently per track_id using an offset multiplier
            color = (
                (track_id * 37) % 255,
                (track_id * 89) % 255,
                (track_id * 151) % 255
            )

            # Draw the bounding rectangle
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

            # Draw the center point
            cv2.circle(annotated_frame, (cx, cy), radius=4, color=color, thickness=-1)

            # Draw the ID label above the box
            label = f"ID: {track_id}"
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated_frame, (x1, y1 - text_h - 10), (x1 + text_w, y1), color, -1)
            cv2.putText(
                annotated_frame, 
                label, 
                (x1, y1 - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, 
                (255, 255, 255), 
                2
            )

        return annotated_frame
