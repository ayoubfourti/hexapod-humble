#!/usr/bin/env python3
# flutter_real.launch.py - Lance tout pour contrôle via Flutter
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction, ExecuteProcess
from hexapod_pkg import config_topics_and_parameters as cfg

def generate_launch_description():
    package_name = "hexapod_pkg"

    # 1 - WebSocket Bridge (reçoit commandes Flutter)
    websocket_bridge = Node(
        package=package_name,
        executable="websocket_bridge.py",
        name="websocket_bridge",
        output="screen",
    )

    # 2 - DDS Cmd Talker (traduit /hl_real_cmd → /cmd_serial)
    dds_cmd_talker = Node(
        package=package_name,
        executable="dds_cmd_talker.py",
        name="dds_cmd_talker",
        output="screen",
        parameters=[{
            "cmd_robot_topic": cfg.TOPIC_CMD_REAL_ROBOT,
            "cmd_serial_topic": cfg.TOPIC_CMD_SERIAL,
            "linear_speed": 127,
            "angular_speed": 127,
            "walk_yaw_trim": -7,
        }],
    )

    # 3 - Serial Bridge (envoie vers Arduino USB)
    serial_bridge = Node(
        package=package_name,
        executable="serial_bridge.py",
        name="serial_bridge",
        output="screen",
    )

    jetson_monitor = Node(
    package=package_name,
    executable="jetson_monitor.py",
    name="jetson_monitor",
    output="screen",
    )


    # 4 - Caméra MJPEG (stream vers Flutter)
    camera_stream = ExecuteProcess(
        cmd=['python3', '/hexapod-humble/camera_stream.py'],
        output='screen',
    )

    return LaunchDescription([
        jetson_monitor,
        websocket_bridge,
        dds_cmd_talker,
        camera_stream,
        TimerAction(period=2.0, actions=[serial_bridge]),
    ])
