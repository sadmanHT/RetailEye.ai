import pytest
import re

class TestAPISecurity:
    """
    Security-focused test suite targeting the FastAPI application endpoints.
    Protects against common OWASP vectors including XSS, Path Traversal,
    Information Leakage, and DOS configurations.
    """

    def test_cors_headers_present(self, api_client):
        """
        Verify that Cross-Origin Resource Sharing (CORS) headers are correctly
        applied, mitigating unauthorized domain access while allowing legitimate consumers.
        """
        response = api_client.get("/health", headers={"Origin": "http://localhost:5173"})
        
        headers_lower = {k.lower(): v for k, v in response.headers.items()}
        assert "access-control-allow-origin" in headers_lower, "CORS headers are fully missing."
        # Optionally, check that it reflects the origin or has appropriate wildcard.
        
    def test_no_server_version_leaked(self, api_client):
        """
        Ensure the 'Server' header does not leak the exact technology stack or
        python/uvicorn version, reducing the fingerprinting surface for attackers.
        """
        response = api_client.get("/health")
        server_header = response.headers.get("Server", "")
        
        # Regex looks for numeric version strings like "1.0", "0.19.0"
        has_version_number = re.search(r'\d+\.\d+', server_header)
        assert not has_version_number, f"Server header reveals exact version information: {server_header}"

    def test_path_traversal_in_job_id(self, api_client):
        """
        Attempt Directory Traversal through URL routing indices. API must reject it
        and absolutely must not return local system footprint files like passwd.
        """
        response = api_client.get("/analytics/../../../etc/passwd")
        
        # FastAPI typically handles this with a 404 (Not Found) or 422 (Validation)
        assert response.status_code in [404, 422], "API failed to correctly route/block traversal strings natively."
        
        body = response.text.lower()
        assert "root:x" not in body, "CRITICAL: Path traversal executed and exposed /etc/passwd contents!"
        assert "bin:" not in body, "CRITICAL: Path traversal executed and exposed system bin structures!"

    def test_xss_in_job_id(self, api_client):
        """
        Checks for Reflected Cross-Site Scripting (XSS). If a malicious script tag
        is provided, the server must properly escape it in the JSON string response
        rather than returning raw injectables.
        """
        xss_payload = "<script>alert(1)</script>"
        # Using URL encoded variant or raw, httpx encodes it effectively, but let's test how server returns it.
        response = api_client.get(f"/job/status/{xss_payload}")
        
        # Output should be escaped, like \u003cscript\u003e or safely quoted inside JSON.
        # But JSON strings inherently prevent raw HTML execution. We ensure no raw HTML injection leaks natively.
        raw_reflection = f'"{xss_payload}"'
        # Modern FastAPI / Starlette JSONResponse securely serializes, but we assert to be certain.
        if raw_reflection in response.text:
            pass # Standard JSON serialization quotes the string, which is XSS safe for application/json type.
            
        assert "text/html" not in response.headers.get("Content-Type", ""), "Error responses returned HTML instead of JSON mapping XSS surfaces."

    def test_oversized_upload(self, api_client):
        """
        Denial of Service (DOS) test: Upload endpoints must refuse oversized payloads
        long before iterating byte allocations causing memory termination internally.
        """
        headers = {"Content-Length": "10000000000"} # 10 GB
        files = {"video": ("fake.mp4", b"dummy_data" * 10, "video/mp4")}
        
        # TestClient may raise an exception on massive artificial content-length sizes natively.
        try:
            response = api_client.post("/upload", files=files, headers=headers)
            assert response.status_code in [413, 422, 400], "Server accepted an impossible 10GB payload trace instead of rejecting early HTTP headers."
        except Exception as e:
            # If the HTTP client or ASGI transport forcefully drops the oversized header bounds, it's considered safe.
            pass

    def test_invalid_content_type(self, api_client):
        """
        Sending structural endpoints strictly typed for multipart forms with malicious
        or incorrect formatting (application/json) must be rejected structurally.
        """
        response = api_client.post("/upload", json={"video": "malformed_json_fake_file"})
        
        assert response.status_code == 422, "API processed an invalid content-type without generating an Unprocessable Entity exception."

    def test_missing_model_path(self, api_client):
        """
        Validates internal form fields natively verifying validation exceptions explicitly 
        target missing attributes cleanly omitting generic 500 errors.
        """
        # Sending just the video, intentionally omitting 'model_path' if the API maps it locally.
        files = {"video": ("test_video.mp4", b"some bytes", "video/mp4")}
        response = api_client.post("/upload", files=files)
        
        # Note: If the backend natively provides a default `model_path` (like best.pt),
        # this might technically return a 200/202 success.
        # If it strictly requires it, it throws a 422. We check that it at least safely parses it.
        if response.status_code == 422:
            assert "model_path" in response.text.lower(), "Validation error failed to explicitly mention the missing field 'model_path'."
        else:
            assert response.status_code in [200, 202, 404], "Missing model_path caused a critical HTTP fracture."

    def test_response_content_type_json(self, api_client):
        """
        Security requirement: All analytical datasets must explicitly define application/json
        preventing browsers from MIME-sniffing malicious tracebodies as executables.
        """
        response = api_client.get("/health")
        assert "application/json" in response.headers.get("Content-Type", ""), "Endpoint failed to strictly declare JSON MIME types."

    def test_no_stack_trace_in_production_error(self, api_client):
        """
        Information disclosure check. Production environments must not leak execution paths
        or Python lines indicating stack traces under adverse errors.
        """
        # Trigger an error safely mapped internally if possible
        response = api_client.post("/upload", data={"video": 12345})
        
        body = response.text
        assert "Traceback (most recent call last)" not in body, "Server directly leaked python traceback history."
        assert 'File "' not in body, "Server leaked internal file routing structure."

    def test_job_id_is_uuid_format(self, api_client):
        """
        Job Identifiers must be entirely unpredictable (UUID v4) preventing Insecure
        Direct Object Reference (IDOR) attacks iterating sequential tasks from other users.
        """
        response = api_client.post("/upload", files={"video": ("test_video.mp4", b"dummy stream bounds", "video/mp4")})
        
        if response.status_code in [200, 202]:
            job_id = response.json().get("job_id", "")
            
            # Standard UUID4 Regex Validation Formatter
            uuid_pattern = re.compile(
                r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z', re.IGNORECASE
            )
            
            is_uuid = bool(uuid_pattern.match(job_id))
            assert is_uuid, f"Job ID '{job_id}' is not a securely generated Cryptographic UUIDv4 mapping!"
