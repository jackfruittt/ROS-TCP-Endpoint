from unittest import mock
import sys

# Mock rclpy before importing
mock_rclpy = mock.MagicMock()
sys.modules['rclpy'] = mock_rclpy
sys.modules['rclpy.node'] = mock.MagicMock()
sys.modules['rclpy.qos'] = mock.MagicMock()
sys.modules['rclpy.serialization'] = mock.MagicMock()

from ros_tcp_endpoint.subscriber import RosSubscriber


def test_subscriber_send():
    mock_tcp_server = mock.MagicMock()
    subscriber = RosSubscriber("color", mock.MagicMock(), mock_tcp_server)
    assert subscriber.node_name == "color_RosSubscriber"
    subscriber.send("test data")
    mock_tcp_server.send_unity_message.assert_called_once()


def test_subscriber_unregister():
    mock_tcp_server = mock.MagicMock()
    subscriber = RosSubscriber("color", mock.MagicMock(), mock_tcp_server)
    assert subscriber.node_name == "color_RosSubscriber"
    subscriber.unregister()
    mock_tcp_server.destroy_subscription.assert_called_once()


def test_subscriber_creation():
    mock_tcp_server = mock.MagicMock()
    mock_message_class = mock.MagicMock()
    
    subscriber = RosSubscriber("test_topic", mock_message_class, mock_tcp_server, queue_size=5)
    
    mock_tcp_server.create_subscription.assert_called_once()
    assert subscriber.topic == "test_topic"
    assert subscriber.queue_size == 5
