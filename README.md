# ROS TCP Endpoint

[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](LICENSE.md)
[![Version](https://img.shields.io/github/v/tag/Unity-Technologies/ROS-TCP-Endpoint)](https://github.com/Unity-Technologies/ROS-TCP-Endpoint/releases)
![ROS2](https://img.shields.io/badge/ros2-humble-brightgreen)

---

## Introduction

[ROS2](https://www.ros.org/) package used to create an endpoint to accept ROS messages sent from a Unity scene. This ROS package works in tandem with the [ROS TCP Connector](https://github.com/Unity-Technologies/ROS-TCP-Connector) Unity package.

This package is designed for **ROS2 Humble**.

### ROS2 Fork

This is a fork of the original [Unity ROS-TCP-Endpoint](https://github.com/Unity-Technologies/ROS-TCP-Endpoint) updated for ROS2 Humble compatibility. Key changes include:
- Migrated from ROS1 (rospy) to ROS2 (rclpy)
- Updated QoS settings for ROS2 publisher/subscriber model
- Converted launch files to ROS2 Python format
- Updated package structure for ament_python build system

## Installation

### Prerequisites

- ROS2 Humble installed
- Python 3.10+

### Building

1. Clone this repository into your ROS2 workspace src folder:
   ```bash
   cd ~/ros2_ws/src
   git clone https://github.com/Unity-Technologies/ROS-TCP-Endpoint.git
   ```

2. Build the package:
   ```bash
   cd ~/ros2_ws
   colcon build --packages-select ros_tcp_endpoint
   ```

3. Source the workspace:
   ```bash
   source ~/ros2_ws/install/setup.bash
   ```

## Usage

### Launch the endpoint

```bash
ros2 launch ros_tcp_endpoint endpoint_launch.py
```

### With custom parameters

```bash
ros2 launch ros_tcp_endpoint endpoint_launch.py tcp_ip:=0.0.0.0 tcp_port:=10000
```

### Run directly

```bash
ros2 run ros_tcp_endpoint default_server_endpoint
```

Instructions and examples on how to use this ROS package can be found on the [Unity Robotics Hub](https://github.com/Unity-Technologies/Unity-Robotics-Hub/blob/master/tutorials/ros_unity_integration/README.md) repository.

## Community and Feedback

The Unity Robotics projects are open-source and we encourage and welcome contributions.
If you wish to contribute, be sure to review our [contribution guidelines](CONTRIBUTING.md)
and [code of conduct](CODE_OF_CONDUCT.md).

## Support
For questions or discussions about Unity Robotics package installations or how to best set up and integrate your robotics projects, please create a new thread on the [Unity Robotics forum](https://forum.unity.com/forums/robotics.623/) and make sure to include as much detail as possible.

For feature requests, bugs, or other issues, please file a [GitHub issue](https://github.com/Unity-Technologies/ROS-TCP-Endpoint/issues) using the provided templates and the Robotics team will investigate as soon as possible.

For any other questions or feedback, connect directly with the
Robotics team at [unity-robotics@unity3d.com](mailto:unity-robotics@unity3d.com).

## License
[Apache License 2.0](LICENSE)