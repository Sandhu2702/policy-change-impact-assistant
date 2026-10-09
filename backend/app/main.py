from fastapi import FastAPI

app = FastAPI(
    title="Policy Change Impact Assistant",
    description="API for tracking and querying policy changes.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "message": "Policy Change Impact Assistant API is running",
    }