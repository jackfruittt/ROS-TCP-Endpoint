from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'ros_tcp_endpoint'

setup(
    name=package_name,
    version='0.7.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Unity Robotics',
    maintainer_email='unity-robotics@unity3d.com',
    description='Acts as the bridge between Unity messages sent via TCP and ROS2 messages.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'default_server_endpoint = ros_tcp_endpoint.default_server_endpoint:main',
        ],
    },
)
