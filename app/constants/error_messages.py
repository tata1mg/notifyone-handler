from enum import Enum


class ErrorMessages(Enum):

    error_message = "Something went wrong"


class ApiHandler(Enum):

    HTTP_REQUEST = "Error while request for METHOD - {}, URL - {}, HEADERS - {}, AUTH - {}, PARAMS - {}"


class JsonDecode(Enum):
    DECODE = "Error while decoding json :: {}"
