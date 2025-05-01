# gesture-based-volume-and-brightness-control

📖 Overview

A touch-free, real-time controller using your webcam. Pinch with your left hand to adjust screen brightness, and pinch with your right hand to adjust system volume. Built with Python, OpenCV, and MediaPipe, this script provides smooth, intuitive feedback and works on a standard desktop.

✨ Features

Continuous Control: Analog adjustment from 0–100% via pinch distance.

Visual Feedback: On-screen bars and percentage overlays.

Smoothing Buffer: A 5-value moving average to eliminate jitter.

Custom Mapping: Easily tune sensitivity with breakpoints.

Cross-Platform Core: OpenCV & MediaPipe support Windows, macOS, Linux (brightness & audio modules OS-specific).

🎬 Demo



🚀 Installation

Clone the repo

git clone https://github.com/yourusername/gesture-control.git
cd gesture-control

Install dependencies

pip install opencv-python mediapipe numpy screen-brightness-control pycaw comtypes

🛠 Usage

Run the script

python gesture_control.py

Controls

Left-hand pinch: Adjusts screen brightness

Right-hand pinch: Adjusts system volume

Press q to quit

⚙️ Configuration

Distance-to-% Mapping: Edit distance_points & value_points arrays in gesture_control.py to change sensitivity curves.

Update Interval: Modify update_interval (in seconds) to control how often system calls are made.

Buffers: Change deque(maxlen=5) to a different length for more/less smoothing.

🧩 Extending the Project

Discrete Gestures: Add play/pause using fist or thumbs-up with MediaPipe gesture classification.

Web Interface: Wrap in Flask to stream video and control via REST endpoints.

Mobile Port: Use MediaPipe on Android/iOS and mobile SDKs for brightness/volume.

AR/VR Integration: Embed into headsets for hands-free control in VR.

📑 Requirements

Library

Purpose

opencv-python

Webcam capture & drawing

mediapipe

Hand landmark detection

numpy

Math & interpolation

screen-brightness-control

Screen brightness API

pycaw, comtypes

Windows audio control (volume)

time, collections.deque

Timing & smoothing buffers

🤝 Contributing

Fork the repository

Create your feature branch (git checkout -b feature/YourFeature)

Commit your changes (git commit -m 'Add feature')

Push to the branch (git push origin feature/YourFeature)

Open a Pull Request
