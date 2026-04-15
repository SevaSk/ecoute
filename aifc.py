"""
Compatibility module for aifc functionality on Python 3.13+
This provides minimal AIFF file support to replace the removed aifc module.
"""

import struct


class Error(Exception):
    """Exception raised for aifc-related errors."""
    pass


class Aifc_read:
    """Simple AIFF reader that mimics the aifc module interface."""
    
    def __init__(self, file):
        self._file = file
        self._nchannels = 1
        self._sampwidth = 2
        self._framerate = 44100
        self._nframes = 0
        self._parseheader()
    
    def _parseheader(self):
        """Parse AIFF header (simplified implementation)."""
        try:
            # Read FORM header
            chunk_type = self._file.read(4)
            if chunk_type != b'FORM':
                raise Error("Not an AIFF file")
            
            # Skip chunk size
            self._file.read(4)
            
            # Read format type
            fmt_type = self._file.read(4)
            if fmt_type not in (b'AIFF', b'AIFC'):
                raise Error("Not an AIFF file")
            
            # Look for COMM chunk
            while True:
                chunk_id = self._file.read(4)
                if not chunk_id:
                    break
                    
                chunk_size = struct.unpack('>L', self._file.read(4))[0]
                
                if chunk_id == b'COMM':
                    self._nchannels = struct.unpack('>H', self._file.read(2))[0]
                    self._nframes = struct.unpack('>L', self._file.read(4))[0]
                    self._sampwidth = struct.unpack('>H', self._file.read(2))[0] // 8
                    
                    # Read 80-bit IEEE extended precision number (sample rate)
                    self._file.read(10)  # Skip IEEE float
                    # Simplified conversion - just use common rates
                    self._framerate = 44100
                    
                    if chunk_size > 18:  # AIFC format
                        self._file.read(chunk_size - 18)
                    break
                else:
                    # Skip other chunks
                    if chunk_size % 2:
                        chunk_size += 1
                    self._file.read(chunk_size)
        except (struct.error, IOError):
            raise Error("Invalid AIFF file")
    
    def getnchannels(self):
        return self._nchannels
    
    def getsampwidth(self):
        return self._sampwidth
    
    def getframerate(self):
        return self._framerate
    
    def getnframes(self):
        return self._nframes
    
    def readframes(self, nframes):
        # Simplified - just return empty bytes for now
        # This would need proper implementation for real AIFF reading
        return b''
    
    def close(self):
        if hasattr(self._file, 'close'):
            self._file.close()


class Aifc_write:
    """Simple AIFF writer that mimics the aifc module interface."""
    
    def __init__(self, file):
        self._file = file
        self._nchannels = 1
        self._sampwidth = 2
        self._framerate = 44100
        self._nframes = 0
        self._frames = []
    
    def setnchannels(self, nchannels):
        self._nchannels = nchannels
    
    def setsampwidth(self, sampwidth):
        self._sampwidth = sampwidth
    
    def setframerate(self, framerate):
        self._framerate = int(framerate)
    
    def writeframes(self, data):
        self._frames.append(data)
    
    def close(self):
        # Write AIFF header and data
        frames_data = b''.join(self._frames)
        self._nframes = len(frames_data) // (self._nchannels * self._sampwidth)
        
        # FORM chunk
        self._file.write(b'FORM')
        # We'll write the size later
        size_pos = self._file.tell()
        self._file.write(b'\x00\x00\x00\x00')
        self._file.write(b'AIFF')
        
        # COMM chunk
        self._file.write(b'COMM')
        self._file.write(struct.pack('>L', 18))  # COMM chunk size
        self._file.write(struct.pack('>H', self._nchannels))
        self._file.write(struct.pack('>L', self._nframes))
        self._file.write(struct.pack('>H', self._sampwidth * 8))
        
        # Sample rate as 80-bit IEEE extended (simplified)
        self._file.write(struct.pack('>HQ', 0x400E, self._framerate << 19))
        
        # SSND chunk
        self._file.write(b'SSND')
        self._file.write(struct.pack('>L', len(frames_data) + 8))
        self._file.write(b'\x00\x00\x00\x00')  # offset
        self._file.write(b'\x00\x00\x00\x00')  # block size
        self._file.write(frames_data)
        
        # Write total size
        current_pos = self._file.tell()
        self._file.seek(size_pos)
        self._file.write(struct.pack('>L', current_pos - 8))
        self._file.seek(current_pos)
        
        if hasattr(self._file, 'close'):
            self._file.close()


def open(filename, mode='rb'):
    """Open an AIFF file for reading or writing."""
    if 'r' in mode:
        if hasattr(filename, 'read'):
            return Aifc_read(filename)
        else:
            with open(filename, 'rb') as f:
                return Aifc_read(f)
    elif 'w' in mode:
        if hasattr(filename, 'write'):
            return Aifc_write(filename)
        else:
            return Aifc_write(open(filename, 'wb'))
    else:
        raise ValueError(f"Invalid mode: {mode}")