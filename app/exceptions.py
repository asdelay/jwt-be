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

class ForbiddenError(AppError):
    status_code = 403
    code = "forbidden"

class BadRequestError(AppError):
    status_code = 400
    code='bad_request'