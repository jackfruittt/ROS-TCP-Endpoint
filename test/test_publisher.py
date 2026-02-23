from unittest import mock
import sys

# Mock rclpy before importing
mock_rclpy = mock.MagicMock()
sys.modules['rclpy'] = mock_rclpy
sys.modules['rclpy.node'] = mock.MagicMock()
sys.modules['rclpy.qos'] = mock.MagicMock()
sys.modules['rclpy.serialization'] = mock.MagicMock()

from ros_tcp_endpoint.publisher import RosPublisher


def test_publisher_send():
    mock_tcp_server = mock.MagicMock()
    mock_message_class = mock.MagicMock()
    
    with mock.patch('ros_tcp_endpoint.publisher.deserialize_message') as mock_deserialize:
        mock_deserialize.return_value = mock.MagicMock()
        publisher = RosPublisher("color", mock_message_class, mock_tcp_server)
        publisher.send(b"test data")
        mock_deserialize.assert_called_once()
        publisher.pub.publish.assert_called_once()


def test_publisher_unregister():
    mock_tcp_server = mock.MagicMock()
    mock_message_class = mock.MagicMock()
    
    publisher = RosPublisher("color", mock_message_class, mock_tcp_server)
    publisher.unregister()
    mock_tcp_server.destroy_publisher.assert_called_once()


def test_publisher_with_latch():
    mock_tcp_server = mock.MagicMock()
    mock_message_class = mock.MagicMock()
    
    publisher = RosPublisher("color", mock_message_class, mock_tcp_server, latch=True)
    assert publisher.pub is not None
    mock_tcp_server.create_publisher.assert_called_once()
