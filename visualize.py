import ast

import cv2
import numpy as np
import pandas as pd


def draw_border(img, top_left, bottom_right, color=(0, 255, 0), thickness=10, line_length_x=200, line_length_y=200):
    x1, y1 = top_left
    x2, y2 = bottom_right

    cv2.line(img, (x1, y1), (x1, y1 + line_length_y), color, thickness)  #-- top-left
    cv2.line(img, (x1, y1), (x1 + line_length_x, y1), color, thickness)

    cv2.line(img, (x1, y2), (x1, y2 - line_length_y), color, thickness)  #-- bottom-left
    cv2.line(img, (x1, y2), (x1 + line_length_x, y2), color, thickness)

    cv2.line(img, (x2, y1), (x2 - line_length_x, y1), color, thickness)  #-- top-right
    cv2.line(img, (x2, y1), (x2, y1 + line_length_y), color, thickness)

    cv2.line(img, (x2, y2), (x2, y2 - line_length_y), color, thickness)  #-- bottom-right
    cv2.line(img, (x2, y2), (x2 - line_length_x, y2), color, thickness)

    return img


results = pd.read_csv('./test_interpolated.csv')

# load video
video_path = './SampleVideo.mp4'  # Updated path to match main.py
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print(f"Error: Could not open video file {video_path}")
    exit(1)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Specify the codec
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter('./out.mp4', fourcc, fps, (width, height))

print("Processing video...")
print(f"Total frames: {int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}")

license_plate = {}
for car_id in np.unique(results['car_id']):
    max_ = np.amax(results[results['car_id'] == car_id]['license_number_score'])
    license_plate[car_id] = {'license_crop': None,
                             'license_plate_number': results[(results['car_id'] == car_id) &
                                                             (results['license_number_score'] == max_)]['license_number'].iloc[0]}
    
    frame_nmr = results[(results['car_id'] == car_id) &
                       (results['license_number_score'] == max_)]['frame_nmr'].iloc[0]
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_nmr)
    ret, frame = cap.read()
    
    if not ret or frame is None:
        print(f"Warning: Could not read frame {frame_nmr} for car {car_id}")
        continue

    x1, y1, x2, y2 = ast.literal_eval(results[(results['car_id'] == car_id) &
                                              (results['license_number_score'] == max_)]['license_plate_bbox'].iloc[0].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))

    # Ensure coordinates are within frame bounds
    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width - 1))
    y2 = max(0, min(y2, height - 1))

    if x2 <= x1 or y2 <= y1:
        print(f"Warning: Invalid bbox coordinates for car {car_id} at frame {frame_nmr}")
        continue

    license_crop = frame[y1:y2, x1:x2, :]
    if license_crop.size == 0:
        print(f"Warning: Empty license plate crop for car {car_id} at frame {frame_nmr}")
        continue
        
    license_crop = cv2.resize(license_crop, (int((x2 - x1) * 400 / (y2 - y1)), 400))

    license_plate[car_id]['license_crop'] = license_crop


frame_nmr = -1

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

# read frames
ret = True
while ret:
    ret, frame = cap.read()
    frame_nmr += 1
    if ret and frame is not None:
        df_ = results[results['frame_nmr'] == frame_nmr]
        for row_indx in range(len(df_)):
            try:
                # draw car
                car_x1, car_y1, car_x2, car_y2 = ast.literal_eval(df_.iloc[row_indx]['car_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                
                # Set color based on violation status
                violation_status = df_.iloc[row_indx]['violation_status']
                if violation_status == 'Violation':
                    car_color = (0, 0, 255)  # Red for violation
                else:
                    car_color = (0, 255, 0)  # Green for correctly parked
                    
                draw_border(frame, (int(car_x1), int(car_y1)), (int(car_x2), int(car_y2)), car_color, 25,
                            line_length_x=200, line_length_y=200)

                # draw license plate
                x1, y1, x2, y2 = ast.literal_eval(df_.iloc[row_indx]['license_plate_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 12)

                # crop license plate
                license_crop = license_plate[df_.iloc[row_indx]['car_id']]['license_crop']

                if license_crop is not None:
                    H, W, _ = license_crop.shape

                    try:
                        frame[int(car_y1) - H - 100:int(car_y1) - 100,
                              int((car_x2 + car_x1 - W) / 2):int((car_x2 + car_x1 + W) / 2), :] = license_crop

                        frame[int(car_y1) - H - 400:int(car_y1) - H - 100,
                              int((car_x2 + car_x1 - W) / 2):int((car_x2 + car_x1 + W) / 2), :] = (255, 255, 255)

                        (text_width, text_height), _ = cv2.getTextSize(
                            license_plate[df_.iloc[row_indx]['car_id']]['license_plate_number'],
                            cv2.FONT_HERSHEY_SIMPLEX,
                            4.3,
                            17)

                        cv2.putText(frame,
                                    license_plate[df_.iloc[row_indx]['car_id']]['license_plate_number'],
                                    (int((car_x2 + car_x1 - text_width) / 2), int(car_y1 - H - 250 + (text_height / 2))),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    4.3,
                                    (0, 0, 0),
                                    17)
                        
                        # Add violation status text
                        (violation_width, violation_height), _ = cv2.getTextSize(
                            violation_status,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            2.0,
                            8)
                        
                        cv2.putText(frame,
                                   violation_status,
                                   (int((car_x2 + car_x1 - violation_width) / 2), int(car_y1 - H - 350 + (violation_height / 2))),
                                   cv2.FONT_HERSHEY_SIMPLEX,
                                   2.0,
                                   car_color,
                                   8)

                    except Exception as e:
                        print(f"Warning: Error drawing license plate for car {df_.iloc[row_indx]['car_id']} at frame {frame_nmr}: {str(e)}")
                        continue

            except Exception as e:
                print(f"Warning: Error processing frame {frame_nmr}: {str(e)}")
                continue

        out.write(frame)
        if frame_nmr % 10 == 0:  # Print progress every 10 frames
            print(f"Processed frame {frame_nmr}")

out.release()
cap.release()
print("Video processing complete. Output saved as 'out.mp4'")
