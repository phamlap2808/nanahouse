from enum import Enum


class ErrorType(Enum):
    INTERNAL_SERVER_ERROR = "internal_server_error"
    BAD_REQUEST = "bad_request"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    CONFLICT = "conflict"
    TOO_MANY_REQUESTS = "too_many_requests"
    UNPROCESSABLE_ENTITY = "unprocessable_entity"

class BaseException(Exception):
    error_type: ErrorType
    error_code: str
    error_message: str
    status_code: int | None = None

    @property
    def error_detail(self):
        return {
            "error_type": self.error_type.value,
            "error_code": self.error_code.value,
            "error_message": self.error_message,
        }

    def __init__(self, error_type: ErrorType, error_code: str, error_message: str, status_code: int | None = None):
        self.error_type = error_type
        self.error_code = error_code
        self.error_message = error_message
        self.status_code = status_code
        super().__init__()
