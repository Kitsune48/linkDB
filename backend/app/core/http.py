from fastapi.responses import JSONResponse


def success_response(data: object, status_code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"success": True, "data": data})


def error_response(
    code: str,
    message: str,
    status_code: int,
    details: object | None = None,
) -> JSONResponse:
    payload: dict[str, object] = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if details is not None:
        payload["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=payload)
