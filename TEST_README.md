# FastAPI Server Testing

This project uses **UV** and **pyproject.toml** for modern Python dependency management.

## 🚀 Setup with UV

### Install UV
```bash
# Install UV (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install Dependencies
```bash
# Install all dependencies including dev dependencies
uv sync

# Or install only production dependencies
uv install

# Add new dependencies
uv add package-name

# Add development dependencies
uv add --dev package-name
```

## Test Scripts

### 1. `test_app.py` - Unit Tests
Comprehensive unit tests using FastAPI's TestClient.

**Features:**
- ✅ Health endpoint testing
- ✅ Image analysis functionality testing  
- ✅ Error case validation
- ✅ Performance benchmarking
- ✅ Edge case testing
- ✅ Load testing

**Run:**
```bash
# Using UV to run tests
uv run pytest test_app.py -v

# Or run the test file directly
uv run python test_app.py
```

### 2. `test_live_server.py` - Integration Tests
Tests against a running server instance (marked with `@pytest.mark.integration`).

**Features:**
- 🌐 Tests actual HTTP requests
- ⚡ Performance monitoring
- 🔄 Error case validation
- 📊 Response time analysis

**Run with pytest (requires running server):**
```bash
# Terminal 1: Start the server
uv run python app.py

# Terminal 2: Run integration tests
uv run pytest test_live_server.py -v -m integration

# Or run all integration tests
uv run pytest -m integration
```

**Run standalone (automatic server check):**
```bash
# This will check if server is running and provide helpful instructions
uv run python test_live_server.py
```

## 🛠️ Development Workflow

### Virtual Environment
```bash
# Create virtual environment (uv handles this automatically)
uv sync

# Activate virtual environment (if needed)
# uv automatically manages the environment
```

### Run the Application
```bash
# Start the FastAPI server
uv run python app.py

# Or start with uvicorn directly
uv run uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Development Commands
```bash
# Install new dependency
uv add fastapi

# Install dev dependency
uv add --dev pytest

# Remove dependency
uv remove package-name

# Update dependencies
uv lock --upgrade

# Show dependency tree
uv tree
```

## 🔧 Project Structure

```
staidrept-postural-eval/
├── pyproject.toml          # Project configuration and dependencies
├── app.py                  # FastAPI application
├── test_app.py            # Unit tests
├── test_live_server.py    # Live server tests
├── TEST_README.md         # This file
└── README.md              # Main project README
```

## 📊 Test Coverage

- **Health Check**: API availability testing
- **Image Upload**: File handling and validation
- **Pose Analysis**: MediaPipe functionality
- **Error Handling**: Invalid files, large files, corrupted images
- **Performance**: Response time and memory usage monitoring
- **CORS**: Cross-origin request testing

## 🐛 Troubleshooting

### Common Issues:
1. **UV not found**: Install UV using the installation script above
2. **Dependencies not found**: Run `uv sync` to install all dependencies
3. **Python version**: Ensure Python 3.8+ is installed
4. **Port conflicts**: Change port in app.py if 8000 is in use

### Performance Tips:
- UV is significantly faster than pip
- Use `uv run` for one-off commands
- Use `uv sync` instead of `pip install -r requirements.txt`
- UV automatically manages virtual environments

## 📈 Benefits of UV + pyproject.toml

✅ **Faster**: 10-100x faster than pip  
✅ **Modern**: PEP 517/518 compliant  
✅ **Unified**: Single file for all project config  
✅ **Reliable**: Consistent dependency resolution  
✅ **Developer-friendly**: Better error messages and UX  

---

**Migration from requirements.txt completed!** 🎉

The old `requirements.txt` has been replaced with `pyproject.toml` for modern Python development. 