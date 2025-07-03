from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import io
import cv2
import numpy as np
import mediapipe as mp
import math
import base64

app = Flask(__name__)
CORS(app)

def get_angle(p1, p2):
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

def analyze_pose_draw(img):
    img_np = np.array(img)
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(img_rgb)

    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Grid (ca înainte)
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
            "Shoulders": (11, 12),
            "ASIS": (23, 24),
            "Knees": (25, 26),
            "Feet": (27, 28),
        }
        colors = {"Shoulders": (255,0,0), "ASIS": (0,128,255), "Knees": (0,255,128), "Feet": (255,128,0)}
        for name, (left_idx, right_idx) in idxs.items():
            left = results.pose_landmarks.landmark[left_idx]
            right = results.pose_landmarks.landmark[right_idx]
            p1 = (int(left.x * w), int(left.y * h))
            p2 = (int(right.x * w), int(right.y * h))

            # Linie de referință (albă)
            ref_x = w // 2
            ref_p1 = (ref_x, p1[1])
            ref_p2 = (ref_x, p2[1])
            draw.line([ref_p1, ref_p2], fill=(255,255,255), width=2)

            # Linie actuală (colorată)
            draw.line([p1, p2], fill=colors[name], width=4)

            # Puncte
            r = 8
            draw.ellipse([p1[0]-r, p1[1]-r, p1[0]+r, p1[1]+r], fill=colors[name])
            draw.ellipse([p2[0]-r, p2[1]-r, p2[0]+r, p2[1]+r], fill=colors[name])

            # Unghi și text mare
            angle = get_angle(p1, p2)
            y_label = int((p1[1] + p2[1]) // 2)
            txt = f"{abs(angle):.0f}°"
            draw.text((ref_x + 25, y_label - 22), txt, fill=(0,0,0), font=font, stroke_width=2, stroke_fill=(255,255,255))

    else:
        draw.text((w//2-100, 20), "Nicio postură detectată!", fill=(255,0,0), font=ImageFont.load_default())

    return img

def analyze_pose_angles(img):
    img_np = np.array(img)
    img_rgb = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(img_rgb)

    angle_results = {}
    if results.pose_landmarks:
        idxs = {
            "Shoulders": (11, 12),
            "ASIS": (23, 24),
            "Knees": (25, 26),
            "Feet": (27, 28),
        }
        for name, (left_idx, right_idx) in idxs.items():
            left = results.pose_landmarks.landmark[left_idx]
            right = results.pose_landmarks.landmark[right_idx]
            p1 = (int(left.x * img.width), int(left.y * img.height))
            p2 = (int(right.x * img.width), int(right.y * img.height))
            angle = abs(get_angle(p1, p2))
            angle_results[name] = angle
    else:
        angle_results["error"] = "No pose detected"
    return angle_results

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    img = Image.open(request.files['file']).convert("RGB")
    
    # Get angle results first
    angle_results = analyze_pose_angles(img)
    
    # Create processed image with pose analysis drawn
    processed_img = analyze_pose_draw(img)
    
    # Convert processed image to base64
    img_io = io.BytesIO()
    processed_img.save(img_io, 'JPEG')
    img_io.seek(0)
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    
    # Return both image and angle results in JSON
    return jsonify({
        'image': f'data:image/jpeg;base64,{img_base64}',
        'angles': angle_results
    })

if __name__ == "__main__":
    app.run()
