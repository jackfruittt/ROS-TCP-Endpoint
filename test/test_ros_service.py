from unittest import mock
import sys

# Mock rclpy before importing
mock_rclpy = mock.MagicMock()
sys.modules['rclpy'] = mock_rclpy
sys.modules['rclpy.node'] = mock.MagicMock()
sys.modules['rclpy.qos'] = mock.MagicMock()
sys.modules['rclpy.serialization'] = mock.MagicMock()

from ros_tcp_endpoint.service import RosService


def test_service_creation():
    mock_tcp_server = mock.MagicMock()
    mock_service_class = mock.MagicMock()
    
    ros_service = RosService("test_service", mock_service_class, mock_tcp_server)
    
    mock_tcp_server.create_client.assert_called_once()
    assert ros_service.srv_class == mock_service_class


def test_service_unregister():
    mock_tcp_server = mock.MagicMock()
    mock_service_class = mock.MagicMock()
    
    ros_service = RosService("test_service", mock_service_class, mock_tcp_server)
    ros_service.unregister()
    
    mock_tcp_server.destroy_client.assert_called_once()


def test_service_send_when_service_unavailable():
    mock_tcp_server = mock.MagicMock()
    mock_service_class = mock.MagicMock()
    
    ros_service = RosService("test_service", mock_service_class, mock_tcp_server)
    ros_service.client.wait_for_service.return_value = False
    
    with mock.patch('ros_tcp_endpoint.service.deserialize_message') as mock_deserialize:
        mock_deserialize.return_value = mock.MagicMock()
        result = ros_service.send(b"test data")
        assert result is None
