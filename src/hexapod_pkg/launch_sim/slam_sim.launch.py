from launch import LaunchDescription
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch.actions import EmitEvent, RegisterEventHandler
from launch_ros.events.lifecycle import ChangeState
import lifecycle_msgs.msg

def generate_launch_description():
    slam_node = LifecycleNode(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        namespace='',
        parameters=[{
            'use_sim_time': True,
            'solver_plugin': 'solver_plugins::CeresSolver',
            'ceres_linear_solver': 'SPARSE_NORMAL_CHOLESKY',
            'ceres_preconditioner': 'SCHUR_JACOBI',
            'ceres_trust_strategy': 'LEVENBERG_MARQUARDT',
            'ceres_dogleg_type': 'TRADITIONAL_DOGLEG',
            'odom_frame': 'odom',
            'map_frame': 'map',
            'base_frame': 'base_link',
            'scan_topic': '/lidar_scan',
            'mode': 'mapping',
            'resolution': 0.05,
            'max_laser_range': 12.0,
            'minimum_time_interval': 0.5,
            'transform_timeout': 0.2,
            'update_rate': 5.0,
            'stack_size_to_use': 40000000,
        }],
        remappings=[('/scan', '/lidar_scan')],
    )

    # Auto configure
    configure_event = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=lambda node: True,
            transition_id=lifecycle_msgs.msg.Transition.TRANSITION_CONFIGURE,
        )
    )

    # Auto activate after configure
    activate_handler = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=slam_node,
            goal_state='inactive',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=lambda node: True,
                        transition_id=lifecycle_msgs.msg.Transition.TRANSITION_ACTIVATE,
                    )
                )
            ],
        )
    )

    return LaunchDescription([
        slam_node,
        activate_handler,
        configure_event,
    ])
