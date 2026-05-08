# RetailEye AI
Real-time retail store intelligence powered by computer vision.

![Python 3.10](https://img.shields.io/badge/python-3.10-blue)
![YOLOv8](https://img.shields.io/badge/YOLO-v8-yellow)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61dafb?logo=react)
![Docker](https://img.shields.io/badge/docker-ready-2496ed?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)

---

## What It Does
* Person detection and tracking
* Zone analytics
* Dwell time analysis
* Queue detection
* Crowd heatmaps
* Automated alerts

---

## Architecture
```text
Video Input
     │
     ▼
Frame Preprocessor
     │
     ▼
YOLOv8 Detector
     │
     ▼
DeepSORT Tracker
     │
     ▼
Analytics Engine
     │
     ▼
FastAPI Backend
     │
     ▼
React Dashboard
```

---

## Model Performance
| Model | Dataset | mAP50 | mAP50-95 | Inference Speed | Training Time |
|-----------|---------|-------|----------|-----------------|---------------------|
| YOLOv8m | 14340 images | 0.679 | 0.433 | 24.8ms per image | 7.3 hours on Tesla T4 |

### Training Results
![Training Results Curve](results.png)

### Confusion Matrix
![Confusion Matrix](confusion_matrix.png)

---

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/sadmanHT/RetailEye.ai.git
   cd retaileye-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install && cd ..
   ```

3. **Place model weights**
   Download the custom trained `best_yolov8m.pt` weights from the [Releases](https://github.com/sadmanHT/RetailEye.ai/releases) section of this repository and place them into the `models/weights/` directory.

4. **Run with Docker Compose**
   ```bash
   docker-compose up --build -d
   ```

5. **Open the browser**
   Navigate to `http://localhost:3000` to view the RetailEye AI React Dashboard!

---

## Project Structure
```text
retaileye-ai/
├── api/                   # FastAPI backend endpoints and routing
├── frontend/              # React Vite application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Dashboard, Analytics, Upload
│   │   ├── hooks/         # Custom React hooks
│   │   ├── App.jsx        # Root component layout
│   └── Dockerfile         # Nginx proxy deployment configuration
├── models/
│   └── weights/           # Trained YOLO weight files
├── pipeline/              # Core ML engine
│   ├── preprocessor.py    
│   ├── detector.py        # YOLOv8 integration
│   ├── tracker.py         # DeepSORT tracking
│   └── analytics.py       # Metrics processing
├── utils/                 # Visualizers and heatmap overlays
├── Dockerfile             # Production Backend Builder
├── docker-compose.yml     # Master Full-Stack Orchestration
├── requirements.txt       # Python dependencies
└── README.md              
```

---

## Tech Stack
| Component | Technology |
|-----------------------|------------|
| Object Detection | YOLOv8 |
| Object Tracking | DeepSORT |
| Core Language | Python 3.10 |
| Backend Services | FastAPI |
| Real-time Feeds | WebSockets |
| Frontend Framework | React 18 |
| Frontend Styling | Tailwind CSS 4 |
| UI Animations | Framer Motion |
| Charts & Graphs | Recharts |
| Reverse Proxy | NGINX |
| In-memory Store | Redis (Alpine) |
| Containerization | Docker Compose |

---

## Results
The system outputs a wide array of production-ready intelligence, generating JSON analytic payloads parsing:
* **Total Tracked Headcount** - Continuous counting of unique individuals present.
* **Interactive Heatmaps** - Thermal-styled `.png` matrices mapping heavy traffic flows and dwell peaks perfectly sized to the video frame.
* **Zone Traversal Rates** - Data mapped over custom polygon boundaries breaking down how crowds navigate standard architectural layouts.
* **Live Base64 Video Feeds** - Rendered inference frames streamed directly to the frontend Dashboard utilizing low-latency WebSockets.

---

## License
MIT