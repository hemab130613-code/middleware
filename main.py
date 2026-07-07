from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import time

app = FastAPI()

EMAIL = "22f2000105@ds.study.iitm.ac.in"

# Allowed Origins
origins = [
    "https://app-mb0kk4.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limit settings
RATE_LIMIT = 8
WINDOW = 10

clients = {}

@app.middleware("http")
async def request_context(request: Request, call_next):

    request_id = request.headers.get("X-Request-ID")

    if request_id is None:
        request_id = str(uuid.uuid4())

    request.state.request_id = request_id

    client = request.headers.get("X-Client-Id", "default")

    now = time.time()

    if client not in clients:
        clients[client] = []

    clients[client] = [
        t for t in clients[client]
        if now - t < WINDOW
    ]

    if len(clients[client]) >= RATE_LIMIT:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )

    clients[client].append(now)

    response = await call_next(request)

    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/ping")
async def ping(request: Request):

    return {
        "email": EMAIL,
        "request_id": request.state.request_id
    }