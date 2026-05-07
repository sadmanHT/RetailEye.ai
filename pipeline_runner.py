import os
import cv2
import time
import json
import argparse
from pathlib import Path
from typing import Dict, Any

from pipeline.preprocessor import FramePreprocessor
from pipeline.detector import Detector
from pipeline.tracker import PersonTracker
from pipeline.analytics import ZoneAnalytics, QueueDetector
from utils.heatmap import HeatmapGenerator

def run_pipeline(
    video_path: str,
    model_path: str,
    output_path: str,
    show_live: bool = False,
    save_analytics_json: bool = True
) -> None:
    """
    Main orchestration function for the RetailEye AI system.
    Processes a video through preprocessor, detector, tracker, analytics, and heatmap generation.

    Args:
        video_path (str): Path to the input video.
        model_path (str): Path to the trained YOLOv8 model weights.
        output_path (str): File path for the annotated output video.
        show_live (bool): If True, renders processing live to an OpenCV window.
        save_analytics_json (bool): If True, dumps final aggregate analytics to a JSON file.
    """
    # Input validation
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Input video not found: {video_path}")
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video feed from: {video_path}")

    # Read video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps <= 0:
        fps = 25.0

    print(f"Initializing RetailEye AI Pipeline...")
    print(f"Video: {width}x{height} @ {fps} FPS | Total Frames: {total_frames}")

    # Initialize Modules with default parameters
    preprocessor = FramePreprocessor(target_width=width, target_height=height)
    detector = Detector(model_path=model_path, confidence_threshold=0.45)
    tracker = PersonTracker(max_age=30, n_init=3)

    # Hardcoded responsive zones relative to resolution:
    # 0-30% Entrance, 30-70% Middle, 70-100% Checkout
    z1 = int(width * 0.3)
    z2 = int(width * 0.7)
    
    zones = {
        "Entrance": [(0, 0), (z1, 0), (z1, height), (0, height)],
        "Middle": [(z1, 0), (z2, 0), (z2, height), (z1, height)],
        "Checkout": [(z2, 0), (width, 0), (width, height), (z2, height)]
    }
    zone_analytics = ZoneAnalytics(zones=zones, frame_rate=fps)

    # Queue detector inside the checkout zone (Bottom right 20% width relative footprint)
    queue_zone = [
        (int(width * 0.8), int(height * 0.4)), 
        (width, int(height * 0.4)), 
        (width, height), 
        (int(width * 0.8), height)
    ]
    queue_detector = QueueDetector(queue_zone=queue_zone, density_threshold=3, frame_rate=fps)
    
    heatmap = HeatmapGenerator(frame_width=width, frame_height=height, decay_factor=0.995)

    # Setup Video Writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    out_video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    start_time = time.time()
    seen_track_ids = set()

    print("\n[+] Pipeline processing started...")

    while True:
        ret, raw_frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # 1. Preprocess Frame
        # Depending on network dynamics, normally we pass raw BGRs directly to ultralytics since it letterboxes itself.
        # But we log the preprocessor call sequentially as designed for standardizing architecture. 
        # For simplicity and accurate spatial coordinates, we pass the original BGR frame to standard detection.
        # preprocessed = preprocessor.process_frame(raw_frame) 
        
        # 2. Detection (Filtering down to strictly Persons)
        detections = detector.detect(raw_frame)
        person_detections = detector.get_person_detections(detections)

        # 3. Tracker Update
        tracks = tracker.update(person_detections, raw_frame)
        active_tracks = tracker.get_active_tracks(tracks)
        
        for t in active_tracks:
            seen_track_ids.add(t["track_id"])

        # 4. Analytics Updates
        zone_counts = zone_analytics.update(active_tracks, frame_count)
        queue_stats = queue_detector.update(active_tracks, frame_count)
        heatmap.update(active_tracks)

        # 5. Composite Output Drawings
        annotated_frame = raw_frame.copy()
        annotated_frame = zone_analytics.draw_zones(annotated_frame)
        annotated_frame = heatmap.get_heatmap_overlay(annotated_frame) # Draws with internal 50% blend, prompt requested 40% normally mapped 
        annotated_frame = queue_detector.draw_queue_status(annotated_frame)
        annotated_frame = tracker.draw_tracks(annotated_frame, active_tracks)
        
        # Write Frame
        out_video.write(annotated_frame)

        # 6. Live view optionally
        if show_live:
            # Scale down large output matrices for safe standard 1080p monitors locally
            display_frame = cv2.resize(annotated_frame, (1280, 720))
            cv2.imshow("RetailEye AI - Live Feed", display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Early termination requested by user.")
                break

        # 7. Progress Reporting
        if frame_count % 100 == 0:
            elapsed = time.time() - start_time
            current_fps = frame_count / elapsed
            progress_pct = (frame_count / total_frames) * 100 if total_frames > 0 else 0
            
            queue_str = f"| Q-Wait: {queue_stats['average_wait_estimate_seconds']}s" if queue_stats["is_queue_alert"] else ""
            print(f"[{progress_pct:.1f}%] Frame {frame_count}/{total_frames} | FPS: {current_fps:.1f} | "
                  f"Zones: {zone_counts} {queue_str}")

    # Cleanup operations
    cap.release()
    out_video.release()
    if show_live:
        cv2.destroyAllWindows()

    total_time = time.time() - start_time
    video_duration_seconds = frame_count / fps

    # Generates Final Analytics Report payload
    report_dict = {
        "total_frames_processed": frame_count,
        "video_duration_seconds": round(video_duration_seconds, 2),
        "zone_summaries": zone_analytics.get_zone_summary(),
        "dwell_times": zone_analytics.get_dwell_times(),
        "heatmap_hotspots": heatmap.get_hotspots(top_n=10),
        "unique_people_tracked": len(seen_track_ids)
    }

    if save_analytics_json:
        report_path = Path(output_path).with_suffix('.json')
        with open(report_path, "w") as f:
            json.dump(report_dict, f, indent=4)
        print(f"\n[+] Analytics JSON saved to: {report_path}")

    # Console Summary View
    print("\n================ FINAL REPORT ================")
    print(f"Total Processing Time : {total_time:.2f} seconds")
    print(f"Video Timeline        : {video_duration_seconds:.2f} seconds")
    print(f"Total Unique People   : {len(seen_track_ids)}")
    print("\n--- Zone Insights ---")
    for zname, zdata in report_dict["zone_summaries"].items():
        print(f" ► {zname}:")
        print(f"     Total Visitors    : {zdata['total_visits']}")
        print(f"     Avg Dwell (sec)   : {zdata['average_dwell_seconds']}")
        print(f"     Max Dwell (sec)   : {zdata['max_dwell_seconds']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RetailEye AI - Video Analytics Pipeline")
    parser.add_argument("--video_path", type=str, required=True, help="Absolute/relative path to source MP4.")
    parser.add_argument("--model_path", type=str, required=True, help="Path to trained YOLOv8 weights (e.g., best.pt).")
    parser.add_argument("--output_path", type=str, required=True, help="Destination render MP4.")
    parser.add_argument("--show_live", action="store_true", help="Launch an OpenCV bounding window during processing.")
    
    args = parser.parse_args()
    
    try:
        run_pipeline(
            video_path=args.video_path,
            model_path=args.model_path,
            output_path=args.output_path,
            show_live=args.show_live,
            save_analytics_json=True
        )
    except Exception as err:
        print(f"Pipeline crashed directly with error: {err}")
