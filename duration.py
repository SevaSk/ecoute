import datetime
import time


class Duration:
    """A class to measure duration of an action.
    Example usage of the class is
        with Duration('Test Operation') as measure:
            print('Performing Test operation')
            ... Do the necessary operations
            time.sleep(2)

    When the with block ends, it will print out the duration
    of the operation in the following format
        Performing Test operation
        Duration(dd:hh:ss:ms) of Test Operation 0:00:02.000826
    """

    def __init__(self, operation_name: str = 'undefined'):
        self.start: datetime.datetime = None
        self.end: datetime.datetime = None
        self.operation_name = operation_name

    def __enter__(self):
        """Records the start time of an operation
        """
        self.start = datetime.datetime.now()

    def __exit__(self, exception_type, exception_value, traceback):
        """Records the end time of an operation
        Prints the duration between start and end of an operation
        """
        self.end = datetime.datetime.now()
        print(f'Duration(dd:hh:ss:ms) of {self.operation_name} {self.end - self.start}')


if __name__ == "__main__":
    print('Start executing main...')
    with Duration('Test Operation') as measure:
        time.sleep(2)
    print('Done executing main...')
