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

from .communication import RosReceiver
from .client import ClientThread


class RosSubscriber(RosReceiver):
    """
    Subscribes to ROS topics and forwards messages to external clients.
    """

    def __init__(self, topic, message_class, tcp_server, queue_size=10, 
                 qos_profile=None, reliability="reliable", durability="volatile", history="keep_last"):
        """
        Args:
            topic:         Topic name to subscribe to
            message_class: Message class for deserialisation
            tcp_server:    TcpServer node instance
            queue_size:    Max messages to buffer
            qos_profile:   Optional QoSProfile (overrides other QoS params)
            reliability:   "reliable" or "best_effort"
            durability:    "volatile" or "transient_local"
            history:       "keep_last" or "keep_all"
        """
        strippedTopic = re.sub("[^A-Za-z0-9_]+", "", topic)
        self.node_name = "{}_RosSubscriber".format(strippedTopic)
        RosReceiver.__init__(self, self.node_name)
        self.topic = topic
        self.msg = message_class
        self.tcp_server = tcp_server
        self.queue_size = queue_size

        # Configure QoS profile for optimal publisher-subscriber compatibility
        if qos_profile is None:
            qos_profile = QoSProfile(depth=queue_size)
            
            # Set reliability policy - critical for matching publisher QoS
            if reliability.lower() == "best_effort":
                qos_profile.reliability = ReliabilityPolicy.BEST_EFFORT
            else:
                qos_profile.reliability = ReliabilityPolicy.RELIABLE
            
            # Set durability policy - determines late-joiner behaviour
            if durability.lower() == "transient_local":
                qos_profile.durability = DurabilityPolicy.TRANSIENT_LOCAL
            else:
                qos_profile.durability = DurabilityPolicy.VOLATILE
            
            # Set history policy - affects message buffering behaviour
            if history.lower() == "keep_all":
                qos_profile.history = HistoryPolicy.KEEP_ALL
            else:
                qos_profile.history = HistoryPolicy.KEEP_LAST

        # Initialise ROS2 subscription with configured QoS
        self.sub = tcp_server.create_subscription(
            self.msg,
            self.topic,
            self.send,
            qos_profile
        )

    def send(self, data):
        """
        Forward ROS message to TCP client.
        
        Args:
            data: Message instance from ROS2

        Returns:
            self.msg: Message class type
        """
        self.tcp_server.send_unity_message(self.topic, data)
        return self.msg

    def unregister(self):
        """
        Destroy the ROS2 subscription.
        """
        if self.sub is not None:
            self.tcp_server.destroy_subscription(self.sub)
            self.sub = None
