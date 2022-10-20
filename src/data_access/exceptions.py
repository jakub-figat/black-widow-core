class DataAccessException(Exception):
    pass


class DoesNotExist(DataAccessException):
    pass


class AlreadyExists(DataAccessException):
    pass
