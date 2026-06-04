from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='camera_pipeline',
            executable='camera_driver',
            name='camera_driver',
            output='screen'
        ),
        Node(
            package='camera_pipeline',
            executable='image_processor',
            name='image_processor',
            output='screen'
        ),
        Node(
            package='camera_pipeline',
            executable='compressed_publisher',
            name='compressed_publisher',
            output='screen'
        ),
    ])