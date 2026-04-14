from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_dir = get_package_share_directory('hexapod_pkg')

    gazebo = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(pkg_dir, 'launch_sim', 'gazebo_hexapod_sim.launch.py')
        )
    )

    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=[{
            'use_sim_time': True,
            'odom_frame': 'odom',
            'map_frame': 'map',
            'base_frame': 'base_link',
            'laser_frame': 'laser_frame',
            'laser_frame': 'laser_frame',
            'scan_topic': '/lidar_scan',
            'mode': 'mapping',
            'resolution': 0.05,
            'max_laser_range': 12.0,
            'minimum_time_interval': 0.5,
            'transform_timeout': 0.2,
            'update_rate': 5.0,
        }],
        output='screen'
    )

    rosbridge = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('rosbridge_server'),
                'launch',
                'rosbridge_websocket_launch.xml'
            )
        ),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    web_video = Node(
        package='web_video_server',
        executable='web_video_server',
        name='web_video_server',
    )

    odom_publisher = Node(
        package='hexapod_pkg',
        executable='odom_publisher.py',
        name='odom_publisher',
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        odom_publisher,
        TimerAction(period=5.0, actions=[slam_node]),
        rosbridge,
        web_video,
    ])
