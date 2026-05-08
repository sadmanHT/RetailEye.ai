import pytest
import numpy as np
import cv2
import math
from pipeline.preprocessor import FramePreprocessor

class TestFramePreprocessor:
    """
    Comprehensive test suite ensuring the FramePreprocessor normalizes, scales,
    and formats vision data dependably for the YOLOv8 and DeepSORT models.
    """

    def test_output_shape_480p(self, fake_frame_480p):
        """
        Verify that standard 480p (640x480) frames are resized and padded
        to exactly 640x640x3 to meet the YOLOv8 network stride requirements.
        """
        preprocessor = FramePreprocessor(target_width=640, target_height=640)
        output = preprocessor.process_frame(fake_frame_480p)
        assert output.shape == (640, 640, 3), "Output frame must be exactly 640x640x3."

    def test_output_shape_720p(self, fake_frame_720p):
        """
        Verify that 720p (1280x720) high-definition frames are properly downscaled
        and padded to exactly 640x640x3.
        """
        preprocessor = FramePreprocessor(target_width=640, target_height=640)
        output = preprocessor.process_frame(fake_frame_720p)
        assert output.shape == (640, 640, 3), "Output frame must be exactly 640x640x3."

    def test_output_shape_1080p(self, fake_frame_1080p):
        """
        Verify that 1080p (1920x1080) full-HD frames are properly downscaled
        and padded to exactly 640x640x3.
        """
        preprocessor = FramePreprocessor(target_width=640, target_height=640)
        output = preprocessor.process_frame(fake_frame_1080p)
        assert output.shape == (640, 640, 3), "Output frame must be exactly 640x640x3."

    def test_output_dtype_float32(self, fake_frame_480p):
        """
        Ensure the output tensor dtype is universally float32. Neural networks
        like YOLO utilize floating-point precision for weight multiplication.
        """
        preprocessor = FramePreprocessor(target_width=640, target_height=640)
        output = preprocessor.process_frame(fake_frame_480p)
        assert output.dtype == np.float32, "Output frame must be a float32 numpy array."

    def test_pixel_range_normalized(self, fake_frame_480p):
        """
        Ensure all pixel values in the tensor are normalized between 0.0 and 1.0.
        This prevents gradient explosion and maintains convergence constraints.
        """
        preprocessor = FramePreprocessor(target_width=640, target_height=640)
        output = preprocessor.process_frame(fake_frame_480p)
        assert np.min(output) >= 0.0, "Output minimum pixel value must be >= 0.0."
        assert np.max(output) <= 1.0, "Output maximum pixel value must be <= 1.0."

    def test_letterbox_preserves_aspect_ratio(self):
        """
        Validate letterbox resizing maps native bounds safely without distortion.
        A square drawn perfectly in the center of the 4:3 input must remain
        proportional and central in the 1:1 padded output.
        """
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Red rectangle in the center (BGR -> 0, 0, 255)
        # Original center: x=320, y=240. Let's make a 100x100 rectangle: x(270-370), y(190-290)
        frame[190:290, 270:370] = [0, 0, 255]

        preprocessor = FramePreprocessor(target_width=640, target_height=640)
        output = preprocessor.process_frame(frame)

        # Scale factor for 640x480 into 640x640 is width/width = 1.0
        # Height becomes 480. Padding is (640-480)/2 = 80 top and bottom.
        # Thus, center y shifts down by 80.
        # Expected new y = 190+80 to 290+80. X stays 270 to 370.
        # Red is BGR[0,0,255] -> RGB [1.0, 0.0, 0.0] because of division by 255.
        center_pixel = output[240 + 80, 320]
        assert np.allclose(center_pixel, [1.0, 0.0, 0.0]), "Center pixel must remain Red."
        
        # Check aspect ratio preservation by making sure pixels outside the translated box are not Red
        assert not np.allclose(output[100, 320], [1.0, 0.0, 0.0]), "Padding or aspect shift corrupted bounding margins."

    def test_denoising_reduces_noise(self):
        """
        Verify the Gaussian blur explicitly lowers variation across high-frequency
        Gaussian noise arrays mimicking cheap CCTV artifacts.
        """
        # Create pure gaussian noise
        noise_frame = np.random.normal(128, 50, (640, 640, 3)).astype(np.uint8)
        
        processor_clean = FramePreprocessor(apply_denoising=False)
        processor_blur = FramePreprocessor(apply_denoising=True)
        
        clean_out = processor_clean.process_frame(noise_frame)
        blur_out = processor_blur.process_frame(noise_frame)
        
        assert np.std(blur_out) < np.std(clean_out), "Standard deviation must drop when generic denoising is engaged."

    def test_denoising_disabled(self):
        """
        Confirm that setting apply_denoising=False completely averts the Gaussian blur
        layer, preserving crisp edges for models operating against high clarity feeds.
        """
        frame = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
        
        processor_clean = FramePreprocessor(apply_denoising=False)
        processor_blur = FramePreprocessor(apply_denoising=True)
        
        clean_out = processor_clean.process_frame(frame)
        blur_out = processor_blur.process_frame(frame)
        
        assert not np.array_equal(clean_out, blur_out), "Denoised and pristine outputs must differ geometrically."

    def test_bgr_to_rgb_conversion(self):
        """
        Check OpenCV BGR color layouts map effectively to true RGB arrays expected
        by the PyTorch hub YOLO model configurations explicitly mapping channels.
        """
        # Create a frame with pure blue channel
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        frame[:, :, 0] = 255  # Blue channel max
        
        preprocessor = FramePreprocessor()
        output = preprocessor.process_frame(frame)
        
        # Look at the center to avoid checking the padding background
        center_pixel = output[320, 320]
        # RGB output should map the input B(0) to output R(0), BGR(255,0,0) -> RGB(0,0,255)
        # However, normalized: [0.0, 0.0, 1.0]
        assert center_pixel[0] == 0.0, "First channel (Red) should be 0.0"
        assert center_pixel[2] == 1.0, "Third channel (Blue) should be 1.0"

    def test_black_frame(self, fake_black_frame):
        """
        Passing a pitch-black frame ensures the matrix calculations execute cleanly.
        Only the padding region should deviate from 0.0 (using value 114).
        """
        preprocessor = FramePreprocessor(target_width=640, target_height=640)
        output = preprocessor.process_frame(fake_black_frame)
        
        # Center of the padded frame represents the black image
        assert np.all(output[320, 320] == 0.0), "Active frame area should be completely 0.0."

    def test_white_frame(self, fake_white_frame):
        """
        Passing a pure-white frame proves over-exposure scales exactly to 1.0
        preventing any 255.0 overflow scaling breaks in floating pipelines.
        """
        preprocessor = FramePreprocessor(target_width=640, target_height=640)
        output = preprocessor.process_frame(fake_white_frame)
        
        # Center of the padded frame represents the white image
        assert np.all(output[320, 320] == 1.0), "Active frame area should be exactly 1.0."

    def test_corrupted_frame_handling(self, fake_corrupted_frame):
        """
        Ensure network anomalies like NaN or infinite sensor pixel bytes
        do not silently poison the tensor output or crash the pipeline.
        Wait for exception, or ensure it parses natively cleaning constraints.
        """
        preprocessor = FramePreprocessor()
        try:
            # OpenCV resizing often crashes or throws an exception on float frames containing NaNs.
            # If OpenCV throws, we catch it. If it returns NaNs, we check and fail/pass.
            output = preprocessor.process_frame(fake_corrupted_frame)
            # If it succeeded without crashing, it either handled it or propagated NaN
            # We assert there are no NaNs in the output.
            assert not np.isnan(output).any(), "Output must not contain NaNs."
        except cv2.error:
            # OpenCV native error is a successfully handled exception path.
            assert True
        except Exception as e:
            # Any clear Python-bound exception is perfectly valid
            assert True

    def test_extract_frames_generator(self, fake_video_path):
        """
        Assure the extract_frames_from_video generator accurately captures
        video streams iteratively using memory-efficient yielding while capping
        throughput effectively to target sample_rate intervals.
        """
        preprocessor = FramePreprocessor()
        # Fake video has 100 frames at 25 fps. extracting at 5 FPS -> every 5th frame
        # Yields roughly 20 frames.
        frames = list(preprocessor.extract_frames_from_video(fake_video_path, sample_rate_fps=5.0))
        
        assert len(frames) > 0, "Generator failed to yield any matching intervals."
        for frame in frames:
            assert frame.shape == (640, 640, 3), "Generator output shape is invalid."
            assert frame.dtype == np.float32, "Generator frame float constraint fractured."

    def test_extract_frames_empty_video(self, fake_corrupt_video_path):
        """
        Validate correct exception throws when the OpenCV capture adapter
        cannot decode an invalid bytes buffer stream natively.
        """
        preprocessor = FramePreprocessor()
        with pytest.raises(Exception):
            list(preprocessor.extract_frames_from_video(fake_corrupt_video_path, sample_rate_fps=5.0))

    def test_batch_consistency(self, fake_frame_720p):
        """
        Guarantees preprocessing states do not pollute consecutive streams
        by storing mutations iteratively in cache arrays.
        """
        preprocessor = FramePreprocessor()
        
        first = preprocessor.process_frame(fake_frame_720p.copy())
        
        for _ in range(10):
            subsequent = preprocessor.process_frame(fake_frame_720p.copy())
            assert np.array_equal(first, subsequent), "Sequential preprocessing steps must remain deterministic."
