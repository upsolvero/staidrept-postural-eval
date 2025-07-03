# Staidrept Postural Evaluation API

A FastAPI-based API for analyzing postural angles from images using MediaPipe and computer vision.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- UV (modern Python package manager)

### Installation

1. **Install UV** (if not already installed):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone and setup the project**:
   ```bash
   git clone <repository-url>
   cd staidrept-postural-eval
   
   # Install all dependencies
   uv sync
   ```

3. **Run the API**:
   ```bash
   uv run python app.py
   ```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### POST `/analyze-image`
Analyzes an uploaded image for postural angles.

**Request**: Multipart form data with image file
**Response**: JSON with processed image (base64) and angle measurements

```json
{
  "image": "data:image/jpeg;base64,...",
  "angles": {
    "Umeri": 2.1,
    "Bazin": 1.8,
    "Genunchi": 0.5,
    "Glezne": 1.2
  },
  "status": "success"
}
```

### GET `/health`
Health check endpoint.

**Response**: `{"status": "healthy"}`

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Unit tests
uv run pytest test_app.py -v

# Live server tests (requires running server)
uv run python test_live_server.py
```

## 🛠️ Development

### Adding Dependencies
```bash
# Production dependency
uv add package-name

# Development dependency
uv add --dev package-name
```

### Project Structure
```
staidrept-postural-eval/
├── pyproject.toml          # Project configuration and dependencies
├── app.py                  # FastAPI application
├── test_app.py            # Unit tests
├── test_live_server.py    # Live server tests
├── TEST_README.md         # Testing documentation
└── README.md              # This file
```

## 🔧 Configuration

The API includes:
- **CORS support** for cross-origin requests
- **File size limits** (10MB max)
- **Image resizing** to prevent memory issues
- **Comprehensive error handling**
- **Logging** for debugging and monitoring

## 📊 Features

- **Pose Detection**: Uses MediaPipe for accurate pose landmark detection
- **Angle Calculation**: Measures postural angles for shoulders, hips, knees, and ankles
- **Image Processing**: Automatic resizing and optimization
- **Romanian Labels**: Anatomical landmarks in Romanian (Umeri, Bazin, Genunchi, Glezne)
- **Visual Feedback**: Processed images with pose analysis overlay

## 🌐 WordPress Integration

This API is designed to work with WordPress websites via AJAX calls. The endpoint handles CORS properly and returns both the processed image and angle data in a single response.

## 📈 Performance

- **Modern Stack**: FastAPI + UV for optimal performance
- **Memory Management**: Automatic garbage collection and image resizing
- **Error Resilience**: Robust error handling prevents crashes
- **Concurrent Support**: Handles multiple requests efficiently

Built with modern Python tools for fast, reliable postural analysis.
