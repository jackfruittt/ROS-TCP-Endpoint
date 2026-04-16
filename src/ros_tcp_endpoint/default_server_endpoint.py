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

import os
import rclpy
from rclpy.executors import MultiThreadedExecutor

from ros_tcp_endpoint import TcpServer


def main(args=None):
    rclpy.init(args=args)
    tcp_server = TcpServer('unity_endpoint')
    tcp_server.start()

    # MultiThreadedExecutor lets sensor stream callbacks (depth, colour, camera_info)
    # run concurrently. Override via ROS_TCP_EXECUTOR_THREADS env var.
    num_threads = int(os.environ.get('ROS_TCP_EXECUTOR_THREADS', '4'))
    executor = MultiThreadedExecutor(num_threads=num_threads)
    executor.add_node(tcp_server)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        tcp_server.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
