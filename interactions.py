import subprocess
import socket


def create_params() -> dict:
    git_version = subprocess.check_output(
        ['git', 'rev-parse', '--short', 'HEAD']).decode("utf-8").strip()
    hostname = socket.gethostname()
    arg_dict = {
        'version': git_version,
        'hostname': hostname
    }
    return arg_dict
