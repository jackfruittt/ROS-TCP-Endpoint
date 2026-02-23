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

from .communication import RosReceiver
from .client import ClientThread


class UnityService(RosReceiver):
    """
    Class to register a ROS service that's implemented in Unity.
    """

    def __init__(self, topic, service_class, tcp_server, queue_size=10):
        """

        Args:
            topic:         Service name to register
            service_class: The service class in the workspace
            tcp_server:    The TcpServer node instance
            queue_size:    Max number of entries to maintain in an outgoing queue
        """
        strippedTopic = re.sub("[^A-Za-z0-9_]+", "", topic)
        self.node_name = "{}_service".format(strippedTopic)

        self.topic = topic
        self.service_class = service_class
        self.tcp_server = tcp_server
        self.queue_size = queue_size

        # ROS2 service creation
        self.service = tcp_server.create_service(
            self.service_class,
            self.topic,
            self.send
        )

    def send(self, request, response):
        """
        Connect to TCP endpoint on client, pass along message and get reply
        Args:
            request: service request data to send outside of ROS network
            response: service response object to fill

        Returns:
            The response message
        """
        result = self.tcp_server.send_unity_service(self.topic, self.service_class, request)
        # Copy the result into the response
        if result is not None:
            for field in result.get_fields_and_field_types().keys():
                setattr(response, field, getattr(result, field))
        return response

    def unregister(self):
        """
        Unregister the service
        """
        if self.service is not None:
            self.tcp_server.destroy_service(self.service)
            self.service = None
