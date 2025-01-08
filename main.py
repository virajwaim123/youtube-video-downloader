from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.items import router

app = FastAPI(
    title="Python YouTube Video Downloader",
    description="Download any YouTube video.",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}