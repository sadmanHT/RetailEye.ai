import pytest
import numpy as np
import cv2
import os
import random
from faker import Faker
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport

from api.main import app

fake = Faker()

@pytest.fixture(scope="function")
def fake_frame_480p():
    return np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)

@pytest.fixture(scope="function")
def fake_frame_720p():
    return np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)

@pytest.fixture(scope="function")
def fake_frame_1080p():
    return np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)

@pytest.fixture(scope="function")
def fake_black_frame():
    return np.zeros((480, 640, 3), dtype=np.uint8)

@pytest.fixture(scope="function")
def fake_white_frame():
    return np.ones((480, 640, 3), dtype=np.uint8) * 255

@pytest.fixture(scope="function")
def fake_corrupted_frame():
    frame = np.random.rand(480, 640, 3).astype(np.float32)
    # Inject NaN and Inf
    frame[10:20, 10:20, :] = np.nan
    frame[50:60, 50:60, :] = np.inf
    return frame

def _generate_tracks(count):
    tracks = []
    for _ in range(count):
        x1 = random.randint(0, 500)
        y1 = random.randint(0, 300)
        w = random.randint(20, 100)
        h = random.randint(50, 150)
        x2 = min(640, x1 + w)
        y2 = min(480, y1 + h)
        
        tracks.append({
            "track_id": fake.unique.random_int(min=1, max=9999),
            "bbox": [x1, y1, x2, y2],
            "confidence": round(random.uniform(0.45, 0.99), 2),
            "class_name": "person",
            "center": (x1 + w//2, y1 + h//2),
            "is_confirmed": True
        })
    return tracks

@pytest.fixture(scope="function")
def fake_track_list():
    return _generate_tracks(5)

@pytest.fixture(scope="function")
def fake_empty_track_list():
    return []

@pytest.fixture(scope="function")
def fake_crowded_track_list():
    return _generate_tracks(50)

@pytest.fixture(scope="function")
def fake_single_track():
    return _generate_tracks(1)

@pytest.fixture(scope="function")
def fake_zones():
    return {
        "entrance": [(0, 0), (213, 0), (213, 480), (0, 480)],
        "middle": [(213, 0), (426, 0), (426, 480), (213, 480)],
        "checkout": [(426, 0), (640, 0), (640, 480), (426, 480)]
    }

def _create_fake_video(path, frames_count):
    out = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*'mp4v'), 25.0, (640, 480))
    for _ in range(frames_count):
        frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        out.write(frame)
    out.release()
    return path

@pytest.fixture(scope="session")
def fake_video_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("videos") / "fake_video.mp4"
    yield _create_fake_video(path, 100)
    if path.exists():
        path.unlink()

@pytest.fixture(scope="session")
def fake_long_video_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("videos") / "fake_long_video.mp4"
    yield _create_fake_video(path, 500)
    if path.exists():
        path.unlink()

@pytest.fixture(scope="session")
def fake_tiny_video_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("videos") / "fake_tiny_video.mp4"
    yield _create_fake_video(path, 5)
    if path.exists():
        path.unlink()

@pytest.fixture(scope="session")
def fake_corrupt_video_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("videos") / "corrupt_video.mp4"
    path.write_bytes(os.urandom(1024))
    yield path
    if path.exists():
        path.unlink()

@pytest.fixture(scope="function")
def api_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
async def async_api_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
def model_path():
    return "models/weights/best_yolov8m.pt"
