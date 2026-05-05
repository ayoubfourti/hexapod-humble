# 🦾 Hexapod Robot for Search and Rescue

> Autonomous six-legged robot designed for search and rescue operations, built with ROS2, SLAM, and AI-powered human detection.

![Hexapod Robot](photo<img width="1536" height="2048" alt="a31f4410-74f4-4812-8450-9fca33a76c88" src="https://github.com/user-attachments/assets/b69e3c7f-00a5-44d7-8872-b1bb5519ce4f" />

.jpg)

---

## 🧠 Architecture

| Component | Role |
|-----------|------|
| **Jetson Nano** | High-level processing: ROS2, SLAM, Nav2, YOLO |
| **ESP32** | Real-time motor control & servo management |
| **LiDAR** | Environment mapping & obstacle detection |
| **MPU6050 (IMU)** | Localization & orientation |
| **Camera** | Live streaming & human detection |

---

## ⚙️ Features

- **Distributed Architecture** — Jetson Nano handles AI/navigation, ESP32 handles real-time motor control
- **SLAM** — Simultaneous Localization and Mapping for autonomous exploration
- **Nav2** — Autonomous navigation and path planning
- **YOLO Detection** — Real-time human identification in rescue scenarios
- **Web Dashboard** — Real-time robot control and live camera streaming
- **Mobile App** — Remote control from smartphone

---

## 🛠️ Tech Stack

- ROS2 (Humble)
- Python / C++
- YOLO (Ultralytics)
- Nav2 + SLAM Toolbox
- ESP32 (MicroROS / Serial)
- Jetson Nano (NVIDIA)
- React (Web Dashboard)

---

## 📸 Robot

![Hexapod](photo.jpg)

---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/ayoubfourti/hexapod-humble.git
cd hexapod-humble

# Build ROS2 workspace
colcon build
source install/setup.bash

# Launch
ros2 launch hexapod_pkg hexapod.launch.py
```

---

## 👤 Author

**Ayoub Fourti** — [GitHub](https://github.com/ayoubfourti)
