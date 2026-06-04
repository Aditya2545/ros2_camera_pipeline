import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class ImageProcessor(Node):
    def __init__(self):
        super().__init__('image_processor')

        # Subscriber: receives raw frames from camera_driver
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.process,
            10
        )

        # Publisher: sends processed frames downstream
        self.publisher = self.create_publisher(Image, '/camera/image_processed', 10)

        self.bridge = CvBridge()

        # Identity camera matrix — assumes no lens distortion
        # In a real deployment you'd replace this with values from
        # cv2.calibrateCamera() using a checkerboard calibration
        self.camera_matrix = np.array([
            [600.0,   0.0, 320.0],
            [  0.0, 600.0, 240.0],
            [  0.0,   0.0,   1.0]
        ], dtype=np.float32)

        # Zero distortion coefficients (k1, k2, p1, p2, k3)
        self.dist_coeffs = np.zeros((5, 1), dtype=np.float32)

        self.get_logger().info('Image processor ready')

    def process(self, msg):
        # Convert ROS Image message → OpenCV BGR frame
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Undistort: corrects lens barrel/pincushion distortion
        # With identity matrix + zero distortion this is a no-op visually,
        # but the pipeline is correct and ready for real calibration values
        undistorted = cv2.undistort(frame, self.camera_matrix, self.dist_coeffs)

        # Resize to standard 640x480 — reduces downstream processing load
        resized = cv2.resize(undistorted, (640, 480))

        # Convert back to ROS Image message
        out_msg = self.bridge.cv2_to_imgmsg(resized, encoding='bgr8')

        # Forward the original timestamp — preserves timing through the pipeline
        out_msg.header.stamp = msg.header.stamp
        out_msg.header.frame_id = msg.header.frame_id

        self.publisher.publish(out_msg)

def main(args=None):
    rclpy.init(args=args)
    node = ImageProcessor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()