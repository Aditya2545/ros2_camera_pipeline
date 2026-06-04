import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class CameraDriver(Node):
    def __init__(self):
        super().__init__('camera_driver')
        
        # Publisher: sends raw frames to /camera/image_raw
        # Queue size 10 means ROS buffers up to 10 messages if subscriber is slow
        self.publisher = self.create_publisher(Image, '/camera/image_raw', 10)
        
        # CvBridge converts between OpenCV frames and ROS Image messages
        self.bridge = CvBridge()
        
        # Open the camera via V4L2 (OpenCV uses V4L2 under the hood on Linux)
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            self.get_logger().error('Could not open /dev/video0')
            return
        
        self.get_logger().info('Camera opened successfully')
        
        # Timer fires at 30hz — calls capture_frame every ~33ms
        self.timer = self.create_timer(1/30, self.capture_frame)

    def capture_frame(self):
        ret, frame = self.cap.read()
        
        if not ret:
            self.get_logger().warn('Failed to capture frame')
            return
        
        # Convert OpenCV BGR frame → ROS Image message
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        
        # Stamp with current ROS time (important for TF and synchronization)
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_frame'
        
        self.publisher.publish(msg)

    def destroy_node(self):
        # Always release the camera when the node shuts down
        if self.cap.isOpened():
            self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CameraDriver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()