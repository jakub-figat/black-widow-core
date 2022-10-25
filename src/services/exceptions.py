class ServiceException(Exception):
    pass


class WebsocketHandlerException(ServiceException):
    pass


class GameServiceException(ServiceException):
    pass
