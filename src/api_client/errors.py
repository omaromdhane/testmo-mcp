import httpx

# Error scenarios:
# - RequestSendError: if request transport fails.
# - ResponseReadError: if response payload cannot be decoded.
# - ErrorResponse: if the response is not a successful status code.
# - ResponseValidationError: if the response payload does not match the expected schema.
# - APIClientError: if any other error occurs.


class APIClientError(Exception):
    """Base API client error. All errors inherit from this class."""

    request: httpx.Request | None = None
    response: httpx.Response | None = None

    def __init__(
        self,
        message: str,
        request: httpx.Request | None = None,
        response: httpx.Response | None = None,
    ):
        super().__init__(message)
        self.request = request
        self.response = response


class RequestSendError(APIClientError):
    """Raised when an HTTP request cannot be sent."""

    def __init__(self, message: str, request: httpx.Request | None = None):
        base_message = (
            "An error occurred while sending the request. Reproducible request: "
        )
        super().__init__(base_message + message, request, None)
        self.request = request


class ResponseReadError(APIClientError):
    """Raised when the API response cannot be parsed/validated."""

    def __init__(
        self,
        message: str,
        request: httpx.Request | None = None,
        response: httpx.Response | None = None,
    ):
        base_message = "An error occurred while reading the response. "
        super().__init__(base_message + message, request, response)
        self.request = request
        self.response = response


class ResponseWithError(APIClientError):
    """Raised when the response is not a successful status code."""

    def __init__(self, message: str, request: httpx.Request, response: httpx.Response):
        base_message = (
            f"HTTP {response.status_code}: {response.text} "
            f"for {request.method} {request.url}. {message}"
        )
        super().__init__(base_message, request, response)
        self.request = request
        self.response = response


class ResponseValidationError(APIClientError):
    """Raised when the response payload does not match the expected schema."""

    def __init__(self, request: httpx.Request, response: httpx.Response):
        super().__init__(
            f"Response payload did not match expected schema for {request.method} {request.url}",
            request,
            response,
        )
        self.request = request
        self.response = response
