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

import re

from rclpy.serialization import deserialize_message
from .communication import RosSender


class RosService(RosSender):
    """
    Class to send messages to a ROS service (client).
    """

    def __init__(self, service, service_class, tcp_server):
        """
        Args:
            service:        The service name in ROS
            service_class:  The service class in the workspace
            tcp_server:     The TcpServer node instance
        """
        strippedService = re.sub("[^A-Za-z0-9_]+", "", service)
        node_name = "{}_RosService".format(strippedService)
        RosSender.__init__(self, node_name)

        self.srv_class = service_class
        self.tcp_server = tcp_server
        self.client = tcp_server.create_client(service_class, service)

    def send(self, data):
        """
        Takes in serialized message data from source outside of the ROS network,
        deserializes it into its class, calls the service with the message, and returns
        the service's response.

        Args:
            data: The already serialized message_class data coming from outside of ROS

        Returns:
            service response
        """
        # ROS2 deserialization for service request
        request = deserialize_message(data, self.srv_class.Request)

        attempt = 0

        while attempt < 3:
            if not self.client.wait_for_service(timeout_sec=1.0):
                attempt += 1
                print("Service not available. Attempt: {}".format(attempt))
                continue
                
            try:
                future = self.client.call_async(request)
                # Wait for the response
                import rclpy
                rclpy.spin_until_future_complete(self.tcp_server, future, timeout_sec=10.0)
                
                if future.result() is not None:
                    return future.result()
                else:
                    attempt += 1
                    print("Service call failed. Attempt: {}".format(attempt))
            except Exception as e:
                attempt += 1
                print("Exception Raised: {}".format(e))

        return None

    def unregister(self):
        """
        Unregister the service client
        """
        if self.client is not None:
            self.tcp_server.destroy_client(self.client)
            self.client = None
