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
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from rclpy.serialization import deserialize_message
from .communication import RosSender


class RosPublisher(RosSender):
    """
    Publishes messages to ROS topics from external clients.
    """

    def __init__(self, topic, message_class, tcp_server, queue_size=10, latch=False,
                 qos_profile=None, reliability="reliable", history="keep_last"):
        """
        Args:
            topic:         Topic name to publish to
            message_class: Message class for serialisation
            tcp_server:    TcpServer node instance
            queue_size:    Max messages to buffer
            latch:         Use transient local durability for late joiners
            qos_profile:   Optional QoSProfile (overrides other QoS params)
            reliability:   "reliable" or "best_effort"
            history:       "keep_last" or "keep_all"
        """
        strippedTopic = re.sub("[^A-Za-z0-9_]+", "", topic)
        node_name = "{}_RosPublisher".format(strippedTopic)
        RosSender.__init__(self, node_name)
        self.msg = message_class
        self.msg_instance = message_class()
        self.tcp_server = tcp_server
        
        if qos_profile is None:
            qos_profile = QoSProfile(depth=queue_size)
            
            if reliability.lower() == "best_effort":
                qos_profile.reliability = ReliabilityPolicy.BEST_EFFORT
            else:
                qos_profile.reliability = ReliabilityPolicy.RELIABLE
            
            if latch:
                qos_profile.durability = DurabilityPolicy.TRANSIENT_LOCAL
            else:
                qos_profile.durability = DurabilityPolicy.VOLATILE
            
            if history.lower() == "keep_all":
                qos_profile.history = HistoryPolicy.KEEP_ALL
            else:
                qos_profile.history = HistoryPolicy.KEEP_LAST
        
        self.pub = tcp_server.create_publisher(message_class, topic, qos_profile)

    def send(self, data):
        """
        Deserialise and publish message to ROS2.

        Args:
            data: Serialised message bytes from external client

        Returns:
            None
        """
        message = deserialize_message(data, self.msg)
        self.pub.publish(message)

        return None

    def unregister(self):
        """
        Destroy the ROS2 publisher.
        """
        if self.pub is not None:
            self.tcp_server.destroy_publisher(self.pub)
            self.pub = None
