import custom_speech_recognition as sr
import pyaudiowpatch as pyaudio
from datetime import datetime
import app_logging as al
from abc import abstractmethod

RECORD_TIMEOUT = 3
ENERGY_THRESHOLD = 1000
DYNAMIC_ENERGY_THRESHOLD = False

root_logger = al.get_logger()


# https://people.csail.mit.edu/hubert/pyaudio/docs/#id6
driver_type = {
    -1: 'Not actually an audio device',
    0: 'Still in development',
    1: 'DirectSound (Windows only)',
    2: 'Multimedia Extension (Windows only)',
    3: 'Steinberg Audio Stream Input/Output',
    4: 'SoundManager (OSX only)',
    5: 'CoreAudio (OSX only)',
    7: 'Open Sound System (Linux only)',
    8: 'Advanced Linux Sound Architecture (Linux only)',
    9: 'Open Audio Library',
    10: 'BeOS Sound System',
    11: 'Windows Driver Model (Windows only)',
    12: 'JACK Audio Connection Kit',
    13: 'Windows Vista Audio stack architecture'
}


def print_detailed_audio_info(print_func=print):
    """
    Print information about Host APIs and devices,
    using `print_func`.

    :param print_func: Print function(or wrapper)
    :type print_func: function
    :rtype: None
    """
    print_func("\n|", "~ Audio Drivers on this machine ~".center(20), "|\n")
    header = f" ^ #{'INDEX'.center(7)}#{'DRIVER TYPE'.center(13)}#{'DEVICE COUNT'.center(15)}#{'NAME'.center(5)}"
    print_func(header)
    print_func("-"*len(header))
    py_audio = pyaudio.PyAudio()
    for host_api in py_audio.get_host_api_info_generator():
        print_func(
            (
            f" » "
            f"{('['+str(host_api['index'])+']').center(8)}|"
            f"{str(host_api['type']).center(13)}|"
            f"{str(host_api['deviceCount']).center(15)}|"
            f"  {host_api['name']}"
            )
        )

    print_func("\n\n\n|", "~ Audio Devices on this machine ~".center(20), "|\n")
    header = f" ^ #{'INDEX'.center(7)}# HOST API INDEX #{'LOOPBACK'.center(10)}#{'NAME'.center(5)}"
    print_func(header)
    print_func("-"*len(header))
    for device in py_audio.get_device_info_generator():
        print_func(
            (
            f" » "
            f"{('['+str(device['index'])+']').center(8)}"
            f"{str(device['hostApi']).center(16)}"
            f"  {str(device['isLoopbackDevice']).center(10)}"
            f"  {device['name']}"
            )
        )

    # Below statements are useful to view all available fields in the
    # driver and device list
    # Do not remove these statements from here
    # print('Windows Audio Drivers')
    # for host_api_info_gen in py_audio.get_host_api_info_generator():
    #    print(host_api_info_gen)

    # print('Windows Audio Devices')
    # for device_info_gen in py_audio.get_device_info_generator():
    #    print(device_info_gen)


class BaseRecorder:
    def __init__(self, source, source_name):
        root_logger.info(BaseRecorder.__name__)
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = ENERGY_THRESHOLD
        self.recorder.dynamic_energy_threshold = DYNAMIC_ENERGY_THRESHOLD

        if source is None:
            raise ValueError("audio source can't be None")

        self.source = source
        self.source_name = source_name

    @abstractmethod
    def get_name(self):
        """Get the name of this device
        """

    def adjust_for_noise(self, device_name, msg):
        root_logger.info(BaseRecorder.adjust_for_noise.__name__)
        print(f"[INFO] Adjusting for ambient noise from {device_name}. " + msg)
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        print(f"[INFO] Completed ambient noise adjustment for {device_name}.")

    def record_into_queue(self, audio_queue):
        def record_callback(_, audio: sr.AudioData) -> None:
            data = audio.get_raw_data()
            audio_queue.put((self.source_name, data, datetime.utcnow()))

        self.recorder.listen_in_background(self.source, record_callback,
                                           phrase_time_limit=RECORD_TIMEOUT)


class DefaultMicRecorder(BaseRecorder):
    def __init__(self):
        root_logger.info(DefaultMicRecorder.__name__)
        with pyaudio.PyAudio() as p:
            # WASAPI is windows specific
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_mic = p.get_device_info_by_index(wasapi_info["defaultInputDevice"])

        self.device_info = default_mic

        source = sr.Microphone(device_index=default_mic["index"],
                               sample_rate=int(default_mic["defaultSampleRate"]),
                               channels=default_mic["maxInputChannels"]
                               )
        super().__init__(source=source, source_name="You")
        print(f'[INFO] Listening to sound from Microphone: {self.get_name()} ')
        # self.adjust_for_noise("Default Mic", "Please make some noise from the Default Mic...")

    def get_name(self):
        return self.device_info['name']


class DefaultSpeakerRecorder(BaseRecorder):
    def __init__(self):
        root_logger.info(DefaultSpeakerRecorder.__name__)
        with pyaudio.PyAudio() as p:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

            if not default_speakers["isLoopbackDevice"]:
                for loopback in p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        default_speakers = loopback
                        break
                else:
                    print("[ERROR] No loopback device found.")

        self.device_info = default_speakers

        source = sr.Microphone(speaker=True,
                               device_index=default_speakers["index"],
                               sample_rate=int(default_speakers["defaultSampleRate"]),
                               chunk_size=pyaudio.get_sample_size(pyaudio.paInt16),
                               channels=default_speakers["maxInputChannels"])
        super().__init__(source=source, source_name="Speaker")
        print(f'[INFO] Listening to sound from Speaker: {self.get_name()} ')
        self.adjust_for_noise("Default Speaker",
                              "Please make or play some noise from the Default Speaker...")

    def get_name(self):
        return self.device_info['name']


if __name__ == "__main__":
    print_detailed_audio_info()
    # Below statements are useful to view all available fields in the
    # default Input Device.
    # Do not delete these lines
    # with pyaudio.PyAudio() as p:
    #     wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
    #     print(wasapi_info)

    # with pyaudio.PyAudio() as p:
    #    wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
    #    default_mic = p.get_device_info_by_index(wasapi_info["defaultInputDevice"])
    #    print(default_mic)
