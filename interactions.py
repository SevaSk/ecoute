import subprocess
import socket
import app_logging as al


root_logger = al.get_logger()


def create_params() -> dict:
    try:
        root_logger.info(create_params.__name__)
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
