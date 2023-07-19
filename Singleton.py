class Singleton(object):
    """ Restricts the instantiation of this class and all its derived classes 
    to a singular instance.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
