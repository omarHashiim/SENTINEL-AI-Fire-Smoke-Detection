# SENTINEL AI — Fire & Smoke Detection

An AI-powered fire and smoke detection system built using Deep Learning, YOLOv8, and Streamlit.

## Overview

SENTINEL AI is a computer vision project designed to detect fire and smoke in images and videos using a trained YOLO object detection model.

The project provides a Streamlit dashboard for running detections, viewing results, and reviewing recorded detection events.

## Features

* Fire and smoke detection using YOLO.
* Image and video analysis.
* Bounding boxes and detection results.
* Streamlit-based interactive dashboard.
* Event logging and detection reports.
* Optional Telegram alert integration, when configured.

## Tech Stack

* Python
* YOLOv8
* Ultralytics
* OpenCV
* Streamlit
* NumPy
* Pandas

## Project Structure

```text
SENTINEL-AI-Fire-Smoke-Detection/
├── app_sentinel_dashboard.py
├── requirements.txt
├── .gitignore
├── README.md
├── alerts/
│   ├── logs/
│   ├── snapshots/
│   └── processed_videos/
└── best.pt
```

*Note: The actual file structure may differ depending on your project setup.*

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/omarHashiim/SENTINEL-AI-Fire-Smoke-Detection.git
cd SENTINEL-AI-Fire-Smoke-Detection
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Model Setup

The application requires trained YOLO model weights.

Place the trained weights file named `best.pt` in the location expected by the application.

Model weights may need to be downloaded separately if they are not included in this repository.

## Run the Application

```bash
python -m streamlit run app_sentinel_dashboard.py
```

Open the local address displayed in the terminal to access the dashboard.

## Limitations

* Detection performance depends on the trained model and input quality.
* Webcam functionality may require additional implementation.
* This project is intended as an educational and demonstration system, not a replacement for certified fire alarm systems.

## Team Project

Developed as a Deep Learning team project focused on computer vision and AI-based fire and smoke detection.

## Disclaimer

This system is a prototype for educational purposes. It should not be relied upon as the sole method of fire detection or emergency protection.
