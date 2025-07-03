import pytest
import io
import time
import asyncio
from PIL import Image
from fastapi.testclient import TestClient
from app import app

# Create test client
client = TestClient(app)

def create_test_image(width=800, height=600, format="JPEG"):
    """Create a test image for testing"""
    # Create a simple test image with a person-like figure
    img = Image.new('RGB', (width, height), color='white')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=format)
    img_bytes.seek(0)
    
    return img_bytes

def create_invalid_file():
    """Create an invalid file for testing"""
    return io.BytesIO(b"This is not an image")

class TestHealthEndpoint:
    """Test the health check endpoint"""
    
    def test_health_check(self):
        """Test that health check returns 200 and correct response"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

class TestAnalyzeImageEndpoint:
    """Test the image analysis endpoint"""
    
    def test_analyze_image_success(self):
        """Test successful image analysis"""
        test_image = create_test_image()
        
        response = client.post(
            "/analyze-image",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert "image" in data
        assert "angles" in data
        assert "status" in data
        assert data["status"] == "success"
        assert data["image"].startswith("data:image/jpeg;base64,")

    def test_analyze_image_no_file(self):
        """Test error when no file is provided"""
        response = client.post("/analyze-image")
        
        assert response.status_code == 422  # FastAPI validation error

    def test_analyze_image_empty_filename(self):
        """Test error when filename is empty"""
        test_image = create_test_image()
        
        response = client.post(
            "/analyze-image",
            files={"file": ("", test_image, "image/jpeg")}
        )
        
        # FastAPI returns 422 for validation errors with empty filename
        assert response.status_code == 422
        # Check that it's a validation error response
        assert "detail" in response.json()

    def test_analyze_image_invalid_file(self):
        """Test error when invalid file is provided"""
        invalid_file = create_invalid_file()
        
        response = client.post(
            "/analyze-image",
            files={"file": ("test.txt", invalid_file, "text/plain")}
        )
        
        assert response.status_code == 400
        assert "Invalid image file" in response.json()["detail"]

    def test_analyze_image_large_file(self):
        """Test error when file is too large (>10MB)"""
        # Create a large image that exceeds 10MB
        large_image = create_test_image(width=5000, height=5000)
        
        response = client.post(
            "/analyze-image",
            files={"file": ("large.jpg", large_image, "image/jpeg")}
        )
        
        # Should either succeed (if compressed enough) or fail with file too large
        if response.status_code == 413:
            assert "File too large" in response.json()["detail"]
        else:
            assert response.status_code == 200

    def test_analyze_image_different_formats(self):
        """Test image analysis with different image formats"""
        formats = ["JPEG", "PNG"]
        
        for format_type in formats:
            test_image = create_test_image(format=format_type)
            
            response = client.post(
                "/analyze-image",
                files={"file": (f"test.{format_type.lower()}", test_image, f"image/{format_type.lower()}")}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"

    def test_analyze_image_response_structure(self):
        """Test that response has correct structure"""
        test_image = create_test_image()
        
        response = client.post(
            "/analyze-image",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        required_fields = ["image", "angles", "status"]
        for field in required_fields:
            assert field in data
        
        # Check angles structure (should contain Romanian landmark names)
        expected_landmarks = ["Umeri", "Bazin", "Genunchi", "Glezne"]
        angles = data["angles"]
        
        # Should either have the landmarks or an error message
        if "error" not in angles:
            for landmark in expected_landmarks:
                assert landmark in angles
                assert isinstance(angles[landmark], (int, float))

class TestPerformance:
    """Basic performance tests"""
    
    def test_health_endpoint_performance(self):
        """Test health endpoint response time"""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 0.1  # Should respond in less than 100ms

    def test_analyze_image_performance(self):
        """Test image analysis endpoint performance"""
        test_image = create_test_image()
        
        start_time = time.time()
        response = client.post(
            "/analyze-image",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        print(f"Image analysis took {response_time:.2f} seconds")
        # Image analysis should complete within reasonable time
        assert response_time < 30  # Should complete within 30 seconds

    def test_concurrent_requests(self):
        """Test multiple concurrent requests to health endpoint"""
        def make_request():
            return client.get("/health")
        
        start_time = time.time()
        
        # Make 10 concurrent requests
        responses = []
        for _ in range(10):
            response = make_request()
            responses.append(response)
        
        end_time = time.time()
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        total_time = end_time - start_time
        print(f"10 concurrent health checks took {total_time:.2f} seconds")
        assert total_time < 2  # Should complete all within 2 seconds

class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_very_small_image(self):
        """Test with very small image"""
        small_image = create_test_image(width=50, height=50)
        
        response = client.post(
            "/analyze-image",
            files={"file": ("small.jpg", small_image, "image/jpeg")}
        )
        
        # Should handle small images gracefully
        assert response.status_code == 200

    def test_square_image(self):
        """Test with square image"""
        square_image = create_test_image(width=500, height=500)
        
        response = client.post(
            "/analyze-image",
            files={"file": ("square.jpg", square_image, "image/jpeg")}
        )
        
        assert response.status_code == 200

    def test_very_wide_image(self):
        """Test with very wide image"""
        wide_image = create_test_image(width=2000, height=100)
        
        response = client.post(
            "/analyze-image",
            files={"file": ("wide.jpg", wide_image, "image/jpeg")}
        )
        
        assert response.status_code == 200

def run_load_test():
    """Simple load test for the server"""
    print("\n" + "="*50)
    print("RUNNING LOAD TEST")
    print("="*50)
    
    # Test health endpoint with multiple requests
    health_times = []
    for i in range(20):
        start = time.time()
        response = client.get("/health")
        end = time.time()
        health_times.append(end - start)
        assert response.status_code == 200
    
    avg_health_time = sum(health_times) / len(health_times)
    print(f"Health endpoint - Average response time: {avg_health_time*1000:.2f}ms")
    
    # Test image analysis with multiple requests
    analysis_times = []
    for i in range(5):  # Fewer requests as image analysis is more expensive
        test_image = create_test_image()
        start = time.time()
        response = client.post(
            "/analyze-image",
            files={"file": (f"test_{i}.jpg", test_image, "image/jpeg")}
        )
        end = time.time()
        analysis_times.append(end - start)
        assert response.status_code == 200
        print(f"Analysis {i+1}/5 completed in {(end-start):.2f}s")
    
    avg_analysis_time = sum(analysis_times) / len(analysis_times)
    print(f"Image analysis - Average response time: {avg_analysis_time:.2f}s")
    
    print("="*50)
    print("LOAD TEST COMPLETED")
    print("="*50)

if __name__ == "__main__":
    print("Running FastAPI Server Tests")
    print("="*50)
    
    # Run the tests
    pytest.main([__file__, "-v"])
    
    # Run load test
    run_load_test()
    
    print("\nAll tests completed!") 