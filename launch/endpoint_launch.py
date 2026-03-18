#!/usr/bin/env python3
#  Copyright 2020 Unity Technologies
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for the ROS-TCP-Endpoint."""
    
    # Declare launch arguments
    tcp_ip_arg = DeclareLaunchArgument(
        'tcp_ip',
        default_value='0.0.0.0',
        description='IP address for the TCP server'
    )
    
    tcp_port_arg = DeclareLaunchArgument(
        'tcp_port',
        default_value='10000',
        description='Port for the TCP server'
    )
    
    enable_zero_copy_arg = DeclareLaunchArgument(
        'enable_zero_copy',
        default_value='false',
        description='Enable zero-copy buffer (requires Unity-side implementation - currently disabled)'
    )
    
    zero_copy_buffer_size_arg = DeclareLaunchArgument(
        'zero_copy_buffer_size',
        default_value='52428800',  # 50MB
        description='Zero-copy buffer size in bytes (default: 50MB for multiple camera streams)'
    )
    
    zero_copy_threshold_arg = DeclareLaunchArgument(
        'zero_copy_threshold',
        default_value='524288',  # 512KB
        description='Message size threshold for using zero-copy in bytes (default: 512KB)'
    )
    
    # Create the node
    endpoint_node = Node(
        package='ros_tcp_endpoint',
        executable='default_server_endpoint',
        name='unity_endpoint',
        output='screen',
        parameters=[{
            'tcp_ip': LaunchConfiguration('tcp_ip'),
            'tcp_port': LaunchConfiguration('tcp_port'),
            'enable_zero_copy': LaunchConfiguration('enable_zero_copy'),
            'zero_copy_buffer_size': LaunchConfiguration('zero_copy_buffer_size'),
            'zero_copy_threshold': LaunchConfiguration('zero_copy_threshold'),
        }]
    )
    
    return LaunchDescription([
        tcp_ip_arg,
        tcp_port_arg,
        enable_zero_copy_arg,
        zero_copy_buffer_size_arg,
        zero_copy_threshold_arg,
        endpoint_node
    ])
