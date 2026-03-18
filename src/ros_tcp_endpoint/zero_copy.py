#  Copyright 2020 Unity Technologies
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import struct
import mmap
import os
import tempfile
from typing import Optional, Tuple


class ZeroCopyBuffer:
    """
    Zero-copy buffer management for large message payloads (e.g., images, depth maps, point clouds).
    Uses memory mapping for efficient data transfer.
    Recommended for 2D/3D sensor streams (cameras, LiDAR, depth sensors).
    """
    
    # Size threshold for using zero-copy (512KB default, good for compressed images)
    ZERO_COPY_THRESHOLD = 512 * 1024
    
    def __init__(self, buffer_size=10 * 1024 * 1024):  # 10MB default
        """
        Initialize zero-copy buffer manager.
        
        Args:
            buffer_size: Size of the shared memory buffer in bytes
        """
        self.buffer_size = buffer_size
        self.enabled = False
        self.mmap_file = None
        self.mmap_buffer = None
        self.write_offset = 0
        
    def initialize(self):
        """Initialize the memory-mapped file for zero-copy transfers."""
        try:
            # Create a temporary file for memory mapping
            self.mmap_file = tempfile.NamedTemporaryFile(
                prefix='ros_tcp_zerocopy_',
                suffix='.bin',
                delete=False
            )
            
            # Resize the file to the buffer size
            self.mmap_file.seek(self.buffer_size - 1)
            self.mmap_file.write(b'\0')
            self.mmap_file.flush()
            
            # Create memory-mapped buffer
            self.mmap_buffer = mmap.mmap(
                self.mmap_file.fileno(),
                self.buffer_size,
                access=mmap.ACCESS_WRITE
            )
            
            self.enabled = True
            self.write_offset = 0
            return True
            
        except Exception as e:
            print(f"Failed to initialize zero-copy buffer: {e}")
            self.enabled = False
            return False
    
    def can_use_zero_copy(self, message_size: int) -> bool:
        """Check if zero-copy should be used for a message of given size."""
        return (self.enabled and 
                message_size >= self.ZERO_COPY_THRESHOLD and
                self.write_offset + message_size <= self.buffer_size)
    
    def write_message(self, data: bytes) -> Tuple[bool, int, int]:
        """
        Write message to zero-copy buffer.
        
        Args:
            data: Message data to write
            
        Returns:
            Tuple of (success, offset, size)
        """
        if not self.enabled:
            return False, 0, 0
        
        size = len(data)
        
        # Check if we have space
        if self.write_offset + size > self.buffer_size:
            # Reset to beginning (simple circular buffer)
            self.write_offset = 0
            
            if size > self.buffer_size:
                return False, 0, 0
        
        # Write data to memory-mapped buffer
        offset = self.write_offset
        self.mmap_buffer[offset:offset + size] = data
        self.write_offset += size
        
        return True, offset, size
    
    def read_message(self, offset: int, size: int) -> Optional[bytes]:
        """
        Read message from zero-copy buffer.
        
        Args:
            offset: Offset in buffer
            size: Size of message
            
        Returns:
            Message data or None if failed
        """
        if not self.enabled:
            return None
        
        if offset + size > self.buffer_size:
            return None
        
        return bytes(self.mmap_buffer[offset:offset + size])
    
    def get_buffer_path(self) -> str:
        """Get the path to the memory-mapped file."""
        if self.mmap_file:
            return self.mmap_file.name
        return ""
    
    def close(self):
        """Close and cleanup the zero-copy buffer."""
        if self.mmap_buffer:
            self.mmap_buffer.close()
            self.mmap_buffer = None
        
        if self.mmap_file:
            file_path = self.mmap_file.name
            self.mmap_file.close()
            try:
                os.unlink(file_path)
            except:
                pass
            self.mmap_file = None
        
        self.enabled = False


def serialize_zero_copy_reference(offset: int, size: int) -> bytes:
    """
    Serialize a zero-copy buffer reference.
    Format: marker (0xFF) + offset (uint64) + size (uint64)
    
    Args:
        offset: Offset in shared buffer
        size: Size of data
        
    Returns:
        Serialized reference
    """
    return struct.pack("<BQQ", 0xFF, offset, size)


def deserialize_zero_copy_reference(data: bytes) -> Optional[Tuple[int, int]]:
    """
    Deserialize a zero-copy buffer reference.
    
    Args:
        data: Serialized reference data
        
    Returns:
        Tuple of (offset, size) or None if not a zero-copy reference
    """
    if len(data) < 17:
        return None
    
    marker, offset, size = struct.unpack("<BQQ", data[:17])
    
    if marker == 0xFF:
        return offset, size
    
    return None
