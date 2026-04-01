from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.src.api.student_query import router as student_query_router
from backend.src.api.student_scores import router as student_router

app = FastAPI(title="Student Score API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router)
app.include_router(student_query_router)


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={
            "detail": {
                "code": "VALIDATION_ERROR",
                "message": "invalid request parameters",
                "errors": exc.errors(),
            }
        },
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
