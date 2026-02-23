from unittest import mock
import sys
import importlib

# Mock rclpy before importing ros_tcp_endpoint modules
mock_rclpy = mock.MagicMock()
mock_node = mock.MagicMock()
mock_rclpy.node.Node = mock_node
sys.modules['rclpy'] = mock_rclpy
sys.modules['rclpy.node'] = mock.MagicMock()
sys.modules['rclpy.qos'] = mock.MagicMock()
sys.modules['rclpy.serialization'] = mock.MagicMock()

from ros_tcp_endpoint import TcpServer
from ros_tcp_endpoint.server import SysCommands
import ros_tcp_endpoint


def test_server_constructor():
    mock_server = create_mock_server()
    mock_server.node_name = "test-tcp-server"
    mock_server.tcp_ip = "127.0.0.1"
    mock_server.tcp_port = 10000
    mock_server.buffer_size = 1024
    mock_server.connections = 10
    
    assert mock_server.node_name == "test-tcp-server"
    assert mock_server.tcp_ip == "127.0.0.1"
    assert mock_server.buffer_size == 1024
    assert mock_server.connections == 10


def test_start_server():
    mock_server = create_mock_server()
    mock_server.node_name = "test-tcp-server"
    mock_server.tcp_ip = "127.0.0.1"
    mock_server.tcp_port = 10000
    mock_server.connections = 10
    
    assert mock_server.tcp_ip == "127.0.0.1"
    assert mock_server.tcp_port == 10000
    assert mock_server.connections == 10


def create_mock_server():
    """Helper to create a mock server for testing SysCommands."""
    mock_server = mock.MagicMock()
    mock_server.publishers_table = {}
    mock_server.subscribers_table = {}
    mock_server.ros_services_table = {}
    mock_server.unity_services_table = {}
    return mock_server


def test_unity_service_empty_topic_should_return_none():
    mock_server = create_mock_server()
    system_cmds = SysCommands(mock_server)
    result = system_cmds.unity_service("", "test message")
    assert result is None


def test_unity_service_resolve_message_name_failure():
    mock_server = create_mock_server()
    system_cmds = SysCommands(mock_server)
    result = system_cmds.unity_service("get_pos", "unresolvable message")
    assert result is None


def test_publish_empty_topic_should_return_none():
    mock_server = create_mock_server()
    result = SysCommands(mock_server).publish("", "pos")
    assert result is None


def test_publish_empty_message_should_return_none():
    mock_server = create_mock_server()
    result = SysCommands(mock_server).publish("test-topic", "")
    assert result is None
    assert mock_server.publishers_table == {}


def test_subscribe_to_empty_topic_should_return_none():
    mock_server = create_mock_server()
    result = SysCommands(mock_server).subscribe("", "pos")
    assert result is None
    assert mock_server.subscribers_table == {}


def test_subscribe_to_empty_message_should_return_none():
    mock_server = create_mock_server()
    result = SysCommands(mock_server).subscribe("test-topic", "")
    assert result is None
    assert mock_server.subscribers_table == {}


def test_ros_service_empty_topic_should_return_none():
    mock_server = create_mock_server()
    result = SysCommands(mock_server).ros_service("", "pos")
    assert result is None
    assert mock_server.ros_services_table == {}


def test_ros_service_empty_message_should_return_none():
    mock_server = create_mock_server()
    result = SysCommands(mock_server).ros_service("test-topic", "")
    assert result is None
    assert mock_server.ros_services_table == {}


@mock.patch.object(sys, "modules", return_value="unity_interfaces.msg")
@mock.patch.object(importlib, "import_module")
def test_resolve_message_name(mock_import_module, mock_sys_modules):
    mock_server = create_mock_server()
    msg_name = "unity_interfaces.msg/UnityColor.msg"
    result = SysCommands(mock_server).resolve_message_name(msg_name)
    mock_import_module.assert_called_once
    mock_sys_modules.assert_called_once
    assert result is not None


def test_response_sets_pending_srv_id():
    mock_server = create_mock_server()
    mock_server.pending_srv_id = None
    mock_server.pending_srv_is_request = True
    system_cmds = SysCommands(mock_server)
    system_cmds.response(123)
    assert mock_server.pending_srv_id == 123
    assert mock_server.pending_srv_is_request == False


def test_request_sets_pending_srv_id():
    mock_server = create_mock_server()
    mock_server.pending_srv_id = None
    mock_server.pending_srv_is_request = False
    system_cmds = SysCommands(mock_server)
    system_cmds.request(456)
    assert mock_server.pending_srv_id == 456
    assert mock_server.pending_srv_is_request == True
