import os
import cv2
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
from ultralytics import YOLO

class Detector:
    """
    YOLOv8-based Object Detector for the RetailEye AI project.
    Handles loading the model, inference, parsing outputs into standardized dictionaries,
    and drawing bounding boxes.
    """

    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.45,
        iou_threshold: float = 0.45,
        device: str = "cpu"
    ):
        """
        Initialize the Detector.

        Args:
            model_path (str): Path to the YOLOv8 weights (.pt file).
            confidence_threshold (float): Minimum confidence for a detection.
            iou_threshold (float): Intersection over Union threshold for NMS.
            device (str): Device to run inference on ('cpu', 'cuda', 'cuda:0', etc.).
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self.model = self._load_model()
        
        # Cache the class names mapping from the YOLO model
        if self.model is not None:
            self.names = self.model.names
        else:
            self.names = {}

    def _load_model(self) -> Optional[YOLO]:
        """
        Loads the YOLOv8 model with error handling.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at: {self.model_path}. Please train or download weights.")
        try:
            model = YOLO(self.model_path)
            model.to(self.device)
            return model
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            return None

    def _parse_results(self, result: Any) -> List[Dict[str, Any]]:
        """
        Helper method to parse ultralytics results object into a list of dictionaries.
        """
        detections = []
        if result.boxes is None or len(result.boxes) == 0:
            return detections

        # Extract tensors to CPU numpy arrays
        boxes = result.boxes.xyxy.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy().astype(int)

        for i in range(len(boxes)):
            conf = float(confidences[i])
            if conf < self.confidence_threshold:
                continue
                
            x1, y1, x2, y2 = map(int, boxes[i])
            class_id = class_ids[i]
            class_name = self.names.get(class_id, "unknown")
            
            # Calculate Center (cx, cy)
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": conf,
                "class_id": class_id,
                "class_name": class_name,
                "center": (cx, cy)
            })

        return detections

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run inference on a single BGR OpenCV frame.

        Args:
            frame (np.ndarray): The BGR image frame.

        Returns:
            List[Dict[str, Any]]: A list of valid detections formatted as dictionaries.
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded. Cannot run inference.")

        # Run model inference
        # verbose=False prevents YOLO from printing frame-by-frame logs to console
        results = self.model(
            frame,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False
        )

        return self._parse_results(results[0])

    def detect_batch(self, frames: List[np.ndarray]) -> List[List[Dict[str, Any]]]:
        """
        Run inference on a batch (list) of BGR OpenCV frames.

        Args:
            frames (List[np.ndarray]): A list of BGR image frames.

        Returns:
            List[List[Dict[str, Any]]]: A list indicating the detections per frame.
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded. Cannot run inference.")

        if not frames:
            return []

        # Run batched inference
        results = self.model(
            frames,
            conf=self.confidence_threshold,
            iou=self.iou_threshold,
            verbose=False,
            stream=False # Force immediate list generation
        )

        batch_detections = []
        for result in results:
            batch_detections.append(self._parse_results(result))

        return batch_detections

    def get_person_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters a list of detections to only return 'person' class instances.

        Args:
            detections (List[Dict[str, Any]]): Unfiltered raw detections.

        Returns:
            List[Dict[str, Any]]: Detections filtered to person.
        """
        return [d for d in detections if d["class_name"].lower() == "person"]

    def draw_detections(self, frame: np.ndarray, detections: List[Dict[str, Any]], color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Draw bounding boxes, labels, and center points on a given frame.

        Args:
            frame (np.ndarray): The BGR frame to draw on.
            detections (List[Dict[str, Any]]): The list of formatted detections.
            color (Tuple[int, int, int]): The BGR color tuple for the bounding box. Default is green.

        Returns:
            np.ndarray: The modified frame copy with drawn annotations.
        """
        annotated_frame = frame.copy()

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            class_name = det["class_name"]
            cx, cy = det["center"]

            # Draw Bounding Box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

            # Draw Center Dot
            cv2.circle(annotated_frame, (cx, cy), radius=4, color=(0, 0, 255), thickness=-1)

            # Draw Label
            label = f"{class_name} {conf:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(annotated_frame, (x1, y1 - 20), (x1 + w, y1), color, -1)
            cv2.putText(annotated_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        return annotated_frame
