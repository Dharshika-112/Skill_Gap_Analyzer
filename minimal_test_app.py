"""Minimal FastAPI test app to diagnose the shutdown issue"""
from fastapi import FastAPI

app = FastAPI(title="Minimal Test App")

@app.get("/")
async def root():
    return {"status": "ok", "message": "App is running"}

@app.get("/health")
async def health():
    return {"health": "good"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001
    )
