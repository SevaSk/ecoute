import subprocess
import socket


def create_params() -> dict:
    try:
        git_version = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']).decode("utf-8").strip()
    except subprocess.CalledProcessError as process_exception:
        git_version = None
        print("Error code:", process_exception.returncode)
        print("Error message:", process_exception.output)

    hostname = socket.gethostname()
    arg_dict = {
        'version': git_version,
        'hostname': hostname
    }
    return arg_dict
