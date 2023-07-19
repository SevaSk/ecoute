import yaml
import sys
import Singleton

class Config(Singleton.Singleton):
    """A Singleton object with all configuration data
    """
    data: dict = None

    def __init__(self, filename: str = 'parameters.yaml'):
        with open(filename, mode='r', encoding='utf-8') as config_file:
            try:
                if self.data is None:
                    self.data = yaml.load(stream=config_file, Loader=yaml.CLoader)
            except ImportError as err:
                print(f'Failed to load yaml file: {filename}.')
                print(f'Error: {err}')
                sys.exit(1)

    def get_data(self) -> dict:
        return self.data
