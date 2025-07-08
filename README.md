# Smart Parking Violation Detection and Notification System

A computer vision-based system designed to detect and notify parking violations in real-time. This end-to-end AI solution integrates deep learning, OCR, and tracking algorithms with a full-stack web interface.

## Overview

This project automates the detection of improperly parked vehicles in designated parking zones using AI. The system detects vehicles and license plates, determines whether they are parked correctly, and displays the results on a monitoring dashboard.

## Technologies Used

- **YOLOv8** – Custom-trained models for Vehicle Detection and License Plate Detection (`VehicleDetection.pt`, `LicensePlateDetection.pt`)
- **EasyOCR** – License plate character recognition
- **SORT** – Tracking algorithm to assign vehicle IDs across frames
- **CVAT + JSON** – Manual parking line annotations (`parking_lines.json`)
- **FastAPI** – Backend API (`backend/main.py`)
- **SQLite** – Lightweight local database (`parking_records.db`)
- **Frontend** – HTML, CSS, and JavaScript interface (`ParkSafe_AI_FrontEnd/`)

## Project Structure

```
smart-parking-violation/
├── LICENSE
├── VehicleDetection.pt
├── LicensePlateDetection.pt
├── SampleVideo.mp4
├── parking_lines.json
├── add_missing_data.py
├── main.py                   # Violation detection entry point
├── serve_frontend.py        # Hosts frontend for local viewing
├── util.py, visualize.py    # Supporting scripts
├── requirements.txt
├── backend/
│   ├── main.py              # FastAPI backend
│   └── parking_records.db   # SQLite database
└── ParkSafe_AI_FrontEnd/
    ├── *.html               # Web dashboard pages
    ├── *.css, *.js          # Styles and scripts
    ├── *.png, *.jpg         # UI images and icons
```

## Violation Logic

1. Vehicles and plates are detected using YOLOv8.
2. License numbers are extracted via EasyOCR.
3. SORT assigns consistent vehicle IDs.
4. Manually annotated parking lines are checked for overlaps with vehicle bounding boxes.
5. If overlap is found, it's flagged as a violation.
6. Results are shown on a web dashboard in real-time.

## Running the Project

1. Clone the repository:
```bash
git clone https://github.com/mamoonzaheer/smart-parking-violation-detection.git
cd smart-parking-violation-detection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run backend server:
```bash
cd backend
uvicorn main:app --reload
```

4. Serve frontend locally:
```bash
cd ..
python serve_frontend.py
```

5. Visit the dashboard:
```
http://localhost:8000 or http://127.0.0.1:5500/ParkSafe_AI_FrontEnd/index.html
```

## 🧠 Features

- Real-time vehicle and license plate detection
- Visual violation alerts on the dashboard
- Tracking via SORT with license plate association
- Local SQLite logging of all violations
- Clean UI with login, camera view, analytics, and uploads page

## 📌 Future Enhancements

- Cloud deployment with live camera integration
- Role-based access for security/admin personnel
- Notification system (SMS/Email)
- Detailed analytics and reporting features

## 📧 Contact

**Mamoon Zaheer**  
📧 mamoonzaheer999@gmail.com  
🔗 [GitHub](https://github.com/mamoonzaheer)