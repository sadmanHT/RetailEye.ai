import pytest
import numpy as np
from pipeline.analytics import ZoneAnalytics, QueueDetector

class TestZoneAnalytics:
    """
    Rigorous unit tests for the ZoneAnalytics class. Ensures polygons accurately
    classify spatial tracks, accumulate dwell times consistently natively to the given
    fps, and summarize the data for export correctly.
    """

    def test_person_in_correct_zone(self, fake_zones):
        """
        Place a single tracked person explicitly residing bounding bounds inside
        the 'entrance' area and assert the counts correctly bin the object mapping.
        """
        analytics = ZoneAnalytics(zones=fake_zones)
        
        # Entrance covers x from 0 to 213. Center at (100, 240) is strictly inside.
        tracks = [{"track_id": 1, "center": (100, 240)}]
        stats = analytics.update(tracks, current_frame=1)
        
        assert stats["entrance"] == 1, "Person within entrance must correctly flag Entrance."
        assert stats["middle"] == 0, "Person strictly inside entrance must not pollute middle."
        assert stats["checkout"] == 0, "Person strictly inside entrance must not pollute checkout."

    def test_person_on_zone_boundary(self, fake_zones):
        """
        Validates spatial intersections right exactly on the bounds between two defined
        polygons to ensure dual-counting bugs or floating point overlaps are mitigated cleanly
        and individuals are aggregated reliably over bounds overlapping.
        """
        analytics = ZoneAnalytics(zones=fake_zones)
        
        # Boundary between 'entrance' (0 to 213) and 'middle' (213 to 426) is exact x = 213.
        tracks = [{"track_id": 99, "center": (213, 240)}]
        stats = analytics.update(tracks, current_frame=1)
        
        # A single person should only add 1 to the overall occupancy globally.
        total_counted = sum(stats.values())
        assert total_counted == 1, f"Person on boundary must be counted in exactly ONE zone, got {total_counted}"

    def test_multiple_people_same_zone(self, fake_zones):
        """
        Validates volume aggregation scales simultaneously over a single area cleanly.
        """
        analytics = ZoneAnalytics(zones=fake_zones)
        
        # 5 people inside entrance zone (x < 213)
        tracks = [
            {"track_id": i, "center": (100 + i*10, 240)}
            for i in range(1, 6)
        ]
        
        stats = analytics.update(tracks, current_frame=1)
        assert stats["entrance"] == 5, "Zone Analytics failed to map multiple people properly."
        assert stats["middle"] == 0
        assert stats["checkout"] == 0

    def test_dwell_time_accumulates(self, fake_zones):
        """
        Verifies dwell time calculation accumulates iteratively for sustained presence
        amounting correctly against the frame_rate divisor translating directly to seconds.
        """
        analytics = ZoneAnalytics(zones=fake_zones, frame_rate=25.0)
        track = [{"track_id": 42, "center": (100, 240)}]
        
        for frame in range(100):
            analytics.update(track, current_frame=frame)
            
        dwells = analytics.get_dwell_times()
        
        # 100 frames / 25 fps = 4 seconds
        assert dwells[42]["entrance"] == 4.0, "Dwell time failed converting iterations to seconds."

    def test_dwell_time_accuracy(self, fake_zones):
        """
        Specifically locks to the explicit boundary frame counts ensuring long-scale
        intervals translate flawlessly avoiding float decay logic (250 frames @ 25fps = 10s).
        """
        analytics = ZoneAnalytics(zones=fake_zones, frame_rate=25.0)
        
        track = [{"track_id": 7, "center": (300, 240)}] # middle zone mapped
        
        for frame in range(250):
            analytics.update(track, current_frame=frame)
            
        dwells = analytics.get_dwell_times()
        
        assert "middle" in dwells[7], "Missing target mapped zone."
        assert abs(dwells[7]["middle"] - 10.0) < 0.1, "Dwell time accumulated outside 0.1s tolerance bound."

    def test_track_leaves_zone(self, fake_zones):
        """
        Individuals transversing between areas must maintain discrete logging mapped separately.
        Moves from Entrance to Middle.
        """
        analytics = ZoneAnalytics(zones=fake_zones, frame_rate=25.0)
        
        track_in_entrance = [{"track_id": 10, "center": (100, 240)}]
        track_in_middle = [{"track_id": 10, "center": (300, 240)}]
        
        for frame in range(0, 50):
            analytics.update(track_in_entrance, current_frame=frame)
            
        for frame in range(50, 100):
            analytics.update(track_in_middle, current_frame=frame)
            
        dwells = analytics.get_dwell_times()
        # 50 frames @ 25fps = 2.0 seconds inside each.
        assert dwells[10]["entrance"] == 2.0, "Entrance dwell severed incorrectly after move."
        assert dwells[10]["middle"] == 2.0, "Middle dwell accumulated incorrectly."

    def test_empty_tracks(self, fake_zones, fake_empty_track_list):
        """
        An empty iteration cycle must evaluate cleanly restoring zero aggregates inherently
        and preventing exceptions cascading across the matrix logic.
        """
        analytics = ZoneAnalytics(zones=fake_zones)
        stats = analytics.update(fake_empty_track_list, current_frame=1)
        
        for zone, count in stats.items():
            assert count == 0, f"Zone {zone} must reflect 0 occupancy on empty frames."

    def test_50_simultaneous_tracks(self, fake_zones, fake_crowded_track_list):
        """
        Mass volumetric handling spreads natively iterating polygons concurrently aggregating
        totals cleanly across wide dictionaries.
        """
        analytics = ZoneAnalytics(zones=fake_zones)
        stats = analytics.update(fake_crowded_track_list, current_frame=1)
        
        # 50 total elements. The fake list bounds x inside 500, which encompasses the layout.
        total = sum(stats.values())
        assert total == 50, f"Simultaneous tracking aggregate failed. Expected 50, got {total}"

    def test_zone_summary_structure(self, fake_zones):
        """
        Confirms the extracted data rollup returns safely adhering to strictly defined key formats
        to ensure API components and dict maps remain uniform implicitly preventing HTTP 500 blocks.
        """
        analytics = ZoneAnalytics(zones=fake_zones, frame_rate=25.0)
        track = [{"track_id": 1, "center": (100, 240)}]
        analytics.update(track, current_frame=1)
        
        summary = analytics.get_zone_summary()
        
        assert "entrance" in summary
        cols = summary["entrance"]
        
        assert "current_count" in cols and cols["current_count"] >= 0
        assert "average_dwell_seconds" in cols and cols["average_dwell_seconds"] >= 0
        assert "max_dwell_seconds" in cols and cols["max_dwell_seconds"] >= 0
        assert "total_visits" in cols and cols["total_visits"] >= 0

    def test_unknown_position_track(self, fake_zones):
        """
        If a track spawns heavily out of logical layout boundaries, it must not induce exceptions
        and simply drops cleanly as untagged preventing polygon mapping errors natively.
        """
        analytics = ZoneAnalytics(zones=fake_zones)
        track = [{"track_id": 200, "center": (-100, -100)}]
        stats = analytics.update(track, current_frame=1)
        
        total = sum(stats.values())
        assert total == 0, "Out-of-bounds coordinates must evaluate natively as zero aggregates."

    def test_draw_zones_output_shape(self, fake_zones, fake_frame_480p):
        """
        Drawing map layers over BGR arrays natively resolves safely enforcing shape preservation.
        """
        analytics = ZoneAnalytics(zones=fake_zones)
        output = analytics.draw_zones(fake_frame_480p)
        
        assert output.shape == (480, 640, 3), "Zone mapping visualizer fractured exact dimension limits."

    def test_draw_zones_modifies_frame(self, fake_zones, fake_white_frame):
        """
        Assures cv2.fillPoly effectively mutated native pixels rendering polygons iteratively
        upon the core image map structure guaranteeing visible markers are applied.
        """
        analytics = ZoneAnalytics(zones=fake_zones)
        output = analytics.draw_zones(fake_white_frame)
        
        assert not np.array_equal(output, fake_white_frame), "No polygons drawn! The visual frame remained unaltered."


class TestQueueDetector:
    """
    Validates thresholds, timings, estimates, and clearing logics mapping exactly
    across queue zone matrices ensuring alerts pop effectively mapping heuristics sequentially.
    """

    @pytest.fixture
    def active_queue_zone(self):
        # A mock restricted rectangular checkout queue queue array.
        return [(426, 0), (640, 0), (640, 480), (426, 480)]

    def test_no_queue_below_threshold(self, active_queue_zone):
        """
        Confirms alert markers remain explicitly False avoiding premature triggers when
        crowd numbers have not broken boundary density limits intrinsically.
        """
        detector = QueueDetector(queue_zone=active_queue_zone, density_threshold=3)
        tracks = [
            {"track_id": 1, "center": (500, 240)},
            {"track_id": 2, "center": (600, 240)}
        ]
        res = detector.update(tracks, current_frame=1)
        assert res["is_queue_alert"] is False, "Alert generated despite count being under threshold constraint."

    def test_queue_triggered_at_threshold(self, active_queue_zone):
        """
        Proves exactly equating to threshold aggregates flips alert flags logically enforcing triggering parameters.
        """
        detector = QueueDetector(queue_zone=active_queue_zone, density_threshold=3)
        tracks = [
            {"track_id": 1, "center": (500, 100)},
            {"track_id": 2, "center": (500, 200)},
            {"track_id": 3, "center": (500, 300)}
        ]
        res = detector.update(tracks, current_frame=1)
        assert res["is_queue_alert"] is True, "Threshold hit correctly but alert remained false."

    def test_queue_duration_increases(self, active_queue_zone):
        """
        Verifies duration markers increment naturally upon subsequent frames remaining within alerting constraints.
        Using exactly 100 loops against the 25.0 frame_rate defaults evaluating directly to 4.0s duration timing.
        """
        detector = QueueDetector(queue_zone=active_queue_zone, density_threshold=3, frame_rate=25.0)
        tracks = [
            {"track_id": 1, "center": (500, 100)},
            {"track_id": 2, "center": (500, 200)},
            {"track_id": 3, "center": (500, 300)}
        ]
        
        # Trigger frame
        detector.update(tracks, current_frame=0)
        
        # Run 100 duration incremental frames
        res = {}
        for f in range(1, 101):
            res = detector.update(tracks, current_frame=f)
            
        assert res["queue_duration_seconds"] == 4.0, "Queue time sequence aggregated out-of-sync."

    def test_queue_resets_when_clear(self, active_queue_zone):
        """
        Clearing numbers under limit parameters immediately neutralizes active flags mitigating ghosts alerts implicitly.
        """
        detector = QueueDetector(queue_zone=active_queue_zone, density_threshold=3)
        tracks_loaded = [{"track_id": i, "center": (500, i*100)} for i in range(1, 4)]
        
        # Exceed threshold
        res = detector.update(tracks_loaded, current_frame=1)
        assert res["is_queue_alert"] is True, "Initial trigger failed."
        
        # Subceed threshold
        tracks_cleared = [{"track_id": 1, "center": (500, 100)}]
        res2 = detector.update(tracks_cleared, current_frame=2)
        assert res2["is_queue_alert"] is False, "Empty/Reduced queue retained active trigger indefinitely."

    def test_wait_estimate_proportional(self, active_queue_zone):
        """
        The implemented basic wait heuristic logic explicitly multiplies constants dynamically natively proportional to line length capacities scaling.
        """
        detector = QueueDetector(queue_zone=active_queue_zone, density_threshold=3)
        
        t_3 = [{"track_id": i, "center": (500, 100)} for i in range(3)]
        res_3 = detector.update(t_3, current_frame=1)
        
        t_6 = [{"track_id": i, "center": (500, 100)} for i in range(6)]
        res_6 = detector.update(t_6, current_frame=2)
        
        assert res_6["wait_estimate_seconds"] > res_3["wait_estimate_seconds"], "Higher crowd occupancy estimate failed to proportionally out-scale smaller intervals."

    def test_empty_queue_zone(self, active_queue_zone, fake_empty_track_list):
        """
        Frames omitting any data traces explicitly calculate gracefully rendering Zero queues sequentially protecting mathematical logic cleanly.
        """
        detector = QueueDetector(queue_zone=active_queue_zone, density_threshold=3)
        res = detector.update(fake_empty_track_list, current_frame=1)
        
        assert res["people_in_queue"] == 0, "Native empty handling failed logic traces."
        assert res["is_queue_alert"] is False, "Empty frames caused a false sequence trigger loop naturally."
