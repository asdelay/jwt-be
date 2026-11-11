class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str = "Internal error"):
        self.message = message
        super().__init__(message)

class NotFoundError(AppError):
    status_code = 404
    code = "not_found"

class AlreadyExistsError(AppError):
    status_code = 409
    code = "already_exists"

class BadRequestError(AppError):
    status_code = 400
    code='bad_request'

class UnauthorizedError(AppError):
    status_code = 401
    code="unauthorized"

    def __init__(self, message: str = "Failed to log in"):
        self.message = message
        super().__init__(message)

class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"
    def __init__(self, message: str = "Not permitted"):
        self.message = message
        super().__init__(message)