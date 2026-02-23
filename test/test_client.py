from unittest import mock
import sys

# Mock rclpy before importing
mock_rclpy = mock.MagicMock()
sys.modules['rclpy'] = mock_rclpy
sys.modules['rclpy.node'] = mock.MagicMock()
sys.modules['rclpy.qos'] = mock.MagicMock()
sys.modules['rclpy.serialization'] = mock.MagicMock()

from ros_tcp_endpoint.client import ClientThread


def create_mock_tcp_server():
    """Helper to create a mock TCP server."""
    mock_server = mock.MagicMock()
    mock_server.node_name = "test-tcp-server"
    mock_server.pending_srv_id = None
    mock_server.pending_srv_is_request = False
    mock_server.publishers_table = {}
    mock_server.ros_services_table = {}
    return mock_server


def test_client_thread_initialization():
    tcp_server = create_mock_tcp_server()
    mock_conn = mock.Mock()
    client_thread = ClientThread(mock_conn, tcp_server, "127.0.0.1", 10000)
    assert client_thread.tcp_server.node_name == "test-tcp-server"
    assert client_thread.incoming_ip == "127.0.0.1"
    assert client_thread.incoming_port == 10000


def test_recvall_should_read_bytes_exact_size():
    mock_conn = mock.Mock()
    mock_conn.recv_into.return_value = 1
    result = ClientThread.recvall(mock_conn, 8)
    assert result == b"\x00\x00\x00\x00\x00\x00\x00\x00"


@mock.patch.object(ClientThread, "recvall", return_value=b"\x01\x00\x00\x00")
def test_read_int32_should_parse_int(mock_recvall):
    mock_conn = mock.Mock()
    result = ClientThread.read_int32(mock_conn)
    mock_recvall.assert_called_once
    assert result == 1


@mock.patch.object(ClientThread, "read_int32", return_value=12)
@mock.patch.object(ClientThread, "recvall", return_value=b"Hello world!")
def test_read_string_should_decode(mock_recvall, mock_read_int):
    tcp_server = create_mock_tcp_server()
    mock_conn = mock.Mock()
    client_thread = ClientThread(mock_conn, tcp_server, "127.0.0.1", 10000)
    result = client_thread.read_string()
    mock_recvall.assert_called_once
    mock_read_int.assert_called_once
    assert result == "Hello world!"


@mock.patch.object(ClientThread, "read_string", return_value="__srv")
@mock.patch.object(ClientThread, "read_int32", return_value=12)
@mock.patch.object(ClientThread, "recvall", return_value=b"Hello world!")
def test_read_message_return_destination_data(mock_recvall, mock_read_int, mock_read_str):
    tcp_server = create_mock_tcp_server()
    mock_conn = mock.Mock()
    client_thread = ClientThread(mock_conn, tcp_server, "127.0.0.1", 10000)
    result = client_thread.read_message(mock_conn)
    assert result == ("__srv", b"Hello world!")


def test_serialize_command():
    class MockParams:
        def __init__(self):
            self.test = "value"
    
    result = ClientThread.serialize_command("__test", MockParams())
    assert b"__test" in result
    assert b"test" in result
