import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node, SetParameter
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    params_file = LaunchConfiguration('params_file')
    map_yaml_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

    # デフォルトのマップファイルを指定
    default_map_path = os.path.join(get_package_share_directory('localize_2dlidar'), 'map', 'field_map.yaml')
    # オドメトリを読み取るlaunchファイルを指定
    odom_launch_file = os.path.join(get_package_share_directory('localize_2dlidar'), 'launch', 'localize_2dlidar.launch.py')
    declare_map_yaml = DeclareLaunchArgument(
        'map',
        default_value=default_map_path,
        description='Full path to map yaml file to load')
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation (Gazebo) clock if true')
    declare_params_file = DeclareLaunchArgument(
        'params_file',
        default_value=[
            TextSubstitution(text=os.path.join(
                get_package_share_directory('emcl2'), 'config', '')),
            TextSubstitution(text='emcl2.param.yaml')],
        description='emcl2 param file path')

    lifecycle_nodes = ['map_server']

    launch_node = GroupAction(
        actions=[
            SetParameter('use_sim_time', use_sim_time),
            Node(
                package='nav2_map_server',
                executable='map_server',
                name='map_server',
                parameters=[{'yaml_filename': map_yaml_file}],
                output='screen'),
            Node(
                name='emcl2',
                package='emcl2',
                executable='emcl2_node',
                parameters=[params_file],
                remappings=[('scan', 'ld06_fixed')],
                output='screen'),
            Node(
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_localization',
                output='screen',
                parameters=[{'autostart': True},
                            {'node_names': lifecycle_nodes}])
        ]
    )

    include_odom_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(odom_launch_file)
    )

    ld = LaunchDescription()
    ld.add_action(declare_map_yaml)
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_params_file)

    ld.add_action(launch_node)

    ld.add_action(include_odom_launch)
    return ld
