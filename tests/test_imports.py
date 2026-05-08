import pytest
import sys
import os

# Ensure the root directory is in the path to allow imports from pipeline, utils, and pipeline_runner
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_detector_import():
    from pipeline.detector import Detector
    assert Detector is not None
    print("Success: pipeline.detector.Detector imported successfully.")

def test_tracker_import():
    from pipeline.tracker import PersonTracker
    assert PersonTracker is not None
    print("Success: pipeline.tracker.PersonTracker imported successfully.")

def test_preprocessor_import():
    from pipeline.preprocessor import FramePreprocessor
    assert FramePreprocessor is not None
    print("Success: pipeline.preprocessor.FramePreprocessor imported successfully.")

def test_analytics_import():
    from pipeline.analytics import ZoneAnalytics, QueueDetector
    assert ZoneAnalytics is not None
    assert QueueDetector is not None
    print("Success: pipeline.analytics.ZoneAnalytics and QueueDetector imported successfully.")

def test_heatmap_import():
    from utils.heatmap import HeatmapGenerator
    assert HeatmapGenerator is not None
    print("Success: utils.heatmap.HeatmapGenerator imported successfully.")

def test_pipeline_runner_import():
    from pipeline_runner import run_pipeline
    assert callable(run_pipeline)
    print("Success: pipeline_runner.run_pipeline imported successfully and is callable.")
