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

import socket
import time
import threading
import struct
import json

from .client import ClientThread
from .thread_pauser import ThreadPauser
from io import BytesIO
from .zero_copy import ZeroCopyBuffer

from queue import Queue
from queue import Empty

# Hot-path import aliases
from rclpy.serialization import serialize_message   as _rclpy_serialize
from rclpy.serialization import deserialize_message as _rclpy_deserialize


class UnityTcpSender:
    """
    Sends messages to Unity.
    """

    def __init__(self, tcp_server, zero_copy_buffer_size=50*1024*1024, zero_copy_threshold=512*1024):
        self.sender_id = 1
        self.tcp_server = tcp_server

        # Each sender thread has its own queue: this is always the queue for the currently active thread.
        self.queue = None
        self.queue_lock = threading.Lock()

        # variables needed for matching up unity service requests with responses
        self.next_srv_id = 1001
        self.srv_lock = threading.Lock()
        self.services_waiting = {}
        
        # Topic ID mapping for compression
        self.topic_to_id = {}
        self.next_topic_id = 1
        self.topic_lock = threading.Lock()

        # Latest-frame slots for streaming topics. Serialization is deferred
        # so frames dropped before the sender thread runs never waste CPU.
        self._stream_slots      = {}   # topic_id (int) -> raw ROS message
        self._stream_slot_lock  = threading.Lock()
        self._stream_event      = threading.Event()
        
        # Zero-copy buffer (TODO: requires Unity-side implementation before enabling)
        self.zero_copy_buffer = ZeroCopyBuffer(buffer_size=zero_copy_buffer_size)
        self.zero_copy_buffer.ZERO_COPY_THRESHOLD = zero_copy_threshold
        self.use_zero_copy = False
    
    def enable_zero_copy(self, enable=True):
        """Enable or disable zero-copy buffer (requires Unity-side implementation)."""
        self.tcp_server.logwarn("Zero-copy not yet supported (requires Unity-side implementation)")
        return False

    def get_or_register_topic_id(self, topic):
        """Get topic ID, registering it if needed. Returns (topic_id, is_new)"""
        with self.topic_lock:
            if topic in self.topic_to_id:
                return self.topic_to_id[topic], False
            else:
                topic_id = self.next_topic_id
                self.next_topic_id += 1
                self.topic_to_id[topic] = topic_id
                return topic_id, True

    def send_unity_info(self, text):
        if self.queue is not None:
            command = SysCommand_Log()
            command.text = text
            serialized_bytes = ClientThread.serialize_command("__log", command)
            self.queue.put(serialized_bytes)

    def send_unity_warning(self, text):
        if self.queue is not None:
            command = SysCommand_Log()
            command.text = text
            serialized_bytes = ClientThread.serialize_command("__warn", command)
            self.queue.put(serialized_bytes)

    def send_unity_error(self, text):
        if self.queue is not None:
            command = SysCommand_Log()
            command.text = text
            serialized_bytes = ClientThread.serialize_command("__error", command)
            self.queue.put(serialized_bytes)

    def send_ros_service_response(self, srv_id, destination, response):
        if self.queue is not None:
            command = SysCommand_Service()
            command.srv_id = srv_id
            serialized_header = ClientThread.serialize_command("__response", command)
            serialized_message = ClientThread.serialize_message(destination, response)
            self.queue.put(b"".join([serialized_header, serialized_message]))

    def send_unity_message(self, topic, message):
        if self.queue is None:
            return

        topic_id, is_new = self.get_or_register_topic_id(topic)

        if is_new:
            # First time seeing this topic - send mapping command via the reliable queue
            topic_map = SysCommand_TopicMap(topic, topic_id)
            self.queue.put(ClientThread.serialize_command("__topic_map", topic_map))

        # Route high-frequency streaming topics through latest-frame slots.
        # Store the RAW message object - serialization happens in sender_loop only
        # for the frame that is actually transmitted (not for dropped frames).
        if any(tok in topic for tok in ('/image', '/depth', '/compressed', '/points')):
            with self._stream_slot_lock:
                self._stream_slots[topic_id] = message   # O(1) - just a reference
            self._stream_event.set()
        else:
            serialized_message = ClientThread.serialize_message_with_topic_id(topic_id, message)
            self.queue.put(serialized_message)

    def send_unity_service_request(self, topic, service_class, request):
        if self.queue is None:
            return None

        thread_pauser = ThreadPauser()
        with self.srv_lock:
            srv_id = self.next_srv_id
            self.next_srv_id += 1
            self.services_waiting[srv_id] = thread_pauser

        command = SysCommand_Service()
        command.srv_id = srv_id
        serialized_header = ClientThread.serialize_command("__request", command)
        serialized_message = ClientThread.serialize_message(topic, request)
        self.queue.put(b"".join([serialized_header, serialized_message]))

        # rclpy starts a new thread for each service request,
        # so it won't break anything if we sleep now while waiting for the response
        thread_pauser.sleep_until_resumed()

        # ROS2 deserialization (module-level import)
        response = _rclpy_deserialize(thread_pauser.result, service_class.Response)
        return response

    def send_unity_service_response(self, srv_id, data):
        thread_pauser = None
        with self.srv_lock:
            thread_pauser = self.services_waiting[srv_id]
            del self.services_waiting[srv_id]

        thread_pauser.resume_with_result(data)

    def get_registered_topic(self, topic):
        if topic in self.tcp_server.publishers_table:
            return self.tcp_server.publishers_table[topic]
        elif topic in self.tcp_server.subscribers_table:
            return self.tcp_server.subscribers_table[topic]
        elif topic in self.tcp_server.ros_services_table:
            return self.tcp_server.ros_services_table[topic]
        elif topic in self.tcp_server.unity_services_table:
            return self.tcp_server.unity_services_table[topic]
        else:
            return None

    def send_topic_list(self):
        if self.queue is not None:
            topic_list = SysCommand_TopicsResponse()
            # ROS2 way to get published topics
            topics_and_types = self.tcp_server.get_topic_names_and_types()
            topic_list.topics = [item[0] for item in topics_and_types]
            topic_list.types = [item[1][0] if item[1] else '' for item in topics_and_types]
            serialized_bytes = ClientThread.serialize_command("__topic_list", topic_list)
            self.queue.put(serialized_bytes)

    def start_sender(self, conn, halt_event):
        sender_thread = threading.Thread(
            target=self.sender_loop, args=(conn, self.sender_id, halt_event)
        )
        self.sender_id += 1

        # Exit the server thread when the main thread terminates
        sender_thread.daemon = True
        sender_thread.start()

    def sender_loop(self, conn, tid, halt_event):
        s = None
        local_queue = Queue()  # unbounded - only non-streaming messages land here
        batch_buffer = []
        pending = []  # snapshot of stream slots, used between lock release and serialization

        # send a handshake message to confirm the connection and version number
        handshake_metadata = SysCommand_Handshake_Metadata()
        handshake = SysCommand_Handshake(handshake_metadata)
        local_queue.put(ClientThread.serialize_command("__handshake", handshake))

        with self.queue_lock:
            self.queue = local_queue

        try:
            while not halt_event.is_set():
                # Wait up to 8ms for a stream or command event.
                # Reduces busy-loop wakeups vs 1ms with negligible latency impact at 30fps.
                self._stream_event.wait(timeout=0.008)
                self._stream_event.clear()

                # 1. Drain command queue first so __topic_map arrives before stream frames.
                while True:
                    try:
                        batch_buffer.append(local_queue.get_nowait())
                    except Empty:
                        break

                # 2. Drain latest-frame slots. Serialize outside the lock to reduce contention.
                with self._stream_slot_lock:
                    if self._stream_slots:
                        pending = list(self._stream_slots.items())
                        self._stream_slots.clear()

                for topic_id, raw_msg in pending:
                    try:
                        batch_buffer.append(
                            ClientThread.serialize_message_with_topic_id(topic_id, raw_msg)
                        )
                    except Exception as e:
                        self.tcp_server.logerr("serialize error topic_id={}: {}".format(topic_id, e))
                pending = []

                # 3. Single sendall regardless of batch size.
                if batch_buffer:
                    try:
                        conn.sendall(b"".join(batch_buffer))
                    except Exception as e:
                        self.tcp_server.logerr("sender_loop send error: {}".format(e))
                        break
                    finally:
                        batch_buffer.clear()

        finally:
            halt_event.set()
            with self.queue_lock:
                if self.queue is local_queue:
                    self.queue = None

    def parse_message_name(self, name):
        try:
            # Example input string: <class 'std_msgs.msg._string.Metaclass_String'>
            names = (str(type(name))).split(".")
            module_name = names[0][8:]
            class_name = names[-1].split("_")[-1][:-2]
            return "{}/{}".format(module_name, class_name)
        except (IndexError, AttributeError, ImportError) as e:
            self.tcp_server.logerr("Failed to resolve message name: {}".format(e))
            return None


class SysCommand_Log:
    def __init__(self):
        self.text = ""


class SysCommand_Service:
    def __init__(self):
        self.srv_id = 0


class SysCommand_TopicsResponse:
    def __init__(self):
        self.topics = []
        self.types = []


class SysCommand_Handshake:
    def __init__(self, metadata):
        self.version = "v0.7.0"
        self.metadata = json.dumps(metadata.__dict__)


class SysCommand_Handshake_Metadata:
    def __init__(self):
        self.protocol = "ROS2"


class SysCommand_TopicMap:
    def __init__(self, topic, topic_id):
        self.topic = topic
        self.topic_id = topic_id
