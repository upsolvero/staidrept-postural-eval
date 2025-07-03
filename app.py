from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import io
import cv2
import numpy as np
import mediapipe as mp
import math
import base64
import logging
import gc
from typing import Dict, Any, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Staidrept Postural Evaluation API",
    description="API for analyzing postural angles from images",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Maximum image dimensions for processing
MAX_IMAGE_WIDTH = 1080
MAX_IMAGE_HEIGHT = 1080

def resize_image_if_needed(img: Image.Image) -> Image.Image:
    """Resize image if it's too large to prevent memory issues"""
    w, h = img.size
    if w > MAX_IMAGE_WIDTH or h > MAX_IMAGE_HEIGHT:
        # Calculate scaling factor
        scale_w = MAX_IMAGE_WIDTH / w
        scale_h = MAX_IMAGE_HEIGHT / h
        scale = min(scale_w, scale_h)
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        logger.info(f"Resizing image from {w}x{h} to {new_w}x{new_h}")
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Force garbage collection
        gc.collect()
    
    return img

def get_angle(p1: tuple, p2: tuple) -> float:
    """Calculate angle between two points"""
    try:
        x1, y1 = p1
        x2, y2 = p2
        radians = math.atan2(y2 - y1, x2 - x1)
        degrees = math.degrees(radians)
        angle = 90 - degrees
        if angle > 180:
            angle -= 360
        if angle < -180:
            angle += 360
        return round(angle, 1)
    except Exception as e:
        logger.error(f"Error calculating angle: {e}")
        return 0.0

def analyze_pose_draw(img: Image.Image) -> Image.Image:
    """Analyze pose and draw on image with error handling"""
    try:
        img_np = np.array(img)
        img_rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        # Initialize MediaPipe with error handling
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
        
        try:
            results = pose.process(img_rgb)
        except Exception as e:
            logger.error(f"MediaPipe pose processing error: {e}")
            return img
        finally:
            pose.close()
            
        draw = ImageDraw.Draw(img)
        w, h = img.size

        # Grid drawing
        num_vert_lines = 8
        num_horiz_lines = 8
        color_grid = (160, 160, 160)
        width_grid = 2
        for i in range(num_vert_lines+1):
            x = i * w // num_vert_lines
            draw.line([(x, 0), (x, h)], fill=color_grid, width=width_grid)
        for i in range(num_horiz_lines+1):
            y = i * h // num_horiz_lines
            draw.line([(0, y), (w, y)], fill=color_grid, width=width_grid)
        draw.line([(w//2, 0), (w//2, h)], fill=(0, 255, 0), width=4)

        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()

        if results.pose_landmarks:
            idxs = {
                "Umeri": (11, 12),
                "Bazin": (23, 24),
                "Genunchi": (25, 26),
                "Glezne": (27, 28),
            }
            colors = {"Umeri": (255,0,0), "Bazin": (0,128,255), "Genunchi": (0,255,128), "Glezne": (255,128,0)}
            for name, (left_idx, right_idx) in idxs.items():
                try:
                    left = results.pose_landmarks.landmark[left_idx]
                    right = results.pose_landmarks.landmark[right_idx]
                    p1 = (int(left.x * w), int(left.y * h))
                    p2 = (int(right.x * w), int(right.y * h))

                    # Reference line
                    ref_x = w // 2
                    ref_p1 = (ref_x, p1[1])
                    ref_p2 = (ref_x, p2[1])
                    draw.line([ref_p1, ref_p2], fill=(255,255,255), width=2)

                    # Actual line
                    draw.line([p1, p2], fill=colors[name], width=4)

                    # Points
                    r = 8
                    draw.ellipse([p1[0]-r, p1[1]-r, p1[0]+r, p1[1]+r], fill=colors[name])
                    draw.ellipse([p2[0]-r, p2[1]-r, p2[0]+r, p2[1]+r], fill=colors[name])

                    # Angle and text
                    angle = get_angle(p1, p2)
                    y_label = int((p1[1] + p2[1]) // 2)
                    txt = f"{abs(angle):.0f}°"
                    draw.text((ref_x + 25, y_label - 22), txt, fill=(0,0,0), font=font, stroke_width=2, stroke_fill=(255,255,255))
                except Exception as e:
                    logger.error(f"Error drawing {name}: {e}")
                    continue
        else:
            draw.text((w//2-100, 20), "Nicio postură detectată!", fill=(255,0,0), font=ImageFont.load_default())

        # Force garbage collection
        gc.collect()
        return img
        
    except Exception as e:
        logger.error(f"Error in analyze_pose_draw: {e}")
        return img

def analyze_pose_angles(img: Image.Image) -> Dict[str, Union[float, str]]:
    """Analyze pose angles with error handling"""
    try:
        img_np = np.array(img)
        img_rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
        
        angle_results = {}
        
        try:
            results = pose.process(img_rgb)
            
            if results.pose_landmarks:
                idxs = {
                    "Umeri": (11, 12),
                    "Bazin": (23, 24),
                    "Genunchi": (25, 26),
                    "Glezne": (27, 28),
                }
                for name, (left_idx, right_idx) in idxs.items():
                    try:
                        left = results.pose_landmarks.landmark[left_idx]
                        right = results.pose_landmarks.landmark[right_idx]
                        p1 = (int(left.x * img.width), int(left.y * img.height))
                        p2 = (int(right.x * img.width), int(right.y * img.height))
                        angle = abs(get_angle(p1, p2))
                        angle_results[name] = angle
                    except Exception as e:
                        logger.error(f"Error calculating angle for {name}: {e}")
                        angle_results[name] = 0.0
            else:
                angle_results["error"] = "No pose detected"
                
        except Exception as e:
            logger.error(f"MediaPipe processing error: {e}")
            angle_results["error"] = f"Processing error: {str(e)}"
        finally:
            pose.close()
            
        # Force garbage collection
        gc.collect()
        return angle_results
        
    except Exception as e:
        logger.error(f"Error in analyze_pose_angles: {e}")
        return {"error": f"Analysis error: {str(e)}"}

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)) -> JSONResponse:
    """
    Analyze uploaded image for postural angles and return processed image with angle data
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        # Check file size (10MB limit)
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=413, detail="File too large")
        
        logger.info(f"Processing image: {file.filename}")
        
        # Open and process image
        try:
            img = Image.open(io.BytesIO(contents)).convert("RGB")
        except Exception as e:
            logger.error(f"Error opening image: {e}")
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Resize if needed to prevent memory issues
        img = resize_image_if_needed(img)
        
        # Get angle results first
        angle_results = analyze_pose_angles(img)
        
        # Create processed image with pose analysis drawn
        processed_img = analyze_pose_draw(img)
        
        # Convert processed image to base64
        try:
            img_io = io.BytesIO()
            processed_img.save(img_io, 'JPEG', quality=85, optimize=True)
            img_io.seek(0)
            img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise HTTPException(status_code=500, detail="Image encoding failed")
        
        # Force garbage collection
        gc.collect()
        
        logger.info("Image processing completed successfully")
        
        # Return both image and angle results in JSON
        return JSONResponse(content={
            'image': f'data:image/jpeg;base64,{img_base64}',
            'angles': angle_results,
            'status': 'success'
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_image: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
