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
    
    # Create the node
    endpoint_node = Node(
        package='ros_tcp_endpoint',
        executable='default_server_endpoint',
        name='unity_endpoint',
        output='screen',
        parameters=[{
            'tcp_ip': LaunchConfiguration('tcp_ip'),
            'tcp_port': LaunchConfiguration('tcp_port'),
        }]
    )
    
    return LaunchDescription([
        tcp_ip_arg,
        tcp_port_arg,
        endpoint_node
    ])
