from unittest import mock
import sys

# Mock rclpy before importing
mock_rclpy = mock.MagicMock()
sys.modules['rclpy'] = mock_rclpy
sys.modules['rclpy.node'] = mock.MagicMock()
sys.modules['rclpy.qos'] = mock.MagicMock()
sys.modules['rclpy.serialization'] = mock.MagicMock()

from ros_tcp_endpoint.unity_service import UnityService


def test_unity_service_creation():
    mock_tcp_server = mock.MagicMock()
    mock_service_class = mock.MagicMock()
    
    unity_service = UnityService("color", mock_service_class, mock_tcp_server)
    
    assert unity_service.node_name == "color_service"
    mock_tcp_server.create_service.assert_called_once()


def test_unity_service_send():
    mock_tcp_server = mock.MagicMock()
    mock_service_class = mock.MagicMock()
    mock_request = mock.MagicMock()
    mock_response = mock.MagicMock()
    mock_response.get_fields_and_field_types.return_value = {}
    
    mock_tcp_server.send_unity_service.return_value = mock_response
    
    unity_service = UnityService("color", mock_service_class, mock_tcp_server)
    result = unity_service.send(mock_request, mock_response)
    
    mock_tcp_server.send_unity_service.assert_called_once()
    assert result == mock_response


def test_unity_service_unregister():
    mock_tcp_server = mock.MagicMock()
    mock_service_class = mock.MagicMock()
    
    unity_service = UnityService("color", mock_service_class, mock_tcp_server)
    unity_service.unregister()
    
    mock_tcp_server.destroy_service.assert_called_once()
