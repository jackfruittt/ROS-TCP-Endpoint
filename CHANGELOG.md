# Changelog

All notable changes to this repository will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased

### Upgrade Notes

This fork targets ROS2 Humble. The ROS1 (rospy) implementation from v0.7.0 has been replaced. Build with colcon, not catkin.

### Added

- `MultiThreadedExecutor` with configurable thread count via `ROS_TCP_EXECUTOR_THREADS` env var (default: 4); allows depth, colour, and camera_info DDS callbacks to run concurrently, enabling 90Hz RealSense streams to render at 60Hz in Unity without frame stalls
- Auto-detected sensor-stream QoS: topics containing `/image`, `/depth`, `/compressed`, `/camera_info`, `/points`, `/gyro`, `/accel`, `/imu` receive BEST_EFFORT reliability and queue depth of 2
- Topic ID compression: Unity negotiates a `uint16` ID per topic on first message; subsequent messages use binary format instead of string topic names (20-50 bytes saved per message)
- Latest-frame slot dropping in `UnityTcpSender`: only the most recent message per streaming topic is serialized and sent, preventing ROS executor stalls at high frame rates
- ROS2 launch description: `launch/endpoint_launch.py` with configurable `tcp_ip`, `tcp_port`, and zero-copy parameters
- QoS parameters on `RosPublisher` and `RosSubscriber`: `reliability`, `durability`, `history` kwargs
- Zero-copy buffer infrastructure in `UnityTcpSender` (disabled; requires Unity-side implementation)
- `ACTIVE_OPTIMIZATIONS.md` and `OPTIMIZATION_GUIDE.md` documenting performance changes
- Socket tuning on accepted connections: `TCP_NODELAY`, 512 KB `SO_SNDBUF`, 64 KB `SO_RCVBUF`
- `ReentrantCallbackGroup` on subscriptions to allow concurrent callbacks on the `MultiThreadedExecutor`

### Changed

- Migrated from ROS1 (rospy) to ROS2 Humble (rclpy)
- `setup.py` converted from catkin to ament/setuptools
- `TcpServer` now subclasses `rclpy.node.Node` instead of standalone class
- Serialization uses `rclpy.serialization` (CDR) instead of ROS1 `BytesIO` serialize
- `default_server_endpoint.py` uses `rclpy.init` / `rclpy.spin` / `rclpy.shutdown`
- Deferred CDR serialization: serialization moved from the ROS executor callback to the TCP sender thread

### Fixed

- Removed `rospy` import from `client.py` (was unused in ROS2 build)

## [0.7.0] - 2022-02-01

### Added

Added Sonarqube Scanner

Private ros params

Send information during hand shaking for ros and package version checks

Send service response as one queue item


## [0.6.0] - 2021-09-30

Add the [Close Stale Issues](https://github.com/marketplace/actions/close-stale-issues) action

### Upgrade Notes

### Known Issues

### Added

Support for queue_size and latch for publishers. (https://github.com/Unity-Technologies/ROS-TCP-Endpoint/issues/82)

### Changed

### Deprecated

### Removed

### Fixed

## [0.5.0] - 2021-07-15

### Upgrade Notes

Upgrade the ROS communication to support ROS2 with Unity

### Known Issues

### Added

### Changed

### Deprecated

### Removed

### Fixed

## [0.4.0] - 2021-05-27

Note: the logs only reflects the changes from version 0.3.0

### Upgrade Notes

RosConnection 2.0: maintain a single constant connection from Unity to the Endpoint. This is more efficient than opening one connection per message, and it eliminates a whole bunch of user issues caused by ROS being unable to connect to Unity due to firewalls, proxies, etc.

### Known Issues

### Added

Add a link to the Robotics forum, and add a config.yml to add a link in the Github Issues page

Add linter, unit tests, and test coverage reporting

### Changed

Improving the performance of the read_message in client.py, This is done by receiving the entire message all at once instead of reading 1024 byte chunks and stitching them together as you go.

### Deprecated

### Removed

Remove outdated handshake references

### Fixed