from ultralytics import YOLO
import cv2
import json
import time
import requests

import util
from sort.sort import *
from util import get_car, read_license_plate

import torch
print("CUDA Available:", torch.cuda.is_available())
print("GPU Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else"No GPU found")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load parking lines annotations
with open('parking_lines.json', 'r') as f:
    parking_lines = json.load(f)

# Initialize current parking lines with the first valid annotation
current_parking_lines = None
for line in parking_lines:
    if line['left_line'] is not None and line['right_line'] is not None:
        current_parking_lines = line
        break

def check_parking_violation(vehicle_bbox, frame_nmr):
    global current_parking_lines
    
    # Update current_parking_lines if a new valid annotation is found for this frame
    for line in parking_lines:
        if line['frame_id'] == frame_nmr and line['left_line'] is not None and line['right_line'] is not None:
            current_parking_lines = line
            break
    
    if current_parking_lines is None:
        return False  # No valid annotations available
        
    x1, y1, x2, y2 = vehicle_bbox
    
    # Use the current_parking_lines
    lines = [current_parking_lines['left_line'], current_parking_lines['right_line']]
    
    for line in lines:
        # Each line is [[x1, y1], [x2, y2]]
        line_x1, line_y1 = line[0]
        line_x2, line_y2 = line[1]
        
        # Check if vehicle bbox overlaps with parking line
        if not (x2 < line_x1 or x1 > line_x2 or y2 < line_y1 or y1 > line_y2):
            return True
    return False

def send_record_to_api(record):
    try:
        response = requests.post('http://localhost:8000/records/', json=record)
        if response.status_code == 200:
            print(f"Record sent successfully for frame {record['frame_nmr']}")
        else:
            print(f"Failed to send record: {response.text}")
    except Exception as e:
        print(f"Error sending record to API: {str(e)}")

results = {}
violation_frames = {}  # Track violation frames for each vehicle

mot_tracker = Sort()

# load models
vehicle_detector = YOLO('VehicleDetection.pt').to(device)
license_plate_detector = YOLO('LicensePlateDetection.pt').to(device)

print("Using Device", device)

# load video
cap = cv2.VideoCapture('./SampleVideo.mp4')

vehicles = [0]

# read frames
frame_nmr = -1
ret = True
while ret:
    frame_nmr += 1
    ret, frame = cap.read()
    if ret:
        results[frame_nmr] = {}
        # detect vehicles
        detections = vehicle_detector(frame)[0]
        detections_ = []
        for detection in detections.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = detection
            if int(class_id) in vehicles:
                detections_.append([x1, y1, x2, y2, score])

        if len(detections_) == 0:
            detections_np = np.empty((0, 5))
        else:
            detections_np = np.asarray(detections_)
            track_ids = mot_tracker.update(detections_np)

        # detect license plates
        license_plates = license_plate_detector(frame)[0]
        for license_plate in license_plates.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = license_plate

            # assign license plate to car
            xcar1, ycar1, xcar2, ycar2, car_id = get_car(license_plate, track_ids)

            if car_id != -1:
                # crop license plate
                license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]

                # process license plate
                license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

                # read license plate number
                license_plate_text, license_plate_text_score = read_license_plate(license_plate_crop_thresh)

                # Check for parking violation
                is_violating = check_parking_violation([xcar1, ycar1, xcar2, ycar2], frame_nmr)
                
                # Initialize violation tracking for new vehicles
                if car_id not in violation_frames:
                    violation_frames[car_id] = {'consecutive_frames': 0, 'warning_sent': False}
                
                if is_violating:
                    violation_frames[car_id]['consecutive_frames'] += 1
                    
                    # Print warning after 1 frame
                    if violation_frames[car_id]['consecutive_frames'] == 1 and not violation_frames[car_id]['warning_sent']:
                        print(f"Warning: Vehicle {car_id} is potentially violating!")
                        violation_frames[car_id]['warning_sent'] = True
                    
                    # Print violation confirmation after 3 consecutive frames
                    if violation_frames[car_id]['consecutive_frames'] == 3:
                        print(f"Vehicle {car_id} is confirmed violating!")
                else:
                    # Reset violation tracking when vehicle is no longer violating
                    violation_frames[car_id] = {'consecutive_frames': 0, 'warning_sent': False}

                if license_plate_text is not None:
                    # Create record for API
                    record = {
                        'frame_nmr': frame_nmr,
                        'car_id': car_id,
                        'car_bbox': f'[{xcar1} {ycar1} {xcar2} {ycar2}]',
                        'license_plate_bbox': f'[{x1} {y1} {x2} {y2}]',
                        'license_plate_bbox_score': float(score),
                        'license_number': license_plate_text,
                        'license_number_score': float(license_plate_text_score),
                        'violation_status': 'Violation' if violation_frames[car_id]['consecutive_frames'] >= 3 else 'Warning' if violation_frames[car_id]['consecutive_frames'] >= 1 else 'Correctly Parked'
                    }
                    
                    # Send record to API
                    send_record_to_api(record)

cap.release()
