import pytest
import cv2
import numpy as np
import psutil
import os
import json
import threading
from pathlib import Path
from pipeline_runner import run_pipeline
from pipeline.analytics import ZoneAnalytics, QueueDetector

class TestVideoEdgeCases:
    """
    Video-specific edge case tests assuring the RetailEye pipeline
    does not crash under abnormal inputs, tiny vectors, broken codec
    files, or heavily prolonged streaming sequences.
    """

    def test_single_frame_video(self, tmp_path, model_path):
        """
        Run the pipeline exactly against a 1-frame video bounds.
        Tests whether loops depend on N+1 assumptions crashing gracefully.
        """
        video_path = tmp_path / "single_frame.mp4"
        out_path = tmp_path / "out_single.mp4"
        out = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*'mp4v'), 25, (640, 480))
        out.write(np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8))
        out.release()
        
        run_pipeline(str(video_path), model_path, str(out_path))
        
        assert out_path.exists(), "Pipeline failed to produce an output file on a 1-frame input."
        assert out_path.with_suffix(".json").exists(), "Pipeline failed to write analytics for 1-frame input."
        
    def test_very_long_video_memory(self, fake_long_video_path, tmp_path, model_path):
        """
        Assure prolonged memory streams do not silently decay caching arrays,
        storing references and scaling limits uncontrollably. Tests memory leakages.
        """
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss
        
        out_path = tmp_path / "long_out.mp4"
        run_pipeline(str(fake_long_video_path), model_path, str(out_path))
        
        mem_after = process.memory_info().rss
        growth_mb = (mem_after - mem_before) / (1024 * 1024)
        
        assert grow_mb < 500.0, "Memory leaped above 500MB indicating a probable leak sequence during long processing loops."

    def test_zero_detections_video(self, tmp_path, model_path, fake_black_frame):
        """
        Pass a purely black silent video array through the engine expecting zero object mappings.
        Ensures dictionary indexing gracefully evaluates omitting KeyError tracebacks natively.
        """
        video_path = tmp_path / "black_video.mp4"
        out_path = tmp_path / "black_out.mp4"
        out = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*'mp4v'), 25, (640, 480))
        for _ in range(10):
            out.write(fake_black_frame)
        out.release()
        
        run_pipeline(str(video_path), model_path, str(out_path))
        
        with open(out_path.with_suffix(".json"), "r") as f:
            data = json.load(f)
            
        assert data["unique_people_tracked"] == 0, "Black frame video hallucinated person mappings."
        assert len(data["dwell_times"]) == 0, "Dwell times dictionaries initiated records over null trackers."

    def test_corrupted_video_file(self, fake_corrupt_video_path, tmp_path, model_path):
        """
        Broken video arrays natively reject bounds cleanly instead of propagating generic Python
        IndexError crashes into the backend web routers.
        """
        out_path = tmp_path / "corrupted_out.mp4"
        with pytest.raises(RuntimeError) as exc_info:
            run_pipeline(str(fake_corrupt_video_path), model_path, str(out_path))
            
        assert "Could not open video feed from:" in str(exc_info.value), "Corrupt video did not throw the expected distinct descriptive bounds Exception limit."

    def test_unsupported_video_format(self, tmp_path, model_path):
        """
        File payloads pretending to be valid codec sequences via suffixes must be structurally
        denied explicitly upon reading sequence boundaries correctly.
        """
        invalid_file = tmp_path / "text_pretending_video.mp4"
        invalid_file.write_text("Not actually video data")
        
        out_path = tmp_path / "out_unsupported.mp4"
        with pytest.raises((ValueError, RuntimeError, IOError)) as exc_info:
            run_pipeline(str(invalid_file), model_path, str(out_path))
            
        assert "Could not open video feed from:" in str(exc_info.value) or "video file" in str(exc_info.value).lower(), "Unsupported video payload failed to safely explicitly deny the pipeline ingestion structure."

    def test_video_with_no_people(self, tmp_path, model_path, fake_white_frame):
        """
        An empty bright literal footprint forces YOLOv8 to trace purely architectural blanks cleanly.
        """
        video_path = tmp_path / "empty_room.mp4"
        out_path = tmp_path / "empty_out.mp4"
        out = cv2.VideoWriter(str(video_path), cv2.VideoWriter_fourcc(*'mp4v'), 25, (640, 480))
        for _ in range(5):
            out.write(fake_white_frame)
        out.release()
        
        run_pipeline(str(video_path), model_path, str(out_path))
        
        with open(out_path.with_suffix(".json"), "r") as f:
            data = json.load(f)
            
        assert data["unique_people_tracked"] == 0, "No unique trackers must instantiate."
        for zone, zdata in data["zone_summaries"].items():
            assert zdata["current_count"] == 0
            assert zdata["total_visits"] == 0


class TestAnalyticsEdgeCases:
    """
    Abnormal bounding tracking limits mapped safely against ZoneAnalytics 
    and dictionary heuristics preventing crash exceptions naturally.
    """
    
    @pytest.fixture
    def basic_zone(self):
        return {"all_space": [(0,0), (640,0), (640,480), (0,480)]}

    def test_track_id_collision(self, basic_zone):
        """
        Overwritten dictionary keys mutating active indices must overwrite properly gracefully
        resolving cleanly via update limits instead of exception looping natively.
        """
        analytics = ZoneAnalytics(zones=basic_zone)
        # Duplicate track IDs in the same frame
        tracks = [
            {"track_id": 5, "center": (100, 100)},
            {"track_id": 5, "center": (200, 200)}
        ]
        stats = analytics.update(tracks, current_frame=1)
        
        # Should cleanly process and result in at most evaluating it properly without throwing 500 key crashes!
        assert stats["all_space"] == 2, "Failed processing ID overlays gracefully cleanly."

    def test_very_high_track_ids(self, basic_zone):
        """
        Heavy numeric float IDs evaluate securely unbothered mapping.
        """
        analytics = ZoneAnalytics(zones=basic_zone)
        tracks = [{"track_id": 999999999999, "center": (100, 100)}]
        stats = analytics.update(tracks, current_frame=1)
        assert stats["all_space"] == 1, "Extremely high ID crashed dictionary limits natively."

    def test_negative_confidence(self, basic_zone):
        """
        Negative values bypass standard heuristic thresholds safely passing to dictionaries cleanly.
        """
        analytics = ZoneAnalytics(zones=basic_zone)
        tracks = [{"track_id": 1, "center": (100, 100), "confidence": -0.5}]
        stats = analytics.update(tracks, current_frame=1)
        assert stats["all_space"] == 1, "Negative confidence mapping fractured processing sequentially."

    def test_confidence_above_one(self, basic_zone):
        """
        Floating ranges bounding exceeding 100% metrics safely iterate sequentially gracefully.
        """
        analytics = ZoneAnalytics(zones=basic_zone)
        tracks = [{"track_id": 1, "center": (100, 100), "confidence": 1.5}]
        stats = analytics.update(tracks, current_frame=1)
        assert stats["all_space"] == 1, "Excessive confidence bounds crashed sequential limits."

    def test_bbox_outside_frame(self, basic_zone):
        """
        Geometry plotting limits spanning exclusively external negative margins maps without arrays failing cleanly.
        """
        analytics = ZoneAnalytics(zones=basic_zone)
        tracks = [{"track_id": 1, "center": (800, 700), "bbox": [700, 600, 900, 800]}]
        stats = analytics.update(tracks, current_frame=1)
        assert stats["all_space"] == 0, "Bbox wildly outside boundaries should not register locally and must not crash."

    def test_inverted_bbox(self, basic_zone):
        """
        X1 > X2 evaluating coordinates parses purely avoiding generic tracebreaks securely.
        """
        analytics = ZoneAnalytics(zones=basic_zone)
        tracks = [{"track_id": 1, "center": (100, 100), "bbox": [200, 200, 100, 100]}]
        stats = analytics.update(tracks, current_frame=1)
        assert stats["all_space"] == 1, "Inverted bbox footprints crashed mappings."

    def test_zero_size_bbox(self, basic_zone):
        """
        Division by zero protection checking arrays mapped closely together completely resolving metrics gracefully.
        """
        analytics = ZoneAnalytics(zones=basic_zone)
        tracks = [{"track_id": 1, "center": (100, 100), "bbox": [100, 100, 100, 100]}]
        stats = analytics.update(tracks, current_frame=1)
        assert stats["all_space"] == 1, "Zero area bbox threw ZeroDivisionError exceptions locally."


class TestAPIEdgeCases:
    """
    Exposes web components to harsh parameters bounding API vectors exclusively mitigating
    Status 500 Internal breaks natively.
    """

    def test_upload_empty_file(self, api_client):
        """
        A 0 byte empty stream payload must yield predictable responses correctly cleanly.
        """
        response = api_client.post("/upload", files={'video': ('empty.mp4', b'', 'video/mp4')})
        assert response.status_code in [400, 422], "API failed to reject 0 byte files appropriately securely."

    def test_upload_non_video_file(self, api_client):
        """
        Non-video traces correctly fallback and evaluate rejection logic smoothly rejecting payloads cleanly.
        """
        response = api_client.post("/upload", files={'video': ('test.txt', b'this is text not video', 'text/plain')})
        # Usually pydantic strictly accepts it initially returning 202 later failing job securely, 
        # or custom file checking generates 400 safely. As long as it is not a 500 error!
        assert response.status_code != 500, "Non-video upload crashed the server securely."

    def test_upload_very_large_filename(self, api_client):
        """
        Path arrays mapping filename lengths exceptionally resolving payloads avoiding crashes sequentially.
        """
        large_name = "a" * 500 + ".mp4"
        response = api_client.post("/upload", files={'video': (large_name, b'dummy_video_data', 'video/mp4')})
        assert response.status_code != 500, "Large filename traces crashed API headers."

    def test_concurrent_uploads(self, api_client):
        """
        Threading evaluating multiple active requests concurrently returning unique job loops iteratively correctly.
        """
        results = []
        def make_request():
            res = api_client.post("/upload", files={'video': ('test.mp4', b'dummy_video_data', 'video/mp4')})
            results.append(res)
            
        threads = [threading.Thread(target=make_request) for _ in range(5)]
        for t in threads: t.start()
        for t in threads: t.join()
        
        valid_jobs = 0
        for res in results:
            assert res.status_code in [200, 202], "Concurrent upload threw invalid server responses."
            if "job_id" in res.json():
                valid_jobs += 1
        
        assert valid_jobs == 5, "Simultaneous streams lost uniquely returning job indices."

    def test_rapid_status_polling(self, api_client):
        """
        Hammer parameter limits generating loops polling sequences heavily securely evaluating natively cleanly.
        """
        for _ in range(100):
            response = api_client.get("/job/status/fake-id")
            assert response.status_code != 500, "Rapid polling crushed server loops causing 500 internal errors."

    def test_malformed_job_id(self, api_client):
        """
        Standard URI pathing loops traversing attempts parsing cleanly mapped routes avoiding 500 crashes cleanly.
        """
        response = api_client.get("/job/status/../../etc/passwd")
        assert response.status_code in [404, 422], "Malformed ID caused API trace exceptions locally."

    def test_sql_injection_in_job_id(self, api_client):
        """
        Direct SQL traces injecting routing bounds maps exactly avoiding generic traceback exceptions.
        """
        response = api_client.get("/job/status/1 OR 1=1")
        assert response.status_code in [404, 422], "Injection ID traces caused unsafe bounds locally."

    def test_extremely_long_job_id(self, api_client):
        """
        Massive URI strings testing standard length configurations mapping sequences sequentially.
        """
        response = api_client.get("/job/status/" + "a" * 10000)
        assert response.status_code in [404, 422, 414], "Extremely enormous URI strings crashed backend limits natively."
