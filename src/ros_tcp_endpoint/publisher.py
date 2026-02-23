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
from rclpy.qos import QoSProfile, DurabilityPolicy
from rclpy.serialization import deserialize_message
from .communication import RosSender


class RosPublisher(RosSender):
    """
    Class to publish messages to a ROS topic
    """

    def __init__(self, topic, message_class, tcp_server, queue_size=10, latch=False):
        """

        Args:
            topic:         Topic name to publish messages to
            message_class: The message class in the workspace
            tcp_server:    The TcpServer node instance
            queue_size:    Max number of entries to maintain in an outgoing queue
            latch:         Whether to use transient local durability (ROS2 equivalent of latch)
        """
        strippedTopic = re.sub("[^A-Za-z0-9_]+", "", topic)
        node_name = "{}_RosPublisher".format(strippedTopic)
        RosSender.__init__(self, node_name)
        self.msg = message_class
        self.msg_instance = message_class()
        self.tcp_server = tcp_server
        
        # Set up QoS profile with transient local durability if latch is True
        qos_profile = QoSProfile(depth=queue_size)
        if latch:
            qos_profile.durability = DurabilityPolicy.TRANSIENT_LOCAL
        
        self.pub = tcp_server.create_publisher(message_class, topic, qos_profile)

    def send(self, data):
        """
        Takes in serialized message data from source outside of the ROS network,
        deserializes it into its message class, and publishes the message to ROS topic.

        Args:
            data: The already serialized message_class data coming from outside of ROS

        Returns:
            None: Explicitly return None so behaviour can be
        """
        # ROS2 deserialization
        message = deserialize_message(data, self.msg)
        self.pub.publish(message)

        return None

    def unregister(self):
        """
        Unregister the publisher
        """
        if self.pub is not None:
            self.tcp_server.destroy_publisher(self.pub)
            self.pub = None
