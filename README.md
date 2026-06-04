# ROS 2 Camera Streaming Pipeline

A 3-node ROS 2 pipeline that captures live camera frames via V4L2/OpenCV, applies image processing (undistortion + resize), publishes compressed video, and streams to a remote viewer via GStreamer.

## Architecture
/dev/video0 (V4L2)
│
▼
┌─────────────────┐
│  camera_driver  │  Opens camera, publishes raw frames at 30Hz
└────────┬────────┘
│ /camera/image_raw (sensor_msgs/Image)
▼
┌─────────────────────┐
│   image_processor   │  Undistortion + resize to 640x480
└──────────┬──────────┘
│ /camera/image_processed (sensor_msgs/Image)
▼
┌──────────────────────────┐
│   compressed_publisher   │  JPEG encodes and publishes compressed stream
└────────────┬─────────────┘
│ /camera/image_compressed (sensor_msgs/CompressedImage)
▼
GStreamer Viewer

## Dependencies

- ROS 2 Humble
- OpenCV (`python3-opencv`)
- cv_bridge (`ros-humble-cv-bridge`)
- image_transport (`ros-humble-image-transport`)
- GStreamer (`gstreamer1.0-tools`, `gstreamer1.0-plugins-good`)

Install all dependencies:
```bash
sudo apt update
sudo apt install -y \
  ros-humble-cv-bridge \
  ros-humble-image-transport \
  ros-humble-compressed-image-transport \
  python3-opencv \
  v4l-utils \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-libav
```

## Build

```bash
mkdir -p ~/camera_ws/src
cd ~/camera_ws/src
git clone https://github.com/Aditya2545/ros2_camera_pipeline.git
cd ~/camera_ws
colcon build
source install/setup.bash
```

## Run

**Launch full pipeline (all 3 nodes):**
```bash
ros2 launch camera_pipeline pipeline.launch.py
```

**Verify topics are publishing:**
```bash
ros2 topic list
ros2 topic hz /camera/image_raw        # ~30 Hz
ros2 topic hz /camera/image_processed  # ~30 Hz
ros2 topic hz /camera/image_compressed # ~30 Hz
```

**Visualize in RViz2:**
```bash
rviz2
# Add → By topic → /camera/image_processed → Image
```

**Stream via GStreamer (simulates remote operator viewer):**
```bash
ros2 run image_transport republish compressed \
  --ros-args \
  -r in/compressed:=/camera/image_compressed \
  -r out:=/camera/image_for_gst
```

## Package Structure

camera_pipeline/
├── camera_pipeline/
│   ├── camera_driver.py        # V4L2 capture via OpenCV → /camera/image_raw
│   ├── image_processor.py      # Undistortion + resize → /camera/image_processed
│   └── compressed_publisher.py # JPEG encoding → /camera/image_compressed
├── launch/
│   └── pipeline.launch.py      # Launches all 3 nodes
├── package.xml
├── setup.py
└── README.md

## Nodes

| Node | Subscribes | Publishes | Description |
|------|-----------|-----------|-------------|
| `camera_driver` | — | `/camera/image_raw` | Opens `/dev/video0` via V4L2/OpenCV, publishes raw BGR frames at 30Hz |
| `image_processor` | `/camera/image_raw` | `/camera/image_processed` | Applies lens undistortion and resizes to 640×480 |
| `compressed_publisher` | `/camera/image_processed` | `/camera/image_compressed` | JPEG encodes frames into `CompressedImage` for low-bandwidth streaming |

## Hardware

Tested on:
- **Camera:** Integrated webcam via V4L2 (`/dev/video0`)
- **OS:** Ubuntu 22.04
- **ROS:** ROS 2 Humble