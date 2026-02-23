import queue
import socket
from unittest import mock
import sys

# Mock rclpy before importing
mock_rclpy = mock.MagicMock()
sys.modules['rclpy'] = mock_rclpy
sys.modules['rclpy.node'] = mock.MagicMock()
sys.modules['rclpy.qos'] = mock.MagicMock()
sys.modules['rclpy.serialization'] = mock.MagicMock()

import ros_tcp_endpoint
import ros_tcp_endpoint.tcp_sender
from ros_tcp_endpoint.tcp_sender import UnityTcpSender


def create_mock_tcp_server():
    """Helper to create a mock TCP server."""
    mock_server = mock.MagicMock()
    mock_server.node_name = "test-tcp-server"
    mock_server.publishers_table = {}
    mock_server.subscribers_table = {}
    mock_server.ros_services_table = {}
    mock_server.unity_services_table = {}
    return mock_server


def test_tcp_sender_constructor():
    server = create_mock_tcp_server()
    tcp_sender = UnityTcpSender(server)
    assert tcp_sender.sender_id == 1
    assert tcp_sender.time_between_halt_checks == 5
    assert tcp_sender.queue is None
    assert tcp_sender.next_srv_id == 1001
    assert tcp_sender.srv_lock is not None
    assert tcp_sender.services_waiting == {}


@mock.patch.object(ros_tcp_endpoint.client.ClientThread, "serialize_message")
def test_send_message_should_serialize_message(mock_serialize_msg):
    server = create_mock_tcp_server()
    sender = UnityTcpSender(server)
    sender.queue = queue.Queue()
    sender.send_unity_message("test topic", "test msg")
    mock_serialize_msg.assert_called_once()


@mock.patch("ros_tcp_endpoint.thread_pauser.ThreadPauser")
def test_send_unity_service_response_should_resume(mock_thread_pauser_class):
    server = create_mock_tcp_server()
    sender = UnityTcpSender(server)
    thread_pauser = mock_thread_pauser_class()
    sender.services_waiting = {"moveit": thread_pauser}
    sender.send_unity_service_response("moveit", b"test data")
    thread_pauser.resume_with_result.assert_called_once()


def test_start_sender_should_increase_sender_id():
    server = create_mock_tcp_server()
    sender = UnityTcpSender(server)
    init_sender_id = 1
    assert sender.sender_id == init_sender_id
    sender.start_sender(mock.Mock(), mock.Mock())
    assert sender.sender_id == init_sender_id + 1


def test_send_unity_error_with_queue():
    server = create_mock_tcp_server()
    sender = UnityTcpSender(server)
    sender.queue = queue.Queue()
    sender.send_unity_error("Test error")
    assert not sender.queue.empty()


def test_send_unity_info_with_queue():
    server = create_mock_tcp_server()
    sender = UnityTcpSender(server)
    sender.queue = queue.Queue()
    sender.send_unity_info("Test info")
    assert not sender.queue.empty()


def test_send_unity_warning_with_queue():
    server = create_mock_tcp_server()
    sender = UnityTcpSender(server)
    sender.queue = queue.Queue()
    sender.send_unity_warning("Test warning")
    assert not sender.queue.empty()


def test_get_registered_topic_publisher():
    server = create_mock_tcp_server()
    mock_publisher = mock.MagicMock()
    server.publishers_table = {"test_topic": mock_publisher}
    sender = UnityTcpSender(server)
    result = sender.get_registered_topic("test_topic")
    assert result == mock_publisher


def test_get_registered_topic_not_found():
    server = create_mock_tcp_server()
    sender = UnityTcpSender(server)
    result = sender.get_registered_topic("unknown_topic")
    assert result is None
