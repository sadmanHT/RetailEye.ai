import pytest
import numpy as np
import sys
import os

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline.preprocessor import FramePreprocessor
from pipeline.detector import Detector
from pipeline.analytics import ZoneAnalytics, QueueDetector
from utils.heatmap import HeatmapGenerator

def test_preprocessor():
    preprocessor = FramePreprocessor(target_width=640, target_height=640)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    processed = preprocessor.process_frame(frame)
    
    assert processed.shape == (640, 640, 3)
    assert processed.dtype == np.float32
    assert np.min(processed) >= 0.0
    assert np.max(processed) <= 1.0

def test_detector_init():
    with pytest.raises(Exception):
        Detector(model_path="non_existent.pt")

def test_zone_analytics(fake_tracks):
    zone_a = [(0, 0), (320, 0), (320, 480), (0, 480)]
    zone_b = [(320, 0), (640, 0), (640, 480), (320, 480)]
    
    analytics = ZoneAnalytics(zones={"zone_a": zone_a, "zone_b": zone_b})
    tracks = fake_tracks([(100, 100), (200, 200), (500, 100)])
    
    # Needs a current_frame integer
    zone_counts = analytics.update(tracks, current_frame=1)
    
    assert zone_counts["zone_a"] == 2
    assert zone_counts["zone_b"] == 1

def test_queue_detector(fake_tracks):
    queue_zone = [(0, 0), (640, 0), (640, 480), (0, 480)]
    detector = QueueDetector(queue_zone=queue_zone, density_threshold=2)
    
    tracks = fake_tracks([(100, 100), (200, 200), (300, 300), (400, 400)])
    
    # Expects an integer frame number, not a Numpy frame!
    result = detector.update(tracks, current_frame=1)
    # The return is a Dict based on the error trace documentation, not a tuple
    
    assert result["is_queue_alert"] is True
    assert result["people_in_queue"] == 4

def test_heatmap_generator(fake_tracks):
    generator = HeatmapGenerator(frame_width=640, frame_height=480)
    tracks = fake_tracks([(100, 100), (200, 200), (300, 300)])
    
    generator.update(tracks)
    
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    heatmap_overlay = generator.get_heatmap_overlay(frame)
    
    assert heatmap_overlay.shape == frame.shape
