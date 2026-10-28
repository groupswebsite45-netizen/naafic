from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.logger import logger


def setup_exception_handlers(app: FastAPI) -> None:
    """Register uniform exception handlers across the application."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"HTTP {exc.status_code} on {request.method} {request.url.path}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "status_code": exc.status_code,
                "detail": str(exc.detail),
                "error": {
                    "message": str(exc.detail),
                    "code": f"HTTP_{exc.status_code}"
                }
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.info(f"Validation error on {request.method} {request.url.path}: {exc.errors()}")
        # Extract first user friendly message
        errors = []
        for err in exc.errors():
            loc = " -> ".join([str(l) for l in err.get("loc", []) if l != "body"])
            msg = err.get("msg", "Invalid value")
            errors.append({"field": loc, "message": msg})

        first_msg = errors[0]["message"] if errors else "Invalid request data."
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "error": {
                    "message": f"Validation Error: {first_msg}",
                    "code": "VALIDATION_ERROR",
                    "details": errors
                }
            }
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled server error on {request.method} {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "error": {
                    "message": "An internal server error occurred. Please try again later.",
                    "code": "INTERNAL_SERVER_ERROR"
                }
            }
        )
