"""
Compatibility module for audioop functionality on Python 3.13+
This provides audio processing functions to replace the removed audioop module.
"""

import struct


class error(Exception):
    """Exception raised for audioop-related errors."""
    pass


def _get_samples(data, width):
    """Convert byte data to samples based on width."""
    if width == 1:
        return list(struct.unpack('B' * len(data), data))
    elif width == 2:
        return list(struct.unpack('<' + 'h' * (len(data) // 2), data))
    elif width == 4:
        return list(struct.unpack('<' + 'i' * (len(data) // 4), data))
    else:
        raise error(f"Unsupported sample width: {width}")


def _samples_to_bytes(samples, width):
    """Convert samples to byte data based on width."""
    if width == 1:
        return struct.pack('B' * len(samples), *[max(0, min(255, s + 128)) for s in samples])
    elif width == 2:
        return struct.pack('<' + 'h' * len(samples), *[max(-32768, min(32767, s)) for s in samples])
    elif width == 4:
        return struct.pack('<' + 'i' * len(samples), *[max(-2147483648, min(2147483647, s)) for s in samples])
    else:
        raise error(f"Unsupported sample width: {width}")


def rms(data, width):
    """Return the RMS (root mean square) of the audio data."""
    if len(data) == 0:
        return 0
    
    samples = _get_samples(data, width)
    if width == 1:
        # Convert unsigned to signed for RMS calculation
        samples = [s - 128 for s in samples]
    
    sum_squares = sum(s * s for s in samples)
    mean_square = sum_squares / len(samples)
    return int(mean_square ** 0.5)


def add(data1, data2, width):
    """Add two audio data streams sample by sample."""
    min_len = min(len(data1), len(data2))
    data1_trimmed = data1[:min_len]
    data2_trimmed = data2[:min_len]
    
    samples1 = _get_samples(data1_trimmed, width)
    samples2 = _get_samples(data2_trimmed, width)
    
    if width == 1:
        samples1 = [s - 128 for s in samples1]
        samples2 = [s - 128 for s in samples2]
    
    result_samples = [s1 + s2 for s1, s2 in zip(samples1, samples2)]
    return _samples_to_bytes(result_samples, width)


def bias(data, width, bias_value):
    """Add a bias to all samples in the audio data."""
    if len(data) == 0:
        return data
    
    samples = _get_samples(data, width)
    if width == 1:
        samples = [s - 128 for s in samples]
    
    biased_samples = [s + bias_value for s in samples]
    return _samples_to_bytes(biased_samples, width)


def byteswap(data, width):
    """Swap the byte order of audio samples."""
    if width == 1:
        return data  # No swapping needed for 1-byte samples
    
    result = bytearray()
    for i in range(0, len(data), width):
        sample_bytes = data[i:i+width]
        result.extend(sample_bytes[::-1])
    
    return bytes(result)


def tomono(data, width, left_gain, right_gain):
    """Convert stereo audio to mono by mixing channels."""
    if len(data) % (width * 2) != 0:
        raise error("Data length not compatible with stereo format")
    
    mono_data = bytearray()
    sample_format = {1: 'B', 2: 'h', 4: 'i'}[width]
    
    for i in range(0, len(data), width * 2):
        left_bytes = data[i:i+width]
        right_bytes = data[i+width:i+width*2]
        
        left_sample = struct.unpack('<' + sample_format, left_bytes)[0]
        right_sample = struct.unpack('<' + sample_format, right_bytes)[0]
        
        if width == 1:
            left_sample -= 128
            right_sample -= 128
        
        mono_sample = int((left_sample * left_gain + right_sample * right_gain) / 2)
        
        if width == 1:
            mono_sample += 128
            mono_sample = max(0, min(255, mono_sample))
        elif width == 2:
            mono_sample = max(-32768, min(32767, mono_sample))
        elif width == 4:
            mono_sample = max(-2147483648, min(2147483647, mono_sample))
        
        mono_data.extend(struct.pack('<' + sample_format, mono_sample))
    
    return bytes(mono_data)


def ratecv(data, width, nchannels, inrate, outrate, state, weightA=1, weightB=0):
    """Convert the sample rate of audio data."""
    if state is None:
        state = {}
    
    if inrate == outrate:
        return data, state
    
    # Simple linear interpolation resampling
    samples = _get_samples(data, width)
    if width == 1:
        samples = [s - 128 for s in samples]
    
    # Calculate the ratio and new length
    ratio = outrate / inrate
    new_length = int(len(samples) * ratio / nchannels) * nchannels
    
    new_samples = []
    for i in range(0, new_length, nchannels):
        old_index = i / ratio
        old_index_int = int(old_index)
        
        if old_index_int < len(samples) - nchannels:
            # Linear interpolation
            frac = old_index - old_index_int
            for ch in range(nchannels):
                if old_index_int + ch < len(samples) and old_index_int + nchannels + ch < len(samples):
                    sample1 = samples[old_index_int + ch]
                    sample2 = samples[old_index_int + nchannels + ch]
                    interpolated = int(sample1 + frac * (sample2 - sample1))
                    new_samples.append(interpolated)
                else:
                    new_samples.append(samples[min(old_index_int + ch, len(samples) - 1)])
        else:
            # Use the last available samples
            for ch in range(nchannels):
                new_samples.append(samples[min(old_index_int + ch, len(samples) - 1)])
    
    return _samples_to_bytes(new_samples, width), state


def lin2lin(data, width, new_width):
    """Convert between different sample widths."""
    if width == new_width:
        return data
    
    samples = _get_samples(data, width)
    if width == 1:
        samples = [s - 128 for s in samples]
    
    # Scale samples to new width
    if width < new_width:
        # Upscaling
        scale_factor = (2 ** (new_width * 8 - 1)) / (2 ** (width * 8 - 1))
        new_samples = [int(s * scale_factor) for s in samples]
    else:
        # Downscaling
        scale_factor = (2 ** (new_width * 8 - 1)) / (2 ** (width * 8 - 1))
        new_samples = [int(s * scale_factor) for s in samples]
    
    return _samples_to_bytes(new_samples, new_width)