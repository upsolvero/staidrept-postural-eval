import requests
import io
import time
from PIL import Image
import pytest

# Server configuration
BASE_URL = "http://localhost:8000"  # Change this to your server URL
# For production: BASE_URL = "https://staidrept-postural-eval.onrender.com"

def create_test_image(width=800, height=600):
    """Create a test image for testing"""
    img = Image.new('RGB', (width, height), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

@pytest.mark.integration
def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    except requests.exceptions.RequestException as e:
        print(f"Health check failed: {e}")
        pytest.skip(f"Server not running at {BASE_URL}. Start server first: uv run python app.py")

@pytest.mark.integration
def test_image_analysis():
    """Test the image analysis endpoint"""
    print("\nTesting image analysis endpoint...")
    
    try:
        # Create test image
        test_image = create_test_image()
        
        # Make request
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/analyze-image",
            files={"file": ("test.jpg", test_image, "image/jpeg")},
            timeout=60  # Give it time for image processing
        )
        end_time = time.time()
        
        print(f"Analysis status: {response.status_code}")
        print(f"Response time: {end_time - start_time:.2f} seconds")
        
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}: {response.text}"
        
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Angles found: {list(data.get('angles', {}).keys())}")
        print(f"Image data size: {len(data.get('image', ''))} characters")
        
        # Verify response structure
        assert 'status' in data, "Response missing 'status' field"
        assert 'angles' in data, "Response missing 'angles' field"
        assert 'image' in data, "Response missing 'image' field"
        assert data['status'] == 'success', f"Expected status 'success' but got '{data.get('status')}'"
            
    except requests.exceptions.RequestException as e:
        print(f"Image analysis failed: {e}")
        pytest.skip(f"Server not running at {BASE_URL}. Start server first: uv run python app.py")

@pytest.mark.integration  
def test_error_cases():
    """Test various error cases"""
    print("\nTesting error cases...")
    
    # Test no file
    try:
        response = requests.post(f"{BASE_URL}/analyze-image", timeout=10)
        print(f"No file test - Status: {response.status_code} (expected 422)")
        assert response.status_code == 422, f"Expected 422 for no file, got {response.status_code}"
    except requests.exceptions.RequestException as e:
        print(f"No file test failed: {e}")
        pytest.skip(f"Server not running at {BASE_URL}. Start server first: uv run python app.py")
    
    # Test invalid file
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-image",
            files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
            timeout=10
        )
        print(f"Invalid file test - Status: {response.status_code} (expected 400)")
        assert response.status_code == 400, f"Expected 400 for invalid file, got {response.status_code}"
        
        if response.status_code == 400:
            print(f"Error message: {response.json().get('detail')}")
            assert 'detail' in response.json(), "Error response should contain 'detail' field"
    except requests.exceptions.RequestException as e:
        print(f"Invalid file test failed: {e}")
        pytest.skip(f"Server not running at {BASE_URL}. Start server first: uv run python app.py")

def run_performance_test():
    """Run basic performance test"""
    print("\nRunning performance test...")
    
    # Test multiple health checks
    health_times = []
    for i in range(10):
        start = time.time()
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            end = time.time()
            if response.status_code == 200:
                health_times.append(end - start)
        except Exception as e:
            print(f"Health check {i+1} failed: {e}")
    
    if health_times:
        avg_time = sum(health_times) / len(health_times)
        print(f"Health endpoint average response time: {avg_time*1000:.2f}ms")
    
    # Test image analysis performance
    print("Testing image analysis performance...")
    test_image = create_test_image()
    
    start = time.time()
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-image",
            files={"file": ("perf_test.jpg", test_image, "image/jpeg")},
            timeout=60
        )
        end = time.time()
        
        if response.status_code == 200:
            print(f"Image analysis completed in {end - start:.2f} seconds")
        else:
            print(f"Image analysis failed with status {response.status_code}")
    except Exception as e:
        print(f"Performance test failed: {e}")

def check_health_endpoint():
    """Check if health endpoint is working (for main function)"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_image_analysis():
    """Check if image analysis endpoint is working (for main function)"""
    try:
        test_image = create_test_image()
        response = requests.post(
            f"{BASE_URL}/analyze-image",
            files={"file": ("test.jpg", test_image, "image/jpeg")},
            timeout=60
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def check_error_cases():
    """Check error cases (for main function)"""
    print("\nTesting error cases...")
    
    # Test no file
    try:
        response = requests.post(f"{BASE_URL}/analyze-image", timeout=10)
        print(f"No file test - Status: {response.status_code} (expected 422)")
    except Exception as e:
        print(f"No file test failed: {e}")
    
    # Test invalid file
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-image",
            files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
            timeout=10
        )
        print(f"Invalid file test - Status: {response.status_code} (expected 400)")
        if response.status_code == 400:
            print(f"Error message: {response.json().get('detail')}")
    except Exception as e:
        print(f"Invalid file test failed: {e}")

def main():
    """Run all tests"""
    print("="*60)
    print("FASTAPI LIVE SERVER TEST")
    print(f"Testing server at: {BASE_URL}")
    print("="*60)
    
    # Check if server is running
    health_ok = check_health_endpoint()
    if not health_ok:
        print("❌ Server is not responding. Make sure it's running!")
        print("\nTo start the server, run:")
        print("uv run python app.py")
        print("or")
        print("uv run uvicorn app:app --host 0.0.0.0 --port 8000")
        return
    
    print("✅ Server is running!")
    
    # Run tests
    image_ok = check_image_analysis()
    if image_ok:
        print("✅ Image analysis working!")
    else:
        print("❌ Image analysis failed!")
    
    check_error_cases()
    run_performance_test()
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Image analysis: {'✅ PASS' if image_ok else '❌ FAIL'}")
    print("="*60)

if __name__ == "__main__":
    main() 